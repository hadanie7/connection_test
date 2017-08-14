# -*- coding: utf-8 -*-
"""
Created on Mon Aug 14 20:59:44 2017

@author: D
"""

import network
import numpy as np
from clock import Clock
from tcp_stream import StreamReader, StreamWriter

if __name__ == "__main__":
    ans =  raw_input("Be Server? (y/n)")
    if ans[0].lower() == 'y':
        ip = None
    else:
        with open('local/con_ip.txt', 'r') as f:
            ip = f.read()
    s = network.get_socket(ip)
    r = StreamReader(s)
    w = StreamWriter(s)
    
    tms = []
    rec = []
    
    c = Clock()
    iii = 0
    for i in range(10*1000):
        tms.append( c.get_time() )
        w.write(str(iii))
        for mes in r.read():
            miii = int(mes)
            assert miii == len(rec)
            rec.append( c.get_time() )            
            
        iii += 1
        c.tick(0.001)
    
    s.close()
    tms = np.array(tms)
    rec = np.array(rec)
    np.savez('local/timing.npz', tms = tms, rec = rec)