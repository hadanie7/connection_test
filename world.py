# -*- coding: utf-8 -*-
"""
Created on Sun Aug 13 15:20:38 2017

@author: D
"""

import math
import copy

def calcolission_r(p1, r1, v1, p2, r2, v2):
    v = v2-v1
    p = p2-p1
    r = r1+r2
    rot = (v/abs(v)).conjugate()
    # rotate the problem about the origin such that v is positive
    v = abs(v) # equiv to (v *= rot) up to numerical error and type
    p *= rot
    if p.real > 0 or abs(p.imag) > r :
        return None
    tth = -p.real/v - math.sqrt(R*R-p.imag*p.imag) # time to hit


class GO:
    def __init__(self, init_pos):
        self.p = init_pos
    
    def get_pos(self):
        """as complex"""
        return self.p
    
    def get_class(self):
        """ 'ac', 'st' """
        if isinstance(self, Actor):
            return 'ac'
        else:
            return 'st'
    
class Actor(GO):
    def __init__(self, init_pos):
        GO.__init__(self, init_pos)
        self.color = 'black'
        self.radius = 19.0/64
        self.v = 0j
    
    def get_radius(self):
        """as float"""
        return self.radius
        
    def get_color(self):
        """'black' or 'white'"""
        return self.color
    
    def accelerate(self, dt, acc):
        self.v += dt*acc
    
    def advance(self, dt):
        self.p += dt*self.v

class Stone(GO):
    def get_type(self):
        """ 'box', 'wall' """
        return 'wall'

class World:
    def __init__(self):
        pass
        self.obj = []
        self.step_time = 0.01
        self.default_setup()

    def default_setup(self):
        self.main_ac = [Actor(10.+6.5j)]
        self.obj.append( self.main_ac )
        for i in range(20):
            self.obj.append( Stone(i+0j))
#interface
    
    def get_view_position(self):
        """return the position of the object that the display should follow
        complex"""
        return self.main_ac[0].get_pos()
    
    def get_objs(self):
        """return list of objects"""
        for i in self.obj:
            yield i

    def get_copy(self):
        return copy.deepcopy(self)
    
    def get_controller_count(self):
        return len(self.main_ac)
#end interface    
    
    def step(self, acc):
        for i,a in enumerate(acc):
            self.main_ac[i].accelerate(self.step_time, a)
        for o in self.obj:
            if hasattr(o, 'advance'):
                o.advance(self.step_time)
