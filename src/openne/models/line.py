from __future__ import print_function
import random
import math
import copy
import numpy as np
from sklearn.linear_model import LogisticRegression
import torch
from ..utils import *
import torch.nn as nn
import torch.nn.functional as F
from .models import *

class _LINE(ModelWithEmbeddings):
    def __init__(self, dim=128, order=2, table_size=1e8, **kwargs):
        kwargs['save'] = False
        super(_LINE, self).__init__(dim=dim, order=order, table_size=table_size, **kwargs)
        self.cur_epoch = 0
        if order == 1:
            self.loss = self.first_loss
        else:
            self.loss = self.second_loss

    @classmethod
    def check_train_parameters(cls, **kwargs):
        check_existance(kwargs, {'dim': 128,
                                 'order': 2,
                                 'table_size': 1e8,
                                 'lr': 0.001,
                                 'batch_size': 1024,
                                 'negative_ratio': 5,
                                 'data_parallel': False})
        check_range(kwargs, {'dim': 'positive',
                             'order': 'positive',
                             'table_size': 'positive',
                             'lr': 'positive',
                             'batch_size': 'positive',
                             'negative_ratio': 'positive'})

    def first_loss(self, s, h, t):
        return -(F.logsigmoid(s * (self._embeddings[h] * self._embeddings[t]).sum(dim=1))).mean()

    def second_loss(self, s, h, t):
        return -(F.logsigmoid(s*(self._embeddings[h]*self.context_embeddings[t]).sum(dim=1))).mean()

    def copy(self, exceptions):
        ret = copy.deepcopy(self)
        for i in exceptions:
            ret.__dict__.__setitem__(i, exceptions[i])
        return ret

    def build(self, graph, *, lr=0.001, batch_size=1024, negative_ratio=5, **kwargs):
        cur_seed = random.getrandbits(32)
        torch.manual_seed(cur_seed)
        self.node_size = graph.nodesize
        self._embeddings = nn.Parameter(nn.init.xavier_normal_(torch.zeros(self.node_size, self.dim)),
                                        requires_grad=True)
        self.context_embeddings = nn.Parameter(nn.init.xavier_normal_(torch.zeros(self.node_size, self.dim)),
                                               requires_grad=True)
        self.optimizer = torch.optim.Adam([self._embeddings, self.context_embeddings], lr=lr)
        look_up = graph.look_up_dict
        self.edges = [(look_up[x[0]], look_up[x[1]]) for x in graph.G.edges()]
        self.batch_size = batch_size
        self.negative_ratio = negative_ratio
        self.gen_sampling_table(graph)

    def train_model(self, graph, **kwargs):
        sum_loss = 0.0
        batches = self.batch_iter(graph.edgesize)
        batch_id = 0
        for batch in batches:
            h, t, sign = batch
            self.optimizer.zero_grad()
            cur_loss = self.loss(sign, h, t)
            sum_loss += cur_loss
            cur_loss.backward()
            self.optimizer.step()
            batch_id += 1
        self.debug_info = sum_loss

    def _get_embeddings(self, graph, **kwargs):
        self.embeddings = self._embeddings.detach()

    def batch_iter(self, data_size):
        table_size = self.table_size
        shuffle_indices = torch.randperm(data_size).tolist()
        mod = 0
        mod_size = 1 + self.negative_ratio
        h = []
        t = []
        sign = 0

        start_index = 0
        end_index = min(start_index+self.batch_size, data_size)
        while start_index < data_size:
            if mod == 0:
                sign = 1.
                h = []
                t = []
                for i in range(start_index, end_index):
                    if not random.random() < self.edge_prob[shuffle_indices[i]]:
                        shuffle_indices[i] = self.edge_alias[shuffle_indices[i]]
                    cur_h = self.edges[shuffle_indices[i]][0]
                    cur_t = self.edges[shuffle_indices[i]][1]
                    h.append(cur_h)
                    t.append(cur_t)
            else:
                sign = -1.
                t = []
                for i in range(len(h)):
                    t.append(self.sampling_table[random.randint(0, table_size-1)])
            sign = torch.tensor([sign], device=self._device)
            yield h, t, sign
            mod += 1
            mod %= mod_size
            if mod == 0:
                start_index = end_index
                end_index = min(start_index+self.batch_size, data_size)

    def gen_sampling_table(self, graph):
        table_size = int(self.table_size)
        power = 0.75
        numNodes = self.node_size

        self.debug("Pre-processing for non-uniform negative sampling!")
        node_degree = torch.zeros(numNodes)  # out degree
        look_up = graph.look_up_dict
        for edge in graph.G.edges():
            node_degree[look_up[edge[0]]] += graph.G[edge[0]][edge[1]]["weight"]

        norm = float((node_degree**power).sum())  # float is faster than tensor when visited
        node_degree = node_degree.tolist()        # list has fastest visit speed
        # torch is much slower when referring to frequent visits
        self.sampling_table = np.zeros(table_size, dtype=np.int32)
        p = 0
        i = 0
        for j in range(numNodes):
            p += math.pow(node_degree[j], power) / norm
            while i < table_size and i / table_size < p:
                self.sampling_table[i] = j
                i += 1

        data_size = graph.G.number_of_edges()
        self.edge_alias = [0 for i in range(data_size)]
        self.edge_prob = [0 for i in range(data_size)]
        large_block = [0 for i in range(data_size)]
        small_block = [0 for i in range(data_size)]
        total_sum = sum([graph.G[edge[0]][edge[1]]["weight"]
                         for edge in graph.G.edges()])
        norm_prob = [graph.G[edge[0]][edge[1]]["weight"] *
                     data_size/total_sum for edge in graph.G.edges()]
        num_small_block = 0
        num_large_block = 0
        cur_small_block = 0
        cur_large_block = 0
        for k in range(data_size-1, -1, -1):
            if norm_prob[k] < 1:
                small_block[num_small_block] = k
                num_small_block += 1
            else:
                large_block[num_large_block] = k
                num_large_block += 1
        while num_small_block and num_large_block:
            num_small_block -= 1
            cur_small_block = small_block[num_small_block]
            num_large_block -= 1
            cur_large_block = large_block[num_large_block]
            self.edge_prob[cur_small_block] = norm_prob[cur_small_block]
            self.edge_alias[cur_small_block] = cur_large_block
            norm_prob[cur_large_block] = norm_prob[cur_large_block] + \
                norm_prob[cur_small_block] - 1
            if norm_prob[cur_large_block] < 1:
                small_block[num_small_block] = cur_large_block
                num_small_block += 1
            else:
                large_block[num_large_block] = cur_large_block
                num_large_block += 1
        while num_large_block:
            num_large_block -= 1
            self.edge_prob[large_block[num_large_block]] = 1
        while num_small_block:
            num_small_block -= 1
            self.edge_prob[small_block[num_small_block]] = 1

