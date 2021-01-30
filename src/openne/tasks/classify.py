# we do not need change this

from __future__ import print_function

import warnings

import numpy
import torch
from sklearn.multiclass import OneVsRestClassifier # data training. TODO: write a PyTorch version of OVRClassifier
from sklearn.metrics import f1_score  # data process
from sklearn.preprocessing import MultiLabelBinarizer # data process
from time import time


class TopKRanker(OneVsRestClassifier):
    def predict(self, X, top_k_list):
        probs = torch.tensor(super(TopKRanker, self).predict_proba(numpy.asarray(X)))  # assume X as a Tensor
        all_labels = []
        for i, k in enumerate(top_k_list):
            probs_ = probs[i, :]
            labels = self.classes_[probs_.argsort()[-k:]].tolist()
            probs_[:] = 0
            probs_[labels] = 1          # mark top k labels
            all_labels.append(probs_)
        return torch.stack(all_labels)  # return a Tensor


class Classifier(object):

    def __init__(self, vectors, clf, simple=False, silent=False):
        self.embeddings = vectors
        self.clf = TopKRanker(clf)
        self.binarizer = MultiLabelBinarizer(sparse_output=True)
        if simple:
            self.f1cat = 2
        else:
            self.f1cat = 4
        self.silent = silent

    def train(self, X, Y, Y_all):
        self.binarizer.fit(Y_all)
        X_train = torch.stack([self.embeddings[x] for x in X])
        Y = self.binarizer.transform(Y)  # lhs Y a numpy array
        self.clf.fit(X_train, Y)

    def evaluate(self, X, Y):  # X Y tensor
        top_k_list = [len(l) for l in Y]
        Y_ = self.predict(X, top_k_list)  # Y_ Tensor
        Y = self.binarizer.transform(Y)  # Y  np array
        averages = ["micro", "macro", "samples", "weighted"][:self.f1cat]
        results = {}

        for average in averages:
            if self.silent:
                with warnings.catch_warnings():
                    warnings.simplefilter("ignore")
                    results[average] = f1_score(Y, numpy.asarray(Y_), average=average)
            else:
                results[average] = f1_score(Y, numpy.asarray(Y_), average=average)
        if not self.silent:
            print(results)
        return results

    def predict(self, X, top_k_list):
        X_ = torch.stack([self.embeddings[x] for x in X])
        Y = self.clf.predict(X_, top_k_list=top_k_list)
        return Y

    def train_and_evaluate(self, graph, train_percent, seed=None):
        X_train, Y_train, _, _, X_test, Y_test = graph.get_split_data(train_percent, seed=seed)
        self.train(X_train, Y_train, graph.labels()[1])
        return self.evaluate(X_test, Y_test)


def load_embeddings(filename):
    fin = open(filename, 'r')
    node_num, size = [int(x) for x in fin.readline().strip().split()]
    vectors = {}
    while 1:
        l = fin.readline()
        if l == '':
            break
        vec = l.strip().split(' ')
        assert len(vec) == size+1
        vectors[vec[0]] = [float(x) for x in vec[1:]]
    fin.close()
    assert len(vectors) == node_num
    return vectors


def read_node_label(filename):
    fin = open(filename, 'r')
    X = []
    Y = []
    while 1:
        l = fin.readline()
        if l == '':
            break
        vec = l.strip().split(' ')
        X.append(vec[0])
        Y.append(vec[1:])
    fin.close()
    return X, Y
