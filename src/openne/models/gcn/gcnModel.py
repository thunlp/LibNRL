from .layers import *
from .metrics import *
import torch.nn.functional as F


class Model(torch.nn.Module):
    def __init__(self, **kwargs):
        super(Model, self).__init__()
        allowed_kwargs = {'name', 'logging', 'silent'} #
        for kwarg in kwargs.keys():
            assert kwarg in allowed_kwargs, 'Invalid keyword argument: ' + kwarg
        name = kwargs.get('name')
        if not name:
            name = self.__class__.__name__.lower()
        self.name = name

        silent = kwargs.get('silent')
        if silent:
            self.silent = True
        else:
            self.silent = False

        logging = kwargs.get('logging', False)
        self.logging = logging

        self.layers = []
        self.sequential = None

        self.input = None
        self.output = None

        self._loss = 0
        self._accuracy = 0
        self.optimizer = None

    def _build(self):
        raise NotImplementedError

    def build(self):
        self._build()

        # Build sequential layer models
        self.sequential = torch.nn.Sequential(*self.layers)
        self._optim()

    def forward(self, inputs):
        self.input = inputs
        self.output = self.sequential(inputs)
        return self.output

    def loss(self, *args):
        raise NotImplementedError

    def accuracy(self, *args):
        raise NotImplementedError

    def _optim(self):
        raise NotImplementedError

    def save(self):
        save_path = "tmp/%s.ckpt" % self.name
        torch.save(self.state_dict(), save_path)
        self.debug("Model saved in file: %s" % save_path)

    def load(self):
        save_path = "tmp/%s.ckpt" % self.name
        state_dict = torch.load(save_path)
        self.load_state_dict(state_dict)
        self.debug("Model restored from file: %s" % save_path)

    def debug(self, *args, **kwargs):
        if not self.silent:
            print(*args, **kwargs)


class GCNModel(Model):
    def __init__(self, input_dim, output_dim, hidden_dims, supports, dropout=0., weight_decay=0.,
                 num_features_nonzero=0, logging=False, sparse_inputs=False, **kwargs):
        super(GCNModel, self).__init__(**kwargs)
        self.dimensions = [input_dim]+hidden_dims+[output_dim]
        self.weight_decay = weight_decay
        self.input_dim = input_dim
        self.output_dim = output_dim
        self.supports = supports
        self.dropout = dropout
        self.logging = logging
        self.sparse_inputs = sparse_inputs
        self.num_features_nonzero = num_features_nonzero
        self.build()

    def loss(self, labels, labels_mask):
        self._loss = 0
        for i in self.parameters():
            self._loss += self.weight_decay * torch.norm(i, 2)
        self._loss += masked_softmax_cross_entropy(self.output, labels, labels_mask)
        return self._loss

    def gae_loss(self, adj_label, pos_weight, norm):
        self._loss = 0
        self._loss += norm * F.binary_cross_entropy_with_logits(torch.sigmoid(torch.mm(self.output, self.output.t())), adj_label, pos_weight=adj_label * pos_weight)

        return self._loss

    def accuracy(self, labels, labels_mask):
        self._accuracy = masked_accuracy(self.output, labels,
                                         labels_mask)
        return self._accuracy

    def _build(self):
        sparse_inputs = [False] * (len(self.dimensions) - 1)
        sparse_inputs[0] = self.sparse_inputs
        for i in range(1,len(self.dimensions)-1):
            self.layers.append(GraphConvolution(input_dim=self.dimensions[i-1],
                                                output_dim=self.dimensions[i],
                                                act=torch.relu,
                                                support=self.supports,
                                                dropout=self.dropout,
                                                sparse_inputs=sparse_inputs[i - 1],
                                                num_features_nonzero=self.num_features_nonzero,
                                                logging=self.logging))

        self.layers.append(GraphConvolution(input_dim=self.dimensions[-2],
                                            output_dim=self.dimensions[-1],
                                            act=lambda x:x,
                                            support=self.supports,
                                            dropout=self.dropout,
                                            sparse_inputs=sparse_inputs[-1],
                                            num_features_nonzero=self.num_features_nonzero,
                                            logging=self.logging))

    def _optim(self):
        self.optimizer = torch.optim.Adam(self.parameters(), lr=1e-2)
