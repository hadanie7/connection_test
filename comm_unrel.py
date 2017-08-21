# -*- coding: utf-8 -*-
"""
Created on Mon Aug 21 13:56:06 2017

@author: J
"""

from network import setup_conn
from clock import Clock
import traceback

import logs

def test(num, freq, pack_size):
    conn = setup_conn()
      
    tms = []
    rec = [float('NaN')]*num
    
    rec_num = 0
    
    c = Clock()
    iii = 0
    STOP = num
    STOP_ANYWAY = 1.1*num
    happy_ending = True
    
    
    if not conn.are_you_OK():
            happy_ending = False
            for e in conn.get_errs():
                print e
    else:
    
        print 'a'
        while True:
            tms.append( c.get_time() )
            print iii
            if iii < STOP:
                conn.write_unrel('{0:{1}}'.format(iii,pack_size))
            for mes in conn.read_unrel():
                miii = int(mes)
    #            print '',miii
#                assert miii == len(rec)
                rec_num += 1
                rec[miii] = c.get_time()
                
            iii += 1
            c.tick(1.0/freq)
            if (len(tms) >= STOP and rec_num >= STOP) or len(tms) >= STOP_ANYWAY:
                break
            if not conn.are_you_OK():
                happy_ending = False
                for e in conn.get_errs():
                    print e
                break
            
    conn.close()
    
    logs.save_log(tms = tms, rec = rec,
             happy_ending=happy_ending)
             
             
if __name__ == "__main__":
    test(10*1000,1000,10)