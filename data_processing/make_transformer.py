#!/usr/bin/env python3

import argparse
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
    return transformer

def pca(folder, vocab, num_blks, num_bits, min_size=5):
    files = [os.path.join(folder, x) for x in os.listdir(folder)]
    random.seed(42)
    random.shuffle(files)
    record = []
    for i in range(len(files) - num_blks, len(files)):
        graph = nx.read_gpickle(files[i])
        for node in graph.nodes(data=True):
            if len(node[1]['data']) < min_size:
                continue
            data = bag_to_vector_no_lut(list_to_bag(node[1]['data']), vocab)
            record.append(data)
    random.shuffle(record)
    data = np.asarray(record[:num_blks])
    data = np.squeeze(data)
    r, c = data.shape
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
    cs = np.cumsum(ex)
    proj = evec.T[:][:num_bits]
    proj = np.expand_dims(proj, axis=2)
    return proj

if __name__=='__main__':
    parser = argparse.ArgumentParser(description="""Tao transformer cho LSH""")
    parser.add_argument('--pca', default=None, help='PCA folder')
    parser.add_argument('--name', default='transformer.npy', help='Ten file de save')
    parser.add_argument('--vocab', help='Duong dan den vocab file', required=True)
    parser.add_argument('--bit', type=int, help='So luong bit trong (sub)label', required=True)
    parser.add_argument('--sub', type=int, default=1, help='So luong sublabels')
    parser.add_argument('--pca_blks', type=int, default=2000, help='So luong block dung de tao PCA')
    args = parser.parse_args()

    if args.pca:
        proj = pca(args.pca, args.vocab, args.bit, args.pca_blks)
    else:
        proj = random_projection(args.vocab, args.bit, args.sub)
    np.save(args.name, proj)
