#!/usr/bin/env python3

import networkx as nx
import sys
import matplotlib.pyplot as plt

def main():
    if len(sys.argv[1]) < 2:
        print("USAGE:\n\tvisualize_graph.py <graph_file>")
        exit()
    g = nx.read_gpickle(sys.argv[1])
    nx.draw_networkx(g)
    plt.show()

    for n in g.nodes(data='data'):
        print(n[1])

if __name__=='__main__':
    main()
