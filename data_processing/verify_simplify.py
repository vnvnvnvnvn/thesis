#!/usr/bin/env python

import os
import sys
from collections import defaultdict

keys = set(["VAR", "IMM", "ADDR", "FUNC", "BB", "REG", "REGPTR"])
vocab = defaultdict(lambda:0)

def main():
    unrecognized = set()
    with open(sys.argv[1]) as f:
        for line in f.readlines():
            #fs = line.split()[1:]
            #for x in fs:
                #if x not in keys:
                    #unrecognized.add(x)
            vocab[line.strip()] += 1
    # print(unrecognized)
    print(len(vocab))
    print(vocab)
    l = sorted(vocab.items(), key=lambda x: x[1])
    print(l)
    words = sorted(vocab.keys())
    with open("word_file_arm", 'w') as wf:
        wf.write("\n".join(words))

if __name__=='__main__':
    main()
