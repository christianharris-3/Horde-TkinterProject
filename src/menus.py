import json, os
import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk
from src.player import WeaponData
from src.utiles import get_now, resourcepath


class funcer:
    """
    this class fixes a bug when making lots of lambda functions in a loop

    example of the bug that this class fixes:

    ## all button will print 9 instead of the numbers 0-9
    ## by storing lambda function in this object they will print 0-9
    def example_function(i):
        print(i)
    for i in range(10):
        tk.Button(root,text=str(i),command=lambda: example_function(i)).pack()
    """
    def __init__(self, func, **args):
        self.func = lambda: func(**args)

# tkinter color list for reference
# https://www.plus2net.com/python/tkinter-colors.php


class Menus:
    """
    Menu object creates and manages all tkinter widgets in the program

    --- import methods and attributes ---
    attribute:  active_menu   Stores the current displayed menu.
    attribute:  frame         Stores a tkinter frame that is used by every menu.
    method   :  set_menu      Deletes all widgets on the frame, then runs the make function
                              for the given menu passing through any data needed.
    methods  : make_          All functions starting with make_ create all widgets for their given
                              menu.
    """
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
        self.frame.place(relx=0.5,rely=0.5,anchor=tk.CENTER)
        self.active_menu = ''
        self.prev_menu = []
        self.set_menu_data_cache = []
        self.title_image = None
        self.set_menu('Start_Screen')

        self.listening_remap_action = None
        self.leaderboard_filter = 'All'
        self.leaderboard_data = []
        self.leaderboard_table_indexes = []
        self.leaderboard_table = None
        self.image_storer = []
        self.score_info_display = None
        self.cheatcode_tkvars = []

        # style for tables
        style = ttk.Style()
        style.theme_use("clam")
        style.configure('Treeview.Heading', font=(self.font, 18), background='#060', relief="flat",
                        borderwidth=0, fieldbackground='#060')
        style.map('Treeview.Heading', background=[('selected', '#060')],
                  foreground=[('selected', '#grey9')])
        style.configure('Treeview', font=(self.font, 16), rowheight=35, background="green",
                        fieldbackground='darkolivegreen2',
                        relief='flat', borderwidth=0, bd=0, highlightthickness=0)
        style.map('Treeview', background=[('selected', 'green4')],
                  foreground=[('selected', 'gray6')])

    def set_menu(self, menu, add_to_prev_menu=True,data=None):
        for widget in self.frame.winfo_children():
            widget.destroy()
        if add_to_prev_menu:
            self.prev_menu.append(self.active_menu)
            self.set_menu_data_cache.append(data)
        self.active_menu = menu
        if self.active_menu != "Game":
            if self.active_menu == "Pause_Screen":
                self.make_pause_menu(data)
            elif self.active_menu == "Shop_Menu":
                self.make_shop_menu(data)
            elif self.active_menu == "Death_Screen":
                self.make_death_screen(data)
            elif self.active_menu == "Score_Entry_Menu":
                self.make_score_entry_menu(data)
            elif self.active_menu == "Save_Game_Menu":
                self.make_save_gamestate_menu(data)
            elif self.active_menu == "CheatCode_Menu":
                self.make_cheatcode_menu(data)
            else:
                self.frame.configure(width=self.window_width, height=self.window_height, bg="darkolivegreen2",
                                     highlightthickness=0)
                if self.active_menu == "Start_Screen":
                    self.make_start_screen()
                elif self.active_menu == "Settings":
                    self.make_settings_menu()
                elif self.active_menu == "Load_Gamestate_Menu":
                    self.make_load_gamestate_menu()
                elif self.active_menu == "Leaderboard_Menu":
                    self.make_leaderboard_menu(data)
                elif self.active_menu == "Level_Select":
                    self.make_level_select_menu()

        else:
            self.frame.lower()

    def menu_back(self):
        del self.set_menu_data_cache[-1]
        if len(self.set_menu_data_cache) == 0:
            self.set_menu_data_cache.append(None)
        self.set_menu(self.prev_menu.pop(-1), False, data = self.set_menu_data_cache.pop(-1))

