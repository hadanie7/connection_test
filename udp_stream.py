# -*- coding: utf-8 -*-
"""
Created on Tue Aug 15 14:02:54 2017

@author: J
"""

import socket
import errno
import time
import threading
from sys import exc_info

class MsgOrder:
    def __init__(me, override = False):
        me.unordered = {}
        me.ord = set()
        me.ovrd = override
        me.cnt = 0
        me.lock = threading.Lock()
    def insert(me, ind, *data):
        #print 'la1'
        ret = False
        me.lock.acquire()
        if not ind in me.ord:
            if me.ovrd or ind not in me.unordered:
                ret = True
                me.unordered[ind] = data
        #print 'lr1'
        me.lock.release()
        return ret
    def flush(me):
        #print 'la2'
        me.lock.acquire()
        while len(me.unordered)>0 and min(me.unordered)==me.cnt:
            fy = me.unordered[me.cnt]
            me.unordered.pop(me.cnt)
            me.ord.add(me.cnt)
            me.cnt+=1
            #print 'lr3'
            me.lock.release()
            yield fy
            #print 'la3'
            me.lock.acquire()
        #print 'lr2'
        me.lock.release()
            
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
            else:
                me.addr = (ip,port)
                me.sock.sendto(me.HELLO, me.addr)
                #print 'a'
                #print me.addr
            me.sock.setblocking(0)
        except socket.error, v:
            if v[0] == errno.EWOULDBLOCK:
                pass
            else:
                me.ok = False
                me.errs.append((v,exc_info()))
#                raise
        except Exception:
            me.ok = False
            me.errs.append(exc_info())
#            raise
    def write(me, msg):
        me.unacknoledged[me.snd_cnt] = msg, time.clock(), 0
        msg = str(me.snd_cnt)+me.SPR+msg
        me.snd_cnt += 1
        try:
            me.sock.sendto(msg,me.addr)
        except socket.error, v:
            if v[0] == errno.EWOULDBLOCK:
                pass
            else:
                me.ok = False
                me.errs.append((v,exc_info()))
#                raise
        except Exception:
            me.ok = False
            me.errs.append(exc_info())
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
                    try:
                        me.sock.sendto(str(num)+me.SPR+msg,me.addr)
                    except socket.error, v:
                        if v[0] == errno.EWOULDBLOCK:
                            pass
                        else:
                            me.ok = False
                            me.errs.append((v,exc_info()))
            #                raise
                else:
                    me.ok = False
                    me.errs.append((time.clock(),tm,att,msg))
    def send_acknoledgement(me, num):
        try:
            msg = me.ACK+me.SPR+str(num)
            me.sock.sendto(msg,me.addr)
        except socket.error, v:
            if v[0] == errno.EWOULDBLOCK:
                pass
            else:
                me.ok = False
                me.errs.append((v,exc_info()))
#                raise
        except Exception:
            me.ok = False
            me.errs.append(exc_info())
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
                
                #print msg
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
                me.errs.append((v,exc_info()))
#                raise
        except Exception:
            me.ok = False
            me.errs.append(exc_info())
#            raise
    def close(me):
        me.sock.close()
    def are_you_OK(me):
        return me.ok
    def get_errs(me):
        return me.errs
        
        
