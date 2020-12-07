#!/usr/bin/env python3

import pickle as pkl
from calculate_wl import label_distance, iou_distance, calculate_wl, setup
import time
import sys
from functools import partial
import numpy as np
from multiprocessing import Pool
import os
import networkx as nx
from collections import defaultdict

def calculate_distance(f, comp, item):
    k, v = item
    distance = f(comp, v)
    return (k, distance)

def top_distance(f, db, item, topk=10):
    pool = Pool(processes=8, maxtasksperchild=10)
    distance_list = pool.map(partial(calculate_distance, f, item), db.items())

    distance_data = {}
    for dl in distance_list:
        distance_data[dl[0]] = dl[1]
    closest = sorted(distance_data.items(), key=lambda x: x[1], reverse=True)
    start_idx = 0
    for i in range(len(closest)):
        if closest[i][1] < 1.0:
            start_idx = i - 1
            break
    if start_idx < 0:
        start_idx = 0
    pool.terminate()
    pool.join()
    del pool
    return closest[:start_idx+topk]

def isin(top, name):
    for idx, elem in enumerate(top):
        k, v = elem
        if k == name:
            continue
        if k[:-2] == name[:-2] and v > 0.01:
            return idx
    return None

def mean_ap(top, name, name_list):
    name = os.path.basename(name)
    relevant_doc = 0
    for i in range(4):
        relevant_name = name[:-1] + str(i)
        if relevant_name in name_list:
            relevant_doc += 1
    if relevant_doc <= 1:
        return None
    correct_so_far = 0
    num_so_far = 0
    ap = 0
    for k, v in top:
        if k == name:
            continue
        num_so_far += 1
        if k[:-2] == name[:-2]:
            correct_so_far += 1
            ap += correct_so_far * 1.0 / num_so_far
    return ap / (relevant_doc - 1)

def classify_malware(name_list, name):
    counter = defaultdict(lambda: 0)
    for n, v in name_list:
        if name == n:
            continue
        c = n.split("/")
        if c[1] == "Benign":
            counter["not_malware"] += 1
        else:
            counter["malware"] += 1
    s = sorted(counter.items(), key=lambda x: x[1], reverse=True)
    if s[0][1] == len(name_list) // 2:
        return 'unsure'
    return s[0][0]

def classify_malware_type(name_list, name):
    counter = defaultdict(lambda: 0)
    for n, v in name_list:
        if name == n:
            continue
        c = n.split("/")
        counter[c[1]] += 1
    s = sorted(counter.items(), key=lambda x: x[1], reverse=True)
    if s[0][1] == len(name_list) // 5:
        return 'unsure'
    return s[0][0]

def main():
    if len(sys.argv) < 3:
        print("USAGE:\n\ttop10.py <database_name> <folder_name> [vocab_file] [transformer_file]")
        exit()
    vocab_file = "word_file_x86"
    transformer_file = "transformer.npy"
    if len(sys.argv) > 3:
        vocab_file = sys.argv[3]
    if len(sys.argv) > 4:
        transformer_file = sys.argv[4]
    setup(vocab_file, transformer_file)

    db_name = sys.argv[1]
    classify_folder = sys.argv[2]
    with open(db_name, 'rb') as handle:
        db = pkl.load(handle)
    todo = [os.path.join(classify_folder, x) for x in os.listdir(classify_folder)]
    classify_result = {}
    for f in todo:
        start = time.clock()
        g = nx.read_gpickle(f)
        wl = calculate_wl(g)
        closest_k = top_distance(iou_distance, db, wl, 10)
        #print(closest_k)
        classify_result[f] = mean_ap(closest_k, f, db.keys())
        #classify_result[f] = classify_malware(closest_k, f)
        #classify_result[f] = classify_malware_type(closest_k, f)
    #print(classify_result)
    for name, score in classify_result.items():
        if score is not None:
            print(name + ":" + str(score))
if __name__=='__main__':
    main()
