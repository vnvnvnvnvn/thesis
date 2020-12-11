#!/usr/bin/env python3

import argparse
import os
import r2pipe as r2
import sys
from multiprocessing import Pool
from functools import partial
import pickle
from concurrent.futures import ProcessPoolExecutor

def create_json(orig_path, root_json="benign_json_test", extension=""):
    name = orig_path.replace("/", "_")
    #name = os.path.basename(orig_path)
    json_path = os.path.join(root_json, name) + extension
    t = r2.open(orig_path, ['-2'])
    # jcontent = t.cmd('aaa;agfj @@f')
    jcontent = t.cmd('aaa;s main;agfj')
    t.quit()
    json_file = open(json_path, 'w')
    json_file.write(jcontent)
    json_file.close()

def create_json_virus(orig_folder, name, root_json="../new_jsons"):
    orig_path = os.path.join(orig_folder, name)
    root_json = os.path.join(orig_folder, root_json)
    json_path = os.path.join(root_json, name)
    if os.path.isfile(json_path):
        return
    maltype = name.split('/')[-2]
    # if maltype != 'Virus':
        # return
    t = r2.open(orig_path, ['-2'])
    jcontent = t.cmd('aaa;agfj @@f')
    t.quit()
    json_file = open(json_path, 'w')
    json_file.write(jcontent)
    json_file.close()

def multi(func, args, workers):
    with ProcessPoolExecutor(workers) as ex:
        ex.map(func, args)
    #pool = Pool(processes=workers, maxtasksperchild=10)
    #pool.map(func, args)
    #pool.terminate()
    #pool.join()
    #del pool

def process_list(name):
    with open(name) as f:
        files = [x.strip() for x in f.readlines()]
        print(len(files))
        multi(create_json, files, 10)

def process_folder(folder, t):
    import random
    import time
    handle = open('reporting_type.pkl', 'rb')
    data_arch = pickle.load(handle)
    handle.close()
    todo = [d for (d, arch) in data_arch.items() if arch == 'x86' and d.split('/')[-2]==t]
    random.seed(time)
    random.shuffle(todo)
    multi(partial(create_json_virus, folder), todo, 3)

if __name__=='__main__':
    if len(sys.argv) < 2:
        print("USAGE:\n\tmake_json.py <folder>\n\tmake_json.py <list_file.txt>\n\tmake_json.py <executable_file>")
        exit()
    if os.path.isdir(sys.argv[1]):
        process_folder(sys.argv[1], sys.argv[2])
        exit()
    if sys.argv[1][-4:] == '.txt':
        process_list(sys.argv[1])
    else:
        create_json(sys.argv[1], os.getcwd(), ".json")
