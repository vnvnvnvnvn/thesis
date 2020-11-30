#!/usr/bin/env python

import networkx as nx
import os
from collections import defaultdict
import sys
import matplotlib.pyplot as plt
import pickle

def main():
    flags = r"(al|eq|ne|cs|cc|hs|lo|mi|pl|vs|vc|hi|ls|ge|lt|gt|le)?"
    branch = r"(b|bl|bx|blx|bxj|cbz|cbnz)" + flags + "(\.w)?$"
    files = [os.path.join(sys.argv[1], x) for x in os.listdir(sys.argv[1])]
    counter = defaultdict(lambda: 0)
    node_counter = {}
    for i in range(len(files)):
        g = nx.read_gpickle(files[i])
        p = False
        for node in g.nodes(data=True):
            l = len(node[1]['data'])
            counter[l] += 1
            if l > 7000:
                p = True
        if p:
            print(files[i])
    count_opcode = sorted(counter.items(), key=lambda x: x[0])

    counter_normal = {}
    for e in count_opcode:
        counter_normal[e[0]] = e[1]
    with open('len_block.pkl', 'wb') as handle:
        pickle.dump(counter_normal, handle)

if __name__=='__main__':
    main()
