# -*- coding: utf-8 -*-
"""
Created on Mon Aug 14 20:37:38 2017

@author: J
"""
import time

class Clock:
    def __init__(me):
        me.first = time.clock()
        me.last = me.first        
        
    def tick(me,wtime):
        time.sleep(max(0,me.last+wtime-time.clock()))
        while time.clock()<me.last+wtime:
            pass
        if time.clock()-(me.last+wtime) > 0.0005:
            me.last = time.clock()
        else:
            me.last = (me.last+wtime)
    
    def get_time(me):
        return time.clock()-me.first