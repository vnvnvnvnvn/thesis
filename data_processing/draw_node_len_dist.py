#!/usr/bin/env python

import pickle as pkl

name = 'len_block.pkl'

with open(name, 'rb') as f:
    data = pkl.load(f)
