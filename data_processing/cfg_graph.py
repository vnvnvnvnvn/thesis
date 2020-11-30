#!/usr/bin/env python

import numpy as np
from distance import hamming

params = {
    'node_insertion': 0.5,
    'node_deletion': 0.5,
    'node_substitution': 0.1,
    'edge_insertion': 0.5,
    'edge_deletion': 0.5,
    'edge_substitution': 0.1
}

def edge_insertion(g):
    out = np.array([params['edge_insertion']] * len(g)) # * np.array([e['weight'] for e in g.values()])
    return out

def edge_deletion(g):
    out = np.array([params['edge_deletion']] * len(g)) # * np.array([e['weight'] for e in g.values()])
    return out

def edge_substitution(g1, g2):
    # g1_weight = np.array([e['weight'] for e in g1.values()])
    # g2_weight = np.array([e['weight'] for e in g2.values()])
    g1_weight = np.array([1 for e in g1.values()])
    g2_weight = np.array([1 for e in g2.values()])
    g1_expand = np.expand_dims(g1_weight, 1)
    out = np.abs(g1_expand - g2_weight) * params['edge_substitution']
    return out

def node_insertion(g):
    # node_only = np.array([params['node_insertion'] * x[1]['length'] for x in g.nodes(data=True)])
    node_only = np.array([params['node_insertion'] for x in g.nodes(data=True)])
    # edge_cost = params['edge_insertion'] # * np.array([sum(e['weight'] for e in g[w].values()) for w in g])
    edge_cost = [params['edge_insertion']] * len(g)
    return node_only + edge_cost

def node_deletion(g):
    # node_only = np.array([params['node_deletion'] * x[1]['length'] for x in g.nodes(data=True)])
    node_only = np.array([params['node_deletion'] for x in g.nodes(data=True)])
    # edge_cost = params['edge_deletion'] * np.array([sum(e['weight'] for e in g[w].values()) for w in g])
    edge_cost = [params['edge_deletion']] * len(g)
    return node_only + edge_cost

def node_substitution(g1, g2):
    def extract_labels(g):
        labels = ["" for x in range(len(g))]
        for node in g.nodes(data=True):
            labels[node[1]['idx']] = node[1]['data'][0]
        return np.array(labels)
    g1_labels = extract_labels(g1)
    g2_labels = extract_labels(g2)
    g1_expand = np.expand_dims(g1_labels, 1)
    combined = np.broadcast(g1_expand, g2_labels)
    out = np.empty(combined.shape)
    out.flat = [hamming(u, v) * params['node_substitution'] for u, v in combined]
    return out
