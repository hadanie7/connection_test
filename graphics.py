# -*- coding: utf-8 -*-
"""
Created on Sun Aug 13 15:15:19 2017

@author: J&D
"""

import pygame

import dummy

from world import World

pygame.init()

scale = 32
w,h = 19,12

ms_spd = 0.01

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
    def __init__(me, world):
        me.world = world
    def get_offset(me):
        p = me.world.get_view_position()
        x = 0.5+0.5j
        return p - mod(p-x,w,h)-x
    def wrld2scrn(me, v, pos = True):
        if pos:
            v -= me.get_offset()
        v *= scale
        return rnd_tup(comp2tup(v))
    def scrn2wrld(me, v, pos = True):
        v = tup2comp(v)
        v /= scale
        if pos:
            v += me.get_offset()
        return v
    def draw(me, scr):
        scr.fill(bg_col)
        
                
        for obj in me.world.get_objs():
            pos = me.wrld2scrn(obj.get_pos())
            cls = obj.get_class()
            if cls == 'st':
                color = st_cols[obj.get_type()]
                pygame.draw.rect(scr, color, pos + (scale,)*2)
                pygame.draw.rect(scr, bord_color, pos + (scale,)*2, 1)
            elif cls == 'ac':
                color = ac_cols[obj.get_color()]
                rad = int(scale*obj.get_radius())
                pygame.draw.circle(scr,color,pos,rad)


def main():
    scr = pygame.display.set_mode((scale*(w+1),scale*(h+1)))
    
    clock = pygame.time.Clock()
    
    #should be changed later    
    #world = dummy.DummyWorld()
    world = World()
    drawer = WorldDrawer(world)
    
    
    while True:
        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                pygame.quit()
                return
                
        world.step([0.0+0.0j])
        drawer.draw(scr)
        
        pygame.display.flip()
        
        clock.tick(fps_lim)
        
if __name__ == "__main__":
    main()