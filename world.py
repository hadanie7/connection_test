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
    if p.real >= 0 or abs(p.imag) >= r :
        return INF, None
    
    hy = p.imag
    hx = - math.sqrt(r*r-hy*hy)
    tth = max(0., (-p.real + hx)/v) # time to hit
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
    if v.imag <= 0:
        return INF, None
    col_vec = -1j
    col_vec /= rot
    if p.imag >= 0:
        if True and p.real > 0 and p.real < sx and p.imag-r2 < 0:
            return 0., col_vec
        else:
            return INF, None
    cx = p.real - p.imag * v.real / v.imag
    if cx >= sx or cx <= 0:
        return INF, None
    
    tth = -p.imag/v.imag
    assert tth >= 0
    if DEBUG and abs(tth)<0.01: pprint.pprint(locals())
    return tth, col_vec

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
    def __init__(self, init_pos, color = 'black', controller = None):
        GO.__init__(self, init_pos)
        assert color in ['black', 'white']
        self.color = color
        self.controller = controller
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
    
    def pre_advance(self, dt, fric):
        ds = dt*fric*abs(self.v)**0.8
        s = abs(self.v)
        if s <= ds:
            self.v = 0j
        else:
            self.v *= (s-ds)/s
    
    def advance(self, dt):
        self.p += dt*self.v
    
    def get_mass(self):
        return 1.0

class Stone(GO):
    def __init__(self, init_pos, tp = 'wall'):
        GO.__init__(self, init_pos)
        self.tp = tp
    def get_type(self):
        """ 'box', 'wall' """
        return self.tp
    
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

class Event():
    def __init__(self, tp, loc):
        self.tp = tp
        self.loc = loc

class World:
    def __init__(self, filename = None):
        pass
        self.obj = []
        self.acs = []
        self.stone_dict = {}
        self.step_time = 0.01
        self.push_speed = 5.
        if filename == None:
            self.default_setup()
        else:
            self.load_from_file(filename)
        self.friction = 3.
        self.last_events = []
        self.cur_time = 0.
        
    def load_from_file(self, filename):
        cls = {
                '#':Stone,
                'B':Stone,
                '1':Actor,
                '2':Actor,
                }
        tps = {
                '#':'wall',
                'B':'box',
                '1':'black',
                '2':'white',
                }
                
        delta = {Stone:0+0j,
                 Actor:0.5+0.5j}
        
        black = None
        white = None
        with open(filename) as f:
            fx,fy = f.readline().split()
            fx = int(fx)
            fy = int(fy)
                        
            for i,line in enumerate(f):
                for j,char in enumerate(line):
                    if char in ' \n':
                        continue
                    cl = cls[char]
                    tp = tps[char]
                    d = delta[cl]
                    y = fy + i
                    x = fx + j
                    obj = cl(x+1j*y + d, tp)
                    self.add_obj(obj)
                    
                    if black == None and tp == 'black':
                        black = obj
                    if white == None and tp == 'white':
                        white = obj
        self.main_ac = [black,white]
        if black:
            black.controller = 0
        if white:
            white.controller = 1
                    

    def default_setup(self):
        self.main_ac = [Actor(10.+6.5j)]
        self.add_obj( self.main_ac[0] )
        self.add_obj( Actor(5.+6.5j, color = 'white') )
        for i in range(1):
            self.add_obj( Stone(i+0j))
    
    def add_obj(self, obj):
        self.obj.append(obj)
        if obj.get_class() == 'ac':
            self.acs.append(obj)
        if obj.get_class() == 'st':
            self.stone_dict[obj.p] = obj
    
    def move_box(self, b, new_pos):
        del self.stone_dict[b.p]
        b.p = new_pos
        self.stone_dict[b.p] = b
        
