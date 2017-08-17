# -*- coding: utf-8 -*-
"""
Created on Thu Aug 17 21:03:51 2017

@author: J
"""

import socket
from sys import exc_info
import errno
import time

from collections import deque

class Unord:
    def __init__(me):
        me.unread = {}
        me.cnt = 0
    def insert(me, num, *data):
        if num < me.cnt or num in me.unread:
            return
        me.unread[num] = data
    def read(me):
        while me.cnt in me.unread:
            yield me.unread[me.cnt]
            me.cnt+=1

class UDPStreamRed:
    ACK = 'ACK'
    HELLO = 'hello'
    SEP = '|'
    MSEP = '\n'
    
    ack_red_num = 1
    num_lim = 20
    ack_lim = 50
    def __init__(me, port, ip):
        me.addr = (ip,port)
        
        me.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        me.sock.bind(('',port))
        
        me.unack = {}
        me.cnt = 0
        
        me.connected = False
        me.ok = True
        me.errs = []
        
        me.unread = Unord()
        
        me.connect()
        
        me.sock.setblocking(0)
    def log(me, *data):
        me.ok = False
        me.errs.append((exc_info(),data))
    def send(me, txt):
#        print txt
        try:
            me.sock.sendto(txt,me.addr)
        except socket.error, v:
            if v[0] == errno.EWOULDBLOCK:
                pass
            else:
                me.log(v)
        except:
            me.log()
    def send_ack(me, nums):
        for i in xrange(0,len(nums),me.ack_lim):
            txt = me.SEP.join([me.ACK]+[str(num) for num in nums[i:i+me.ack_lim]])
            for i in xrange(me.ack_red_num):
                me.send(txt)
    def resend(me):
        nums = list(me.unack)
        for i in xrange(0,len(nums),me.num_lim):
            txt = me.MSEP.join(str(num)+me.SEP+me.unack[num][0] for num in nums[i:i+me.num_lim])
            me.send(txt)
    def ack(me, num):
        if num in me.unack:
            me.unack.pop(num)
    def get_msgs(me):
        try:
            while True:
                msg,addr = me.sock.recvfrom(1024)
                if addr!=me.addr:
                    continue
                if msg == '':
                    return
                if msg == me.HELLO:
                    me.connected = True
                    return
                msgs = msg.split(me.MSEP)
                nums_to_ack = []
                for msg in msgs:
                    msg = msg.split(me.SEP)
                    if msg[0] == me.ACK:
                        for num in msg[1:]:
                            me.ack(int(num))
                    else:
                        num = int(msg[0])
                        nums_to_ack.append(num)
                        me.unread.insert(num,msg[1])
                if len(nums_to_ack)>0:
                    me.send_ack(nums_to_ack)
        except socket.error, v:
            if v[0] == errno.EWOULDBLOCK:
                pass
            else:
                me.log(v)
        except:
            me.log()
            
    def connect(me):
        while not me.connected:
            me.send(me.HELLO)
            me.get_msgs()
        me.send(me.HELLO)
            
    def write(me, msg):
        me.unack[me.cnt] = msg, time.clock()
        me.cnt+=1
        
        me.resend()
    def read(me):
        me.get_msgs()
        for data in me.unread.read():
            yield data[0]
    def close(me):
        try:
            me.sock.close()
        except:
            me.log()
    def are_you_OK(me):
        return me.ok
    def get_errs(me):
        return me.errs
        
class UDPStreamGrp:
    SEP = '|'
    ACK = 'ACK'
    HELLO = 'hello'
    
    class MsgPack:
        lim = 20
        def __init__(me, num, msg):
            me.n = num
            me.txt = msg
            me.l = 1
            me.sts = [0]
        def full(me):
            return me.l==me.lim
        def insert(me, msg):
            me.l+=1
            me.sts.append(len(me.txt)+1)
            me.txt += UDPStreamGrp.SEP + msg
        def get_txt(me):
            return str(me.n)+UDPStreamGrp.SEP+me.txt
        def cut(me, N):
            if me.n+me.l-1 <= N:
                return True
            d = N-me.n+1
            me.l -= d
            print me.n, me.l, N, d
            print me.txt, me.sts
            me.txt = me.txt[me.sts[d]-me.sts[0]:]
            me.sts = me.sts[d:]
            me.n = N
            return False
            
            
    def __init__(me, port, ip):
        me.addr = (ip,port)
        
        me.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        me.sock.bind(('',port))
        
        me.unack = deque()
        me.snd_cnt = 0
        
        me.connected = False
        me.ok = True
        me.errs = []
        
        me.unread = deque()
        me.rec_cnt = 0
        
        me.connect()
        
        me.sock.setblocking(0)
        
    def log(me, *data):
        me.ok = False
        me.errs.append((exc_info(),data))

    def send(me, txt):
#        print txt
        try:
            me.sock.sendto(txt,me.addr)
        except socket.error, v:
            if v[0] == errno.EWOULDBLOCK:
                pass
            else:
                me.log(v)
        except:
            me.log()
    def send_ack(me, num):
        me.send(me.ACK + me.SEP + str(num))
    def resend(me):
        for mp in me.unack:
            me.send(mp.get_txt())
    
    def get_msgs(me):
        try:
            while True:
                msg,addr = me.sock.recvfrom(1024)
                if addr!=me.addr:
                    continue
                if msg == '':
                    return
                if msg == me.HELLO:
                    me.connected = True
                    return
                msg = msg.split(me.SEP)
                if msg[0] == me.ACK:
                    n = int(msg[1])
                    while len(me.unack)>0 and me.unack[0].cut(n):
                        me.unack.popleft()
                else:
                    n = int(msg[0])
                    l = len(msg)-1
                    if me.rec_cnt < n+l and me.rec_cnt >= n:
                        me.send_ack(n+l-1)
                        me.unread.extend(msg[1+me.rec_cnt-n:])
                        me.rec_cnt = n+l
        except socket.error, v:
            if v[0] == errno.EWOULDBLOCK:
                pass
            else:
                me.log(v)
        except:
            me.log()
    def connect(me):
        while not me.connected:
            me.send(me.HELLO)
            me.get_msgs()
        me.send(me.HELLO)
    
    
    def write(me, msg):
        if len(me.unack)==0 or me.unack[-1].full():
            me.unack.append(me.MsgPack(me.snd_cnt, msg))
        else:
            me.unack[-1].insert(msg)
        me.snd_cnt += 1
        
        me.resend()
    def read(me):
        me.get_msgs()
        
        while len(me.unread)>0:
            yield me.unread.popleft()
    def close(me):
        try:
            me.sock.close()
        except:
            me.log()
    def are_you_OK(me):
        return me.ok
    def get_errs(me):
        return me.errs
