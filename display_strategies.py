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
    
class MovingExtrapolate:
    act_num_w = 2
    act_num_p = 4
    def __init__(self, world):
        self.world = world
        self.pred = None
        self.pred_diff = 0
        self.sec_pred = None
        self.pred_diff2 = 0
    
    def step(self, queues, my_cont):
        to_real = min(len(q) for q in queues)
                
        wrld_mv = min(to_real, self.act_num_w)
        for i in xrange(wrld_mv):
            self.world.step([q.popleft() for q in queues])
        self.pred_diff -= wrld_mv
        self.pred_diff2 -= wrld_mv
        
        if self.pred_diff2 <= 0:
            self.pred_diff2 = 0
            self.pred2 = self.world.get_copy()
        
        real_to_disp = len(queues[my_cont])
        if real_to_disp == 0:
            self.pred_diff = 0
            self.pred = self.world.get_copy()
        elif real_to_disp-self.pred_diff2 < self.act_num_p:
            for i in xrange(self.pred_diff2,real_to_disp):
                self.pred2.step([q[i] if len(q)>i else 0+0j for q in queues])
            self.pred_diff2 = real_to_disp
            self.pred_diff = self.pred_diff2
            self.pred = self.pred2
            self.pred_diff2 = 0
        else:
            ac_p = real_to_disp - self.pred_diff
            ac_2 = max(0,self.act_num_p-ac_p)
            
            for i in xrange(self.pred_diff,real_to_disp):
                self.pred.step([q[i] if len(q)>i else 0+0j for q in queues])
            self.pred_diff = real_to_disp
            
            for i in xrange(self.pred_diff2,self.pred_diff2+ac_2):
                self.pred2.step([q[i] if len(q)>i else 0+0j for q in queues])
            self.pred_diff2 += ac_2
            
        return self.pred

def get_disp_strat(world):
    with open('local/disp_strat.txt') as f:
        params = f.read().split()
    tp = params[0]
    params = params[1:]
    cls = {'SimpleExtrapolate':SimpleExtrapolate, 'SimpleDelayed':SimpleDelayed, 'SmoothedDelayed':SmoothedDelayed, 'MovingExtrapolate':MovingExtrapolate}[tp]
    return cls(world, *params)
#    if tp == 'SimpleExtrapolate':
#        return SimpleExtrapolate(world)
#    elif tp == 'SimpleDelayed':
#        return SimpleDelayed(world)