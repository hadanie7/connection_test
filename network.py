# -*- coding: utf-8 -*-
"""
Created on Sun Aug 13 22:26:59 2017

@author: J
"""

import socket
import struct

import tcp_stream
import udp_stream
import udp_stream_v2
import enet_conn

PORT = 5552

def yes_or_no(s):
    return s.lower == 'y'

def print_my_ips():
    print 'your IP addresses are:'
    for ip in socket.gethostbyname_ex(socket.gethostname())[2]:
        print ip

def get_tcp_socket(serv_ip, serv_port = PORT):
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
    
def setup_conn():
    '''
    returns connection object
    interface:
        read():
            iterator over all new messages
        write(msg):
            send msg to other side
        close():
            close connection
        are_you_OK():
            returns True if no errors occured
        get_errs():
            returns list of error data for all errors
    '''
    params = []
    with open('local\\conn_type.txt') as f:
        for line in f:
            if line[-1] == '\n':
                line = line[:-1]
            params.append(line)
        
        # "TCP stream"
        #   <'serv'/'clnt'>
        #
        #or
        #
        # "UDP stream"
        #  <'serv'/'clnt'>
        #
        #or
        #
        # "UDP stream 2"
        #
        #or
        #
        # "UDP stream 2thrd"
        #
        #or
        #
        # "UDP stream red"
    with open('local\\conn_ip.txt') as f:
        ip = f.read() 
        
    if params[0] == 'TCP stream':
        if params[1] == 'serv':
            ip = None
        s = get_tcp_socket(ip)
        return tcp_stream.StreamRW(s)
    if params[0] == 'UDP stream':
        if params[1] == 'serv':
            ip = None
        return udp_stream.UDPStream(PORT,ip)
    if params[0] == 'UDP stream 2':
        return udp_stream.UDPStream_v2(PORT,ip)
    if params[0] == 'UDP stream 2thrd':
        return udp_stream.UDPStream_v2_Thread(PORT,ip)
    if params[0] == 'UDP stream red':
        return udp_stream_v2.UDPStreamRed(PORT,ip)
    if params[0] == 'UDP stream grp':
        return udp_stream_v2.UDPStreamGrp(PORT,ip)
    if params[0] == 'Enet':
        if params[1] == 'serv':
            return enet_conn.EnetConn(PORT)
        return enet_conn.EnetConn(PORT,ip,False)