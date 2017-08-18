import errno
import socket
import threading
from collections import deque

from sys import exc_info

class StreamReader:
    def __init__(me,s):
        me.s=s
        me.queue = deque()
    def read(me):
        try:
            while True:
                r = me.s.recv(1024)
                if r=='':
                    break
                for c in r:
                    me.queue.append(c)
                msgs = []
                last = 0
                for i,c in enumerate(me.queue):
                    if c == '|':
                        msgs.append(i - last)
                        last = i+1
                for l in msgs:
                    yield ''.join(me.queue.popleft() for i in xrange(l))
                    me.queue.popleft()
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

class StreamRW:
    def __init__(me, s):
        me.s = s
        me.r = StreamReader(s)
        me.w = StreamWriter(s)
        me.ok = True
        me.errs = []
    def are_you_OK(me):
        return me.ok
    def close(me):
        me.s.close()
    def read(me):
        try:
            for msg in me.r.read():
                yield msg
        except Exception:
            me.ok = False
            me.errs.append(exc_info())
    def write(me,msg):
        try:
            me.w.write(msg)
        except Exception:
            me.ok = False
            me.errs.append(exc_info())
    def get_errs(me):
        return me.errs
    def get_ext_data(me):
        {}