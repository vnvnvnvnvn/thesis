#!/usr/bin/env python

import networkx as nx
import re
import sys
import copy
import os

jump_instr = set()
jump_arch = {"x86": ("j", "jmp", set(), "#"),
             "arm": ("b", "b", set(["bic"]), "@")}
unreachable = set()
func_names = set()

def process(lines, func, arch):
    # print("\n\n"+func)
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
            # if len(cur_blocks) > 0:
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
    # print(blocks)
    # print(branch_points)
    # cur_id = func + "_0"
    # cur_branch = 1

    # for i, l in enumerate(lines):
    #     l = l.split(jump_arch[arch][3])[0].strip()
    #     if len(l) == 0:
    #         continue
    #     if l[0] == ".":
    #         continue

    #     if i == branch_points[cur_branch][1]:
    #         cur_branch += 1
    #         if len(cur_blocks) > 0:
    #             blocks[cur_id] = copy.deep_copy(cur_blocks)
    #             cur_blocks = []
    #         if cur_branch >= len(branch_points):
    #             break

    #     l = l.replace("\t", " ")
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
            #    dest = func + "_" + str(ids[dest])
            #    edge_list.append((cur_id, dest))
                edge_list.append((bid[0], dest))
                jump_instr.add(instr)
            #    cur_blocks.append(l)
            #    print(cur_blocks)
            #    g.add_node(cur_id, data=copy.deepcopy(cur_blocks))
                # cur_blocks = []
                # j = i+1
                # while lines[j] == "":
                #     j += 1
                # if lines[j].strip()[0] != ".":
                #     next_blk = func + "_" + str(j)
                # else:
                #     while lines[j].strip()[0] == "." and lines[j].split(":")[0] not in ids:
                #         j += 1
                #     if lines[j].split(":")[0] not in ids:
                #         print(lines[j] + " not in ids")
                #     next_blk = func + "_" + str(j)
                if instr != jump_arch[arch][1] and bpidx < len(branch_points) - 1:
                    next_blk = branch_points[bpidx+1][0]
                    edge_list.append((bid[0], next_blk))
                # cur_id = next_blk
            else:
                if dest in func_names:
                    unresolved.append((bid[0], dest))
#                print("In " + func + " Dest not in id " + l)
                unreachable.add(dest)
                # cur_blocks.append(l)
        else:
            # cur_blocks.append(l)
            if bpidx < len(branch_points) - 1:
                next_blk = branch_points[bpidx+1][0]
                edge_list.append((bid[0], next_blk))
    # g.add_node(cur_id, data=copy.deepcopy(cur_blocks))
    # print(edge_list)
    # for p in edge_list:
    #     g.add_edge(*p)
    g.add_edges_from(edge_list)
    # print(len(g.edges))
    return g

def save_file(path, arch, functions):
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
    saved_dirname = os.path.join(os.getcwd(), "graphs", arch)
    if not os.path.exists(saved_dirname):
        os.mkdir(saved_dirname)

    for name, data in functions.items():
        saved_path = os.path.join(saved_dirname,
                                  "_".join([file_name, name, level]))
        nx.write_gpickle(data, saved_path)

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

if __name__=='__main__':
    fs = read_file(sys.argv[1], "x86")
    for name, fn in fs.items():
        print(name)
        for node in fn.nodes(data='data'):
            print(node[0])
            print(node[1])
    # cnt = 0
    # for name in os.listdir(sys.argv[1]):
    #     fns = read_file(os.path.join(sys.argv[1], name), "arm")
    #     save_file(os.path.join(sys.argv[1], name), "arm", fns)
    #     cnt += 1
    #     if cnt >= 200:
    #         break
    # print(jump_instr)
    # print(unreachable)
