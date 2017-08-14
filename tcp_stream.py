import errno
import socket
import threading

class StreamReader:
    size = 2048
    def __init__(me,s):
        me.s=s
        me.arr = [None for _ in xrange(me.size)]
        me.start = 0
        me.end = 0
    def read(me):
        try:
            while True:
                for c in me.s.recv(1024):
                    me.arr[me.end] = c
                    me.end+=1
                    me.end %= me.size
                i = 0
                while (me.start+i)%me.size != me.end:
                    if me.arr[(me.start+i)%me.size] == '|':
                        yield ''.join(me.arr[(me.start+j)%me.size] for j in xrange(i))
                        me.start += i+1
                        me.start %= me.size
                        i = -1
                    i+=1
        except socket.error,v:
            if v[0] == errno.EWOULDBLOCK:
                pass
            else:
                raise
class StreamWriter:
    def __init__(me,s):
        me.lock = threading.Lock()
        me.s = s
    def write(me,msg):
        me.lock.acquire()
        try:
            me.s.sendall(msg+'|')
        except socket.error,v:
            if v[0] == errno.EWOULDBLOCK:
                pass
            else:
                raise
        me.lock.release()
