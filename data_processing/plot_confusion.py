#!/usr/bin/env python

import seaborn as sn
import pandas as pd
import matplotlib.pyplot as plt
import sys
import ast

def read_file(name):
    with open(name) as f:
        lines = f.readlines()
        collect_lines = []
        for l in lines:
            if len(l.strip()) > 0:
                collect_lines.append(l.strip())
        current_method = ""
        saved_data = {}
        for idx, l in enumerate(collect_lines):
            if len(l) == 3:
                current_method = l
                continue
            if "{" in l:
                name = (collect_lines[idx-2], current_method)
                start = l.find("{")
                end = l.find("}")
                saved_data[name] = ast.literal_eval(l[start:end+1])
        for name, value in saved_data.items():
            df = pd.DataFrame(data=0, index=["Virus","Worm","Backdoor","Trojan","Adware"],
                              columns=["Virus","Worm","Backdoor","Trojan","Adware"], dtype=int, copy=False)
            for k, v in value.items():
                df[k[0]][k[1]] = v
            plt.figure(figsize = (10,7))
            title = "_".join([name[0], name[1]])
            plt.title(title)
            sn.heatmap(df, annot=True)
            plt.savefig(title+".png")

def read_file_detect(name):
    with open(name) as f:
        lines = f.readlines()
        collect_lines = []
        for l in lines:
            if len(l.strip()) > 0:
                collect_lines.append(l.strip())
        current_method = ""
        saved_data = {}
        for idx, l in enumerate(collect_lines):
            if len(l) == 3:
                current_method = l
                continue
            if "{" in l:
                name = (collect_lines[idx-2], current_method)
                start = l.find("{")
                end = l.find("}")
                saved_data[name] = ast.literal_eval(l[start:end+1])
        for name, value in saved_data.items():
            df = pd.DataFrame(data=0, index=["malware", "not_malware"],
                              columns=["malware", "not_malware"], dtype=int, copy=False)
            for k, v in value.items():
                df[k[0]][k[1]] = v
            precision = df["malware"]["malware"] * 1.0 / (df["malware"]["malware"] + df["not_malware"]["malware"])
            recall = df["malware"]["malware"] * 1.0 / (df["malware"]["malware"] + df["malware"]["not_malware"])
            f1 = 2 * precision * recall / (precision + recall)
            print(name)
            print(str(precision) + " " + str(recall) + " " + str(f1))

def main():
    read_file_detect(sys.argv[1])
if __name__=='__main__':
    main()
