# -*- coding: utf-8 -*-
"""
Created on Sun Aug 13 15:15:19 2017

@author: J&D
"""

import pygame
from collections import deque

import dummy

from world import World

pygame.init()

scale = 64
w,h = 19,12

ms_spd = 1.0

bg_col = (0,192,0)

fps_lim = 100

st_cols = {'box':(192,128,0),
          'wall':(195,195,195)}
          
bord_color = (0,0,0)
          
ac_cols = {'black':(0,0,0),
          'white':(255,255,255)}

def tup2comp(v):
    x,y = v
    return x + y*1j
def comp2tup(v):
    return (v.real, v.imag)
def rnd_tup(v):
    return tuple(int(x) for x in v)
def mod(v1,mx,my):
    x,y = comp2tup(v1)
    x %= mx
    y %= my
    return tup2comp((x,y))

class WorldDrawer:
    def get_offset(me,world):
        p = world.get_view_position()
        x = 0.5+0.5j
        return p - mod(p-x,w,h)-x
    def wrld2scrn(me,world, v, pos = True):
        if pos:
            v -= me.get_offset(world)
        v *= scale
        return rnd_tup(comp2tup(v))
    def scrn2wrld(me,world, v, pos = True):
        v = tup2comp(v)
        v /= scale
        if pos:
            v += me.get_offset(world)
        return v
    def draw(me, scr, world):
        scr.fill(bg_col)
        
                
        for obj in world.get_objs():
            pos = me.wrld2scrn(world,obj.get_pos())
            cls = obj.get_class()
            if cls == 'st':
                color = st_cols[obj.get_type()]
                pygame.draw.rect(scr, color, pos + (scale,)*2)
                pygame.draw.rect(scr, bord_color, pos + (scale,)*2, 1)
            elif cls == 'ac':
                color = ac_cols[obj.get_color()]
                rad = int(scale*obj.get_radius())
                pygame.draw.circle(scr,color,pos,rad)

def world_steps(world, queues, my_cont):
    while all([len(q)>0 for q in queues]):
        world.step([q.popleft() for q in queues])
    prediction = world.get_copy()
    for i in xrange(len(queues[my_cont])):
        prediction.step([q[i] if len(q)>i else 0+0j for q in queues])
    return prediction

def main():
    scr = pygame.display.set_mode((scale*(w+1),scale*(h+1)), pygame.FULLSCREEN)
    
    clock = pygame.time.Clock()
    
    #should be changed later    
    #world = dummy.DummyWorld()
    world = World()
    drawer = WorldDrawer()
    
    pygame.mouse.set_visible(False)
    
    queues = [deque() for i in xrange(world.get_controller_count())]
    
    my_cont = 0
    
    while True:
        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                pygame.quit()
                return
            if e.type == pygame.KEYDOWN:
                if e.key == pygame.K_ESCAPE:
                    pygame.quit()
                    return
        queues[my_cont].append(tup2comp(pygame.mouse.get_rel()) * ms_spd)
                
        pred = world_steps(world,queues,my_cont)
        drawer.draw(scr,pred)
        
        pygame.display.flip()
        
        clock.tick(fps_lim)
        
if __name__ == "__main__":
    try:
        main()
    except:
        pygame.quit()
        raise