class UDPStream_v2:
    HELLO = 'hello'
    ACK = 'ACK'
    SEP = '|'
    def __init__(me, port, ip):
        me.unread = MsgOrder(False)
        
        me.ack_lock = threading.Lock()
        me.unack = {}
        me.cnt = 0
        
        me.ok = True
        me.errs = []
        me.ok_lock = threading.Lock()
        
        me.connected = False
        
        me.snd_lock = threading.Lock()
        me.addr = (ip,port)
        me.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        try:
            me.sock.bind(('',port))
        except:
            me.log()

        me.connect()
        me.sock.setblocking(0)
    def are_you_OK(me):
        me.ok_lock.acquire()
        ret = me.ok
        me.ok_lock.release()
        return ret
    def get_errs(me):
        return me.errs
    def close(me):
        me.sock.close()  
        
    def read(me):
        me.check_msgs()
        return me.get_msgs()
    def write(me,msg):
        me.insert_msg(msg)
        me.check_msgs()
        me.send_msgs()
    def log(me,*data):
        me.ok_lock.acquire()
        me.ok = False
        me.ok_lock.release()
        me.errs.append((exc_info(), data))
        
    def get_msgs(me):
        for m in me.unread.flush():
            yield m[0]
    def insert_msg(me,msg):
        #print 'la4'
        me.ack_lock.acquire()
        me.unack[me.cnt] = msg, time.clock()
        me.cnt+=1
        #print 'lr4'
        me.ack_lock.release()
        
    def send(me,txt):
        me.snd_lock.acquire()
        me.sock.sendto(txt,me.addr)
        me.snd_lock.release()
    def check_msgs(me):
        try:
            while True:
                #print 'r'
                msg,addr = me.sock.recvfrom(1024)
                #print msg,addr,me.addr
                if addr != me.addr:
                    continue
                if msg == me.HELLO:
                    me.connected = True
                    #print me.connect, me.sock.gettimeout()
                    if me.sock.gettimeout() is None:
                        return
                    else:
                        continue
                msg = msg.split(me.SEP)
                if msg[0] == me.ACK:
                    #print 'la5'
                    me.ack_lock.acquire()
                    num = int(msg[1])
                    if num in me.unack:
                        me.unack.pop(num)
                    #print 'lr5'
                    me.ack_lock.release()
                else:
                    num = int(msg[0])
                    if me.unread.insert(num,msg[1]):
                        me.send_ack(num)
        except socket.timeout:
            pass
        except socket.error, v:
            if v[0] == errno.EWOULDBLOCK:
                pass
            else:
                me.log(v)
        except:
            me.log()
    def send_ack(me, num):
        txt = me.ACK+me.SEP+str(num)
        try:
            #print txt
            me.send(txt)
        except socket.error, v:
            if v[0] == errno.EWOULDBLOCK:
                pass
            else:
                me.log(v)
        except:
            me.log()
    def send_msgs(me):
        #print 'la6'
        me.ack_lock.acquire()
        for num in me.unack:
            msg,tm = me.unack[num]
            txt = str(num)+me.SEP+msg
            try:
                #print txt
                me.send(txt)
            except socket.error, v:
                if v[0] == errno.EWOULDBLOCK:
                    pass
                else:
                    me.log(v)
            except:
                me.log()
        #print 'lr6'
        me.ack_lock.release()
    def connect(me):
        while not me.connected:
            try:
                #print me.HELLO
                me.send(me.HELLO)
            except socket.error, v:
                if v[0] == errno.EWOULDBLOCK:
                    pass
                else:
                    me.log(v)
            except:
                me.log()
            me.check_msgs()
        try:
            #print me.HELLO
            me.send(me.HELLO)
        except socket.error, v:
            if v[0] == errno.EWOULDBLOCK:
                pass
            else:
                me.log(v)
        except:
            me.log()
            

class UDPStream_v2_Thread(UDPStream_v2):
    def __init__(me, port, ip):
        UDPStream_v2.__init__(me,port,ip)
        me.sock.settimeout(0.1)
        
        me.open = True
        
        me.write_cond = threading.Condition()
        
        me.check_thread = threading.Thread(target = me.check_thrd_f)
        me.send_thread = threading.Thread(target = me.send_thrd_f)
        
        me.check_thread.start()
        me.send_thread.start()
    
    def close(me):
        me.ok_lock.acquire()
        me.open = False
        me.ok_lock.release()
        
        UDPStream_v2.close(me)
    def read(me):
        return me.get_msgs()
    def write(me,msg):
        me.insert_msg(msg)
        
        me.write_cond.acquire()
        me.write_cond.notify()
        me.write_cond.release()
    
    def is_open(me):
        me.ok_lock.acquire()
        ret = me.open
        me.ok_lock.release()
        return ret
        
    def check_thrd_f(me):
        while me.is_open() and me.are_you_OK():
            me.check_msgs()
    def send_thrd_f(me):
        while me.is_open() and me.are_you_OK():
            me.write_cond.acquire()
            me.write_cond.wait(0.05)
            me.send_msgs()
    