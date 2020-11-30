#!/usr/bin/env python

import codecs
import pickle

f = codecs.open("x86.html", 'r')
data = f.read().split("<h2>")
print(len(data))
core = data[1].split("tbody")
for i in range(2, len(data)):
    print(data[i])
core_table = core[1].replace("<tr>","")
core_table = core_table.replace("</tr>", "\n")
core_table = core_table.replace("<td>", "")
core_table = core_table.replace("</td>", " ")
table = core_table.split("\n")
print(len(table))

instr = {}
for i in range(1, len(table)):
    s = table[i].replace("</a", "")
    s = s.split(">")
    if len(s) < 3:
        print(table[i])
        continue
    instr[s[1].strip()] = s[2].strip()

print(len(instr))
print(instr["XTEST"])
with open('core_x86.pkl', 'w') as handle:
    pickle.dump(instr, handle)
