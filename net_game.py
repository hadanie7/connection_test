# -*- coding: utf-8 -*-
"""
Created on Tue Aug 15 23:16:37 2017

@author: D
"""

import clock
from graphics import Main
from network import setup_conn
from network import pack_movement, unpack_movement
import logs
import lag_balancing

def main_loop(my_ac, game, conn, c, log, **args):
    iii = 0
    oiii = 0
    while True:
        force_ref = [None]
        if not game.step(mouse_force_rec = force_ref):
            conn.write("bye")
            print "game closed normally"
            return
        
        log['tms'].append(c.get_time())
        conn.write('m'+pack_movement(my_ac, force_ref[0]))
        c.tick(lag_balancing.get_step())
#        for i in xrange(len(main.queues)): # simulate non moving mouse on other side
#            if i!=main.my_cont and iii > -1:
#                    main.add_controls(i,0+0j)
        for m in conn.read():
            if m == "bye": # always shorter than a packed movement
                game.close()
                print "game closed by other side"
                return
            elif m[0] == 'm':
                log['rec'].append(c.get_time())
                ctr, frc = unpack_movement(m[1:])
                game.add_controls(ctr, frc)
                lag_balancing.report_delay(iii-oiii)
                oiii += 1
            elif m[0] == 'l':
                a = m.split()
                lag_balancing.recv(a[1], a[2])

        if not conn.are_you_OK():
            print "a connection error ocurred:"
            print(conn.get_errs())
            print ''
            raise Exception("connection error")
        iii += 1

if __name__ == "__main__":
    try:
        my_ac = int(raw_input('choose controller: '))
        conn = setup_conn()
        game = Main(my_cont = my_ac)
        c = clock.Clock()
        log = dict(tms=[], rec=[])
        
        lag_balancing.normal_step = 0.01
        lag_balancing.send = lambda i, m, conn = conn: conn.write('l {} {}'.format(i, m))
        ## select our actor our actor
        main_loop(**locals())
    except:
        game.close()
        raise
    conn.close()
    logs.save_log(**log)