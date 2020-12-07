#!/usr/bin/env python3

import os
import r2pipe as r2
import sys
from multiprocessing import Pool

def create_json(orig_path, root_json="benign_json_test", extension=""):
    #name = orig_path.replace("/", "_")
    name = os.path.basename(orig_path)
    json_path = os.path.join(root_json, name) + extension
    t = r2.open(orig_path, ['-2'])
    jcontent = t.cmd('aaa;s main;agfj')
    t.quit()
    json_file = open(json_path, 'w')
    json_file.write(jcontent)
    json_file.close()

def create_json_virus(name, root_virus="malware/data/RAW_final_dataset", root_json="malware/data/jsons"):
    orig_path = os.path.join(root_virus, name)
    json_path = os.path.join(root_json, name)
    t = r2.open(orig_path, ['-2'])
    jcontent = t.cmd('aaa;agfj')
    t.quit()
    json_file = open(json_path, 'w')
    json_file.write(jcontent)
    json_file.close()

def multi(func, args, workers):
    pool = Pool(processes=workers, maxtasksperchild=5)
    pool.map(func, args)
    pool.terminate()
    pool.join()
    del pool

def process_list(name):
    with open(name) as f:
        files = [x.strip() for x in f.readlines()]
        print(len(files))
        multi(create_json, files, 5)

def process_folder(folder):
    for d in os.listdir(folder):
        todo = [os.path.join(d, x) for x in os.listdir(os.path.join(folder, d))]
        multi(create_json_virus, todo, 5)

if __name__=='__main__':
    if len(sys.argv) < 2:
        print("USAGE:\n\tmake_json.py <folder>\n\tmake_json.py <list_file.txt>\n\tmake_json.py <executable_file>")
        exit()
    if os.path.isdir(sys.argv[1]):
        process_folder(sys.argv[1])
        exit()
    if sys.argv[1][-4:] == '.txt':
        process_list(sys.argv[1])
    else:
        create_json(sys.argv[1], os.getcwd(), ".json")
