#!/usr/bin/env python

from top10 import *
import pickle as pkl
from itertools import product
from calculate_wl import label_distance, iou_distance
from collections import defaultdict
from ga_ged import ga
import networkx as nx
import os

def generate_test_data(item_list, number, exclude=False):
    cnt = 0
    ret_data = []
    for k, v in item_list:
        if exclude and k[-1] == '0':
            continue
        ret_data.append((k, v))
        cnt += 1
        if cnt >= number:
            break
    return ret_data

def process_data(f, data, test_data):
    name_list = set(data.keys())
    ap_list = []
    time_list = []
    result_list = {}

    for k, v in test_data:
        start = time.clock()

        ged_g1 = nx.read_gpickle(os.path.join("ged_x86_misa", k))
        closest_k = top_distance(f, data, v)
        ged_order = {}
        for cand, dist in closest_k:
            ged_g2 = nx.read_gpickle(os.path.join("ged_x86_misa", cand))
            ged_dist, _, _ = ga(ged_g1, ged_g2, 1)
            ged_order[cand] = ged_dist
        ged_sorted = sorted(ged_order.items(), key=lambda x: x[1])

        cur_map = mean_ap(ged_sorted, k, name_list)
        if cur_map is None:
            continue
        time_list.append(time.clock() - start)
        result_list[k] = cur_map
        ap_list.append(cur_map)

    ma = np.mean(ap_list)
    var_ap = np.var(ap_list)
    mean_time = np.mean(time_list)
    var_time = np.var(time_list)
    print(str(ma) + " " +
          str(mean_time) + " " +
          str(var_time))
    print(len(np.where(np.asarray(ap_list) < 0.01)[0]))

def process_data_vs(f, data, test_data):
    total_result = defaultdict(lambda: 0)
    def classify(name_list, name):
        counter = defaultdict(lambda: 0)
        for n, v in name_list:
            if name == n:
                continue
            c = n.split("/")
            counter[c[1]] += 1
        s = sorted(counter.items(), key=lambda x: x[1], reverse=True)
        if s[0][1] == 2:
            return 'unsure'
        return s[0][0]

    time_list = []
    result_list = {}

    for k, v in test_data:
        start = time.clock()
        closest_k = top_distance(f, data, v, {}, 11)
        time_list.append(time.clock() - start)
        result_list[k] = classify(closest_k, k)
    for name, res in result_list.items():
        orig_class = name.split("/")[1]
        total_result[(orig_class, res)] += 1
    mean_time = np.mean(time_list)
    var_time = np.var(time_list)
    print(str(mean_time) + " " +
          str(var_time))
    print(total_result)

def result_database(f, dbname, idfdb_name=None, test_num=100):
    idf_db = {}
    if idfdb_name is not None:
        with open(idfdb_name, 'rb') as idf_handle:
            idf_db = pkl.load(idf_handle)

    with open(dbname, 'rb') as handle:
        data = pkl.load(handle)
        item_list = list(data.items())
        updated_item_list = []
        if len(idf_db) > 0:
            for k, v in item_list:
                new_v = {}
                for label, freq in v.items():
                    new_data = freq * idf_db[label]
                    new_v[label] = new_data
                updated_item_list.append((k, new_v))
        else:
            updated_item_list = item_list
        test_data = generate_test_data(updated_item_list, test_num)
        process_data(f, data, test_data)

def experiment_misa_code_len(num, expr="IOU"):
    # db_list = ["wl_arm_db_", "wl_x86_db_"]
    # code_len_list = ["8", "16", "32", "64"]
    code_len_list = ["32"]
    # core = "wl_x86_db_32"
    # front = ["big_", "small_"]
    # end = ["_4", ""]
    # data_list = product(db_list, code_len_list)
    # data_list = product(front, end)
    core = "wl_x86_db_"
    data_list = code_len_list
    func = {
        "IOU": iou_distance,
        "BOL": label_distance,
        "TF_IDF": label_distance
    }

    if expr == "TF_IDF":
        print(expr)
        for db in data_list:
            # name = "".join([db[0], db[1], ".pkl"])
            # idf_name = "".join([db[0], db[1], "_idf.pkl"])
            name = "".join([core, db, ".pkl"])
            idf_name = "".join([core, db, "_idf.pkl"])
            print(name)
            result_database(func[expr], name, idf_name, num)
    else:
        print(expr)
        for db in data_list:
            # name = "".join([db[0], db[1], ".pkl"])
            # name = "".join([db[0], core, db[1], ".pkl"])
            name = "".join([core, db, ".pkl"])
            print(name)
            result_database(func[expr], name, None, num)

def experiment_vs_k(num, expr="IOU"):
    func = {
        "IOU": iou_distance,
        "BOL": label_distance,
        "TF_IDF": label_distance
    }
    core = "vs_db_32"
    front = [""]
    # front = ["big", ""]
    end = ["_4", ""]
    addon = product(front, end)
    if expr == "TF_IDF":
        print(expr)
        for a in addon:
            name = "".join([a[0], core, a[1], ".pkl"])
            idf_name = "".join([a[0], core, a[1], "_idf.pkl"])
            print(name)
            result_database(func[expr], name, idf_name, num)
    else:
        print(expr)
        for a in addon:
            name = "".join([a[0], core, a[1], ".pkl"])
            print(name)
            result_database(func[expr], name, None, num)


def main():
    # experiment_vs_k(int(sys.argv[1]), "TF_IDF")
    experiment_misa_code_len(int(sys.argv[1]), "BOL")
    experiment_misa_code_len(int(sys.argv[1]), "IOU")
    experiment_misa_code_len(int(sys.argv[1]), "TF_IDF")

if __name__=='__main__':
    main()
