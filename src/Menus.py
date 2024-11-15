import tkinter as tk
from PIL import Image, ImageTk
from src.Player import WeaponData
import json, os


# class that fixes a bug when making lots of lambda functions in a loop
class funcer:
    def __init__(self, func, **args):
        self.func = lambda: func(**args)


class Menus:
    def __init__(self, window, inp, window_width, window_height, menu_funcs, control_map, control_map_defaults, font):
        self.window = window
        self.inp = inp
        self.window_width = window_width
        self.window_height = window_height
        self.menu_funcs = menu_funcs
        self.control_map = control_map
        self.control_map_defaults = control_map_defaults

        self.font = font

        self.frame = tk.Frame(self.window)
        self.frame.pack()
        self.active_menu = ''
        self.prev_menu = []
        self.set_menu('Start_Screen')

        self.listening_remap_action = None

    def make_start_screen(self):
        image = Image.open('Sprites/Title.png').resize((300, 150), resample=Image.Resampling.BOX)
        self.image = ImageTk.PhotoImage(image)
        title = tk.Canvas(self.frame, width=300, height=150, bg="darkolivegreen2", bd=0, highlightthickness=0)
        title.create_image(0, 0, image=self.image, anchor=tk.NW)
        title.place(relx=0.5, rely=0.5, y=-100, anchor=tk.S)

        tk.Button(self.frame, text='Start', command=self.start_game,
                  font=(self.font, 20), bg="green", relief=tk.GROOVE, bd=4, activebackground="green4",
                  ).place(relx=0.5, rely=0.5, y=-40, width=141, height=78, anchor=tk.CENTER)

        tk.Button(self.frame, text='Settings', command=lambda: self.set_menu("Settings"),
                  font=(self.font, 20), bg="green", relief=tk.GROOVE, bd=4, activebackground="green4",
                  ).place(relx=0.5, rely=0.5, y=60, width=178, height=84, anchor=tk.CENTER)

    def make_settings_menu(self):
        tk.Button(self.frame, text='Back', command=self.menu_back,
                  font=(self.font, 20), bg="green", relief=tk.GROOVE, bd=4, activebackground="green4", padx=5,
                  pady=0).place(x=10, y=10, anchor=tk.NW)

        tk.Label(self.frame, text="Edit Keybinds", bg="darkolivegreen2", font=(self.font, 40)
                 ).place(relx=0.5, y=50, anchor=tk.CENTER)

        for i, action in enumerate(self.control_map):
            txt = f"{action}: {self.control_map[action]['Key']}".replace('1', 'Left Click').replace('3', 'Right Click')
            key = tk.Button(self.frame, text=txt,
                            font=(self.font, 15), bg="green", relief=tk.GROOVE, bd=4, activebackground="green4")
            key.place(relx=0.53, x=-10, y=130 + 65 * i, height=50, width=246, anchor=tk.E)
            func = funcer(self.start_key_listener, action=action, button=key)
            key.configure(command=func.func)
            func = funcer(self.reset_keybind, action=action)
            tk.Button(self.frame, text='Reset Keybind', command=func.func,
                      font=(self.font, 15), bg="green", relief=tk.GROOVE, bd=4, activebackground="green4",
                      padx=0, pady=0).place(relx=0.53, x=10, y=130 + 65 * i, height=50, width=168, anchor=tk.W)

    def make_pause_menu(self):
        self.frame.configure(width=270, height=345, highlightbackground="darkgreen", highlightthickness=3)
        self.frame.lift()
        self.frame.place(relx=0.5, rely=0.5, anchor=tk.CENTER)

        tk.Button(self.frame, text="Resume", width=15, command=self.menu_funcs['pause'],
                  font=(self.font, 15), bg="green", relief=tk.GROOVE, bd=4, activebackground="green4", padx=0,
                  pady=0).place(relx=0.5, y=20, anchor=tk.N)
        tk.Button(self.frame, text='Settings', width=12, command=lambda: self.set_menu("Settings"),
                  font=(self.font, 15), bg="green", relief=tk.GROOVE, bd=4, activebackground="green4", padx=0,
                  pady=0).place(relx=0.5, y=100, anchor=tk.N)
        tk.Button(self.frame, text='Save', width=10,
                  font=(self.font, 15), bg="green", relief=tk.GROOVE, bd=4, activebackground="green4",
                  padx=0, pady=0).place(relx=0.5, y=180, anchor=tk.N)
        tk.Button(self.frame, text='Exit To Main Menu', width=16, command=self.menu_funcs['end_game'],
                  font=(self.font, 15), bg="green", relief=tk.GROOVE, bd=4, activebackground="green4",
                  padx=0, pady=0).place(relx=0.5, y=260, anchor=tk.N)

    def make_shop_menu(self,shop_data):
        self.frame.configure(width=500, height=319, highlightbackground="darkgreen", highlightthickness=3)
        self.frame.lift()
        self.frame.place(relx=0.5, rely=0.5, anchor=tk.CENTER)
        self.image_storer = []
        player = shop_data["Player_Object"]

        ## Weapon Shop
        for i,weapon in enumerate(WeaponData.data):
            x_pos = i*120+70
            img = Image.open(WeaponData.data[weapon]["File"]).convert("RGBA")
            img_height = 60
            img = img.resize((int(img_height*img.width/img.height),img_height),resample=Image.Resampling.BOX)
            self.image_storer.append(ImageTk.PhotoImage(img))
            if weapon == player.active_weapon:
                label_font = (self.font,15,"bold")
            else:
                label_font = (self.font,13)
            tk.Label(self.frame, text=weapon, image=self.image_storer[-1],compound="top",highlightbackground="darkgreen", highlightthickness=3,
                      bg="darkolivegreen2",width=100,height=151,font=label_font,anchor=tk.N,pady=10).place(x=x_pos,y=10,anchor=tk.N)
            if not(weapon in shop_data['Owned_Guns']):
                func = funcer(self.buy_weapon, player_func=player.set_weapon, new_weapon=weapon, shop_data=shop_data,
                              price=WeaponData.data[weapon]["Price"])
                tk.Button(self.frame, text=f'Buy: {WeaponData.data[weapon]["Price"]}', command=func.func,
                          font=(self.font, 14), bg="green", relief=tk.GROOVE, bd=4, activebackground="green4",
                          ).place(x=x_pos,y=135,width=100,height=50,anchor=tk.N)
            else:
                func = funcer(self.set_weapon,player_func=player.set_weapon,new_weapon=weapon,shop_data=shop_data)
                tk.Button(self.frame, text='Equip', command=func.func,
                          font=(self.font, 14), bg="green", relief=tk.GROOVE, bd=4, activebackground="green4",
                          ).place(x=x_pos, y=135, width=100, height=50, anchor=tk.N)

        ## Temp Upgrades
        temp_upgrades = [{'Name':'Heal','Func':Menus.buy_heal,'Counter':-1,'Price':10},
                         {'Name':'Shield','Func':Menus.buy_shield,'Counter':1, 'Price':20},
                         {'Name': 'Force Push', 'Func': self.buy_forcepush, 'Counter': 10, 'Price': 5},
                         {'Name': 'Grenade', 'Func': self.buy_grenade,'Counter':10, 'Price':8}]
        for i,upgrade in enumerate(temp_upgrades):
            x_pos = i*120+70
            tk.Label(self.frame, text=upgrade['Name'],highlightbackground="darkgreen", highlightthickness=3,
                      bg="darkolivegreen2",font=(self.font,14),anchor=tk.N,pady=0
                     ).place(x=x_pos,y=200,width=112,height=96,anchor=tk.N)
            func = funcer(upgrade['Func'],price=upgrade["Price"],shop_data=shop_data,counter=upgrade["Counter"])
            txt = f'Buy: {upgrade["Price"]}'
            tk.Button(self.frame, text=txt, command=func.func,
                      font=(self.font, 14), bg="green", relief=tk.GROOVE, bd=4, activebackground="green4",
                      ).place(x=x_pos, y=240, width=100, height=50, anchor=tk.N)

    def make_death_screen(self,game_stats):
        self.frame.configure(width=400, height=530, highlightbackground="darkgreen", highlightthickness=3)
        self.frame.lift()
        self.frame.place(relx=0.5, rely=0.5, anchor=tk.CENTER)

        tk.Label(self.frame,text='YOU DIED',font=(self.font,40,'bold'), fg='red', bg="darkolivegreen2",
                 ).place(relx=0.5, y=15, anchor=tk.N)

        tk.Label(self.frame,text=f'Score: {game_stats["Score"]}',font=(self.font,30), bg="darkolivegreen2",
                 ).place(relx=0.5, y=100, anchor=tk.N)

        display_info = ['Wave Reached', 'Zombie Kills', 'Damage Dealt', 'Coins Earned',
                        'Rounds Fired', 'Grenades Thrown', 'Force Pushes Used']
        for i,dat in enumerate(display_info):
            stat = game_stats[dat]
            if type(stat) == float:
                stat = int(stat)
            tk.Label(self.frame,text=f'{dat}: {stat}',font=(self.font,15), bg="darkolivegreen2",
                 ).place(x=20, y=175+i*40, anchor=tk.NW)

        tk.Button(self.frame, text='Save', command=lambda: self.set_menu('Score_Entry_Menu',data=game_stats),
                  font=(self.font, 14), bg="green", relief=tk.GROOVE, bd=4, activebackground="green4",
                  ).place(relx=0.7,y=460,width=140,height=50,anchor=tk.N)

        tk.Button(self.frame, text='Main Menu', command= self.menu_funcs["end_game"],
                  font=(self.font, 14), bg="green", relief=tk.GROOVE, bd=4, activebackground="green4",
                  ).place(relx=0.3, y=460, width=140, height=50, anchor=tk.N)

    def make_score_entry_menu(self,game_stats):
        self.frame.configure(width=400, height=185, highlightbackground="darkgreen", highlightthickness=3)
        self.frame.lift()
        self.frame.place(relx=0.5, rely=0.5, anchor=tk.CENTER)

        tk.Label(self.frame,text=f'Save Score: {game_stats["Score"]}',font=(self.font,25),  bg="darkolivegreen2",
                 ).place(relx=0.5, y=5, anchor=tk.N)

        name_entry = tk.Entry(self.frame, bg="darkolivegreen2", borderwidth=3, font=('arial',15))
        name_entry.place(relx=0.5, x=-50,y=90, width=200, anchor=tk.W)

        tk.Label(self.frame, text='Enter Name:' ,bg="darkolivegreen2", font=('arial', 15),
                 ).place(relx=0.5,x=-50, y=90,  anchor=tk.E)

        tk.Button(self.frame, text='Save', command=lambda: self.save_score(game_stats,name_entry),
                  font=(self.font, 16), bg="green", relief=tk.GROOVE, bd=4, activebackground="green4",
                  ).place(relx=0.5,y=120,width=140,height=50,anchor=tk.N)

    def save_score(self, game_stats, name_entry):
        game_stats["Username"] = name_entry.get()
        data = [game_stats]
        if os.path.isfile('Data/player_scores.json'):
            with open('Data/player_scores.json','r') as f:
                data = json.load(f)
                data.append(game_stats)

        with open('Data/player_scores.json','w') as f:
            json.dump(data,f)

        self.menu_funcs["end_game"]()

    def set_weapon(self,player_func,new_weapon,shop_data):
        player_func(new_weapon)
        self.set_menu('Shop_Menu',False,shop_data)
    def buy_weapon(self,player_func,new_weapon,shop_data,price):
        if shop_data['Coins']>=price:
            shop_data['Coins']-=price
            shop_data['Owned_Guns'].append(new_weapon)
            self.set_weapon(player_func,new_weapon,shop_data)

    @staticmethod
    def buy_heal(price,shop_data,counter):
        if shop_data['Coins']>=price and shop_data["Player_Object"].health < shop_data["Player_Object"].max_health:
            shop_data['Coins'] -= price
            shop_data["Player_Object"].health = shop_data["Player_Object"].max_health

    @staticmethod
    def buy_shield(price,shop_data,counter):
        if shop_data['Coins'] >= price and shop_data["Player_Object"].shield < shop_data["Player_Object"].max_health:
            shop_data['Coins'] -= price
            shop_data["Player_Object"].shield = shop_data["Player_Object"].max_health

    def buy_grenade(self,price,shop_data,counter):
        if shop_data['Coins'] >= price and shop_data["Temp_Upgrades"]["Grenade"] < counter:
            shop_data['Coins'] -= price
            shop_data["Temp_Upgrades"]["Grenade"] += 1
    def buy_forcepush(self,price,shop_data,counter):
        if shop_data['Coins'] >= price and shop_data["Temp_Upgrades"]["Force Push"] < counter:
            shop_data['Coins'] -= price
            shop_data["Temp_Upgrades"]["Force Push"] += 1

    def start_key_listener(self, action, button):
        if self.listening_remap_action is None:
            self.window.bind('<ButtonPress>', self.get_key_mapping)
            self.window.bind('<KeyPress>', self.get_key_mapping)
            self.listening_remap_action = action
            button.configure(bg="green2")

    def get_key_mapping(self, event):
        if not self.listening_remap_action is None:
            if event.keysym != '??':
                self.control_map[self.listening_remap_action]["Key"] = event.keysym
            elif event.num != '??':
                self.control_map[self.listening_remap_action]["Key"] = event.num
            self.inp.refresh_binding()
            self.set_menu("Settings",False)
            self.listening_remap_action = None

    def reset_keybind(self, action):
        self.control_map[action]["Key"] = self.control_map_defaults[action]["Key"]
        self.set_menu("Settings",False)

    def set_menu(self, menu, add_to_prev_menu=True,data=None):
        for widget in self.frame.winfo_children():
            widget.destroy()
        if add_to_prev_menu:
            self.prev_menu.append(self.active_menu)
        self.active_menu = menu
        if self.active_menu != "Game":
            if self.active_menu == "Pause_Screen":
                self.make_pause_menu()
            elif self.active_menu == "Shop_Menu":
                self.make_shop_menu(data)
            elif self.active_menu == "Death_Screen":
                self.make_death_screen(data)
            elif self.active_menu == "Score_Entry_Menu":
                self.make_score_entry_menu(data)
            else:
                self.frame.configure(width=self.window_width, height=self.window_height, bg="darkolivegreen2")
                if self.active_menu == "Start_Screen":
                    self.make_start_screen()
                elif self.active_menu == "Settings":
                    self.make_settings_menu()

        else:
            self.frame.lower()

    def menu_back(self):
        self.set_menu(self.prev_menu.pop(-1), False)

    def start_game(self):
        self.set_menu("Game")
        self.menu_funcs['start_game']()


    def window_resize(self,window_width, window_height):
        self.window_width = window_width
        self.window_height = window_height
        if self.active_menu != "Shop_Menu":
            self.set_menu(self.active_menu,False)
