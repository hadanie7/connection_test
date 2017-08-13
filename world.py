# -*- coding: utf-8 -*-
"""
Created on Sun Aug 13 15:20:38 2017

@author: D
"""

import math
import copy
import pprint

DEBUG = True
INF = float('inf')

def calcolission_r(p1, r1, v1, p2, r2, v2):
    v = v2-v1
    p = p2-p1
    r = r1+r2
    try:
        rot = (v/abs(v)).conjugate()
    except ZeroDivisionError:
        return INF, None
    # rotate the problem about the origin such that v is positive
    v = abs(v) # equiv to (v *= rot) up to numerical error and type
    p *= rot
    if p.real > 0 or abs(p.imag) > r :
        return INF, None
    
    hy = p.imag
    hx = - math.sqrt(r*r-hy*hy)
    tth = (-p.real + hx)/v # time to hit
    col_vec = hx + 1j*hy
    col_vec /= abs(col_vec)
    col_vec *= rot.conjugate()
    if DEBUG and abs(tth)<0.01: pprint.pprint(locals())
    return tth, col_vec

def calcolission_seg(p1, r1, v1, p2, r2, v2):
    raise NotImplementedError

def phys_col(o1, o2, col_vec):
    if DEBUG: print 'boom!'
    if not o2.is_dynamic():
        o1, o2 = o2, o1
    if not o1.is_dynamic():
        assert o2.is_dynamic()
        o2.v /= col_vec
        o2.v = -o2.v.real+1j*o2.v.imag
        o2.v *= col_vec
        return
    raise NotImplementedError

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
    
    def is_dynamic(self):
        return self.get_class() == 'ac'
    
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
    
    def get_corners(self):
        ret = []
        for i in range(2):
            for j in range(2):
                ret.append(self.get_pos()+i+1j*j)
        return ret
        
class World:
    def __init__(self):
        pass
        self.obj = []
        self.step_time = 0.01
        self.default_setup()

    def default_setup(self):
        self.main_ac = [Actor(10.+6.5j)]
        self.obj.append( self.main_ac[0] )
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
            
        while True:
            cola = []
            for i in xrange(len(self.obj)):
                for j in xrange(i):
                    o1 = self.obj[i]
                    o2 = self.obj[j]
                    if not (o1.is_dynamic() or o2.is_dynamic()):
                        continue
                    if o1.is_dynamic():
                        o1, o2 = o2, o1
                    if o1.get_class() == 'st':
                        for cor in o1.get_corners():
                            cola.append((o1, o2)+
                                calcolission_r(cor,0.,0.,o2.p, o2.get_radius(), o2.v) )

            cola.sort(key=lambda x: x[2])
            if len(cola) == 0 or cola[0][2] >= self.step_time:
                break
            curc = cola[0]
            phys_col(curc[0],curc[1],curc[3])
            
                    
        
        for o in self.obj:
            if hasattr(o, 'advance'):
                o.advance(self.step_time)
