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

def calcolission_seg(p11, p12, p2, r2, v2):
    sx = p12-p11
    p = p2-p11
    rot = (sx/abs(sx)).conjugate()
    sx = abs(sx) # equiv to (sy *= rot) up to numerical error and type
    p *= rot
    v = v2 * rot
    p += r2*1j
    if v.imag <= 0 or p.imag >= 0:
        return INF, None
    cx = p.real - p.imag * v.real / v.imag
    if cx >= sx or cx <= 0:
        return INF, None
    col_vec = -1j
    tth = -p.imag/v.imag
    col_vec /= rot
    if DEBUG and abs(tth)<0.01: pprint.pprint(locals())
    return tth, col_vec

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
    #dynamic collision:
    o2.v /= col_vec
    o1.v /= col_vec
    vr1 = o1.v.real
    vr2 = o2.v.real
    # not solving this:
    ## vr1*m1 + vr2*m2 = ur1*m1 + ur2*m2 
    ## vr1^2*m1 + vr2^2*m2 = ur1^2*m1 + ur2^2*m2
    ## we assume the masses are equal
    assert o1.get_mass() == o2.get_mass()
    o2.v = vr1+1j*o2.v.imag
    o1.v = vr2+1j*o1.v.imag
    o2.v *= col_vec
    o1.v *= col_vec

class GO:
    def __init__(self, init_pos):
        assert isinstance(init_pos, complex)
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
    def __init__(self, init_pos, color = 'black'):
        GO.__init__(self, init_pos)
        assert color in ['black', 'white']
        self.color = color
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
    
    def get_mass(self):
        return 1.0

class Stone(GO):
    def get_type(self):
        """ 'box', 'wall' """
        return 'wall'
    
    def get_corners(self):
        ret = []
        hrot = 0.5+0.5j
        for i in range(4):
            ret.append(self.get_pos()+ hrot*(1+1j**i) )
        return ret
    
    def get_sides(self):
        cn = self.get_corners()
        ret = []
        for i in range(4):
            ret.append( (cn[i-1], cn[i]) )
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
        self.obj.append( Actor(5.+6.5j, color = 'white') )
        for i in range(1):
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
                        for sd in o1.get_sides():
                            cola.append((o1, o2)+
                                calcolission_seg(sd[0], sd[1],o2.p, o2.get_radius(), o2.v) )
                    elif o1.get_class() == 'ac':
                        cola.append((o1, o2)+
                                calcolission_r(o1.p, o1.get_radius(), o1.v,
                                                 o2.p, o2.get_radius(), o2.v) )

            cola.sort(key=lambda x: x[2])
            if len(cola) == 0 or cola[0][2] >= self.step_time:
                break
            curc = cola[0]
            phys_col(curc[0],curc[1],curc[3])
            
                    
        
        for o in self.obj:
            if hasattr(o, 'advance'):
                o.advance(self.step_time)
