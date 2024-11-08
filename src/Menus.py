import tkinter as tk
from PIL import Image, ImageTk

class Menus:
    def __init__(self,window, window_width, window_height, start_game_func):
        self.window = window
        self.window_width = window_width
        self.window_height = window_height
        self.start_game_func = start_game_func

        self.frame = tk.Frame(self.window)
        self.active_menu = ''
        self.set_menu('Start_Screen')


    def make_start_screen(self):
        image = Image.open('Sprites/Title.png').resize((300,150), resample=Image.Resampling.BOX)
        self.image = ImageTk.PhotoImage(image)
        title = tk.Canvas(self.frame,width=300,height=150,bg="darkolivegreen2",bd=0,highlightthickness=0)
        title.create_image(0,0,image=self.image,anchor=tk.NW)
        title.place(relx=0.5,rely=0.5,y=-100,anchor=tk.S)

        start_game = tk.Button(self.frame,text='Start', command=self.start_game,
                               font=('calibri', 20), bg="green",relief=tk.GROOVE,bd=4,activebackground="green4",padx=20,pady=0)
        start_game.place(relx=0.5,rely=0.5,y=-40,anchor=tk.CENTER)

        other = tk.Button(self.frame, text='Hi',
                          font=('calibri', 20), bg="green",relief=tk.GROOVE,bd=4,activebackground="green4",padx=20,pady=0)
        other.place(relx=0.5, rely=0.5,y=30, anchor=tk.CENTER)

    def set_menu(self,menu):
        self.frame.destroy()
        self.active_menu = menu
        if self.active_menu != "Game":
            self.frame = tk.Frame(self.window, width=self.window_width, height=self.window_height, bg="darkolivegreen2")
            self.frame.pack()
            if self.active_menu == "Start_Screen":
                self.make_start_screen()

    def start_game(self):
        self.set_menu("Game")
        self.start_game_func()