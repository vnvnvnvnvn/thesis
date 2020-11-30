#!/usr/bin/env python

import networkx as nx
import sys
import matplotlib.pyplot as plt

g = nx.read_gpickle(sys.argv[1])
nx.draw_networkx(g)
plt.show()

for n in g.nodes(data='data'):
    print(n[1])
