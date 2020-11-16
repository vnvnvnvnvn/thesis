#!/usr/bin/env python

from collections import defaultdict
from sparse_vector import SparseVector
import sys
from sklearn import random_projection
import numpy as np
from numpy.linalg import norm
import networkx as nx
import pickle as pkl
from math import sqrt
import os
from itertools import product
import scipy.stats as st
import matplotlib.pyplot as plt
import random
from distance import hamming
import copy

transformer = None
lut = None

def name_to_index(data):
    data.sort()
    lut = {}
    for i, d in enumerate(data):
        lut[d.strip()] = i
    return lut

def bag_to_vector(bag):
    global lut
    if lut is None:
        wf = open("word_file_arm")
        lut = name_to_index(wf.readlines())
    sv = np.zeros((1, len(lut)))
    for k, v in bag.items():
        try:
            sv[0][lut[k]] = v
        except:
            continue
    return sv

def list_to_bag(ls):
    bag = defaultdict(lambda: 0)
    for l in ls:
        # bag[l] += 1
        bag[l] = 1
    return bag

def random_hash(vector):
    # print(vector.shape)
    new_vector = vector.astype('int')
    return ''.join([str(x) for x in new_vector[0]])
    global transformer
    if transformer is None:
        # random.seed(42)
        # transformer = np.random.randn(32, len(lut)) #random_projection.SparseRandomProjection(32)
        # np.save("transformer.npy", transformer)
        with open("transformer.npy", 'rb') as f:
            transformer = np.load(f)
    # new_vector = transformer.fit_transform(vector)
    # new_vector = np.where(new_vector > 0, 1, 0)[0]
    # new_vector = np.dot(vector, transformer.T)
    new_vector = (np.dot(vector, transformer.T) > 0).astype('int')
    h = ''.join([str(x) for x in new_vector])
    return h #new_vector

def pca(data):
    print(data.shape)
    data = np.reshape(data, data.shape[:2])
    r, c = data.shape
    print(data.shape)
    res = np.zeros((r, c))
    tmp = np.zeros(r)
    for col in range(c):
        m = np.mean(data[:, col])
        v = np.std(data[:, col])
        nv = (data[:, col] - m) / (v + 1e-10)
        res[:, col] = nv
    cov = np.cov(res.T)
    ev, evec = np.linalg.eig(cov)
    ex = []
    sev = sum(ev)
    for i in ev:
        ex.append(i/sev*100)
    print(ex)
    cs = np.cumsum(ex)
    print(cs)
    proj = (evec.T[:][:32])
    return proj

