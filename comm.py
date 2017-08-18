# -*- coding: utf-8 -*-
"""
Created on Mon Aug 14 20:59:44 2017

@author: D
"""

from network import setup_conn
from clock import Clock
import traceback

import logs

if __name__ == "__main__":
    conn = setup_conn()
      
    tms = []
    rec = []
    
    c = Clock()
    iii = 0
    STOP = 10*1000
    STOP_ANYWAY = 20*1000
    happy_ending = True
    
    print 'a'
    while True:
        tms.append( c.get_time() )
        print iii
        if iii < STOP:
            conn.write(str(iii))
        for mes in conn.read():
            miii = int(mes)
#            print '',miii
            assert miii == len(rec)
            rec.append( c.get_time() )            
            
        iii += 1
        c.tick(0.001)
        if (len(tms) >= STOP and len(rec) >= STOP) or len(tms) >= STOP_ANYWAY:
            break
        if not conn.are_you_OK():
            happy_ending = False
            for e in conn.get_errs():
                print e
            break
        
    conn.close()
    
    logs.save_log(tms = tms, rec = rec,
             happy_ending=happy_ending)