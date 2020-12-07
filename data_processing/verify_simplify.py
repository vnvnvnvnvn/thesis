#!/usr/bin/env python3

import os
import sys
from collections import defaultdict
import matplotlib.pyplot as plt
import networkx as nx
import pickle

keys = set(["VAR", "IMM", "ADDR", "FUNC", "BB", "REG", "REGPTR"])

def generate_word_file(name):
    vocab = defaultdict(lambda:0)
    unrecognized = set()
    with open(name) as f:
        for line in f.readlines():
            #fs = line.split()[1:]
            #for x in fs:
                #if x not in keys:
                    #unrecognized.add(x)
            vocab[line.strip()] += 1
    # print(unrecognized)
    print(len(vocab))
    print(vocab)
    l = sorted(vocab.items(), key=lambda x: x[1])
    print(l)
    words = sorted(vocab.keys())
    with open("word_file_x86", 'w') as wf:
        wf.write("\n".join(words))
    wc = zip(*l)[1]
    plt.bar(range(len(wc)), wc, log=True)
    plt.show()

def generate_vocab_list(folder):
    file_list = []
    for subdir in os.listdir(folder):
        subdir_path = os.path.join(folder, subdir)
        file_list += [os.path.join(subdir_path, x) for x in os.listdir(subdir_path)]
    vocab = defaultdict(lambda:0)
    for f in file_list:
        g = nx.read_gpickle(f)
        for node in g.nodes(data='data'):
            for opcode in node[1]:
                vocab[opcode] += 1
    print(len(vocab))
    vocab_saved = {}
    for item, value in vocab.items():
        vocab_saved[item] = value
    words = sorted(vocab.keys())
    with open("vs_word_file", "w") as wf:
        wf.write("\n".join(words))
    with open("vs_vocab_freq.pkl", "wb") as handle:
        pickle.dump(vocab_saved, handle)

def main():
    generate_vocab_list(sys.argv[1])

if __name__=='__main__':
    main()
