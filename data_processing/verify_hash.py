#!/usr/bin/env python3

import argparse
import sys
import numpy as np
import networkx as nx
from distance import hamming
import os
from collections import defaultdict
import copy
import pickle as pkl
import time
import random
from calculate_wl import setup, bag_to_vector, list_to_bag, random_hash
from itertools import islice


def generate_block(dbname, num_blks, folder, nested, min_size=3):
    record = []
    files = []

    if nested:
        for subdir in os.listdir(folder):
            subdir_path = os.path.join(folder, subdir)
            files += [os.path.join(subdir_path, x) for x in os.listdir(subdir_path)]
    else:
        files = [os.path.join(folder, x) for x in os.listdir(folder)]

    random.shuffle(files)
    for name in islice(files, num_blks):
        graph = nx.read_gpickle(name)
        for node in graph.nodes(data=True):
            if len(node[1]['data']) < min_size:
                continue
            data = bag_to_vector(list_to_bag(node[1]['data']))
            record.append(data)
    random.shuffle(record)
    all_data = np.asarray(record[:num_blks])
    with open(dbname, 'wb') as handle:
        pkl.dump(all_data, handle)


def hashing_sim_half(p, q):
    cnt = max(len(q) / 2, 1)
    for a, b in zip(p, q):
        if a == b:
            cnt -= 1
        if cnt == 0:
            return cnt
    return cnt

def hashing_sim_or(p, q):
    for a, b in zip(p, q):
        if a == b:
            return 0
    return 1

def hash_distance(fn, sim_file, sensitivity=0.9):
    hashed_blks = []
    with open(sim_file, 'rb') as f:
        vectorized_blks = pkl.load(f)

    vectorized_blks = np.squeeze(vectorized_blks)
    def normalise(A):
        lengths = ((A**2).sum(axis=1, keepdims=True)**.5)
        return A/(lengths + 1e-10)
    def cosine_sim(p, q):
        return np.dot(p, q.T)


    hash_convert_time = 0
    normed_test = normalise(np.asarray(vectorized_blks))
    for b in normed_test:
        start = time.clock()
        h = random_hash(np.expand_dims(b, axis=0))
        end = time.clock()
        hash_convert_time += (end - start)
        hashed_blks.append(copy.deepcopy(h))

    average_conversion_time = hash_convert_time / len(normed_test)
    print("Average conversion time:" + str(average_conversion_time))

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
            hash_dist = fn(hashed_blks[i], hashed_blks[j])
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

    print(sim_file + ": (" + str(precision)+", "+str(recall)+")")
    print(f1)
    print("Average time for cosine "+ str(cosine_time / total_pairs))
    print("Average time for hash "+ str(hash_time / total_pairs))
    return precision, recall, f1

def main():
    parser = argparse.ArgumentParser(description="""Tinh precision va recall cua cac cach gan nhan voi so bit khac nhau""")
    parser.add_argument('--folder', help='Duong dan den folder can xu li')
    parser.add_argument('--database', help='Ten cua database ket qua', required=True)
    parser.add_argument('-n', '--number_of_blocks', default=2000, type=int, help='So luong blocks se co trong database')
    parser.add_argument('--nested', default=False, type=bool, help='Folder da cho co nested khong')
    parser.add_argument('--vocab', default='word_file_x86', help='Duong dan den vocab')
    parser.add_argument('--transformer', default='transformer.npy', help='Duong dan den LSH transformer')
    parser.add_argument('-s', '--sensitivity', default=0.9, type=float, help='Min cosine distance de coi hai nhan la giong nhau')
    parser.add_argument('--half', default=True, type=bool, help='Hai nhan tinh la giong nhau neu mot nua so sublabel giong nhau (True) hay mot nhan con giong nhau (False)')
    args = parser.parse_args()
    setup(args.vocab, args.transformer)
    if args.folder:
        generate_block(args.database, args.number_of_blocks, args.folder, args.nested)
    else:
        if args.half:
            fn = hashing_sim_half
        else:
            fn = hashing_sim_or
        hash_distance(fn, args.database, args.sensitivity)


if __name__=='__main__':
    main()
