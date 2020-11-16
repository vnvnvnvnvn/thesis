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
    for idx, elem in enumerate(top):
        k, v = elem
        if k == name:
            continue
        if k[:-2] == name[:-2]:
            return idx
    return None

def main():
    db_name = "wl_db.pkl"
    handle = open(db_name, 'rb')
    db = pkl.load(handle)
    cnt = 0
    item_list = db.items()
    random.shuffle(item_list)
    for k, v in item_list[:100]:
        closest = top_distance(db, v)
        correct = isin(closest, k)
        if correct is not None:
            print(k+" "+closest[correct][0]+": "+str(closest[correct][1]))
            cnt += 1
    print(cnt*1.0/100)

if __name__=='__main__':
    main()
