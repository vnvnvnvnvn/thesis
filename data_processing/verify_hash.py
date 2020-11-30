#!/usr/bin/env python

import sys
import numpy as np
import networkx as nx
from distance import hamming
import os
from collections import defaultdict
import copy
import pickle as pkl
import time

transformer_file = "transformer.npy"
word_file = "vs_word_file"
lut = None
transformer = None

def name_to_index(data):
    data.sort()
    lut = {}
    for i, d in enumerate(data):
        lut[d.strip()] = i
    return lut

def bag_to_vector(bag):
    global lut
    if lut is None:
        wf = open(word_file)
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
        bag[l] += 1
    return bag

def random_hash(vector):
    global transformer
    if transformer is None:
        with open(transformer_file, 'rb') as f:
            transformer = np.load(f)
    new_vector = (np.dot(vector, transformer.T) > 0).astype('int')
    # h = ''.join([str(x) for x in new_vector.reshape(np.prod(new_vector.shape))])
    h = [''.join([str(y) for y in x]) for x in new_vector]
    return h


def hash_distance(sim_file, sensitivity=0.9):
    # files = [os.path.join(folder, x) for x in os.listdir(folder)]
    # test = []
    # after = []
    # current_blk_cnt = 0
    # for i in range(n):
    #     if current_blk_cnt >= max_blk_cnt:
    #         break
    #     graph = nx.read_gpickle(files[i])
    #     for node in graph.nodes(data=True):
    #         if len(node[1]['data']) == 0:
    #             continue
    #         d = bag_to_vector(list_to_bag(node[1]['data']))
    #         test.append(copy.deepcopy(d[0]))
    #         current_blk_cnt += 1
    # print(current_blk_cnt)
    after = []
    with open(sim_file, 'rb') as f:
        vectorized_blks = pkl.load(f)

    vectorized_blks = np.squeeze(vectorized_blks)
    print(vectorized_blks.shape)

    def normalise(A):
        lengths = ((A**2).sum(axis=1, keepdims=True)**.5)
        return A/lengths
    def cosine_sim(p, q):
        return np.dot(p, q)

    def hashing_sim(p, q):
        cnt = max(len(q) / 2, 1)
        for a, b in zip(p, q):
            if a == b:
                cnt -= 1
            # d.append(hamming(a, b))
        # d.sort()
        if cnt < 0:
            cnt = 0
        return cnt #sum(d[:2]) / 2

    hash_convert_time = 0
    normed_test = normalise(np.asarray(vectorized_blks))
    for b in normed_test:
        start = time.clock()
        h = random_hash(b)
        end = time.clock()
        hash_convert_time += (end - start)
        after.append(copy.deepcopy(h))

    average_conversion_time = hash_convert_time / len(normed_test)
    print(average_conversion_time)
    print(len(normed_test))
    print(len(after[0]))
    print(len(after[0][0]))
    high_score = 0
    same_label = 0
    same_high = 0

    cosine_time = 0
    hash_time = 0
    total_pairs = 0

    for i in range(len(normed_test)):
        for j in range(i + 1, len(normed_test)):
            start_cosine = time.clock()
            orig_dist = cosine_sim(normed_test[i], normed_test[j])
            end_cosine = time.clock()
            hash_dist = hashing_sim(after[i], after[j])
            end_hash = time.clock()
            cosine_time += (end_cosine - start_cosine)
            hash_time += (end_hash - end_cosine)
            total_pairs += 1
            if orig_dist >= sensitivity:
                high_score += 1
            if hash_dist == 0:
                same_label += 1
            if orig_dist >= sensitivity and hash_dist == 0:
                same_high += 1

    precision = same_high * 1.0 / same_label
    recall = same_high * 1.0 / high_score
    f1 = 2 * precision * recall / (precision + recall)
    print(high_score)
    print("(" + str(precision)+", "+str(recall)+")")
    # print(recall)
    print(f1)
    print(total_pairs)
    print("Average time for cosine "+ str(cosine_time / total_pairs))
    print("Average time for hash "+ str(hash_time / total_pairs))

def main():
    hash_distance(sys.argv[1], 0.95)

if __name__=='__main__':
    main()
