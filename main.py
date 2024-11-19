import tkinter as tk
from PIL import ImageTk
import src.TkinterController as TC
from src.Game import Game
from src.Menus import Menus
import copy,time,os,json
import webbrowser

#tkinter color list
#https://www.plus2net.com/python/tkinter-colors.php

class Main:
    def __init__(self):
        self.window_width = 1200
        self.window_height = 800

        self.window = tk.Tk()
        self.window.geometry(f'{self.window_width}x{self.window_height}')
        self.window.title("Horde")
        self.icon = ImageTk.PhotoImage(file="Sprites/Player.png")
        self.window.wm_iconphoto(False, self.icon)
        self.input = TC.Input(self.window)

        self.control_map_defaults = {'Left': {'Key': 'a', 'continuous': True},
                                     'Right': {'Key': 'd', 'continuous': True},
                                     'Up': {'Key': 'w', 'continuous': True},
                                     'Down': {'Key': 's', 'continuous': True},
                                     'Shoot': {'Key': 1, 'continuous': False},
                                     'Shop': {'Key': 'e', 'continuous': False},
                                     'Reload': {'Key': 'r', 'continuous': False},
                                     'Grenade': {'Key': 3, 'continuous': False},
                                     'Force Push': {'Key': 'space', 'continuous': False},
                                     'Pause': {'Key': 'Escape', 'continuous': False}}
        self.load_control_map()

        self.game_paused = False
        self.pause_button_down = False
        self.game_active = False
        self.game = None
        self.font = 'Segoe Print'

        self.target_fps = [60]

        menu_funcs  = {'start_game':self.start_game,
                       'pause':self.pause,
                       'end_game':self.end_game}
        self.menus = Menus(self.window, self.input, self.window_width, self.window_height, menu_funcs,
                           self.control_map, self.control_map_defaults, self.font)

        self.window.bind('<Tab>',self.boss_key)
        self.boss_key_active = False
        self.boss_key_image = ImageTk.PhotoImage(file='Sprites/Boss Key.png')

        # this thing messes up everything so hard for no reason
        # self.window.bind('<Configure>', self.window_resize)
        # self.window_resize_timestamp = time.perf_counter()


    def game_loop(self, delta_time):
        if not self.game_active:
            return True
        else:
            if not self.game_paused:
                # Run main gameloop when not paused
                done = False
                player_died, open_shop = self.game.gameloop(delta_time)
                if player_died:
                    self.menus.set_menu("Death_Screen",data=self.game.game_stats)
                elif open_shop:
                    self.game_paused = True
                    self.menus.set_menu("Shop_Menu",data=self.game.shop_data)
            else:
                done = False

                ## Code to shut shop with same key that opens it
                if self.input.get_pressed(self.control_map["Shop"]["Key"]):
                    if self.menus.active_menu == 'Shop_Menu' and not(self.control_map["Shop"]["Key"] in self.game.player.buttons_down):
                        self.pause()
                        self.game.player.buttons_down.append(self.control_map["Shop"]["Key"])
                else:
                    try:
                        self.game.player.buttons_down.remove(self.control_map["Shop"]["Key"])
                    except:
                        pass
            if done:
                self.end_game()
            else:
                self.game.render_frame()
                if self.input.get_pressed(self.control_map["Pause"]["Key"]):
                    if self.menus.active_menu != "Death_Screen":
                        self.pause()
                    else:
                        done = True
                        self.end_game()
                else:
                    self.pause_button_down = False
                if self.input.get_cheatcode_active():
                    self.game_paused = True
                    self.menus.set_menu('CheatCode_Menu',data=self.game.cheat_info)
            return done


    def window_resize(self,event):
        if self.window_resize_timestamp+0.1 < time.perf_counter():
            self.window_resize_timestamp = time.perf_counter()
            self.window_width = event.width
            self.window_height = event.height
            self.menus.window_resize(self.window_width, self.window_height)
            if self.game_active:
                self.game.window_resize(self.window_width,self.window_height)

    def start_game(self,gamefile=None,level='Level 3'):
        self.game_paused = False
        self.game_active = True
        self.game = Game(self.window, self.input, self.window_width, self.window_height, self.control_map, self.menus,
                         self.font, gamefile, level)
        self.menus.menu_funcs["save_game"] = self.game.save_game
        self.menus.menu_funcs["game_object"] = self.game
        TC.game_looper(self.game_loop, self.window, self.target_fps)


    def end_game(self):
        self.game_active = False
        self.game.screen.destroy()
        self.game = -1
        self.menus.set_menu('Start_Screen')
        self.menus.prev_menu = []

    def pause(self):
        if not self.pause_button_down:
            self.target_fps[0] = int(60*self.game.cheat_info["speed of time"])
            self.pause_button_down = True
            self.game_paused = not self.game_paused
            if self.game_paused:
                self.menus.set_menu("Pause_Screen",data=self.game.gamefile)
            else:
                self.menus.set_menu("Game")

    def boss_key(self,_):
        self.boss_key_active = not self.boss_key_active
        if self.boss_key_active:
            webbrowser.open('https://en.wikipedia.org/wiki/Boss_key')
            self.window.geometry('120x26')
            self.window.iconify()
            if self.game_active and not self.game_paused:
                self.pause()
            self.boss_key_label = tk.Label(self.window,image=self.boss_key_image,borderwidth=0)
            self.boss_key_label.pack()
            self.boss_key_label.tkraise(self.menus.frame)
        else:
            self.window.geometry(f'{self.window_width}x{self.window_height}')
            self.boss_key_label.destroy()

    def load_control_map(self):
        if os.path.exists('Data/control_map.json'):
            with open('Data/control_map.json','r') as f:
                self.control_map = json.load(f)
        else:
            self.control_map = copy.deepcopy(self.control_map_defaults)
            with open('Data/control_map.json','w') as f:
                json.dump(self.control_map,f)


if __name__ == "__main__":
    main = Main()
    main.window.mainloop()
