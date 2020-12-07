#!/usr/bin/env python3

from collections import defaultdict
import sys
import numpy as np
from numpy.linalg import norm
import networkx as nx
import pickle as pkl
from math import sqrt
import os
from itertools import product
import matplotlib.pyplot as plt
import random
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
    with open(vocab_file) as wf:
        lut = name_to_index(wf.readlines())
    return lut

def load_transformer(name):
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

def bag_to_vector_no_lut(bag, vocab_name):
    lut = load_lut(vocab_name)
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
    return bag

def random_hash(vector):
    new_vector = (np.dot(vector, transformer.T) > 0).astype('int')
    h = [''.join([str(y) for y in x]) for x in new_vector[0]]
    h = tuple(h)
    return h

def random_hash_no_transformer(vector, transform_file):
    transformer = load_transformer(transform_file)
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

def calculate_wl(graph, k=1):
    wl = {}
    for i in range(k):
        for node in graph.nodes(data='data'):
            if node[1] is None or len(node[1]) == 0:
                continue
            else:
                data = bag_to_vector(list_to_bag(node[1]))
            h = random_hash(data)
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
                dot += 1
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

def build_database(file_list, n=12000):
    database = {}
    cnt = 0
    for i in range(len(file_list)):
        graph = nx.read_gpickle(file_list[i])
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
        if subdir == "Benign":
            continue
        subdir_path = os.path.join(folder, subdir)
        files += [os.path.join(subdir_path, x) for x in os.listdir(subdir_path)]
    random.shuffle(files)
    benign_files = [os.path.join(folder, "Benign", x) for x in os.listdir(os.path.join(folder, "Benign"))]
    benign_files += files
    return benign_files

def setup(vocab_file, transformer_file):
    global transformer, lut
    lut = load_lut(vocab_file)
    transformer = load_transformer(transformer_file)

def main():
    if len(sys.argv) < 2:
        print("USAGE:\n\tcalculate_wl.py <folder> [database_name] [vocab_file] [transformer_file]\n\tcalculate_wl.py <file_name>")
        exit()

    vocab_file = "word_file_x86"
    transformer_file = "transformer.npy"
    db_name = "wl_db.pkl"
    if os.path.isdir(sys.argv[1]):
        if len(sys.argv) > 2:
            db_name = sys.argv[2]
        if len(sys.argv) > 3:
            vocab_file = sys.argv[3]
        if len(sys.argv) > 4:
            transformer_file = sys.argv[4]
        setup(vocab_file, transformer_file)
        file_list = generate_file_list_nested(sys.argv[1])
        # file_list = generate_file_list(sys.argv[1])
        db = build_database(file_list)
        with open(db_name, 'wb') as handle:
            pkl.dump(db, handle)
    else:
        if len(sys.argv) > 2:
            vocab_file = sys.argv[2]
        if len(sys.argv) > 3:
            transformer_file = sys.argv[3]
        setup(vocab_file, transformer_file)
        g = nx.read_gpickle(sys.argv[1])
        wl = calculate_wl(g)
        print(wl)

if __name__=='__main__':
    main()
