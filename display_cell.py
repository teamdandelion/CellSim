#!/Library/Frameworks/Python.framework/Versions/2.7/bin/python

import pygame, sys
from pygame.locals import *
# set up pygame
pygame.init()
# set up the window
windowSurface = pygame.display.set_mode((500, 400), 0, 32)
pygame.display.set_caption('Multicell Simulator')
# set up the colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
BROWN = (69, 51, 37)
FLORA = (102, 255, 102)
FERN = (64, 128, 0)
SKY = (102, 204, 255)
# set up fonts
basicFont = pygame.font.SysFont(None, 48)
# set up the text

# draw the white background onto the surface
windowSurface.fill(BROWN)
# draw a green polygon onto the surface
pygame.draw.polygon(windowSurface, SKY, ((0, 0), (0, 200), (500, 200), (500, 0)))
# draw some blue lines onto the surface

# draw a blue circle onto the surface
# draw a red ellipse onto the surface
# draw the text's background rectangle onto the surface
# get a pixel array of the surface
pixArray = pygame.PixelArray(windowSurface)


pixArray[480][380] = BLACK
del pixArray
# draw the text onto the surface
# draw the window onto the screen
pygame.display.update()
# run the game loop
while True:
    for event in pygame.event.get():
        if event.type == QUIT:
            pygame.quit()
            sys.exit()

# import sys
# import pygame
# from pygame.locals import *
# import cell
# 
# # set up pygame
# pygame.init()
# 
# # set up teh window

# 
# # set up the colors

# 
# windowSurface.fill(WHITE)
# 
# pygame.draw.polygon(windowSurface, SKY, ((100, 0), (100, 100), 
#     (0, 100), (0, 0) )
#     
# pygame.display.update()
# 
# while True:
#     for event in pygame.event.get():
#         if event.type == QUIT:
#             pygame.quit()
#             sys.exit()