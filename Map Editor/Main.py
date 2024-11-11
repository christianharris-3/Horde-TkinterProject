import pygame,math,random,sys,os
import PyUI as pyui

pygame.init()
screenw = 1200
screenh = 900
screen = pygame.display.set_mode((screenw, screenh),pygame.RESIZABLE)
ui = pyui.UI()
done = False
clock = pygame.time.Clock()
##ui.styleload_green() 
ui.styleset(col=(175,160,156),textcol=(246,230,219),wallpapercol=(150,130,120),textsize=30,verticalspacing=2,
            horizontalspacing=5,clickdownsize=2,roundedcorners=4,scalesize=False)

from Environment.Map_Editor import Map_Editor


game = Map_Editor(ui)
 
while not done:
    for event in ui.loadtickdata():
        if event.type == pygame.QUIT:
            done = True 
        if event.type == pygame.VIDEORESIZE:
            game.resize()
    game.game_tick(screen)
    
    ui.rendergui(screen)
    ui.write(screen,1,1,str(round(clock.get_fps(),1)),20,center=False)
    pygame.display.flip()
    clock.tick(60)                                               
pygame.quit() 
