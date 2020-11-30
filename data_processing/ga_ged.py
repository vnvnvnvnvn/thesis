#!/usr/bin/env python

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

def ga(g1, g2, iterations=10, mutation_prob=0.3):
    orig_cm = node_cost_matrix(g1, g2)
    orig_sol = Solution(orig_cm, g1, g2)
    initial_dist = orig_sol.solve()
    orig_mapping = orig_sol.mapping
    initial = {}
    for r, c in zip(*orig_mapping):
        s = Solution(orig_cm, g1, g2)
        s.cost_matrix[r][c] = INF
        initial[s] = s.solve()
    full = max(len(g1) + len(g2), 6)
    full = min(full, 30)
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

def estimated_vs_real(folder):
    file_list = [os.path.join(folder, x) for x in os.listdir(folder)][:100]
    database = []
    for f in file_list:
        database.append(nx.read_gpickle(f))
    real = []
    estimated = []
    orig = []
    count = 0
    for i in range(len(file_list)):
        for j in range(i+1, len(file_list)):
            count += 1
            if count % 50 == 0:
                print("Done " + str(count))
            # cm = node_cost_matrix(database[i], database[j])
            # dist, est = ged(database[i], database[j], cm)
            dist, est, orig_cost = ga(database[i], database[j], 7)
            real.append(dist)
            estimated.append(est)
            orig.append(orig_cost)
    m = max(real)
    n = max(estimated)
    mn = max(m, n)
    plt.xlim(0, mn)
    plt.ylim(0, mn)
    plt.gca().set_aspect('equal', adjustable='box')
    plt.scatter(real, orig, s=1)
    plt.show()
    r = spearmanr(real, orig)
    print(r)

def main():
    estimated_vs_real(sys.argv[1])
    # folder = sys.argv[1]
    # file_list = [os.path.join(folder, x) for x in os.listdir(folder)]
    # for f in file_list:
    #     g = nx.read_gpickle(f)
    #     if len(g.nodes()) > 5 and len(g.nodes()) < 10:
    #         name = f
    #         break
    # print(name)
    # g1 = nx.read_gpickle(name)
    # dif_end = (int(f[-1]) + 1) % 4
    # g2 = nx.read_gpickle(name[:-1]+str(dif_end))

    # ga(g1, g2)

if __name__=='__main__':
    main()