def hash_distance(folder, n=100):
    global transformer
    files = [os.path.join(folder, x) for x in os.listdir(folder)]
    before = []
    test = []
    after = []
    before_dist = []
    after_dist = []
    for i in range(n):
        graph = nx.read_gpickle(files[i])
        for node in graph.nodes(data=True):
            if len(node[1]['data']) == 0:
                continue
            d = bag_to_vector(list_to_bag(node[1]['data']))
            # if i < n*9:
                # before.append(copy.deepcopy(d[0]))
            # else:
            test.append(copy.deepcopy(d[0]))
            # h = random_hash(d)
            # after.append(copy.deepcopy(h))
    def normalise(A):
        lengths = ((A**2).sum(axis=1, keepdims=True)**.5)
        return A/lengths
    # before = np.asarray(before)
    # print(before.shape)
    # normed_before = normalise(before)
    # print(normed_before)
    def cosine_sim(p, q):
        return np.dot(p, q)
    # plt.hist(s, density=True, bins=32)
    # plt.show()
    # transformer = pca(np.asarray(copy.deepcopy(normed_before)))

    normed_test = normalise(np.asarray(test))
    print(normed_test.shape)
    for b in normed_test:
        h = random_hash(b.T)
        after.append(copy.deepcopy(h))
    # normed_after = normalise(np.asarray(after))
    s = list(map(lambda x: cosine_sim(x[0], x[1]), product(normed_test, normed_test)))
    a = list(map(lambda x:
                 # [hamming(x[0][(y-1)*32:y*32], x[1][(y-1)*32:y*32]) for y in range(1,5)],
                 hamming(x[0], x[1]),
                 product(after, after)))
    # a = list(map(lambda x: cosine_sim(x[0], x[1]), product(normed_after, normed_after)))
    # for i, j in product(range(len(before)), range(len(before))):
    #     before_dist.append(cosine_sim(before[i][0], before[j][0]))
    #     after_dist.append(hamming(after[i], after[j]))
    # plt.scatter(s, a)
    # plt.show()
    a = np.asarray(a)
    print(a.shape)
    same_label = 0
    high_score_09 = 0
    high_score_095 = 0
    same_high = 0

    for bh, ah in zip(s, a):
        if bh >= 0.9:
            high_score_09 += 1
        if bh >= 0.95:
            high_score_095 += 1
        if any([ahx == 0 for ahx in ah]):
            same_label += 1
        if bh >= 0.9 and any([ahx == 0 for ahx in ah]):
            same_high += 1
        # if bh >= 0.9 and any([ahx == 0 for ahx in ah]):
        #     same_high += 1
        #     same_label += 1
        #     high_score += 1
        # elif bh >= 0.9:
        #     high_score += 1
        # elif any([ahx == 0 for ahx in ah]) and bh < 0.9:
        #     same_label += 1
    print(len(s))
    print(same_high)
    print(same_label)
    print(high_score_095)
    print(high_score_09)
    precision = same_high * 1.0 / same_label
    recall = same_high * 1.0 / high_score_09
    print(precision)
    print(recall)

def add_bag(graph, node):
    s = graph.nodes[node]['data']
    for n in graph[node]:
        s += graph.nodes[n]['data']
    return s

def calculate_wl(path, k=4):
    graph = nx.read_gpickle(path)
    if len(graph) == 0:
        return {}
    wl = {}
    for i in range(k):
        for node in graph.nodes(data='data'):
            if node[1] is None or len(node[1]) == 0:
                # graph.nodes[node[0]]['data'] = bag_to_vector({})
                # data = bag_to_vector({})
                continue
            else:
                data = bag_to_vector(list_to_bag(node[1]))
            h = random_hash(data)
            # print(h)
            if h in wl.keys():
                wl[h] += 1
            else:
                wl[h] = 1
        for node in graph:
            graph.nodes[node]['neighbors'] = add_bag(graph, node)
        for node in graph:
            graph.nodes[node]['data'] = graph.nodes[node]['neighbors']
    return wl

def label_distance(w1, w2):
    same = set(w1.keys()).intersection(set(w2.keys()))
    scale = sqrt(sum(np.square(np.array(w1.values()))) *
                 sum(np.square(np.array(w2.values()))))
    dot = 0
    for s in same:
        dot += w1[s] * w2[s]
    return dot / scale

def build_database(path, n=10000):
    database = {}
    files = os.listdir(path)
    files.sort()
    saved_w = {}
    for i in range(n):
        print(files[i])
        w = calculate_wl(os.path.join(path, files[i]))
        if files[i] == "arlex_yylex_destroy_0":
            saved_w = w
        if len(w) == 0:
            continue
        database[files[i]] = w
    return database, saved_w

def main():
    # hash_distance(sys.argv[1])
    db_name = "wl_db.pkl"
    if not os.path.isfile(db_name):
        db, w = build_database(sys.argv[1])
        with open("wl_db.pkl", 'wb') as handle:
            pkl.dump(db, handle)
        print(w)
    else:
        handle = open(db_name, 'rb')
        db = pkl.load(handle)
        w = calculate_wl(sys.argv[1])
        print(w)
    distance_list = {}
    for k, v in db.items():
        distance_list[k] = label_distance(v, w)
    closest = sorted(distance_list.items(), key=lambda x: x[1], reverse=True)
    print(closest[:10])

if __name__=='__main__':
    main()
