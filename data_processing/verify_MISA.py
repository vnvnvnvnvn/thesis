#!/usr/bin/env python

import networkx as nx
import sys
import matplotlib.pyplot as plt
import process_MISA as proc
import os
import random
import shutil
import read_MISA as rmisa

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
    #plt.show()

def simplify_collect(g, arch, simp):
    instr = []
    for d in g.nodes(data=True):
        if 'data' not in d[1].keys():
            print("No data " + d[0])
            continue
        sim_block = simp.simplify(d[1]['data'], arch)
        instr += sim_block
        #except:
        #    print("Failed")
        #    print(d)
    return instr

def generate_vocab(simp, folder):#, n=200):
    collected = []
    arch = folder.split("/")[-1]
    files = [os.path.join(folder, x) for x in os.listdir(folder)]
    random.shuffle(files)
    dirpath = os.path.join(os.getcwd(), "vocab", arch)
    for i in range(len(files)):
        fns = rmisa.read_file(files[i], arch)
        for name, data in fns.items():
            collected += simplify_collect(data, arch, simp)
    with open(os.path.join(dirpath, "saved"), 'w') as f:
        f.write("\n".join(collected))

def generate_data(folder):
    arch = folder.split("/")[-1]
    files = [os.path.join(folder, x) for x in os.listdir(folder)]
    for i in range(len(files)):
        fns = rmisa.read_file(files[i], arch)
        rmisa.save_file(files[i], arch, fns)

def generate_simplified_graph(simp, folder):
    arch = folder.split("/")[-1]
    saved_dirname = os.path.join(os.getcwd(), "simp_graphs", arch)
    for f in os.listdir(folder):
        full_path = os.path.join(folder, f)
        orig_g = nx.read_gpickle(full_path)
        for d in orig_g.nodes(data=True):
            if 'data' not in d[1].keys():
                print("No data " + d[0])
                continue
            sim_block = simp.simplify(d[1]['data'], arch)
            d[1]['data'] = sim_block
        saved_path = os.path.join(saved_dirname, f)
        nx.write_gpickle(orig_g, saved_path)

def main():
    simp = proc.InstructionSimplifier()
    if os.path.isdir(sys.argv[1]):
        generate_simplified_graph(simp, os.path.join(sys.argv[1], "arm"))
        pass
        # generate_vocab(simp, os.path.join(sys.argv[1], "arm"))
        # generate_vocab(simp, os.path.join(sys.argv[1], "x86"))
    else:
        fns = rmisa.read_file(sys.argv[1], "x86")
        for name, data in fns.items():
            #print(simplify_collect(data, "x86", simp))
            nx.draw_networkx(data)
            plt.show()
    simp.conclude()
    # g = nx.read_gpickle(sys.argv[1])
    # for d in g.nodes(data=True):
    #     print("\n\n")
    #     print(d)
    #     print(g[d[0]])
    #     sim_block = simp.simplify(d[1]['data'], 'arm')
    #     print(sim_block)
    # for e in g.edges(data=True):
    #     print(e)
    # # draw(g)
    # nx.draw_networkx(g)
    # plt.show()

if __name__=='__main__':
    main()
