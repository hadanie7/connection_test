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
        
def null_func():
    pass
        
class SmoothedDelayed:
    
    def once_per_10(self,x):
        if self.cnt>0:
            self.cnt -= 1
            return min(x,1)
        else:
            if x>1:
                self.cnt = 10
            return min(x,2)
    def init_once(self):
        self.cnt = 0
        
        
    def __init__(self, world, func_type = 'simple'):
        self.smooth_types = {
                        'simple':lambda x: (min(x,5),null_func),
                        'once_per_10':(self.once_per_10,self.init_once),
                        }
        self.world = world
        self.smooth, init = self.smooth_types[func_type]
        init()
    def step(self, queues, my_cont):
        x = min([len(q) for q in queues])
        for i in xrange(self.smooth(x)):
            self.world.step([q.popleft() for q in queues])
        return self.world

def get_disp_strat(world):
    with open('local/disp_strat.txt') as f:
        params = f.read().split()
    tp = params[0]
    params = params[1:]
    cls = {'SimpleExtrapolate':SimpleExtrapolate, 'SimpleDelayed':SimpleDelayed, 'SmoothedDelayed':SmoothedDelayed}[tp]
    return cls(world, *params)
#    if tp == 'SimpleExtrapolate':
#        return SimpleExtrapolate(world)
#    elif tp == 'SimpleDelayed':
#        return SimpleDelayed(world)