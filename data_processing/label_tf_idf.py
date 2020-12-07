#!/usr/bin/env python3

import pickle
import sys
import random
from collections import defaultdict
import math
from itertools import product

def tf_idf(db):
    label_df = defaultdict(lambda: 0)
    label_freq = defaultdict(lambda: 0)
    num_doc = 0
    label_idf = {}
    label_freq_save = {}
    with open(db, 'rb') as handle:
        data = pickle.load(handle)
        items = data.items()
        for name, wl in items:
            for label, freq in wl.items():
                label_df[label] += 1
                label_freq[label] += freq
            num_doc += 1
        for name, v in label_df.items():
            label_idf[name] = 1 + math.log(num_doc * 1.0 / v)
        for name, v in label_freq.items():
            label_freq_save[name] = v
    idf_name = db.split('.')[0] + "_idf.pkl"
    with open(idf_name, 'wb') as handle:
        pickle.dump(label_idf, handle)
    freq_name = db.split('.')[0] + "_freq.pkl"
    with open(freq_name, 'wb') as handle:
        pickle.dump(label_freq_save, handle)

def main():
    # db_list = ["wl_arm_db_", "wl_x86_db_"]
    # code_len_list = ["8", "16", "32", "64"]
    # data_list = product(db_list, code_len_list)
    # data_list = ["1_wl_x86_db_32"]
    data_list = ["benign"]
    for db in data_list:
        name = "".join([db, ".pkl"])
        tf_idf(name)

if __name__=='__main__':
    main()
