#!/usr/bin/env python

import pickle as pkl
from calculate_wl import *

def top_distance(db, item, topk=10):
    distance_list = {}
    for k, v in db.items():
        distance_list[k] = label_distance(v, item)
    closest = sorted(distance_list.items(), key=lambda x: x[1], reverse=True)
    return closest[:topk]

def isin(top, name):
    for k, v in top:
        if k == name:
            continue
        if k[:-2] == name[:-2]:
            return True
    return False

def main():
    db_name = "wl_db.pkl"
    handle = open(db_name, 'rb')
    db = pkl.load(handle)
    cnt = 0
    for k, v in db.items()[:100]:
        closest = top_distance(db, v, 5)
        if isin(closest, k):
            cnt += 1
    print(cnt*1.0/100)

if __name__=='__main__':
    main()