##### Functions starting with make_ are used to create a menu

    def make_start_screen(self):
        image = Image.open(resourcepath('Sprites/Title.png')).resize((300, 150), resample=Image.Resampling.BOX)
        self.title_image = ImageTk.PhotoImage(image)
        title = tk.Canvas(self.frame, width=300, height=150, bg="darkolivegreen2", bd=0, highlightthickness=0)
        title.create_image(0, 0, image=self.title_image, anchor=tk.NW)
        title.place(relx=0.5, rely=0.5, y=-180, anchor=tk.S)

        tk.Button(self.frame, text='Start', command=lambda:self.set_menu("Level_Select"),
                  font=(self.font, 20), bg="green", relief=tk.GROOVE, bd=4, activebackground="green4",
                  ).place(relx=0.5, rely=0.5, y=-100, width=141, height=78, anchor=tk.CENTER)

        tk.Button(self.frame, text='Load Save', command=lambda: self.set_menu("Load_Gamestate_Menu"),
                  font=(self.font, 20), bg="green", relief=tk.GROOVE, bd=4, activebackground="green4",
                  ).place(relx=0.5, rely=0.5, width=185, height=84, anchor=tk.CENTER)

        tk.Button(self.frame, text='LeaderBoard', command=lambda: self.set_menu("Leaderboard_Menu"),
                  font=(self.font, 20), bg="green", relief=tk.GROOVE, bd=4, activebackground="green4",
                  ).place(relx=0.5, rely=0.5, y=100, width=220, height=84, anchor=tk.CENTER)

        tk.Button(self.frame, text='Settings', command=lambda: self.set_menu("Settings"),
                  font=(self.font, 20), bg="green", relief=tk.GROOVE, bd=4, activebackground="green4",
                  ).place(relx=0.5, rely=0.5, y=200, width=178, height=84, anchor=tk.CENTER)

        tk.Button(self.frame, text='Quit', command=self.window.destroy,
                  font=(self.font, 20), bg="red", relief=tk.GROOVE, bd=4, activebackground="red4",
                  ).place(relx=0.5, rely=0.5, y=300, width=100, height=84, anchor=tk.CENTER)

    def make_settings_menu(self):
        tk.Button(self.frame, text='Back', command=self.menu_back,
                  font=(self.font, 20), bg="green", relief=tk.GROOVE, bd=4, activebackground="green4", padx=5,
                  pady=0).place(x=10, y=10, anchor=tk.NW)

        tk.Label(self.frame, text="Edit Keybinds", bg="darkolivegreen2", font=(self.font, 40, "bold")
                 ).place(relx=0.5, y=50, anchor=tk.CENTER)


        ## Detects 2 controls with same input
        used = []
        conflicts = []
        for action in self.control_map:
            if self.control_map[action]['Key'] in used:
                conflicts.append(self.control_map[action]['Key'])
            else:
                used.append(self.control_map[action]['Key'])

        for i, action in enumerate(self.control_map):
            txt = f"{action}: {self.control_map[action]['Key']}".replace('1', 'Left Click').replace('3', 'Right Click')
            swap_col = 'green'
            if self.control_map[action]['Key'] in conflicts:
                swap_col = 'red3'
            key = tk.Button(self.frame, text=txt, font=(self.font, 15), bg=swap_col,
                            relief=tk.GROOVE, bd=4, activebackground="green4")
            key.place(relx=0.53, x=-10, y=130 + 65 * i, height=50, width=246, anchor=tk.E)
            func = funcer(self.start_key_listener, action=action, button=key)
            key.configure(command=func.func)

            func = funcer(self.reset_keybind, action=action)
            reset_color = 'green'
            if self.control_map[action]['Key'] != self.control_map_defaults[action]['Key']:
                reset_color = 'green3'
            tk.Button(self.frame, text='Reset Keybind', command=func.func,
                      font=(self.font, 15), bg=reset_color, relief=tk.GROOVE, bd=4, activebackground="green4",
                      padx=0, pady=0).place(relx=0.53, x=10, y=130 + 65 * i, height=50, width=168, anchor=tk.W)

    def make_pause_menu(self,gamefile):
        save_and_quit = os.path.exists(os.path.abspath(f'Data/Game Saves/{gamefile}.json'))

        self.frame.configure(width=270, height=345+80*save_and_quit, highlightbackground="darkgreen", highlightthickness=3)
        self.frame.lift()
        self.frame.place(relx=0.5, rely=0.5, anchor=tk.CENTER)

        tk.Button(self.frame, text="Resume", command=self.menu_funcs['pause'],
                  font=(self.font, 15), bg="green", relief=tk.GROOVE, bd=4, activebackground="green4",
                  ).place(relx=0.5, y=20, anchor=tk.N, width=207, height=63)
        tk.Button(self.frame, text='Settings', command=lambda: self.set_menu("Settings"),
                  font=(self.font, 15), bg="green", relief=tk.GROOVE, bd=4, activebackground="green4",
                  ).place(relx=0.5, y=100, anchor=tk.N, width=168, height=63)
        tk.Button(self.frame, text='Save', command=lambda: self.set_menu("Save_Game_Menu",data=gamefile),
                  font=(self.font, 15), bg="green", relief=tk.GROOVE, bd=4, activebackground="green4",
                  ).place(relx=0.5, y=180, anchor=tk.N, width=142, height=63)
        tk.Button(self.frame, text='Exit To Main Menu', command=self.menu_funcs['end_game'],
                  font=(self.font, 15), bg="green", relief=tk.GROOVE, bd=4, activebackground="green4",
                  ).place(relx=0.5, y=260, anchor=tk.N, width=220, height=63)
        if save_and_quit:
            tk.Button(self.frame, text='Save and Exit', command=self.save_and_quit,
                      font=(self.font, 15), bg="green", relief=tk.GROOVE, bd=4, activebackground="green4",
                      ).place(relx=0.5, y=340, anchor=tk.N, width=194, height=63)

    def make_shop_menu(self,shop_data):
        self.frame.configure(width=500, height=375, highlightbackground="darkgreen", highlightthickness=3)
        self.frame.lift()
        self.frame.place(relx=0.5, rely=0.5, anchor=tk.CENTER)
        self.image_storer = []
        player = shop_data["Player_Object"]

        ## title/coins/exit button
        tk.Label(self.frame,text='Shop',font=(self.font, 24, "bold"),bg="darkolivegreen2"
                 ).place(relx=0.5,anchor=tk.N)
        tk.Button(self.frame, text='Done', font=(self.font, 14), bg="green", relief=tk.GROOVE, bd=4,
                  activebackground="green4", command=self.menu_funcs['pause'],
                  ).place(relx=1,x=-10, y=10, anchor=tk.NE, height=50, width=100)
        tk.Label(self.frame,text=f'Coins: {shop_data["Coins"]}',font=(self.font, 20),bg="darkolivegreen2"
                 ).place(x=10,y=10, anchor=tk.NW)

        ## Weapon Shop
        for i,weapon in enumerate(WeaponData.data):
            x_pos = i*120+70
            img = Image.open(resourcepath(WeaponData.data[weapon]["File"])).convert("RGBA")
            img_height = 60
            img = img.resize((int(img_height*img.width/img.height),img_height),resample=Image.Resampling.BOX)
            self.image_storer.append(ImageTk.PhotoImage(img))
            if weapon == player.active_weapon:
                label_font = (self.font,15,"bold")
            else:
                label_font = (self.font,13)
            tk.Label(self.frame, text=weapon, image=self.image_storer[-1],compound="top",highlightbackground="darkgreen", highlightthickness=3,
                      bg="darkolivegreen2",width=100,height=151,font=label_font,anchor=tk.N,pady=10).place(x=x_pos,y=70,anchor=tk.N)
            if not(weapon in shop_data['Owned_Guns']):
                func = funcer(self.buy_weapon, player_func=player.set_weapon, new_weapon=weapon, shop_data=shop_data,
                              price=WeaponData.data[weapon]["Price"])
                if WeaponData.data[weapon]["Price"] <= shop_data["Coins"]:
                    col = 'green'
                    state = 'active'
                else:
                    col = '#484'
                    state = 'disabled'
                tk.Button(self.frame, text=f'Buy:{WeaponData.data[weapon]["Price"]}', command=func.func,
                          font=(self.font, 14), bg=col, relief=tk.GROOVE, bd=4, activebackground="green4",state=state,
                          disabledforeground='#333'
                          ).place(x=x_pos,y=195,width=100,height=50,anchor=tk.N)
            else:
                func = funcer(self.set_weapon,player_func=player.set_weapon,new_weapon=weapon,shop_data=shop_data)
                tk.Button(self.frame, text='Equip', command=func.func,
                          font=(self.font, 14), bg="green", relief=tk.GROOVE, bd=4, activebackground="green4",
                          ).place(x=x_pos, y=195, width=100, height=50, anchor=tk.N)

        ## Temp Upgrades
        temp_upgrades = [{'Name':'Heal','Func':self.buy_heal,'Counter':-1,'Price':10},
                         {'Name':'Shield','Func':self.buy_shield,'Counter':1, 'Price':20},
                         {'Name': 'Force Push', 'Func': self.buy_forcepush, 'Counter': 10, 'Price': 5},
                         {'Name': 'Grenade', 'Func': self.buy_grenade,'Counter':10, 'Price':8}]
        for i,upgrade in enumerate(temp_upgrades):
            x_pos = i*120+70
            tk.Label(self.frame, text=upgrade['Name'],highlightbackground="darkgreen", highlightthickness=3,
                      bg="darkolivegreen2",font=(self.font,14),anchor=tk.N,pady=0
                     ).place(x=x_pos,y=260,width=112,height=96,anchor=tk.N)
            func = funcer(upgrade['Func'],price=upgrade["Price"],shop_data=shop_data,counter=upgrade["Counter"])
            txt = f'Buy:{upgrade["Price"]}'
            if upgrade["Price"]<=shop_data["Coins"]:
                col = 'green'
                state = 'active'
            else:
                col = '#484'
                state = 'disabled'
            tk.Button(self.frame, text=txt, command=func.func, disabledforeground='#333',
                      font=(self.font, 14), bg=col, relief=tk.GROOVE, bd=4, activebackground="green4",state=state,
                      ).place(x=x_pos, y=300, width=100, height=50, anchor=tk.N)


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

    def make_save_gamestate_menu(self, gamefile):
        self.frame.configure(width=400, height=185, highlightbackground="darkgreen", highlightthickness=3)
        self.frame.lift()
        self.frame.place(relx=0.5, rely=0.5, anchor=tk.CENTER)

        tk.Label(self.frame,text='Save Game',font=(self.font,25),  bg="darkolivegreen2",
                 ).place(relx=0.5, y=5, anchor=tk.N)

        name_entry = tk.Entry(self.frame, bg="darkolivegreen2", borderwidth=3, font=('arial',15))
        name_entry.place(relx=0.5, x=-50,y=90, width=200, anchor=tk.W)
        if gamefile:
            name_entry.insert(0, gamefile)

        tk.Label(self.frame, text='Save Name:' ,bg="darkolivegreen2", font=('arial', 15),
                 ).place(relx=0.5,x=-50, y=90,  anchor=tk.E)

        tk.Button(self.frame, text='Save', command=lambda: self.save_game(self.menu_funcs["game_object"],name_entry),
                  font=(self.font, 16), bg="green", relief=tk.GROOVE, bd=4, activebackground="green4",
                  ).place(relx=0.5,y=120,width=140,height=50,anchor=tk.N)

    def make_load_gamestate_menu(self):
        tk.Button(self.frame, text='Back', command=self.menu_back,
                  font=(self.font, 20), bg="green", relief=tk.GROOVE, bd=4, activebackground="green4", padx=5,
                  pady=0).place(x=10, y=10, height=70, anchor=tk.NW)

        tk.Label(self.frame, text='Game Saves', font=(self.font, 30, "bold"), bg="darkolivegreen2",
                 ).place(relx=0.5,y=5,anchor=tk.N)

        gamestates = []
        path = "Data\\Game Saves\\"
        if not os.path.exists(path):
            os.makedirs(path)
        for filename in os.listdir(path):
            with open(path+filename,'r') as f:
                gamestates.append(json.load(f))
        gamestates.sort(reverse=True,key=lambda x: x["save_timestamp"]["unix_time"])

        titles = [('Name', 300), ('Level', 100), ('Date', 150), ('Time', 140), ('Score', 130), ('Wave', 130)]

        table = ttk.Treeview(self.frame, columns=[a[0] for a in titles], show='headings', style='Treeview', height=len(gamestates))

        for i,t in enumerate(titles):
            table.column(t[0], width=t[1], anchor='center')
            table.heading(t[0], text=t[0])

        for i,state in enumerate(gamestates):
            if "level" in state:
                table.insert('','end',iid=i,values=[state["filename"],state["level"]["title"],state["save_timestamp"]["date"],
                                                    state["save_timestamp"]["time"],state["game_stats"]['Score'],
                                                    state["game_stats"]["Wave Reached"]])
        table.place(relx=0.5,x=-80,y=90,anchor=tk.N)

        tk.Button(self.frame, text='Load', command=lambda: self.load_gamestate(table),
                  font=(self.font, 20), bg="green", relief=tk.GROOVE, bd=4, activebackground="green4"
                  ).place(relx=0.5, x=500, y=140, anchor=tk.CENTER, width=104, height=84)

        tk.Button(self.frame, text='Delete', command=lambda: self.delete_gamestate(table),
                  font=(self.font, 20), bg="green", relief=tk.GROOVE, bd=4, activebackground="green4",
                  ).place(relx=0.5, x=500, y=240, anchor=tk.CENTER, width=122, height=84)

    def make_leaderboard_menu(self,filter_):
        if not filter_:
            filter_ = 'All'
        self.leaderboard_filter = filter_

        # back button and title
        tk.Button(self.frame, text='Back', command=self.menu_back,
                  font=(self.font, 20), bg="green", relief=tk.GROOVE, bd=4, activebackground="green4", padx=5,
                  pady=0).place(x=10, y=10, height=70, anchor=tk.NW)
        tk.Label(self.frame, text='Leaderboard', font=(self.font, 30, "bold"), bg="darkolivegreen2",
                 ).place(relx=0.5, y=5, anchor=tk.N)

        # load leaderboard data
        if os.path.exists('Data/player_scores.json'):
            with open('Data/player_scores.json', 'r') as f:
                self.leaderboard_data = json.load(f)
        else:
            self.leaderboard_data = []
        self.leaderboard_data.sort(reverse=True,key=lambda x: x["Score"])

        # filter select
        options = ['All','Level 1','Level 2','Level 3']
        tk.Label(self.frame,text='Filter:',font=(self.font, 20),bg='darkolivegreen2',
                 ).place(x=80,y=125, anchor=tk.W)
        for i,o in enumerate(options):
            col = 'green'
            if o == filter_:
                col = 'green3'
            func = funcer(self.set_menu,menu='Leaderboard_Menu',add_to_prev_menu=False,data=o)
            tk.Button(self.frame, text=o, command=func.func,
                      font=(self.font, 14), bg=col, relief=tk.GROOVE, bd=4,
                      activebackground="green4",
                      ).place(x=180+i*150, y=125, height=50, width=120, anchor=tk.W)


        # Leaderboard table
        rows = []
        self.leaderboard_table_indexes = []
        for i,score in enumerate(self.leaderboard_data):
            if filter_ == 'All' or filter_ == score["Level"]:
                self.leaderboard_table_indexes.append(i)
                rows.append([score["Username"],score["Level"],score['Score'],score["Wave Reached"]])

        titles = [('Username', 350), ('Level', 150), ('Score', 150), ('Wave', 150)]
        self.leaderboard_table = ttk.Treeview(self.frame, columns=[a[0] for a in titles], show='headings', style='Treeview',
                             height=len(rows))

        for i, t in enumerate(titles):
            self.leaderboard_table.column(t[0], width=t[1], anchor='center')
            self.leaderboard_table.heading(t[0], text=t[0])

        for i, row in enumerate(rows):
            self.leaderboard_table.insert('', 'end', iid=i, values=row)

        self.leaderboard_table.place(relx=0.5,x=-150, y=160, anchor=tk.N)

        # frame for displaying info
        self.score_info_display = tk.Frame(self.frame, highlightbackground="darkgreen", highlightthickness=3,
                                           background='darkolivegreen2')
        self.score_info_display.place(relx=0.5,x=280,y=160,width=270,height=450,anchor=tk.NW)


        self.leaderboard_table.bind('<1>',self.detect_selected_leaderboard_entry)

    def make_cheatcode_menu(self, cheat_info):
        self.frame.configure(width=400, height=425, highlightbackground="darkgreen", highlightthickness=3)
        self.frame.lift()
        self.frame.place(relx=0.5, rely=0.5, anchor=tk.CENTER)

        tk.Label(self.frame,text='Cheat Menu', font=(self.font, 20), bg="darkolivegreen2",
                 ).place(relx=0.5,y=5,anchor=tk.N)

        ## Give money button
        tk.Button(self.frame, text='+100\nCoins', command=self.cheat_add_coins,
                  font=(self.font, 14), bg="green", relief=tk.GROOVE, bd=4,
                  activebackground="green4",
                  ).place(x=240, y=90, height=80, width=100, anchor=tk.NW)

        ## Toggles
        titles = ["Immortal", "Infinite Ammo", "Infinite Abilities"]
        self.cheatcode_tkvars = []
        for i,t in enumerate(titles):
            self.cheatcode_tkvars.append(tk.IntVar())
            toggle = tk.Checkbutton(self.frame,text=t, font=(self.font, 15), bg="darkolivegreen2",
                                    variable=self.cheatcode_tkvars[i])
            toggle.place(x=20,y=60+i*50,anchor=tk.NW)
            func = funcer(self.cheat_widget_input,variable=self.cheatcode_tkvars[i],
                          cheat_info=cheat_info,info_type=t.lower())
            toggle.configure(command=func.func)
            if cheat_info[t.lower()]:
                toggle.select()


        ## Sliders
        self.cheat_info = cheat_info
        sliders = [{'title':'Damage\nMultiplier','key':'damage multiplier','from':1,'to':32,'res':1,'func':self.move_slider_damage},
                   {'title':'Spawn Time\nMultiplier','key':'spawn time multiplier','from':0,'to':5,'res':0.1,'func':self.move_slider_spawntime},
                   {'title':'Time\nMultiplier','key':'speed of time','from':0.1,'to':3,'res':0.1,'func':self.move_slider_timespeed}]

        for i,info in enumerate(sliders):
            self.cheatcode_tkvars.append(tk.DoubleVar())
            tk.Label(self.frame,text=info['title'], font=(self.font, 13), bg="darkolivegreen2"
                     ).place(x=60,y=200+i*70,anchor=tk.N)
            slider = tk.Scale(self.frame,from_=info['from'],to=info['to'],orient=tk.HORIZONTAL, font=(self.font, 13),
                              bg="darkolivegreen2",length=240,borderwidth=0,relief=tk.FLAT, resolution=info['res'],
                              variable=self.cheatcode_tkvars[i+3],command=info['func'])
            slider.place(x=120,y=210+i*70,anchor=tk.NW)
            slider.set(self.cheat_info[info["key"]])

    def make_level_select_menu(self):
        tk.Button(self.frame, text='Back', command=self.menu_back,
                  font=(self.font, 20), bg="green", relief=tk.GROOVE, bd=4, activebackground="green4", padx=5,
                  pady=0).place(x=10, y=10, height=70, anchor=tk.NW)
        tk.Label(self.frame, text='Level Select', font=(self.font, 30, "bold"), bg="darkolivegreen2",
                 ).place(relx=0.5, y=5, anchor=tk.N)

        levels = [{'Title': 'Level 1: Easy', 'file': 'Level 1'},
                  {'Title': 'Level 2: Normal', 'file': 'Level 2'},
                  {'Title': 'Level 3: Hard', 'file': 'Level 3'}]

        for i,level in enumerate(levels):
            func = funcer(self.menu_funcs['start_game'],level=level['file'])
            tk.Button(self.frame, text=level['Title'], command=func.func,
                  font=(self.font, 20), bg="green", relief=tk.GROOVE, bd=4, activebackground="green4", padx=5,
                  ).place(relx=0.5, y=100+i*80, height=70, anchor=tk.N)

