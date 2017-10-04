# -*- coding: utf-8 -*-
"""
pygame_color_picker.pyw
@author: enom
"""
import sys
import pygame
from pygame.locals import QUIT, KEYDOWN, \
    K_x, K_c, K_v, K_s, K_d, K_f, K_q, K_w, K_e, K_r


def main():
    WIDTH = 700
    HEIGHT = 300
    FPS = 60
    DELAY = 60
    INTERVAL = 60
    RGBMAX = 256
    THRESHOLD = 384
    
    pygame.init()
    pygame.key.set_repeat(DELAY, INTERVAL)
    SURFACE = pygame.display.set_mode((WIDTH, HEIGHT))
    FPSCLOCK = pygame.time.Clock()
    FONT = pygame.font.SysFont(None, 72)
    
    bgcolor = [0, 0, 0]
    fontcolor = (255, 255, 255)
    r_auto = False
    g_auto = False
    b_auto = False
    
    while True:
        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == KEYDOWN:
                if event.key == K_q:
                    pygame.quit()
                    sys.exit()
                elif event.key == K_w:
                    r_auto = not r_auto
                elif event.key == K_e:
                    g_auto = not g_auto
                elif event.key == K_r:
                    b_auto = not b_auto
                elif event.key == K_x:
                    bgcolor[0] -= 1
                    bgcolor[0] %= RGBMAX
                elif event.key == K_c:
                    bgcolor[1] -= 1
                    bgcolor[1] %= RGBMAX
                elif event.key == K_v:
                    bgcolor[2] -= 1
                    bgcolor[2] %= RGBMAX
                elif event.key == K_s:
                    bgcolor[0] += 1
                    bgcolor[0] %= RGBMAX
                elif event.key == K_d:
                    bgcolor[1] += 1
                    bgcolor[1] %= RGBMAX
                elif event.key == K_f:
                    bgcolor[2] += 1
                    bgcolor[2] %= RGBMAX

        if r_auto:
            bgcolor[0] += 1
            bgcolor[0] %= RGBMAX
        if g_auto:
            bgcolor[1] += 1
            bgcolor[1] %= RGBMAX
        if b_auto:
            bgcolor[2] += 1
            bgcolor[2] %= RGBMAX
        
        SURFACE.fill(bgcolor)
        
        rgb_str = 'RGB color: #'
        if sum(bgcolor) > THRESHOLD:
            fontcolor = (0, 0, 0)
        else:
            fontcolor = (255, 255, 255)
        for i in range(3):
            rgb_str += hex(bgcolor[i])[2:].zfill(2)
        rgb_text = FONT.render(rgb_str, True, fontcolor)
        rgb_rect = rgb_text.get_rect()
        rgb_rect.midleft = (50, HEIGHT / 2)
        SURFACE.blit(rgb_text, rgb_rect)
        
        rgb_str = 'RGB color: ' + str(bgcolor)
        rgb_text = FONT.render(rgb_str, True, fontcolor)
        rgb_rect = rgb_text.get_rect()
        rgb_rect.midleft = (50, HEIGHT / 2 + 50)
        SURFACE.blit(rgb_text, rgb_rect)
    
        pygame.display.update()
        FPSCLOCK.tick(FPS)


if __name__ == '__main__':
    main()