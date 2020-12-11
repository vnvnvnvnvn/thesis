#!/usr/bin/env python3

import argparse
import networkx as nx
import sys
import matplotlib.pyplot as plt
import process_MISA as proc
import os
import shutil
import read_MISA as rmisa
import pickle
from collections import defaultdict
from itertools import islice

def draw(G):
    pos = nx.layout.spring_layout(G)
    node_sizes = [3 + 10 * i for i in range(len(G))]
    M = G.number_of_edges()
    edge_colors = range(2, M + 2)
    nodes = nx.draw_networkx_nodes(G, pos, node_size=node_sizes, node_color="blue")
    edges = nx.draw_networkx_edges(
        G,
        pos,
        node_size=node_sizes,
        arrowstyle="->",
        arrowsize=10,
        edge_color=edge_colors,
        edge_cmap=plt.cm.Blues,
        width=2,
    )
    plt.show()

def generate_vocab(folder, vocab_path):
    vocab = defaultdict(lambda:0)
    unrecognized = set()
    files = [os.path.join(folder, x) for x in os.listdir(folder)]
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
    return len(vocab_saved)

def generate_data(folder, arch, saved_dirname):
    files = [os.path.join(folder, x) for x in os.listdir(folder)]
    for i in range(len(files)):
        fns = rmisa.read_file(files[i], arch)
        rmisa.save_file(files[i], arch, fns, saved_dirname)
    return len(files)

def generate_simplified_graph(simp, folder, arch, saved_dirname, print_progress=False):
    cnt = 0
    for f in os.listdir(folder):
        cnt += 1
        if print_progress and cnt % 100 == 0:
            print("Done with "+ str(cnt))
        full_path = os.path.join(folder, f)
        orig_g = nx.read_gpickle(full_path)
        for d in orig_g.nodes(data=True):
            if 'data' not in d[1].keys():
                continue
            sim_block = simp.simplify(d[1]['data'], arch)
            d[1]['data'] = sim_block
        saved_path = os.path.join(saved_dirname, f)
        nx.write_gpickle(orig_g, saved_path)
    return cnt

def generate_all_data(folder, saved_graphs_path, saved_simplified, arch):
    simp = proc.InstructionSimplifier()
    generate_data(folder, arch, saved_graphs_path)
    generate_simplified_graph(simp, saved_graphs_path, arch, saved_simplified)

def main():
    root_folder = os.getcwd()
    parser = argparse.ArgumentParser(description="""Chuyen MISA .c.s file thanh graph""")
    parser.add_argument('-a', '--all', action='store_true', help='Xu ly toan bo MISA folder')
    parser.add_argument('-f', '--folder', help='Folder chua file MISA')
    parser.add_argument('--simplified_folder', default='simp_graphs', help='Folder de save file simplified')
    parser.add_argument('--graphs_folder', default='graphs', help='Folder de save file graph')
    parser.add_argument('--file', action='append', help='File can xu ly')
    parser.add_argument('--arch', choices=['arm', 'x86'], default='x86', help='Architecture')
    parser.add_argument('--vocab', const='word_file_', action='store_const', help='Tao ra file vocab va dem tu')
    parser.add_argument('--root', default=root_folder, help='Root folder de save file')
    parser.add_argument('--example_folder', default='example_graph_MISA', help='Folder de save example graph')
    parser.add_argument('--example_simplified', default='example_simplified_MISA', help='Folder de save simplified example graph')
    parser.add_argument('--visualize', action='store_true', help='Visualize a graph')
    parser.add_argument('--inspect', action='store_true', help='In cac basic blocks')
    parser.add_argument('--number_of_graphs', default=2, help='So graph muon ve hoac in', type=int)
    args = parser.parse_args()

    if args.all and args.folder:
        saved_dir = os.path.join(args.root, args.graphs_folder)
        simp_dir = os.path.join(args.root, args.simplified_folder)
        generate_all_data(args.folder, saved_dir, simp_dir, args.arch)
    if args.vocab:
        generate_vocab(os.path.join(args.root, args.simplified_folder), args.vocab + args.arch)
    if args.file:
        example_saved_dir = os.path.join(args.root, args.example_folder)
        example_simp_dir = os.path.join(args.root, args.example_simplified)
        if os.path.isdir(example_saved_dir):
            os.makedirs(example_saved_dir)
        if os.path.isdir(example_simp_dir):
            os.makedirs(example_simp_dir)

        simp = proc.InstructionSimplifier()
        for name in args.file:
            fns = rmisa.read_file(name, args.arch)
            rmisa.save_file(name, args.arch, fns, example_saved_dir)
        generate_simplified_graph(simp, example_saved_dir, args.arch, example_simp_dir)

        if args.visualize:
            for name, data in islice(fns.items(), args.number_of_graphs):
                nx.draw_networkx(data)
                plt.show()

        if args.inspect:
            for name, data in islice(fns.items(), args.number_of_graphs):
                for node in data.nodes(data='data'):
                    print(node[1])
                    sb = simp.simplify(node[1], arch)
                    print(sb)


if __name__=='__main__':
    main()
