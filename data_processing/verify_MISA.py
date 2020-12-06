#!/usr/bin/env python3

import networkx as nx
import sys
import matplotlib.pyplot as plt
import process_MISA as proc
import os
import shutil
import read_MISA as rmisa
import pickle
from collections import defaultdict

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

def generate_vocab(folder):
    vocab = defaultdict(lambda:0)
    unrecognized = set()
    arch = folder.split("/")[-1]
    files = [os.path.join(folder, x) for x in os.listdir(folder)]
    vocab_path = "_".join(["word_file", arch])
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

def generate_data(folder):
    arch = folder.split("/")[-1]
    files = [os.path.join(folder, x) for x in os.listdir(folder)]
    saved_dirname = os.path.join(os.getcwd(), "graphs", arch)
    for i in range(len(files)):
        fns = rmisa.read_file(files[i], arch)
        rmisa.save_file(files[i], arch, fns, saved_dirname)
    return saved_dirname

def generate_simplified_graph(simp, folder):
    arch = folder.split("/")[-1]
    saved_dirname = os.path.join(os.getcwd(), "simp_graphs", arch)
    cnt = 0
    for f in os.listdir(folder):
        cnt += 1
        if cnt % 100 == 0:
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
    return saved_dirname

def generate_all_data(folder):
    simp = proc.InstructionSimplifier()
    saved_graphs_path = generate_data(folder)
    saved_simplified = generate_simplified_graph(simp, saved_graphs_path)
    generate_vocab(saved_simplified)

def main():
    if len(sys.argv) < 2:
        print("USAGE:\n\tverify_MISA.py <folder>\n\tverify_MISA.py <filename> <architecture>")
        exit()
    if os.path.isdir(sys.argv[1]):
        generate_all_data(sys.argv[1])
    else:
        simp = proc.InstructionSimplifier()
        arch = "x86"
        if len(sys.argv) >= 3:
            arch = sys.argv[2]
        fns = rmisa.read_file(sys.argv[1], arch)
        for name, data in fns.items():
            for node in data.nodes(data='data'):
                print(node[1])
                sb = simp.simplify(node[1], arch)
                print(sb)
                print("\n\n")
            nx.draw_networkx(data)
            plt.show()

if __name__=='__main__':
    main()
