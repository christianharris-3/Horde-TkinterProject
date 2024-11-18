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
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_TAB:
                game.table_move_input([0,1])
            elif event.key == pygame.K_DOWN:
                game.table_move_input([0,1])
            elif event.key == pygame.K_UP:
                game.table_move_input([0,-1])
            elif event.key == pygame.K_LEFT:
                game.table_move_input([-1,0])
            elif event.key == pygame.K_RIGHT:
                game.table_move_input([1,0])
    game.game_tick(screen)
    
    ui.rendergui(screen)
    ui.write(screen,1,1,str(round(clock.get_fps(),1)),20,center=False)
    pygame.display.flip()
    clock.tick(60)                                               
pygame.quit() 
