#!/usr/bin/env python3

import networkx as nx
import re
import sys
import copy
import os
import matplotlib.pyplot as plt

jump_instr = set()
jump_arch = {"x86": ("j", "jmp", set(), "#"),
             "arm": ("b", "b", set(["bic"]), "@")}
unreachable = set()
func_names = set()

def process(lines, func, arch):
    unresolved = []
    ids = {}
    edge_list = []
    blocks = {}
    g = nx.DiGraph()
    cur_blocks = []

    for i, l in enumerate(lines):
        if len(l.strip()) == 0:
            continue
        if (l[:2] == ".L" and l[:5] != ".Ltmp") or ("%bb" in l[:5]):
            label = l.split(":")[0]
            ids[label] = i
            if i > 0:
                blocks[last_label] = copy.deepcopy(cur_blocks)
            last_label = label
            cur_blocks = []
        else:
            if l[0] != "\t" and l[0] != " ":
                continue
            l = l.split(jump_arch[arch][3])[0].strip()
            if len(l) == 0 or l[0] == '.':
                continue
            l = l.replace("\t", " ")
            cur_blocks.append(l)
    branch_points = [x for x in ids.items() if x[0] in blocks.keys()]
    branch_points = sorted(branch_points, key=lambda x: x[1])
    for bpidx, bid in enumerate(branch_points):
        if bid[0] not in blocks.keys():
            continue
        g.add_node(bid[0], data=blocks[bid[0]])
        if len(blocks[bid[0]]) == 0:
            if bpidx < len(branch_points) - 1:
                next_blk = branch_points[bpidx+1][0]
                edge_list.append((bid[0], next_blk))
            continue
        l = blocks[bid[0]][-1]
        cmd = l.split()

        if l[0] == jump_arch[arch][0] and all([x != cmd[0] for x in jump_arch[arch][2]]):
            instr = cmd[0]
            dest = cmd[1]
            if dest in ids:
                edge_list.append((bid[0], dest))
                jump_instr.add(instr)
                if instr != jump_arch[arch][1] and bpidx < len(branch_points) - 1:
                    next_blk = branch_points[bpidx+1][0]
                    edge_list.append((bid[0], next_blk))
            else:
                if dest in func_names:
                    unresolved.append((bid[0], dest))
                unreachable.add(dest)
        else:
            if bpidx < len(branch_points) - 1:
                next_blk = branch_points[bpidx+1][0]
                edge_list.append((bid[0], next_blk))
    g.add_edges_from(edge_list)
    return g

def save_file(path, arch, functions, saved_dirname):
    file_name = os.path.basename(path)
    file_name = re.sub(".c.s$", "", file_name)
    file_name = file_name.split("-")
    p = re.compile("^O(?P<level>\d$)")
    level = None
    level_idx = -1
    for idx, part in enumerate(file_name):
        matched = p.search(part)
        if matched:
            level = matched.group('level')
            level_idx = idx
            break
    file_name = "_".join(file_name[level_idx+1:])
    if not os.path.exists(saved_dirname):
        os.mkdir(saved_dirname)

    for name, data in functions.items():
        saved_path = os.path.join(saved_dirname,
                                  "_".join([file_name, name, level]))
        nx.write_gpickle(data, saved_path)
    return file_name

def read_file(path, arch):
    print("Processing " + path)
    ids = {}
    functions = {}

    with open(path) as f:
        lines = f.readlines()
        for idx, line in enumerate(lines):
            if line == "\n": continue
            if not line[0] in ["\t", " "]:
                label = line.split(":")[0]
                if "func" in label:
                    if label in ids.keys():
                        label += "_1"
                    ids[label] = idx
                if ".Lfunc_begin" in label:
                    func_names.add(lines[idx-1].split(":")[0])
        for label in ids.keys():
            if ".Lfunc_begin" in label:
                func_id = label[12:]
                name = lines[ids[label] - 1].split(":")[0]
                end = ".Lfunc_end" + func_id
                functions[name] = process(lines[ids[label] : ids[end]+1], name, arch)
    return functions

def inspect(name, arch):
    fs = read_file(name, arch)
    for name, fn in fs.items():
        print(name)
        for node in fn.nodes(data='data'):
            print(node[0])
            print(node[1])
        nx.draw_networkx(fn)
        plt.show()

if __name__=='__main__':
    if len(sys.argv) < 3:
        print("USAGE:\n\tread_MISA.py <file_name> <architecture>")
        exit()
    inspect(sys.argv[1], sys.argv[2])
