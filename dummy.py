# -*- coding: utf-8 -*-
"""
Created on Sun Aug 13 15:26:21 2017

@author: J
"""

class DummyBall:
    def __init__(me, pos, col):
        me.pos = pos
        me.col = col
    def get_radius(me):
        return 0.4
    def get_pos(me):
        return me.pos
    def get_color(me):
        return me.col
    def get_class(me):
        return 'ac'
    def move(me, x):
        me.pos += x
        
class DummyWall:
    def __init__(me, pos, tp):
        me.pos = pos
        me.tp = tp
    def get_pos(me):
        return me.pos
    def get_type(me):
        return me.tp
    def get_class(me):
        return 'st'
        
        

class DummyWorld:
    def __init__(me):
        me.objs = [DummyBall(15+2j,'black'),
                   DummyBall(2+3j,'white'),
                   DummyWall(3+2j,'box'),
                   DummyWall(3+3j,'box'),
                   DummyWall(3+4j,'wall'),
                   DummyWall(2+4j,'wall'),
                   DummyWall(20+4j,'wall'),
                   DummyWall(23+4j,'wall'),
                   ]

    def get_view_position(me):
        return me.objs[0].get_pos()
    def step(me, x):
        me.objs[0].move(x)
    def get_objs(me):
        return me.objs