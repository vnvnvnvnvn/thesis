#!/usr/bin/env python

import random
import numpy as np

def name_to_index(data):
    data.sort()
    lut = {}
    for i, d in enumerate(data):
        lut[d.strip()] = i
    return lut

wf = open("word_file_arm")
lut = name_to_index(wf.readlines())

random.seed(42)
transformer = np.random.randn(32, len(lut))
np.save("transformer.npy", transformer)
