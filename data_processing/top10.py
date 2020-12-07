#!/usr/bin/env python3

import pickle as pkl
from calculate_wl import label_distance, iou_distance
import time
import sys
from functools import partial
import numpy as np
from multiprocessing import Pool

def calculate_distance(f, comp, item):
    k, v = item
    distance = f(comp, v)
    return (k, distance)

def top_distance(f, db, item, idf_db={}, topk=10):
    pool = Pool(processes=8, maxtasksperchild=10)
    distance_list = pool.map(partial(calculate_distance, f, item), db.items())

    distance_data = {}
    for dl in distance_list:
        distance_data[dl[0]] = dl[1]
    closest = sorted(distance_data.items(), key=lambda x: x[1], reverse=True)
    start_idx = 0
    for i in range(len(closest)):
        if closest[i][1] < 1.0:
            start_idx = i - 1
            break
    if start_idx < 0:
        start_idx = 0
    pool.terminate()
    pool.join()
    del pool
    return closest[:start_idx+topk]

def isin(top, name):
    for idx, elem in enumerate(top):
        k, v = elem
        if k == name:
            continue
        if k[:-2] == name[:-2] and v > 0.1:
            return idx
    return None

def mean_ap(top, name, name_list):
    relevant_doc = 0
    for i in range(4):
        relevant_name = name[:-1] + str(i)
        if relevant_name in name_list:
            relevant_doc += 1
    if relevant_doc == 1:
        return None
    correct_so_far = 0
    num_so_far = 0
    ap = 0
    for k, v in top:
        if k == name:
            continue
        num_so_far += 1
        if k[:-2] == name[:-2]:
            correct_so_far += 1
            ap += correct_so_far * 1.0 / num_so_far
    return ap / (relevant_doc - 1)

def main():
    db_name = sys.argv[1]
    test_num = int(sys.argv[2])
    handle = open(db_name, 'rb')
    db = pkl.load(handle)
    handle.close()
    print("Finished loading")
    print("Testing bag of words")
    cnt = 0
    item_list = list(db.items())
    # random.shuffle(item_list)
    ap_list = []
    name_list = set(db.keys())
    for k, v in item_list[:test_num]:
        start = time.clock()
        closest_k = top_distance(iou_distance, db, v)
        if cnt % 10 == 0:
            print("Done with " + str(cnt))
        cnt += 1
        ap_list.append(mean_ap(closest_k, k, name_list))
    #     correct = isin(closest_k, k)
    #     if correct is not None:
    #         print(k+" "+closest_k[correct][0]+": "+str(closest_k[correct][1])+ " @"+str(correct))
    #         cnt += 1
    #     for c in closest_k:
    #         if c[0] != k:
    #             print(k+" closest to "+c[0]+": "+str(c[1]))
    #             break
    # print(cnt*1.0/test_num)
    print(ap_list)
    print(closest_k)
    # print(np.mean(ap_list))
    # print(len(np.where(np.asarray(ap_list) < 0.01)[0]))

if __name__=='__main__':
    main()
