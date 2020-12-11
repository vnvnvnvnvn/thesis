#!/usr/bin/env python3

import argparse
import networkx as nx
import os
import sys
import pickle
import matplotlib.pyplot as plt


def plot_idf(word_count, df_count, num_doc, title):
    wc_list = sorted(word_count.items(), key=lambda x: x[1])
    wl, wc_num = list(zip(*wc_list))
    plt.bar(range(len(wc_num)), wc_num, log=True)
    plt.savefig(title+'_wc.png')

    cnt = []
    for w in wl:
        cnt.append(df_count[w])
    percentage = [1.0 * x / num_doc for x in cnt]
    plt.bar(range(len(wc_num)), percentage, log=True)
    plt.savefig(title+'_idf.png')


def idf(folder, word_file, nested=False):
    with open(word_file, 'r') as wf:
        words = wf.readlines()
    words.sort()
    counter = {}
    word_count = {}
    num_doc = 0
    for w in words:
        counter[w.strip()] = 0
        word_count[w.strip()] = 0

    if nested:
        files = []
        for subdir in os.listdir(folder):
            files += [os.path.join(folder, subdir, x) for x in os.listdir(os.path.join(folder, subdir))]
    else:
        files = [os.path.join(folder, x) for x in os.listdir(folder)]

    for name in files:
        graph = nx.read_gpickle(files[i])
        for node in graph.nodes(data=True):
            distinct = set(node[1]['data'])
            if len(distinct) == 0:
                continue
            num_doc += 1
            for w in distinct:
                counter[w.strip()] += 1
            for w in node[1]['data']:
                word_count[w.strip()] += 1
    with open(word_file+'_'+str(num_doc)+'_idf.pkl', 'wb') as idf_handle:
        pickle.dump(counter, idf_handle)
    with open(word_file+'_'+str(num_doc)+'_wc.pkl', 'wb') as wc_handle:
        pickle.dump(word_count, wc_handle)
    plot_idf(word_count, counter, num_doc, word_file)


def main():
    parser = argparse.ArgumentParser(description="""Tinh IDF cho cac blocks""")
    parser.add_argument('--folder', help='Folder simplified graph can xu ly', required=True)
    parser.add_argument('--vocab', help='Vocab tuong ung voi folder', required=True)
    parser.add_argument('--nested', action='store_true', help='Folder da cho co nested khong')
    args = parser.parse_args()

    idf(args.folder, args.vocab, args.nested is not None)


if __name__=='__main__':
    main()
