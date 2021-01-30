import warnings

from .tasks import BaseTask
from .classify import Classifier
from ..utils import *
from ..models import ModelWithEmbeddings
from sklearn.linear_model import LogisticRegression

class UnsupervisedNodeClassification(BaseTask):
    def __init__(self, **kwargs):
        super(UnsupervisedNodeClassification, self).__init__(**kwargs)

    def check(self, modelclass, datasetclass):
        assert(issubclass(modelclass, ModelWithEmbeddings))
        self.kwargs = modelclass.check(datasetclass, **self.train_kwargs())

    def train_kwargs(self):
        #  by default validate == False
        #  validate is always false
        check_existance(self.kwargs, {"_validate": False, "_no_validate": False})
        check_existance(self.kwargs, {"validate": False, 'clf_ratio': 0.5})


        def f_v(model, graph, **kwargs):
            model.make_output(graph, **kwargs)
            model._get_vectors(graph)

            res = self._classify(graph, model.vectors, simple=True, silent=True)
            if model.setvalue('best_result', res['macro']):
                if kwargs['auto_save']:
                    model.setvalue('best_vectors', model.vectors, lambda x, y: True)
            model.debug_info += "; val_acc = {}".format(res)

        check_existance(self.kwargs, {'auto_save': True, '_validation_hooks': [f_v] if self.kwargs['validate'] else []})
        super(UnsupervisedNodeClassification, self).train_kwargs()
        return self.kwargs

    def evaluate(self, model, res, graph):
        return self._classify(graph, res, 0)

    def _classify(self, graph, vectors, seed=None, simple=False):
        self.debug("Training classifier using {:.2f}% nodes...".format(
                self.kwargs['clf_ratio']*100))
        clf = Classifier(vectors=vectors, clf=LogisticRegression(solver='lbfgs'), simple=simple, silent=self.kwargs['silent'])
        return clf.train_and_evaluate(graph, self.train_kwargs()['clf_ratio'], seed=seed)