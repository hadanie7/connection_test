# -*- coding: utf-8 -*-
"""
Created on Fri Aug 18 00:39:13 2017

@author: D
"""

from collections import deque

exchange_freq = 1*100
past_interval = 2*100
time_modulus = 1.0/64
max_delays = deque()
my_maxs = deque()
his_maxs = deque()
cur_dif = 0
# send
# normal_step

def add_delay(i, d):
    while len(max_delays) > 0 and d > max_delays[-1][1]:
        max_delays.pop()
    max_delays.append((i,d))

def get_max():
    if len(max_delays) == 0:
        return 0
    while  max_delays[-1][0] - past_interval >= max_delays[0][0]:
        max_delays.popleft()
    return max_delays[0][1]

def try_cal():
    while len(my_maxs) > 0 and len(his_maxs) > 0:
        mm = my_maxs.popleft()
        hm = his_maxs.popleft()
        global cur_dif
        cur_dif = mm-hm


def recv(i, m):
    his_maxs.append(m)
    try_cal()

def report_delay(i, d):
    add_delay(i,d)
    if i % exchange_freq == 0:
        m = get_max()
        send(i, get_max())
        my_maxs.append(m)
        try_cal()

def get_step():
    """returns step size"""
    global cur_dif
    sgn = 0 if cur_dif == 0 else (-1 if cur_dif < 0 else 1)
    cur_dif -= time_modulus*sgn*2
    return normal_step*(1+time_modulus*sgn)