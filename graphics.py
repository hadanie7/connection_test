# -*- coding: utf-8 -*-
"""
Created on Sun Aug 13 15:15:19 2017

@author: J&D
"""

import pygame
from collections import deque
import os.path
from math import floor

import dummy

from world import World, Event

pygame.mixer.pre_init(buffer=512)
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
          
coll_t = 10
coll_s = 0.2
coll_col = (255,128,0)

sounds = {}
def get_sound_path(name):
    return os.path.join('sounds',name)
def get_sound(name,filename):
    sounds[name] = pygame.mixer.Sound(get_sound_path(filename))
def play_sound(name):
    sounds[name].play()
get_sound('b_coll', 'ballcollision.wav')

def tup2comp(v):
    x,y = v
    return x + y*1j
def comp2tup(v):
    return (v.real, v.imag)
def rnd_tup(v):
    return tuple(int(floor(x)) for x in v)
def rnd_comp(v):
    return tup2comp(rnd_tup(comp2tup(v)))
def mod(v1,mx,my):
    x,y = comp2tup(v1)
    x %= mx
    y %= my
    return tup2comp((x,y))

class WorldDrawer:
    def __init__(me):
        me.positions = []
        me.off = None
        me.pcoll = []
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
    def neighbor_tiles(me, v):
        ds = [i+1j*j for i in xrange(-1,2) for j in xrange(-1,2)]
        return {v+d for d in ds}
    def tiles(me, obj, ppos = None):
        tile = rnd_comp(obj.get_pos())
        if ppos!=None:
            ptile = rnd_comp(ppos)
        if obj.get_class() == 'ac':
            ret = me.neighbor_tiles(tile)
            if ppos!=None:
                ret |= me.neighbor_tiles(ptile)
        else:
            ret = {tile}
            if ppos!=None:
                ret.add(ptile)
        return ret
    def draw(me, scr, world, collisions):
        view_moved = me.off != me.get_offset(world)
        moved = [view_moved for obj in world.get_objs()]
        
        
        tiles_to_draw = set()
        
        for i,(obj,p) in enumerate(zip(world.get_objs(),me.positions)):
            if p!=obj.get_pos():
                moved[i] = True
                
        
        for i,(obj,mv) in enumerate(zip(world.get_objs(), moved)):
            if mv:
                p = me.positions[i] if i<len(me.positions) else None
                ext = me.tiles(obj,p)
                tiles_to_draw |= ext
        for coll in collisions:
            ext = rnd_comp(coll.loc)
            ext = me.neighbor_tiles(ext)
            tiles_to_draw |= ext
        for loc in me.pcoll:
            ext = rnd_comp(loc)
            ext = me.neighbor_tiles(ext)
            tiles_to_draw |= ext
        
        if view_moved:
            scr.fill(bg_col)
        else:
            for t in tiles_to_draw:
                pos = me.wrld2scrn(world,t)
                rect = pos + (scale,)*2
                pygame.draw.rect(scr,bg_col,rect)
        
                
        for obj in world.get_objs():
            rpos = obj.get_pos()
            if not any([t in tiles_to_draw for t in me.tiles(obj)]):
                continue
            pos = me.wrld2scrn(world,rpos)
            cls = obj.get_class()
            if cls == 'st':
                color = st_cols[obj.get_type()]
                pygame.draw.rect(scr, color, pos + (scale,)*2)
                pygame.draw.rect(scr, bord_color, pos + (scale,)*2, 1)
            elif cls == 'ac':
                color = ac_cols[obj.get_color()]
                rad = int(scale*obj.get_radius())
                pygame.draw.circle(scr,color,pos,rad)
                
        for coll in collisions:
            rad = coll_s * (coll_t+1 - collisions[coll])/float(coll_t)
            rad *= scale
            rad = int(rad)
            pos = me.wrld2scrn(world,coll.loc)
            pygame.draw.circle(scr,coll_col,pos,rad,1)
            
        me.pcoll = [coll.loc for coll in collisions]
        me.off = me.get_offset(world)
        me.positions = [obj.get_pos() for obj in world.get_objs()]

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
    world = World('levels\\test_level.txt')
    drawer = WorldDrawer()
    
    pygame.mouse.set_visible(False)
    
    queues = [deque() for i in xrange(world.get_controller_count())]
    
    my_cont = 0
    
    collisions = {}
    
    while True:
        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                pygame.quit()
                return
            if e.type == pygame.KEYDOWN:
                if e.key == pygame.K_ESCAPE:
                    pygame.quit()
                    return
                if e.key == pygame.K_t:
                    scr.fill((128,128,128))
        queues[my_cont].append(tup2comp(pygame.mouse.get_rel()) * ms_spd)
        for i,q in enumerate(queues):
            if i!=my_cont:
                q.append(0+0j)
                
        pred = world_steps(world,queues,my_cont)
        fr = set()
        for coll in collisions:
            collisions[coll] -= 1
            if collisions[coll] == 0:
                fr.add(coll)
        for coll in fr:
            collisions.pop(coll)
                
        for e in pred.get_last_events():
            if e.tp == 'ball collision':
                play_sound('b_coll')
            if e.tp == 'wall collision':
                collisions[e] = coll_t
        drawer.draw(scr,pred, collisions)
        
        pygame.display.flip()
        
        clock.tick(fps_lim)
        
if __name__ == "__main__":
    try:
        main()
    except:
        pygame.quit()
        raise