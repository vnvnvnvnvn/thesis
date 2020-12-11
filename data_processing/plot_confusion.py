#!/usr/bin/env python

import argparse
import seaborn as sn
import pandas as pd
import matplotlib.pyplot as plt
import sys
import ast


def process_detection_result(data):
    type_name = ["malware", "not_malware"]
    df = pd.DataFrame(data=0, index=type_name,
                      columns=type_name, dtype=int, copy=False)
    for k, v in data.items():
        df[k[0]][k[1]] = v
    precision = df["malware"]["malware"] * 1.0 / (df["malware"]["malware"] + df["not_malware"]["malware"])
    recall = df["malware"]["malware"] * 1.0 / (df["malware"]["malware"] + df["malware"]["not_malware"])
    f1 = 2 * precision * recall / (precision + recall)
    return precision, recall, f1

def process_classification_result(data):
    type_name = ["Virus","Worm","Backdoor","Trojan","Adware"]
    df = pd.DataFrame(data=0, index=type_name,
                      columns=type_name, dtype=int, copy=False)
    correct = 0
    total = 0
    for k, v in data.items():
        df[k[0]][k[1]] = v
        if k[0] == k[1]:
            correct += v
        total += v
    perc = correct * 1.0 / total
    return df, perc


def read_file(name):
    saved_data = {}
    with open(name) as f:
        lines = f.readlines()
        collect_lines = []
        for l in lines:
            if len(l.strip()) > 0:
                collect_lines.append(l.strip())
        current_method = ""
        for idx, l in enumerate(collect_lines):
            if len(l) == 3:
                current_method = l
                continue
            if "{" in l:
                name = (collect_lines[idx-2], current_method)
                start = l.find("{")
                end = l.find("}")
                saved_data[name] = ast.literal_eval(l[start:end+1])
    return saved_data

def read_file_classify(file_name):
    saved_data = read_file(file_name)
    for name, value in saved_data.items():
        df, perc = process_classification_result(value)
        plt.figure(figsize = (10,7))
        title = "_".join([name[0], name[1], str(perc)])
        print("Correct: " + str(perc))
        plt.title(title)
        sn.heatmap(df, annot=True)
        plt.savefig(title+".png")

def read_file_detect(file_name):
    saved_data = read_file(file_name)
    for name, value in saved_data.items():
        precision, recall, f1 = process_detection_result(value)
        print(name)
        print(str(precision) + " " + str(recall) + " " + str(f1))

def main():
    parser = argparse.ArgumentParser(description="""Ve bieu do tu ket qua thi nghiem classify va in ket qua precision recall cho thi nghiem detect""")
    parser.add_argument('--file', help='File chua ket qua thi nghiem', required=True)
    parser.add_argument('--task', choices=['detect', 'classify'], default='detect', help='Task cua thi nghiem')
    args = parser.parse_args()

    fn_lookup = {
        'detect': read_file_detect,
        'classify': read_file_classify
    }
    fn_lookup[args.task](args.file)


if __name__=='__main__':
    main()
