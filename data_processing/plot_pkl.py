#!/usr/bin/env python

import pickle
import matplotlib.pyplot as plt

# num_doc = 1210767
# num_doc = 2053336
num_doc = 849256

handle = open('wc.pkl', 'rb')
df_handle = open('idf.pkl', 'rb')
word_count = pickle.load(handle)
wc_list = sorted(word_count.items(), key=lambda x: x[1])
wl, wc_num = list(zip(*wc_list))
print(len(wc_num))
# percentage = [1.0 * x / num_doc for x in wc_num]
plt.bar(range(len(wc_num)), wc_num, log=True)
plt.show()

df_count = pickle.load(df_handle)
cnt = []
for w in wl:
    cnt.append(df_count[w])
percentage = [1.0 * x / num_doc for x in cnt]
plt.bar(range(len(wc_num)), percentage, log=True)
plt.show()
