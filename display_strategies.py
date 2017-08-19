# -*- coding: utf-8 -*-
"""
Created on Sat Aug 19 12:17:15 2017

@author: D
"""

# interface for
#class DispStrat:
#    def __init__(self, world):
#        raise NotImplementedError
#    
#    def step(queues, my_cont):
#        """returns a world object to be drawn to the screen"""
#        raise NotImplementedError

class SimpleExtrapolate:
    def __init__(self, world):
        self.world = world
    
    def step(self, queues, my_cont):
        while all([len(q)>0 for q in queues]):
            self.world.step([q.popleft() for q in queues])
        prediction = self.world.get_copy()
        for i in xrange(len(queues[my_cont])):
            prediction.step([q[i] if len(q)>i else 0+0j for q in queues])
        return prediction

class SimpleDelayed:
    def __init__(self, world):
        self.world = world
    
    def step(self, queues, my_cont):
        while all([len(q)>0 for q in queues]):
            self.world.step([q.popleft() for q in queues])
        return self.world

def get_disp_strat(world):
    with open('local/disp_strat.txt') as f:
        tp = f.read()
    cls = {'SimpleExtrapolate':SimpleExtrapolate, 'SimpleDelayed':SimpleDelayed}[tp]
    return cls(world)
#    if tp == 'SimpleExtrapolate':
#        return SimpleExtrapolate(world)
#    elif tp == 'SimpleDelayed':
#        return SimpleDelayed(world)