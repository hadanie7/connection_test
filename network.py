# -*- coding: utf-8 -*-
"""
Created on Sun Aug 13 22:26:59 2017

@author: J
"""

import socket
import struct

def print_my_ips():
    print 'your IP addresses are:'
    for ip in socket.gethostbyname_ex(socket.gethostname())[2]:
        print ip

def get_socket(serv_ip, serv_port = 5555):
    if serv_ip == None:
        print_my_ips()
        serv = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        serv.bind(('',serv_port))
        serv.listen(1)
        sock,addr = serv.accept()
        serv.close()
    else:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.connect((serv_ip,serv_port))
    sock.setblocking(0)
    return sock
        
def pack(f):
    return str(struct.unpack('!q',struct.pack('!d',f))[0])
def unpack(s):
    return struct.unpack('!d',struct.pack('!q', int(s)))[0]
    
def pack_movement(cont, vec):
    strs = str(cont),pack(vec.real),pack(vec.imag)
    return ','.join(strs)
def unpack_movement(s):
    c,x,y = s.split(',')
    return int(c),unpack(x)+1j*unpack(y)