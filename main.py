import tkinter as tk
import src.TkinterController as TC
from src.Game import Game
from src.Menus import Menus

#tkinter color list
#https://www.plus2net.com/python/tkinter-colors.php

class Main:
    def __init__(self):
        self.window_width = 1200
        self.window_height = 1000

        self.window = tk.Tk()
        self.window.geometry(f'{self.window_width}x{self.window_height}')
        self.input = TC.Input(self.window)

        self.game_active = False
        self.game = -1
        self.menus = Menus(self.window, self.window_width, self.window_height,self.start_game)


    def game_loop(self, delta_time):
        done = self.game.gameloop(delta_time)
        self.game.render_frame()
        if done:
            self.end_game()
        return done


    def window_resize(self,event):
        print('config',event)
        self.window_width = event.width
        self.window_height = event.height
        if self.game_active:
            self.game.window_resize(self.window_width,self.window_height)

    def start_game(self):
        self.game_active = True
        self.game = Game(self.window, self.input, self.window_width, self.window_height)
        TC.game_looper(self.game_loop, self.window)

        # this thing fucks everything so hard for no reason
        # self.window.bind('<Configure>', self.window_resize)

    def end_game(self):
        self.game_active = False
        self.game.screen.destroy()
        self.game = -1
        self.menus.set_menu('Start_Screen')



if __name__ == "__main__":
    main = Main()
    main.window.mainloop()
