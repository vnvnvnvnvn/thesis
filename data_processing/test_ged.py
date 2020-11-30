#!/usr/bin/env python

from ged import *
import networkx as nx
import sys
import os
import matplotlib.pyplot as plt
from calculate_wl import bag_to_vector, list_to_bag, random_hash, load_lut, load_transformer
import time
import pickle
from top10 import mean_ap
from concurrent.futures import ProcessPoolExecutor
from functools import partial

def test_graph(g1, g2):
    start = time.clock()
    cm = node_cost_matrix(g1, g2)
    end = time.clock()
    ged(g1, g2, cm)
    print((end-start) * 10000)

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

def test_run(folder):
    file_list = [os.path.join(folder, x) for x in os.listdir(folder)]
    for f in file_list:
        g = nx.read_gpickle(f)
        if len(g.nodes()) > 5 and len(g.nodes()) < 10:
            name = f
            break
    print(name)
    g1 = nx.read_gpickle(name)
    dif_end = (int(f[-1]) + 1) % 4
    g2 = nx.read_gpickle(name[:-1]+str(dif_end))

    g1 = process_graph(g1)
    g2 = process_graph(g2)
    # nx.draw_networkx(g1)
    # plt.show()
    # nx.draw_networkx(g2)
    # plt.show()
    print(nx.get_node_attributes(g1, 'idx'))
    print(nx.get_node_attributes(g2, 'idx'))
    print(g1.edges(data=True))
    print(g2.edges(data=True))
    test_graph(g1, g2)

def generate_data(folder, saved_dir):
    load_lut("word_file_x86")
    load_transformer("transformer.npy")
    for f in os.listdir(folder):
        path = os.path.join(folder, f)
        g = nx.read_gpickle(path)
        g = process_graph(g)
        name = os.path.join(saved_dir, f)
        nx.write_gpickle(g, name)

def calculate_ged_distance(g1, item):
    name, g2 = item
    cm = node_cost_matrix(g1, g2)
    distance = ged(g1, g2, cm)[0]
    return (name, distance)

def top_distance_ged(database, name, topk=10):
    distance_list = []
    with ProcessPoolExecutor(10) as ex:
        distance_list.append(ex.map(partial(calculate_ged_distance, database[name]), list(database.items())))
    distance_data = {}
    for dl in distance_list:
        for d in dl:
            distance_data[d[0]] = d[1]
    closest = sorted(distance_data.items(), key=lambda x: x[1])
    start_idx = 0
    for i in range(len(closest)):
        if closest[i][1] < 1.0:
            start_idx = i - 1
            break
    if start_idx < 0:
        start_idx = 0
    return closest[:start_idx+topk]

def run_misa(database, test_num=100):
    ap_list = []
    time_list = []
    result_list = {}
    with open(database, 'rb') as handle:
        data = pickle.load(handle)
    name_list = data.keys()
    processed_graph = {}
    for name in list(name_list)[:100]:
        processed_graph[name] = nx.read_gpickle(os.path.join("ged_x86_misa", name))
    print("Finished loading")
    for name in list(name_list)[:test_num]:
        print("Processing " + name + "...")
        start = time.clock()
        closest_k = top_distance_ged(processed_graph, name)
        cur_map = mean_ap(closest_k, name, name_list)
        if cur_map is None:
            continue
        time_list.append(time.clock() - start)
        result_list[name] = cur_map
        ap_list.append(cur_map)

    ma = np.mean(ap_list)
    var_ap = np.var(ap_list)
    mean_time = np.mean(time_list)
    var_time = np.var(time_list)
    print(str(ma) + " " +
          str(mean_time) + " " +
          str(var_time))
    print(len(np.where(np.asarray(ap_list) < 0.01)[0]))
    return result_list

def main():
    res = run_misa(sys.argv[1], 20)
    print(res)

if __name__=='__main__':
    main()