#interface
    
    def get_view_position(self, controller):
        """return the position of the object that the display should follow
        complex"""
        return self.main_ac[controller].get_pos()
    
    def get_objs(self):
        """return list of objects"""
        for i in self.obj:
            yield i

    def get_copy(self):
        return copy.deepcopy(self)
    
    def get_controller_count(self):
        return 1+max(-1, max(a.controller for a in self.acs))
    
    def get_last_events(self):
        return self.last_events
#end interface    
    
    def step(self, acc):
        self.last_events = []
        
        for a in self.acs:
            if isinstance(a.controller, int):
                a.accelerate(self.step_time, acc[a.controller])

        for o in self.obj:
            if hasattr(o, 'pre_advance'):
                o.pre_advance(self.step_time, self.friction)

        def adv_all(dt):
            for o in self.obj:
                if hasattr(o, 'advance'):
                    o.advance(dt)
            self.cur_time += dt

        dtr = self.step_time
        cola = []
        def cons_sa(o1, o2):
            for cor in o1.get_corners():
                cola.append((o1, o2)+
                    calcolission_r(cor,0.,0.,o2.p, o2.get_radius(), o2.v) )
            for sd in o1.get_sides():
                cola.append((o1, o2)+
                    calcolission_seg(sd[0], sd[1],o2.p, o2.get_radius(), o2.v) )

        def cons_aa(o1, o2):
            cola.append((o1, o2)+
                calcolission_r(o1.p, o1.get_radius(), o1.v,
                                 o2.p, o2.get_radius(), o2.v) )

        while True:
            cola = []
            for i in xrange(len(self.acs)):
                for j in xrange(i):
                    o1 = self.acs[i]
                    o2 = self.acs[j]
                    cons_aa(o1, o2)
            
            for a in self.acs:
                p2 = a.p+dtr*a.v
                d = tuple((p.real, p.imag) for p in (a.p, p2))
                bnd = tuple( tuple( int(ad + a.get_radius()*ml + op(d[i][j] for i in (0,1)) ) \
                    for j in (0,1) ) for op, ml, ad in zip((min, max), (-1,1), (-0.001, 1.001)) )
                for i in range(bnd[0][0], bnd[1][0]):
                    for j in range(bnd[0][1], bnd[1][1]):
                        c = complex(i,j)
                        if c in self.stone_dict:
                            cons_sa(self.stone_dict[c], a)

            cola.sort(key=lambda x: x[2])
            if len(cola) == 0 or cola[0][2] >= dtr:
                break
            curc = cola[0]
            dt = curc[2]
            adv_all(dt)
            dtr -= dt
            self.phys_col(curc[0],curc[1],curc[3])
        ## end collision loop
        adv_all(dtr)
    
    def phys_col(self, o1, o2, col_vec):
        if DEBUG: print 'boom!'
        if not o2.is_dynamic():
            o1, o2 = o2, o1
        if not o1.is_dynamic():
            assert o2.is_dynamic()
            o2.v /= col_vec
            v_x = o2.v.real
            o2.v = -o2.v.conjugate()
            o2.v *= col_vec
            locx = min(o1.p.real+1, max(o2.p.real, o1.p.real))
            locy = min(o1.p.imag+1, max(o2.p.imag, o1.p.imag))
            self.last_events.append(Event('wall collision', complex(locx, locy)))
            if abs(v_x) >= self.push_speed and col_vec in [1j**i for i in range(4)]:
                self.stone_impact(o1, -col_vec)
        else:
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
            loc = (o1.p*o2.get_radius() + o2.p*o1.get_radius()) / (o1.get_radius()+o2.get_radius())
            self.last_events.append(Event('ball collision', loc))
    
    def stone_impact(self, o, dear):
        assert isinstance(o, Stone)
        if not o.get_type() == 'box':
            return
        for o2 in self.obj:
            if o2.get_class() == 'st' and o2.get_pos() == o.get_pos()+dear:
                return
        self.move_box(o, o.p + dear)
        self.last_events.append(Event('box move', o.get_pos()))
        

