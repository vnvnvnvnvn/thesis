#!/usr/bin/env python

import networkx as nx
import os
import sys
import pickle

word_file = "word_file_x86"

def idf(folder, max_blk_cnt):
    wf = open(word_file)
    words = wf.readlines()
    words.sort()
    counter = {}
    word_count = {}
    num_doc = 0
    for w in words:
        counter[w.strip()] = 0
        word_count[w.strip()] = 0

    # files = []
    # for subdir in os.listdir(folder):
        # files += [os.path.join(folder, subdir, x) for x in os.listdir(os.path.join(folder, subdir))]
    files = [os.path.join(folder, x) for x in os.listdir(folder)]
    current_blk_cnt = 0
    for i in range(len(files)):
        # if current_blk_cnt >= max_blk_cnt:
            # break
        if i % 100 == 0:
            print("Done with " + str(i))
        if i >= len(files):
            break
        graph = nx.read_gpickle(files[i])
        for node in graph.nodes(data=True):
            current_blk_cnt += 1
            distinct = set(node[1]['data'])
            if len(distinct) == 0:
                continue
            num_doc += 1
            for w in distinct:
                counter[w.strip()] += 1
            for w in node[1]['data']:
                word_count[w.strip()] += 1
    # idf_data = sorted(counter.items(), key=lambda x: x[1])
    # for d in idf_data:
    #     print(d)
    # word_data = sorted(word_count.items(), key=lambda x:x[1])
    # for wd in word_data:
    #     print(wd)
    print(num_doc)
    print(len(word_count))
    with open('idf.pkl', 'wb') as idf_handle:
        pickle.dump(counter, idf_handle)
    with open('wc.pkl', 'wb') as wc_handle:
        pickle.dump(word_count, wc_handle)

def main():
    idf(sys.argv[1], int(sys.argv[2]))

if __name__=='__main__':
    main()
