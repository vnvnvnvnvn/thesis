#!/usr/bin/env python3

import argparse
import pickle
import sys
import random
from collections import defaultdict
import math
from itertools import product

def convert_from_default(d):
    updated = {}
    for name, v in d.items():
        updated[name] = v
    return updated

def tf_idf(db):
    label_df = defaultdict(lambda: 0)
    label_freq = defaultdict(lambda: 0)
    num_doc = 0
    label_idf = {}
    label_freq_save = {}
    normed_data = {}

    with open(db, 'rb') as handle:
        data = pickle.load(handle)
        for name, wl in data.items():
            for label, freq in wl.items():
                label_df[label] += 1
                label_freq[label] += freq
            num_doc += 1

    for name, v in label_df.items():
        label_idf[name] = 1 + math.log(num_doc * 1.0 / v)
    label_freq_save = convert_from_default(label_freq)

    for name, wl in data.items():
        updated_wl = {}
        wc = sum(list(wl.values()))
        for label, count in wl.items():
            updated_wl[label] = count * label_idf[label] * 1.0 / wc
        normed_data[name] = updated_wl

    idf_name = db.split('.')[0] + "_idf.pkl"
    with open(idf_name, 'wb') as handle:
        pickle.dump(label_idf, handle)
    freq_name = db.split('.')[0] + "_freq.pkl"
    with open(freq_name, 'wb') as handle:
        pickle.dump(label_freq_save, handle)
    tf_idf_name = db.split('.')[0] + "_normed.pkl"
    with open(tf_idf_name, 'wb') as handle:
        pickle.dump(normed_data, handle)

def main():
    parser = argparse.ArgumentParser(description="""Tinh IDF va chuan bi database cho TF-IDF""")
    parser.add_argument('--core', action='append', help='Ten cua database can xu ly', required=True)
    parser.add_argument('--prefix', action='append', default=[""], help='Prefix cua cac database muon xu ly')
    parser.add_argument('--postfix', action='append', default=[""], help='Postfix cua cac database muon xu ly')
    args = parser.parse_args()

    data_list = product(args.prefix, args.core, args.postfix)
    for db in data_list:
        name = "".join(list(db) + [".pkl"])
        tf_idf(name)

if __name__=='__main__':
    main()
