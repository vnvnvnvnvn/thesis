#!/usr/bin/env python3

import argparse
from ged import *
import networkx as nx
import sys
import os
import matplotlib.pyplot as plt
import time
import pickle
from top10 import mean_ap
from concurrent.futures import ProcessPoolExecutor
from functools import partial
from scipy.stats import spearmanr
from itertools import product
import random

class Solution():
    def __init__(self, cost_matrix, g1, g2):
        self.cost_matrix = np.array(cost_matrix)
        self.g1 = g1
        self.g2 = g2

    def solve(self):
        self.mapping = linear_sum_assignment(self.cost_matrix)
        self.estimate = self.cost_matrix[self.mapping].sum()
        self.dist = correct_cost(self.g1, self.g2, self.mapping)
        return self.dist

    def cross(self, other):
        cost_matrix = np.maximum(self.cost_matrix, other.cost_matrix)
        s = Solution(cost_matrix, self.g1, self.g2)
        return s

def ga(g1, g2, iterations=10, mutation_prob=0.3, min_mutation=6, max_mutation=30):
    orig_cm = node_cost_matrix(g1, g2)
    orig_sol = Solution(orig_cm, g1, g2)
    initial_dist = orig_sol.solve()
    orig_mapping = orig_sol.mapping
    initial = {}
    for r, c in zip(*orig_mapping):
        s = Solution(orig_cm, g1, g2)
        s.cost_matrix[r][c] = INF
        initial[s] = s.solve()
    full = max(len(g1) + len(g2), num_mutation)
    full = min(full, max_mutation)
    best_so_far = (orig_sol, initial_dist)
    for i in range(iterations):
        population = sorted(initial.items(), key=lambda x: x[1])[:full // 3]
        if population[0][1] < best_so_far[1]:
            best_so_far = population[0]
        pairs = list(product(population, population))
        random.shuffle(pairs)
        pairs = pairs[:full * 2 // 3]
        new_initial = {}
        for p, q in pairs:
            new_sol = p[0].cross(q[0])
            new_initial[new_sol] = new_sol.solve()
        for p in population:
            sol = p[0]
            if random.random() < mutation_prob:
                shuffled_mapping = list(zip(*sol.mapping))
                random.shuffle(shuffled_mapping)
                sol.cost_matrix[shuffled_mapping[0][0]][shuffled_mapping[0][1]] = INF
                new_cost = sol.solve()
            else:
                new_cost = p[1]
            new_initial[sol] = new_cost
        initial = new_initial
    answer = sorted(initial.items(), key=lambda x: x[1])
    if answer[0][1] < best_so_far[1]:
        best_so_far = answer[0]
    return best_so_far[1], orig_sol.estimate, orig_sol.dist

def estimated_vs_real(folder, number_of_files=100, plot_name=''):
    file_list = [os.path.join(folder, x) for x in os.listdir(folder)][:number_of_files]
    database = []
    for f in file_list:
        database.append(nx.read_gpickle(f))
    real = []
    estimated = []
    orig = []
    for i in range(len(file_list)):
        for j in range(i+1, len(file_list)):
            dist, est, orig_cost = ga(database[i], database[j], 7)
            real.append(dist)
            estimated.append(est)
            orig.append(orig_cost)
    mn = max(real+estimated)
    plt.xlim(0, mn)
    plt.ylim(0, mn)
    plt.gca().set_aspect('equal', adjustable='box')
    plt.scatter(real, orig, s=1)
    plt.savefig(plot_name+'.png')
    r = spearmanr(real, orig)
    return r

def main():
    parser = argparse.ArgumentParser(description="""So sanh khoang cach GED khi su dung va khi khong su dung GA""")
    parser.add_argument('--folder', help='Duong dan den folder can xu li')
    parser.add_argument('--plot', default='estimated_vs_real', help='Ten cua plot ket qua')
    parser.add_argument('-n', '--number_of_files', default=100, type=int, help='So luong file se co trong database')
    args = parser.parse_args()
    estimated_vs_real(args.folder, args.number_of_files, args.plot)

if __name__=='__main__':
    main()
