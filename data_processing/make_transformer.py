#!/usr/bin/env python3

import numpy as np
import sys
import os
import random
import networkx as nx
from collections import defaultdict
from calculate_wl import name_to_index, bag_to_vector_no_lut, list_to_bag

def random_projection(vocab, s1, s2):
    wf = open(vocab)
    lut = name_to_index(wf.readlines())

    np.random.seed(42)
    transformer = np.random.randn(s1, len(lut), s2)
    np.save("transformer.npy", transformer)

def pca(folder, vocab, num_blks, num_bits):
    files = [os.path.join(folder, x) for x in os.listdir(folder)]
    random.seed(42)
    random.shuffle(files)
    record = []
    for i in range(len(files) - num_blks, len(files)):
        graph = nx.read_gpickle(files[i])
        for node in graph.nodes(data=True):
            if len(node[1]['data']) < 5:
                continue
            data = bag_to_vector_no_lut(list_to_bag(node[1]['data']), vocab)
            record.append(data)
    random.shuffle(record)
    print(len(record))
    data = np.asarray(record[:num_blks])
    data = np.squeeze(data)
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
    proj = evec.T[:][:num_bits]
    proj = np.expand_dims(proj, axis=2)
    print(proj.shape)
    np.save("transformer.npy", proj)
    return proj

if __name__=='__main__':
    if len(sys.argv) < 4:
        print("USAGE:\n\tmake_transformer.py <vocab_file> <number_of_bits> <number_of_sublabels>")
        exit()
    random_projection(sys.argv[1], int(sys.argv[2]), int(sys.argv[3]))
    # pca(sys.argv[1], sys.argv[2], int(sys.argv[3]), int(sys.argv[4]))
