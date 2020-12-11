#!/usr/bin/env python3

import argparse
import pickle as pkl
from calculate_wl import label_distance, iou_distance, tf_distance, calculate_wl, setup
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

def top_distance(f, db, item, topk=10, reverse=True):
    pool = Pool(processes=8, maxtasksperchild=10)
    distance_list = pool.map(partial(calculate_distance, f, item), db.items())

    distance_data = {}
    for dl in distance_list:
        distance_data[dl[0]] = dl[1]
    closest = sorted(distance_data.items(), key=lambda x: x[1], reverse=reverse)
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

def mean_ap(name_list, top, name):
    # name = os.path.basename(name)
    relevant_doc = 0
    for i in range(4):
        relevant_name = name[:-1] + str(i)
        if relevant_name in name_list:
            relevant_doc += 1
    if relevant_doc <= 2:
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
        if c[-2] == "Benign":
            counter["not_malware"] += 1
        else:
            counter["malware"] += 1
    s = sorted(counter.items(), key=lambda x: x[1], reverse=True)
    if s[0][1] <= len(name_list) // 2:
        return 'unsure'
    return s[0][0]

def classify_malware_type(name_list, name):
    counter = defaultdict(lambda: 0)
    for n, v in name_list:
        if name == n:
            continue
        c = n.split("/")
        counter[c[-2]] += 1
    s = sorted(counter.items(), key=lambda x: x[1], reverse=True)
    if s[0][1] <= len(name_list) // 5:
        return 'unsure'
    return s[0][0]

def main():
    parser = argparse.ArgumentParser(description="""Chay thu mot so task (classification, detection, retrieval) cho mot file""")
    parser.add_argument('-t', '--task', choices=['detect', 'classify', 'retrieve'], default='detect', help='Task muon thu')
    parser.add_argument('-d', '--database', help='Database da xay dung tu truoc', required=True)
    parser.add_argument('--number_of_neighbors', default=10, type=int, help='So nearest neighbors duoc vote')
    parser.add_argument('--distance_type', choices=['iou', 'cosine', 'idf'], default='iou', help='Phep tinh do tuong dong')
    parser.add_argument('--idf_database', help='Database IDF tuong ung voi database dung de thu nghiem, chi can thiet neu dung distance_type la idf')
    parser.add_argument('-f', '--folder', help='Folder chua file simplified graph')
    parser.add_argument('--file', action='append', help='File can xu ly')
    parser.add_argument('--arch', choices=['arm', 'x86'], default='x86', help='Architecture')
    parser.add_argument('--vocab', default='word_file_x86', help='Duong dan den vocab')
    parser.add_argument('--transformer', default='transformer.npy', help='Duong dan den LSH transformer')
    args = parser.parse_args()

    setup(args.vocab, args.transformer)

    with open(args.database, 'rb') as handle:
        db = pkl.load(handle)

    if args.folder:
        todo = [os.path.join(args.folder, x) for x in os.listdir(args.folder)]
    if args.file:
        todo = args.file

    fn_lookup = {
        'iou': iou_distance,
        'cosine': label_distance,
        'idf': tf_distance
    }

    task_lookup = {
        'classify': classify_malware_type,
        'detect': classify_malwarem,
        'retrieve': partial(mean_ap, db.keys())
    }

    if args.distance_type == 'idf':
        if args.idf_database is None:
            print("Need IDF database with this distance type")
            exit(1)
        with open(args.idf_database, 'rb') as handle:
            idf_database = pkl.load(handle)
        fn_lookup['idf'] = partial(tf_distance, idf_database)

    result = {}
    for f in todo:
        g = nx.read_gpickle(f)
        wl = calculate_wl(g)
        closest_k = top_distance(fn_lookup[args.distance_type], db, wl, topk=args.number_of_neighbors)
        result[f] = task_lookup[args.task](closest_k, f)
    for name, score in result.items():
        if score is not None:
            print(name + ":" + str(score))


if __name__=='__main__':
    main()
