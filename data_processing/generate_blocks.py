#!/usr/bin/env python

import pickle as pkl
import os
import sys
import random
import networkx as nx
import numpy as np
from collections import defaultdict
from verify_hash import *

def main():
    record = []
    files = []

    folder = sys.argv[1]
    for subdir in os.listdir(folder):
        subdir_path = os.path.join(folder, subdir)
        files += [os.path.join(subdir_path, x) for x in os.listdir(subdir_path)]

    # files = [os.path.join(sys.argv[1], x) for x in os.listdir(sys.argv[1])]
    random.shuffle(files)
    num_blks = int(sys.argv[2])
    cnt = 0
    for i in range(num_blks):
        graph = nx.read_gpickle(files[i])
        for node in graph.nodes(data=True):
            if len(node[1]['data']) < 3:
                continue
            data = bag_to_vector(list_to_bag(node[1]['data']))
            record.append(data)
    random.shuffle(record)
    print(len(record))
    all_data = np.asarray(record[:num_blks])
    with open(sys.argv[3], 'wb') as handle:
        pkl.dump(all_data, handle)

if __name__=='__main__':
    main()