#### All following functions are functions used by widgets in the menu system

    def cheat_add_coins(self):
        self.menu_funcs["game_object"].shop_data["Coins"]+=100
    def cheat_widget_input(self,variable,cheat_info,info_type):
        cheat_info[info_type] = bool(variable.get())
    def move_slider_damage(self,val):
        self.cheat_info["damage multiplier"] = int(val)
    def move_slider_spawntime(self, val):
        self.cheat_info["spawn time multiplier"] = float(val)
    def move_slider_timespeed(self, val):
        self.cheat_info["speed of time"] = float(val)

    def detect_selected_leaderboard_entry(self,_):
        self.leaderboard_table.after(1,self.detect_selected_leaderboard_entry_delayed)
    def detect_selected_leaderboard_entry_delayed(self):
        if self.leaderboard_table.selection() != ():
            for widget in self.score_info_display.winfo_children():
                widget.destroy()
            index = self.leaderboard_table_indexes[int(self.leaderboard_table.selection()[0])]
            data = self.leaderboard_data[index]

            tk.Button(self.score_info_display, text='Delete', font=(self.font, 17), background='red',
                      activebackground='red4', command=lambda: self.delete_leaderboard_item(index),
                      ).place(relx=0.5, y=390, anchor=tk.N, width=100, height=40)

            tk.Label(self.score_info_display,text=data["Username"],font=(self.font,17), bg="darkolivegreen2"
                     ).place(relx=0.5,y=5,anchor=tk.N)

            data_list = ["Level","Wave Reached","Zombie Kills","Damage Dealt","Damage Taken","Coins Earned","Rounds Fired","Grenades Thrown","Force Pushes Used","Date","Time"]
            for i,d in enumerate(data_list):
                txt = f'{d}: {data[d]}'
                if d in ["Damage Dealt","Damage Taken"]: txt = f'{d}: {int(data[d])}'
                tk.Label(self.score_info_display,text=txt,font=(self.font,13), bg="darkolivegreen2"
                         ).place(x=20,y=50+i*30,anchor=tk.NW)

    def delete_leaderboard_item(self,index):
        del self.leaderboard_data[index]
        with open('Data/player_scores.json', 'w') as f:
            json.dump(self.leaderboard_data,f)
        self.set_menu("Leaderboard_Menu",False,self.leaderboard_filter)

    def load_gamestate(self,table):
        selection = table.selection()
        if selection != ():
            self.menu_funcs['start_game'](table.item(selection)["values"][0])

    def delete_gamestate(self,table):
        selection = table.selection()
        path = "\\Data\\Game Saves\\"
        if selection != ():
            os.remove(os.path.abspath('')+path+table.item(selection)["values"][0]+'.json')
            self.set_menu('Load_Gamestate_Menu',False)

    def save_score(self, game_stats, name_entry):
        game_stats["Username"] = name_entry.get()
        game_stats["Date"] = get_now()[0]
        game_stats["Time"] = get_now()[1]
        data = [game_stats]
        if os.path.isfile('Data/player_scores.json'):
            with open('Data/player_scores.json','r') as f:
                data = json.load(f)
                data.append(game_stats)

        with open('Data/player_scores.json','w') as f:
            json.dump(data,f)

        self.menu_funcs["end_game"]()
        self.set_menu('Leaderboard_Menu',data=game_stats["Level"])

    def save_game(self, game, name_entry):
        game.save_game(name_entry.get())
        self.window.after(1,self.menu_back)

    def save_and_quit(self):
        self.menu_funcs["game_object"].save_game()
        self.menu_funcs['end_game']()

    def set_weapon(self,player_func,new_weapon,shop_data):
        player_func(new_weapon)
        self.set_menu('Shop_Menu',False,shop_data)
    def buy_weapon(self,player_func,new_weapon,shop_data,price):
        if shop_data['Coins']>=price:
            shop_data['Coins']-=price
            shop_data['Owned_Guns'].append(new_weapon)
            self.set_weapon(player_func,new_weapon,shop_data)

    def buy_heal(self,price,shop_data,counter):
        if shop_data['Coins']>=price and shop_data["Player_Object"].health < shop_data["Player_Object"].max_health:
            shop_data['Coins'] -= price
            shop_data["Player_Object"].health = shop_data["Player_Object"].max_health
            self.set_menu('Shop_Menu', False, shop_data)

    def buy_shield(self,price,shop_data,counter):
        if shop_data['Coins'] >= price and shop_data["Player_Object"].shield < shop_data["Player_Object"].max_health:
            shop_data['Coins'] -= price
            shop_data["Player_Object"].shield = shop_data["Player_Object"].max_health
            self.set_menu('Shop_Menu', False, shop_data)

    def buy_grenade(self,price,shop_data,counter):
        if shop_data['Coins'] >= price and shop_data["Temp_Upgrades"]["Grenade"] < counter:
            shop_data['Coins'] -= price
            shop_data["Temp_Upgrades"]["Grenade"] += 1
            self.set_menu('Shop_Menu', False, shop_data)

    def buy_forcepush(self,price,shop_data,counter):
        if shop_data['Coins'] >= price and shop_data["Temp_Upgrades"]["Force Push"] < counter:
            shop_data['Coins'] -= price
            shop_data["Temp_Upgrades"]["Force Push"] += 1
            self.set_menu('Shop_Menu', False, shop_data)

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
            with open('Data/control_map.json','w') as f:
                json.dump(self.control_map,f)
            self.inp.refresh_binding()
            self.set_menu("Settings",False)
            self.listening_remap_action = None

    def reset_keybind(self, action):
        self.control_map[action]["Key"] = self.control_map_defaults[action]["Key"]
        with open('Data/control_map.json', 'w') as f:
            json.dump(self.control_map, f)
        self.set_menu("Settings",False)

    def start_game(self):
        self.set_menu("Game")
        self.menu_funcs['start_game']()


    def window_resize(self,window_width, window_height):
        self.window_width = window_width
        self.window_height = window_height
        if self.active_menu != "Shop_Menu":
            self.set_menu(self.active_menu,False)