class LINE(ModelWithEmbeddings):
    def __init__(self, dim=128, order=3, **kwargs):
        super(LINE, self).__init__(dim=dim, order=order, **kwargs)
        self.best_result = 0
        if order == 3:
            self.model1 = _LINE(dim=dim // 2, order=1, **kwargs)
            self.model2 = _LINE(dim=dim // 2, order=2, **kwargs)
        else:
            self.model = _LINE(dim=dim, order=order, **kwargs)

    @classmethod
    def check_train_parameters(cls, **kwargs):
        check_existance(kwargs, {'dim': 128,
                                 'table_size': 1e8,
                                 'lr': 0.001,
                                 'batch_size': 1024,
                                 'negative_ratio': 5,
                                 'epochs': 40,
                                 'data_parallel': False})
        check_range(kwargs, {'dim': 'positive',
                             'order': 'positive',
                             'table_size': 'positive',
                             'lr': 'positive',
                             'batch_size': 'positive',
                             'negative_ratio': 'positive',
                             'epochs': 'positive'})
        return kwargs

    def build(self, graph, **kwargs):
        if self.order == 3:
            self.model1.build(graph, **kwargs)
            self.model2.build(graph, **kwargs)
            # self.model2 = self.model1.copy({'order': 2})  # works but reduces accuracy
        else:
            self.model.build(graph, **kwargs)

    def after_build(self, graph, **kwargs):
        if self.order == 3 and kwargs.get('data_parallel', False) and len(kwargs.get('_device', [])) >= 2:
            self.model2.to(kwargs['_device'][1])

    def train_model(self, graph, **kwargs):
        if self.order == 3:
            self.model1.train_model(graph, **kwargs)
            self.model2.train_model(graph, **kwargs)
            self.debug_info = "sum of loss: {!s}".format(self.model1.debug_info + self.model2.debug_info)
        else:
            self.model.train_model(graph, **kwargs)
            self.debug_info = "sum of loss: {!s}".format(self.model.debug_info)

    def _get_embeddings(self, graph, **kwargs):
        if self.order == 3:
            self.embeddings = torch.cat((self.model1.embeddings, self.model2.embeddings), dim=1)
        else:
            self.embeddings = self.model.embeddings
            
    def make_output(self, graph, **kwargs):
        if self.order == 3:
            self.model1.make_output(graph, **kwargs)
            self.model2.make_output(graph, **kwargs)
        else:
            self.model.make_output(graph, **kwargs)
        super(LINE, self).make_output(graph, **kwargs)