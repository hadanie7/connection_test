# -*- coding: utf-8 -*-
"""
Created on Sat Aug 19 14:27:39 2017

@author: J
"""

import enet
from collections import deque
from sys import exc_info

class EnetConn:
    def __init__(me, port, ip = None, serv = True):
        me.ok = True
        me.errs = []
        me.connected = False
        
        addr = enet.Address("", port) if serv else None
        print addr
        try:
            me.host = enet.Host(addr,1,0,0)
        except:
            me.log(exc_info, "Unable to create host", addr)
        
        me.peer = None
        
        if serv:
            me.wait_for_connection()
        else:
            me.connect(enet.Address(ip,port))
        
        
        me.unread = deque()
        me.unread_unrel = deque()
        
    def log(me, *data):
        me.ok = False
        me.errs.append(data)
        
    def send(me, msg, rel = True):
        if me.connected == False:
            return
        pack = enet.Packet(msg,enet.PACKET_FLAG_RELIABLE if rel else 0)
        me.peer.send(0,pack)
    def handle_event(me, event):
        if event.type == enet.EVENT_TYPE_NONE:
            return False
        
        if event.type == enet.EVENT_TYPE_CONNECT:
            me.connected = True
            me.peer = event.peer
        elif event.type == enet.EVENT_TYPE_RECEIVE:
            if event.peer == me.peer:
                data = event.packet.data
                if event.packet.flags & enet.PACKET_FLAG_RELIABLE:
                    me.unread.append(data)
                else:
                    me.unread_unrel.append(data)                    
        elif event.type == enet.EVENT_TYPE_DISCONNECT:
            if event.peer == me.peer:
                me.connected = False
        return True
        
    def all_events(me, timeout = 0):
        while me.handle_event(me.host.service(timeout)):
            pass
    def connect(me, addr):
        me.peer = me.host.connect(addr, 1)
        event = me.host.service(5000)
        if event.type == enet.EVENT_TYPE_CONNECT:
            me.connected = True
        else:
            me.log("connection failed", addr)
    def wait_for_connection(me):
        while not me.connected and me.ok:
            me.handle_event(me.host.service(1000))
        
    def close(me):
        if me.peer is not None:
            me.peer.disconnect_later()
            me.all_events(3000)
            if me.connected and me.ok:
                me.peer.reset()
    def read(me):
        me.all_events()
        while len(me.unread)>0:
            yield me.unread.popleft()
    def read_unrel(me):
        me.all_events()
        while len(me.unread_unrel)>0:
            yield me.unread_unrel.popleft()
    def write(me,msg):
        me.send(msg)
    def write_unrel(me,msg):
        me.send(msg, False)
    def are_you_OK(me):
        return me.ok
    def get_errs(me):
        return me.errs