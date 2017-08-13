# -*- coding: utf-8 -*-
"""
Created on Sun Aug 13 15:15:19 2017

@author: J&D
"""

import pygame

pygame.init()

scale = 32
w,h = 19,14

bg_col = (150,150,150)


def main():
    scr = pygame.display.set_mode((scale*(w+1),scale*(h+1)))
    
    clock = pygame.time.Clock()
    
    while True:
        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                pygame.quit()
                return
        
        scr.fill(bg_col)
        
        pygame.display.flip()
        
        clock.tick()
        
if __name__ == "__main__":
    main()