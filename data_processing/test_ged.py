#!/usr/bin/env python3

import argparse
from ged import *
from ga_ged import ga
import networkx as nx
import sys
import os
import matplotlib.pyplot as plt
from calculate_wl import bag_to_vector, list_to_bag, random_hash, setup
import time
import pickle
from top10 import mean_ap, top_distance
from functools import partial


def test_graph_pair(fn, g1, g2):
    start_in = time.time()
    d = fn(g1, g2)
    end_in = time.time()
    return d, end_in-start_in

def process_graph(g):
    nx.set_edge_attributes(g, values = 1, name = 'weight')
    remove_node_list = []
    for edge in g.edges(data=True):
        edge[2]['weight'] = len(g.nodes[edge[0]]['data']) + len(g.nodes[edge[1]]['data'])
    for node in g.nodes(data=True):
        if len(node[1]['data']) == 0:
            remove_node_list.append(node[0])
            continue
        node[1]['length'] = len(node[1]['data'])
        node[1]['data'] = random_hash(bag_to_vector(list_to_bag(node[1]['data'])))
    g.remove_nodes_from(remove_node_list)
    for idx, node in enumerate(g.nodes(data=True)):
        node[1]['idx'] = idx
    return g

def test_run(fn, folder, min_node=15, max_node=20):
    file_list = [os.path.join(folder, x) for x in os.listdir(folder)]
    cnt = 2
    name = []
    for f in file_list:
        g = nx.read_gpickle(f)
        l = len(g.nodes(data=True))
        if l > min_node and l < max_node:
            name.append(f)
            cnt -= 1
            if cnt == 0:
                break
    print(name)
    g1 = nx.read_gpickle(name[0])
    # dif_end = (int(f[-1]) + 1) % 4
    # g2 = nx.read_gpickle(name[:-1]+str(dif_end))
    g2 = nx.read_gpickle(name[1])
    g1 = process_graph(g1)
    g2 = process_graph(g2)
    print(nx.get_node_attributes(g1, 'idx'))
    print(nx.get_node_attributes(g2, 'idx'))
    print(g1.edges(data=True))
    print(g2.edges(data=True))
    dist, t = test_graph_pair(fn, g1, g2)
    print(dist)
    print(t)

def generate_data(folder, saved_dir, database, num_files):
    with open(database, 'rb') as handle:
        data = pickle.load(handle)
    todo = list(data.keys())
    if not os.path.isdir(saved_dir):
        os.makedirs(saved_dir)
    if num_files > 0:
        todo = todo[:num_files]
    for path in todo:
        g = nx.read_gpickle(path)
        g = process_graph(g)
        name = os.path.join(saved_dir, os.path.basename(path))
        nx.write_gpickle(g, name)


def ged_distance(g1, g2):
    cm = node_cost_matrix(g1, g2)
    distance = ged(g1, g2, cm)[0]
    return distance

def ged_ga_distance(g1, g2):
    distance, _, _ = ga(g1, g2)
    return distance


def run_misa(f, database, ged_folder, test_num=100, neighbors=10):
    ap_list = []
    time_list = []
    result_list = {}
    with open(database, 'rb') as handle:
        data = pickle.load(handle)
    name_list = [os.path.basename(x) for x in data.keys()]
    processed_graph = {}
    for name in name_list[:1000]:
        processed_graph[name] = nx.read_gpickle(os.path.join(ged_folder, os.path.basename(name)))

    for name in name_list[:test_num]:
        start_time = time.time()
        closest_k = top_distance(f, processed_graph, processed_graph[name], neighbors, False)
        cur_map = mean_ap(name_list, closest_k, name)
        if cur_map is None:
            continue
        time_list.append(time.time() - start_time)
        result_list[name] = cur_map
        ap_list.append(cur_map)

    ma = np.mean(ap_list)
    mean_time = np.mean(time_list)
    var_time = np.var(time_list)
    no_answer = len(np.where(np.asarray(ap_list) < 0.01)[0])
    return ma, no_answer, mean_time, var_time


def main():
    parser = argparse.ArgumentParser(description="""Chay thu task retrieval su dung GED""")
    parser.add_argument('-d', '--database', help='Database da xay dung tu truoc')
    parser.add_argument('-q', '--query', type=int, default=20, help='So queries')
    parser.add_argument('-n', '--number_of_neighbors', default=10, type=int, help='So nearest neighbors duoc vote')
    parser.add_argument('-f', '--folder', help='Folder chua file simplified graph')
    parser.add_argument('-g', '--ged_folder', help='Folder chua file graph da chuyen ve dang dung duoc cho GED')
    parser.add_argument('-v', '--vocab', default='word_file_x86', help='Duong dan den vocab')
    parser.add_argument('-t', '--transformer', default='transformer.npy', help='Duong dan den LSH transformer')
    parser.add_argument('--ga', action='store_true', help='Su dung GA')
    parser.add_argument('--test', action='store_true', help='Chay test run voi mot cap graph nho')
    parser.add_argument('--num_files', type=int, default=-1, help='So luong file can chuyen hoa')
    args = parser.parse_args()
    setup(args.vocab, args.transformer)
    fn = ged_distance
    if args.ga:
        fn = ged_ga_distance

    if args.test:
        test_run(fn, args.folder)
        exit()
    if args.folder:
        generate_data(args.folder, args.ged_folder, args.database, args.num_files)
    else:
        res = run_misa(fn, args.database, args.ged_folder, args.query, args.number_of_neighbors)
        print(res)


if __name__=='__main__':
    main()
