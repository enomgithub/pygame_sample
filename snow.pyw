# -*- coding: utf-8 -*-
"""
snow.pyw
@author: enom
"""
import sys
from random import randint
import pygame
from pygame.locals import QUIT, Rect, KEYDOWN, K_q

WIDTH = 640
HEIGHT = 480
SNOWCOLOR = (255, 255, 255)
BGCOLOR = (0, 0, 0)
FPS = 60
N = 100


def main():
    pygame.init()
    SURFACE = pygame.display.set_mode((WIDTH, HEIGHT))
    FPSCLOCK = pygame.time.Clock()
    snows = []
    for i in range(N):
        pos_x = randint(0, WIDTH - 1)
        pos_y = randint(0, HEIGHT - 1)
        size = randint(1, 10)
        snows.append(Rect(pos_x, pos_y, size, size))
        
    while True:
        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == KEYDOWN:
                if event.key == K_q:
                    pygame.quit()
                    sys.exit()
                
        SURFACE.fill(BGCOLOR)
        
        for snow in snows:
            snow.move_ip(randint(1, 3), randint(1, 5))
            snow.x %= WIDTH
            snow.y %= HEIGHT            
            pygame.draw.ellipse(SURFACE, SNOWCOLOR, snow)
            
        pygame.display.update()
        FPSCLOCK.tick(FPS)


if __name__ == '__main__':
    main()