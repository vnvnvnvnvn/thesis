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

def load_lut(vocab_file):
    global lut
    with open(vocab_file) as wf:
        lut = name_to_index(wf.readlines())
    return lut

def load_transformer(name):
    global transformer
    with open(name, 'rb') as f:
        transformer = np.load(f)
    return transformer

def bag_to_vector(bag):
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
        bag[l] += 1
        # bag[l] = 1
    return bag

def random_hash(vector):
    new_vector = (np.dot(vector, transformer.T) > 0).astype('int')
    h = [''.join([str(y) for y in x]) for x in new_vector[0]]
    h = tuple(h)
    return h

def add_bag(graph, node):
    s = graph.nodes[node]['data']
    for n in graph[node]:
        s += graph.nodes[n]['data']
    return s

def normalise(A):
    lengths = ((A**2).sum(axis=1, keepdims=True)**.5)
    return A/lengths

def calculate_wl(graph, k=4):
    wl = {}
    for i in range(k):
        for node in graph.nodes(data='data'):
            if node[1] is None or len(node[1]) == 0:
                continue
            else:
                data = bag_to_vector(list_to_bag(node[1]))
            h = random_hash(data)
            # h = tuple(*data.astype(int))
            if h in wl.keys():
                wl[h] += 1
            else:
                wl[h] = 1
        for node in graph:
            graph.nodes[node]['neighbors'] = add_bag(graph, node)
        for node in graph:
            graph.nodes[node]['data'] = graph.nodes[node]['neighbors']
    return wl

def cosine_sim(p, q):
    return np.dot(p, q)

def hashing_sim(p, q):
    cnt = 2
    for a, b in zip(p, q):
        if a == b:
            cnt -= 1
    if cnt < 0:
        cnt = 0
    return cnt

def orig_distance(f, thres, w1, w2):
    dot = 0
    scale = 0
    for k1 in w1.keys():
        for k2 in w2.keys():
            scale += 1
            if f(k1, k2) >= thres:
                dot += 1 #w1[k1] * w2[k2]
                scale -= 1
    return dot * 1.0 / scale

def label_distance(w1, w2):
    same = set(w1.keys()).intersection(set(w2.keys()))
    dot = 0
    for s in same:
        dot += w1[s] * w2[s]
    scale = sqrt(sum(np.square(np.array(list(w1.values())))) *
                 sum(np.square(np.array(list(w2.values())))))
    return dot / scale

def iou_distance(w1, w2):
    same = set(w1.keys()).intersection(set(w2.keys()))
    dot = len(same)
    scale = len(set(w1.keys()).union(set(w2.keys()))) * 1.0
    return dot / scale

def build_database(file_list, n=10000):
    database = {}
    cnt = 0
    for i in range(len(file_list)):
        graph = nx.read_gpickle(file_list[i])
        if len(graph) < 10:
            continue
        w = calculate_wl(graph)
        if len(w) == 0:
            continue
        cnt += 1
        database[file_list[i]] = w
        if i % 500 == 0:
            print("Finished with file " + str(i))
        if cnt >= n:
            break
    return database

def generate_file_list(folder):
    files = os.listdir(folder)
    files.sort()
    return files

def generate_file_list_nested(folder):
    import random
    random.seed(42)
    files = []
    for subdir in os.listdir(folder):
        subdir_path = os.path.join(folder, subdir)
        files += [os.path.join(subdir_path, x) for x in os.listdir(subdir_path)]
    random.shuffle(files)
    return files

def main():
    vocab_file = "word_file_x86"
    transformer = "transformer.npy"
    db_name = "wl_db.pkl"

    if len(sys.argv) > 2:
        db_name = sys.argv[2]
    if len(sys.argv) > 3:
        vocab_file = sys.argv[3]
    load_lut(vocab_file)
    if len(sys.argv) > 4:
        transformer = sys.argv[4]
    load_transformer(transformer)

    file_list = generate_file_list_nested(sys.argv[1])
    db = build_database(file_list)
    for k, v in db.items():
        print(k)
        print(v)
        break
    with open(db_name, 'wb') as handle:
        pkl.dump(db, handle)

if __name__=='__main__':
    main()
