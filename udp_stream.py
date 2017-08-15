# -*- coding: utf-8 -*-
"""
Created on Tue Aug 15 14:02:54 2017

@author: J
"""

import socket
import errno
import time

#unthreaded

class UDPStream:
    ACK = 'ACK'
    HELLO = 'hello'
    SPR = '|'
    timeout = 1.0
    max_attempts = 3
    def __init__(me, port, ip = None):
        me.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        me.ok = True
        me.snd_cnt = 0
        me.rcv_cnt = 0
        me.unacknoledged = {} #msg_num : msg, time_sent, attempt_num
        me.unordered = {} # msg_num : msg
        me.errs = []
        try:
            if ip == None:
                me.sock.bind(('',port))
                msg = ''
                while msg != me.HELLO:
                    msg,addr = me.sock.recvfrom(1024)
                me.addr = addr
                me.sock.sendto(me.HELLO,me.addr)
            else:
                me.addr = (ip,port)
                me.sock.sendto(me.HELLO, me.addr)
                addr,msg = None,None
                while addr != me.addr or msg != me.HELLO:
                    msg,addr = me.sock.recvfrom(1024)
            me.sock.setblocking(0)
        except Exception as e:
            me.ok = False
            me.err.append(e)
#            raise
    def write(me, msg):
        me.unacknoledged[me.snd_cnt] = msg, time.clock(), 0
        msg = str(me.snd_cnt)+me.SPR+msg
        me.snd_cnt += 1
        try:
            me.sock.sendto(msg,me.addr)
        except Exception as e:
            me.ok = False
            me.err.append(e)
#            raise
            
        me.check_acknoledged()
    def get_min_unordered_num(me):
        return min(me.unordered)
    def get_min_unordered_msg(me):
        return me.unordered[min(me.unordered)]
    def remove_min_unordered(me):
        me.unordered.pop(min(me.unordered))
    def has_unordered(me):
        return len(me.unordered)>0
    def check_acknoledged(me):
        for num in me.unacknoledged:
            msg,tm,att = me.unacknoledged[num]
            if time.clock()-tm > me.timeout:
                if att+1<me.max_attempts:
                    me.unacknoledged[num] = msg,time.clock(),att+1
                    me.sock.sendto(str(num)+me.SPR+msg,me.addr)
                else:
                    me.ok = False
#                    raise
    def send_acknoledgement(me, num):
        try:
            msg = me.ACK+me.SPR+str(num)
            me.sock.sendto(msg,me.addr)
        except Exception as e:
            me.ok = False
            me.err.append(e)
#            raise
    def acknoledged(me, num):
        if num in me.unacknoledged:
            me.unacknoledged.pop(num)
    def read(me):
        try:
            while True:
                msg,addr = me.sock.recvfrom(1024)
                if addr!=me.addr:
                    continue
                
                print msg
                num,msg = msg.split(me.SPR)
                
                if num == me.ACK:
                    num = int(msg)
                    me.acknoledged(num)
                    continue
                
                num = int(num)
                me.send_acknoledgement(num)
                if num not in me.unordered:
                    me.unordered[num] = msg
                while me.has_unordered() and me.get_min_unordered_num() == me.rcv_cnt:
                    me.rcv_cnt += 1
                    yield me.get_min_unordered_msg()
                    me.remove_min_unordered()
        except socket.error, v:
            if v[0] == errno.EWOULDBLOCK:
                pass
            else:
                me.ok = False
                me.err.append(v)
        except Exception as e:
            me.ok = False
            me.err.append(e)
#                raise
    def close(me):
        me.sock.close()
    def are_you_OK(me):
        return me.ok
    def get_errs(me):
        return me.errs