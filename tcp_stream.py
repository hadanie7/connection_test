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
                r = me.s.recv(1024)
                if r=='':
                    break
                for c in r:
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
        except Exception as e:
            me.ok = False
            me.err.append(e)
    def write(me,msg):
        try:
            me.w.write(msg)
        except Exception as e:
            me.ok = False
            me.err.append(e)
    def get_errs(me):
        return me.errs