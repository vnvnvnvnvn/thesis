#!/usr/bin/env python3

import argparse
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
    g.add_edges_from(edge_list)
    return g, jmp_pts

def simplify_graph(saved_dir, name):
    g = nx.read_gpickle(name)
    for d in g.nodes(data=True):
        if 'data' not in d[1].keys():
            d[1]['data'] = []
            continue
        sim_block = simp.simplify(d[1]['data'], "x86")
        d[1]['data'] = sim_block
        saved_path = os.path.join(saved_dir, name)
        nx.write_gpickle(g, saved_path)
    return saved_path

def generate_graph(json_folder, saved_dir, simp_dir, data):
    d, arch = data
    t, name = d.split("/")
    # if t not in set(["Adware", "Backdoor", "Trojan", "Virus", "Worm"]):
        # return
    if arch == 'x86':
        g, jmp_pts = json_to_graph(os.path.join(json_folder, d))
        if len(g.nodes()) == 0:
            return
        saved_path = os.path.join(saved_dir, d)
        saved_folder = os.path.join(saved_dir, t)
        if not os.path.isdir(saved_folder):
            os.makedirs(saved_folder)
        nx.write_gpickle(g, saved_path)
        saved_subdir = os.path.join(simp_dir, t)
        if not os.path.isdir(saved_subdir):
            os.makedirs(saved_subdir)
        for d in g.nodes(data=True):
            if 'data' not in d[1].keys():
                d[1]['data'] = []
                continue
            sim_block = simp.simplify(d[1]['data'], "x86", jmp_pts)
            d[1]['data'] = sim_block
        simp_saved_path = os.path.join(saved_subdir, name)
        nx.write_gpickle(g, simp_saved_path)
    return simp_saved_path

def generate_graph_nonrec(saved_dir, saved_subdir, file_name):
    if not os.path.isdir(saved_subdir):
        os.makedirs(saved_subdir)
    if not os.path.isdir(saved_dir):
        os.makedirs(saved_dir)
    name = os.path.basename(file_name)
    g, jmp_pts = json_to_graph(file_name)
    if len(g.nodes()) == 0:
        return
    saved_path = os.path.join(saved_dir, name)
    nx.write_gpickle(g, saved_path)
    for d in g.nodes(data=True):
        if 'data' not in d[1].keys():
            d[1]['data'] = []
            continue
        sim_block = simp.simplify(d[1]['data'], "x86", jmp_pts)
        d[1]['data'] = sim_block
    simp_saved_path = os.path.join(saved_subdir, name)
    nx.write_gpickle(g, simp_saved_path)
    return simp_saved_path

def process_all_virus_data(json_folder, saved_type, virus_saved_dir, simp_dir):
    handle = open(saved_type, 'rb')
    data_arch = pickle.load(handle)
    handle.close()
    print(len(data_arch))
    with ProcessPoolExecutor(10) as ex:
        ex.map(partial(generate_graph, json_folder, virus_saved_dir, simp_dir), data_arch.items())

def process_benign_data(json_folder, benign_saved_dir, saved_subdir):
    todo = [os.path.join(json_folder, x) for x in os.listdir(json_folder)]
    with ProcessPoolExecutor(10) as ex:
        ex.map(partial(generate_graph_nonrec, benign_saved_dir, saved_subdir), todo)

def generate_vocab(folder, vocab_path):
    vocab = defaultdict(lambda:0)
    unrecognized = set()
    files = []
    for subdir in os.listdir(folder):
        subdir_path = os.path.join(folder, subdir)
        files += [os.path.join(subdir_path, x) for x in os.listdir(subdir_path)]
    for i in range(len(files)):
        g = nx.read_gpickle(files[i])
        for node in g.nodes(data='data'):
            for opcode in node[1]:
                vocab[opcode] += 1
    vocab_saved = {}
    for item, value in vocab.items():
        vocab_saved[item] = value
    words = sorted(vocab.keys())
    with open(vocab_path, 'w') as wf:
        wf.write("\n".join(words))
    freq_saved = vocab_path + "_freq.pkl"
    with open(freq_saved, "wb") as handle:
        pickle.dump(vocab_saved, handle)
    return vocab_path

def main():
    root_folder = os.getcwd()
    parser = argparse.ArgumentParser(description="""Chuyen VirusShare json thanh graph""")
    parser.add_argument('-a', '--all', action='store_true', help='Xu ly toan bo VS folder')
    parser.add_argument('-f', '--folder', help='Folder chua file virus VS json')
    parser.add_argument('--simplified_folder', default='simp_vsgraphs', help='Folder de save file simplified')
    parser.add_argument('--graphs_folder', default='vsgraphs', help='Folder de save file graph')
    parser.add_argument('-b', '--benign', help='Folder chua file benign json')
    parser.add_argument('--file', action='append', help='File can xu ly')
    parser.add_argument('--vocab', const='vs_word_file', action='store_const', help='Tao ra file vocab va dem tu')
    parser.add_argument('--root', default=root_folder, help='Root folder de save file')
    parser.add_argument('--example_folder', default='example_graph', help='Folder de save example graph')
    parser.add_argument('--example_simplified', default='example_simplified', help='Folder de save simplified example graph')
    parser.add_argument('--saved_type', default='reporting_type.pkl', help='File pickle co chua architecture cua cac file trong VS')
    args = parser.parse_args()

    if args.all:
        if args.benign:
            benign_saved_dir = os.path.join(args.root, args.graphs_folder, "Benign")
            saved_subdir = os.path.join(args.root, args.simplified_folder, "Benign")
            process_benign_data(args.benign, benign_saved_dir, saved_subdir)
        if args.folder:
            virus_saved_dir = os.path.join(args.root, args.graphs_folder)
            simp_dir = os.path.join(args.root, args.simplified_folder)
            process_all_virus_data(args.folder, args.saved_type, virus_saved_dir, simp_dir)
        if args.vocab:
            generate_vocab(os.path.join(args.root, args.simplified_folder), args.vocab)
    if args.file:
        example_saved_dir = os.path.join(args.root, args.example_folder)
        example_simp_dir = os.path.join(args.root, args.example_simplified)
        for name in args.file:
            generate_graph_nonrec(example_saved_dir, example_simp_dir, name)

if __name__=='__main__':
    main()
