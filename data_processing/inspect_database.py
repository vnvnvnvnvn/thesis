#!/usr/bin/env python

import pickle
import matplotlib.pyplot as plt
import sys

def plot_data(name):
    with open(name, 'rb') as handle:
        data = pickle.load(handle)
        wc_list = sorted(data.items(), key=lambda x: x[1])
        print(len(wc_list))
        wl, wc_num = list(zip(*wc_list))
        # plt.bar(range(len(wc_num)), wc_num)
        # plt.show()
        print(wc_num[0])
        print(wc_num[-1])

def main():
    plot_data(sys.argv[1])

if __name__=='__main__':
    main()
