# -*- coding: utf-8 -*-
"""
Created on Mon Aug 14 21:47:34 2017

@author: D
"""

import numpy as np
import matplotlib.pyplot as plt

def get_dump_name():
    with open('timing/counter.txt', 'r') as f:
        n = int(f.read())-1
    n = str(n).zfill(4)
    return 'timing/dump{}.npz'.format(n)

class Struct:
    def __init__(self, **entries):
        self.__dict__.update(entries)

d = np.load(get_dump_name())
d = Struct(**{f:d[f] for f in d.files})

tms = d.tms
rec = d.rec

def plot_delay(rec):
    fig, ax = plt.subplots()
    ax.set_yscale('log')
    time = arange(0,len(rec))*0.001
    ax.plot(time, rec-time)
    ax.set_xlabel('time[s]')
    ax.set_ylabel('delay[s]')
    ax.grid(True, which='both')
