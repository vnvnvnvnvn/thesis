#!/usr/bin/env python3


from scipy.optimize import linear_sum_assignment
import numpy as np
import cfg_graph
import time
from itertools import product

INF = 1e22

def make_cost_matrix(g1, g2, ins_fun, del_fun, subs_fun):
    m = len(g1)
    n = len(g2)
    cost_matrix = np.zeros([m+n, m+n])
    cost_matrix[m:, 0:n] = INF
    cost_matrix[0:m, n:] = INF
    np.fill_diagonal(cost_matrix[m:, 0:n], ins_fun(g2))
    np.fill_diagonal(cost_matrix[0:m, n:], del_fun(g1))
    cost_matrix[0:m, 0:n] = subs_fun(g1, g2)
    return cost_matrix

def edge_edit(g1, g2):
    edge_cost = make_cost_matrix(g1, g2,
                                 cfg_graph.edge_insertion,
                                 cfg_graph.edge_deletion,
                                 cfg_graph.edge_substitution)
    row_ind, col_ind = linear_sum_assignment(edge_cost)
    dist = edge_cost[row_ind, col_ind].sum()
    return dist

def node_cost_matrix(g1, g2):
    node_cost = make_cost_matrix(g1, g2,
                                 cfg_graph.node_insertion,
                                 cfg_graph.node_deletion,
                                 cfg_graph.node_substitution)
    for i1, n1 in enumerate(g1.nodes):
        if len(g1[n1]) == 0:
            continue
        for i2, n2 in enumerate(g2.nodes):
            if len(g2[n2]) == 0:
                continue
            node_cost[i1][i2] += edge_edit(g1[n1], g2[n2])
    return node_cost

def correct_cost(g1, g2, assignment):
    edge_cost = make_cost_matrix(g1.edges, g2.edges,
                                 cfg_graph.edge_insertion,
                                 cfg_graph.edge_deletion,
                                 cfg_graph.edge_substitution)
    node_cost = make_cost_matrix(g1, g2,
                                 cfg_graph.node_insertion,
                                 cfg_graph.node_deletion,
                                 cfg_graph.node_substitution)
    node = node_cost[assignment].sum()
    swapped_node_g1 = {}
    swapped_node_g2 = {}
    edge_row_idx = []
    edge_col_idx = []
    edge_g1_to_idx = {}
    for idx,e in enumerate(g1.edges):
        edge_g1_to_idx[e] = idx
    edge_g2_to_idx = {}
    for idx, e in enumerate(g2.edges):
        edge_g2_to_idx[e] = idx

    for r, c in zip(*assignment):
        if r < len(g1) and c < len(g2):
            swapped_node_g1[list(g1.nodes)[r]] = list(g2.nodes)[c]
            swapped_node_g2[list(g2.nodes)[c]] = list(g1.nodes)[r]
    for idx, e in enumerate(g1.edges.data('weight')):
        if e[0] in swapped_node_g1.keys() and e[1] in swapped_node_g1.keys():
            other_edge = (swapped_node_g1[e[0]], swapped_node_g1[e[1]])
            if g2.has_edge(*other_edge):
                subbed_edge = g2.get_edge_data(*other_edge)
                edge_row_idx.append(idx)
                edge_col_idx.append(edge_g2_to_idx[other_edge])
            else:
                edge_row_idx.append(idx)
                edge_col_idx.append(idx+len(g2.edges))
        else:
            edge_row_idx.append(idx)
            edge_col_idx.append(idx+len(g2.edges))
    for idx, e in enumerate(g2.edges.data('weight')):
        if e[0] in swapped_node_g2.keys() and e[1] in swapped_node_g2.keys():
            other_edge = (swapped_node_g2[e[0]], swapped_node_g2[e[1]])
            if g1.has_edge(*other_edge):
                continue
            else:
                edge_row_idx.append(idx+len(g1.edges))
                edge_col_idx.append(idx)
        else:
            edge_row_idx.append(idx+len(g1.edges))
            edge_col_idx.append(idx)
    edge = edge_cost[edge_row_idx, edge_col_idx].sum()
    return node + edge

def ged(g1, g2, cost_matrix):
    row_ind, col_ind = linear_sum_assignment(cost_matrix)
    estimated_dist = cost_matrix[row_ind, col_ind].sum()
    dist = correct_cost(g1, g2, (row_ind, col_ind))
    return dist, estimated_dist
