#!/usr/bin/env python3

import argparse
from top10 import *
import pickle as pkl
from itertools import product, islice
from functools import partial
from calculate_wl import label_distance, iou_distance, tf_distance
from collections import defaultdict
from ga_ged import ga
import networkx as nx
import os
from plot_confusion import process_detection_result, process_classification_result, plot_confusion_matrix


def generate_test_data(item_list, number):
    ret_data = []
    for data in islice(item_list.items(), number):
        ret_data.append(data)
    return ret_data

def generate_detect_data(item_list, number):
    cnt = 0
    ret_data = []
    for k, v in item_list.items():
        orig_class = k.split("/")[-2]
        if orig_class == "Benign":
            ret_data.append((k, v))
            cnt += 1
        if cnt >= number // 2:
            break

    for k, v in item_list.items():
        orig_class = k.split("/")[-2]
        if orig_class == "Benign":
            continue
        ret_data.append((k, v))
        cnt += 1
        if cnt >= number:
            break
    return ret_data


def process_retrieve_data(f, data, test_data, ged=None, neighbors=10):
    name_list = [os.path.basename(x) for x in set(data.keys())]
    time_list = []
    result_list = {}

    for k, v in test_data:
        start = time.time()
        closest_k = top_distance(f, data, v, neighbors)

        if ged is not None:
            ged_g1 = nx.read_gpickle(os.path.join(ged, k))
            ged_order = {}
            for cand, dist in closest_k:
                ged_g2 = nx.read_gpickle(os.path.join(ged, cand))
                ged_dist, _, _ = ga(ged_g1, ged_g2, 1)
                ged_order[cand] = ged_dist
            ged_sorted = sorted(ged_order.items(), key=lambda x: x[1])
            cur_map = mean_ap(name_list, ged_sorted, k)
        else:
            cur_map = mean_ap(name_list, closest_k, k)
        if cur_map is None:
            continue
        time_list.append(time.time() - start)
        result_list[k] = cur_map

    ma = np.mean(list(result_list.values()))
    mean_time = np.mean(time_list)
    var_time = np.var(time_list)
    no_result = len(np.where(np.asarray(list(result_list.values())) < 0.01)[0])
    return ma, no_result, mean_time, var_time


def process_classify_data(f, data, test_data, neighbors=11):
    total_result = defaultdict(lambda: 0)
    time_list = []
    result_list = {}

    for k, v in test_data:
        start = time.time()
        closest_k = top_distance(f, data, v, neighbors)
        time_list.append(time.time() - start)
        result_list[k] = classify_malware_type(closest_k, k)
    for name, res in result_list.items():
        orig_class = name.split("/")[-2]
        total_result[(orig_class, res)] += 1
    mean_time = np.mean(time_list)
    var_time = np.var(time_list)
    return total_result, mean_time, var_time


def process_detect_data(f, data, test_data, neighbors=6):
    total_result = defaultdict(lambda: 0)
    time_list = []
    result_list = {}

    for k, v in test_data:
        start = time.time()
        closest_k = top_distance(f, data, v, neighbors)
        time_list.append(time.time() - start)
        result_list[k] = classify_malware(closest_k, k)
    for name, res in result_list.items():
        orig_class = name.split("/")[-2]
        if orig_class == "Benign":
            orig_class = "not_malware"
        else:
            orig_class = "malware"
        total_result[(orig_class, res)] += 1
    mean_time = np.mean(time_list)
    var_time = np.var(time_list)
    return total_result, mean_time, var_time


def retrieve_experiment(ged, num, database_list, save_file, expr="IOU", neighbors=10):
    func = {
        "IOU": iou_distance,
        "BOL": label_distance,
        "IDF": label_distance
    }

    result_data = [expr]
    for db in database_list:
        result_data.append(db)
        with open(db, 'rb') as handle:
            data = pkl.load(handle)
        test_data = generate_test_data(data, num)
        result, no_answer, mt, vt = process_retrieve_data(func[expr], data, test_data, ged)
        result_data.append(str(mt) + "\t" + str(vt))
        result_data.append(str(result) + "\t" + str(no_answer)+"\n")
    with open(save_file, 'a+') as f:
        f.write("\n".join(result_data))


def classify_experiment(plot, num, database_list, save_file, expr="IOU", neighbors=11):
    func = {
        "IOU": iou_distance,
        "BOL": label_distance,
        "IDF": label_distance
    }

    result_data = [expr]
    for db in database_list:
        result_data.append(db)
        with open(db, 'rb') as handle:
            data = pkl.load(handle)
        test_data = generate_test_data(data, num)
        result, mt, vt = process_classify_data(func[expr], data, test_data)
        result_data.append(str(mt) + "\t" + str(vt))
        result_data.append(str(result)+"\n")
        if plot:
            df, perc = process_classification_result(result)
            print(perc)
            plot_confusion_matrix(df, expr)
    with open(save_file, 'a+') as f:
        f.write("\n".join(result_data))


def detect_experiment(plot, num, database_list, save_file, expr="IOU", neighbors=6):
    func = {
        "IOU": iou_distance,
        "BOL": label_distance,
        "IDF": label_distance
    }

    result_data = [expr]
    for db in database_list:
        result_data.append(db)
        with open(db, 'rb') as handle:
            data = pkl.load(handle)
        test_data = generate_detect_data(data, num)
        result, mt, vt = process_detect_data(func[expr], data, test_data)
        result_data.append(str(mt) + "\t" + str(vt))
        result_data.append(str(result)+"\n")
        if plot:
            print(process_detection_result(result))
    with open(save_file, 'a+') as f:
        f.write("\n".join(result_data))


def main():
    parser = argparse.ArgumentParser(description="""Chay cac thi nghiem tren database da tao ra tu truoc""")
    parser.add_argument('-q', '--query', type=int, default=1000, help='So luong queries muon thuc hien')
    parser.add_argument('--core', action='append', help='Ten cua database can xu ly', required=True)
    parser.add_argument('--prefix', action='append', default=[""], help='Prefix cua cac database muon xu ly')
    parser.add_argument('--postfix', action='append', default=[""], help='Postfix cua cac database muon xu ly')
    parser.add_argument('-t', '--task', choices=['detect', 'classify', 'retrieve'], default='detect', help='Task muon thu')
    parser.add_argument('-n', '--number_of_neighbors', default=10, type=int, help='So nearest neighbors duoc vote')
    parser.add_argument('-d', '--distance_type', choices=['iou', 'cosine', 'idf'], default='iou', help='Phep tinh do tuong dong')
    parser.add_argument('-f', '--file', help='File de viet ket qua', required=True)
    parser.add_argument('-v', '--visualize', action='store_true', help='Plot confusion matrix')
    parser.add_argument('--ged', help='GED graph folder')
    args = parser.parse_args()

    task_lookup = {
        'classify': partial(classify_experiment, args.visualize is not None),
        'detect': partial(detect_experiment, args.visualize is not None),
        'retrieve': partial(retrieve_experiment, args.ged)
    }

    distance_lookup = {
        'iou': 'IOU',
        'cosine': 'BOL',
        'idf': 'IDF'
    }

    database_list = product(args.prefix, args.core, args.postfix)
    database_list = ["".join(list(x) + ['.pkl']) for x in database_list]
    task_lookup[args.task](args.query, database_list, args.file, distance_lookup[args.distance_type], args.number_of_neighbors)


if __name__=='__main__':
    main()
