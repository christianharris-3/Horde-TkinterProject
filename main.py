import tkinter as tk
import src.TkinterController as TC
from src.Game import Game
from src.Menus import Menus
import copy,time

#tkinter color list
#https://www.plus2net.com/python/tkinter-colors.php

class Main:
    def __init__(self):
        self.window_width = 1200
        self.window_height = 800

        self.window = tk.Tk()
        self.window.geometry(f'{self.window_width}x{self.window_height}')
        self.input = TC.Input(self.window)

        self.control_map_defaults = {'Left': {'Key': 'a', 'continuous': True},
                                     'Right': {'Key': 'd', 'continuous': True},
                                     'Up': {'Key': 'w', 'continuous': True},
                                     'Down': {'Key': 's', 'continuous': True},
                                     'Shoot': {'Key': 1, 'continuous': False},
                                     'Shop': {'Key': 'b', 'continuous': False},
                                     'Reload': {'Key': 'r', 'continuous': False},
                                     'Pause': {'Key': 'Escape', 'continuous': False}}
        self.control_map = copy.deepcopy(self.control_map_defaults)

        self.game_paused = False
        self.pause_button_down = False
        self.game_active = False
        self.game = None
        menu_funcs  = {'start_game':self.start_game,
                       'pause':self.pause,
                       'end_game':self.end_game}
        self.menus = Menus(self.window, self.input, self.window_width, self.window_height, menu_funcs,
                           self.control_map, self.control_map_defaults)


    def game_loop(self, delta_time):
        if not self.game_active:
            return True
        else:
            if not self.game_paused:
                done, open_shop = self.game.gameloop(delta_time)
                if open_shop:
                    self.game_paused = True
                    self.menus.set_menu("Shop_Menu",shop_data=self.game.shop_data)
            else:
                done = False
            if done:
                self.end_game()
            else:
                self.game.render_frame()
                if self.input.get_pressed(self.control_map["Pause"]["Key"]):
                    self.pause()
                else:
                    self.pause_button_down = False
            return done


    def window_resize(self,event):
        self.window_width = event.width
        self.window_height = event.height
        if self.game_active:
            self.game.window_resize(self.window_width,self.window_height)

    def start_game(self):
        self.game_paused = False
        self.game_active = True
        self.game = Game(self.window, self.input, self.window_width, self.window_height, self.control_map, self.menus)
        TC.game_looper(self.game_loop, self.window)

        # this thing messes up everything so hard for no reason
        # self.window.bind('<Configure>', self.window_resize)

    def end_game(self):
        self.game_active = False
        self.game.screen.destroy()
        self.game = -1
        self.menus.set_menu('Start_Screen')
        self.menus.prev_menu = []

    def pause(self):
        if not self.pause_button_down:
            self.pause_button_down = True
            self.game_paused = not self.game_paused
            if self.game_paused:
                self.menus.set_menu("Pause_Screen")
            else:
                self.menus.set_menu("Game")



if __name__ == "__main__":
    main = Main()
    main.window.mainloop()
