#!/usr/bin/env python

import json
import networkx as nx
import sys
from process_VS import *
import pickle
import matplotlib.pyplot as plt
import re
import os
from functools import partial
from concurrent.futures import ProcessPoolExecutor

simp = InstructionSimplifier()

def json_to_graph(name):
    g = nx.DiGraph()
    jmp_pts = set()
    jmp_pts_dec = []
    try:
        f = open(name)
    except:
        print("Cannot open " + name)
        return g, jmp_pts
    func_addr = set()
    try:
        jsong = json.load(f)
    except:
        return g, jmp_pts
    if len(jsong) == 0:
        return g, jmp_pts
    if 'blocks' not in jsong[0].keys():
        return g, jmp_pts

    saved_data = {}
    edge_list = set()
    entry_offset = jsong[0]['offset']
    for item in jsong[0]['blocks']:
        if 'ops' not in item.keys():
            print("Warning: block without ops in " + name)
            continue
        current_bag = []
        for op in item['ops']:
            if 'opcode' in op.keys():
                current_bag.append(op['opcode'])
            if 'fcn_addr' in op.keys():
                func_addr.add(op['fcn_addr'])
        off = item['offset']
        if off != entry_offset:
            jmp_pts.add(hex(off))
            jmp_pts_dec.append(off)
        saved_data[off] = item
        g.add_node(str(off), data=current_bag)
        if 'jump' in item.keys():
            # g.add_edge(str(off), str(item['jump']))
            edge_list.add((str(off), str(item['jump'])))

    jmp_pts_dec.sort()
    for idx, jp in enumerate(jmp_pts_dec):
        data = g.nodes(data=True)[str(jp)]['data']
        if len(data) < 1:
            continue
        last_call = data[-1].split()[0]
        if last_call[0] == 'j':
            cmd = data[-1].split()
            dest = cmd[1]
            if dest in jmp_pts:
                edge_list.add((str(jp), str(int(dest, 16))))
                if cmd[0] != 'jmp' and idx < len(jmp_pts_dec) - 1:
                    next_idx = jmp_pts_dec[idx+1]
                    edge_list.add((str(jp), str(next_idx)))
        else:
            if idx < len(jmp_pts_dec) - 1:
                next_idx = jmp_pts_dec[idx+1]
                edge_list.add((str(jp), str(next_idx)))
    # print(edge_list)
    g.add_edges_from(edge_list)
    # for node in g.nodes(data='data'):
        # if len(g[node[0]]) == 0:
            # print(node[0])
        # if node[1] is None or len(node[1]) == 0:
            # print(saved_data[node[0]])
            # print(node[1])
    # print(func_addr)
    return g, jmp_pts

def simplify_graph(saved_dir, name):
    g = nx.read_gpickle(name)
    for d in g.nodes(data=True):
        if 'data' not in d[1].keys():
            print("No data " + d[0])
            d[1]['data'] = []
            print(d[1]['data'])
            continue
        sim_block = simp.simplify(d[1]['data'], "x86")
        d[1]['data'] = sim_block
        saved_path = os.path.join(saved_dir, name)
        nx.write_gpickle(g, saved_path)

def generate_graph(json_folder, saved_dir, data):
    d, arch = data
    t, name = d.split("/")
    if t not in set(["Adware", "Backdoor", "Trojan", "Virus", "Worm"]):
        return
    if arch == 'x86':
        g, jmp_pts = json_to_graph(os.path.join(json_folder, d))
        if len(g.nodes()) == 0:
            return
        # saved_path = os.path.join(saved_dir, d)
        # nx.write_gpickle(g, saved_path)
        saved_subdir = os.path.join(os.getcwd(), "simp_vsgraphs", t)
        for d in g.nodes(data=True):
            if 'data' not in d[1].keys():
                print("No data " + d[0])
                d[1]['data'] = []
                print(d[1]['data'])
                continue
            sim_block = simp.simplify(d[1]['data'], "x86", jmp_pts)
            d[1]['data'] = sim_block
        simp_saved_path = os.path.join(saved_subdir, name)
        nx.write_gpickle(g, simp_saved_path)

def main():
    handle = open('reporting_type.pkl', 'rb')
    data_arch = pickle.load(handle)
    handle.close()
    print(len(data_arch))
    saved_dir = os.path.join(os.getcwd(), "vsgraphs", "x86")
    json_folder = sys.argv[1]
    with ProcessPoolExecutor(10) as ex:
        ex.map(partial(generate_graph, json_folder, saved_dir), data_arch.items())

if __name__=='__main__':
    main()
