# -*- coding: utf-8 -*-
"""
Created on Thu Aug 17 22:06:00 2017

@author: D
"""

import numpy as np
import os
import time

def get_new_log_name():
    with open('local/timing_path.txt') as f:
        timing_path = f.read()
    try:    
        with open(os.path.join(timing_path,'counter.txt'), 'r+') as f:
            n = int(f.read())
            f.seek(0)
            f.write(str(n+1))
            f.truncate()
    except:
        n = 10000+int(time.clock()*1000000) # choose random name
    n = str(n).zfill(4)
    return os.path.join(timing_path,'dump{}.npz'.format(n))

def save_log(**args):
    np.savez(get_new_log_name(), **args)