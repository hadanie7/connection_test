# -*- coding: utf-8 -*-
"""
Created on Tue Aug 15 23:16:37 2017

@author: D
"""

import clock
from graphics import Main
from network import setup_conn
from network import pack_movement, unpack_movement

if __name__ == "__main__":
    try:
        main = Main()
        conn = setup_conn()
        c = clock.Clock()
        ## select our actor our actor
        my_ac = int(raw_input('choose controller: '))        
        
        iii = 0
        while True:
            force_ref = [None]
            if not main.step(mouse_force_rec = force_ref):
                break
            conn.write(pack_movement(my_ac, force_ref[0]))
            c.tick(0.01)
#            for i in xrange(len(main.queues)): # simulate non moving mouse on other side
#                if i!=main.my_cont and iii > -1:
#                    main.add_controls(i,0+0j)
            for m in conn.read():
                ctr, frc = unpack_movement(m)
                main.add_controls(ctr, frc)
            iii += 1
    except:
        pygame.quit()
        raise