# -*- coding: utf-8 -*-
"""
Created on Sun Aug 13 22:26:59 2017

@author: J
"""

import socket

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
        return sock
    else:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.connect((serv_ip,serv_port))
        sock.setblocking(0)
        return sock