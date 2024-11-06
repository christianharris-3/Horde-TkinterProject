import tkinter as tk
from PIL import ImageTk
from src.Player import Player
from src.Enemy import Enemy
from src.Utiles import Coords, Vec

class Game:
    def __init__(self,window,inp,screen_width,screen_height):
        self.window = window
        self.inp = inp
        self.screen_width = screen_width
        self.screen_height = screen_height

        self.screen = tk.Canvas(self.window, width=self.screen_width, height=self.screen_height, bg="green")
        self.screen.pack()

        self.control_map = {'Left':{'Key':'a','continuous':True},
                            'Right':{'Key':'d','continuous':True},
                            'Up':{'Key':'w','continuous':True},
                            'Down':{'Key':'s','continuous':True},
                            'Shoot':{'Key':1,'continuous':False}}

        self.player = Player(0,0,self.control_map)
        self.enemies = [Enemy(5,0)]
        self.projectiles = []
        self.camera_pos = Vec()

        self.player_img=0
        self.enemy_img = 0
        self.world_mpos = Vec()

    def gameloop(self,delta_time):
        self.get_world_mpos()
        self.projectiles += self.player.control(self.inp,self.world_mpos)
        self.player.physics(delta_time)

        # Handle Projectile Physics and deletion
        rem = []
        for proj in self.projectiles:
            proj.physics(delta_time)
            if proj.get_dead():
                rem.append(proj)
        for r in rem:
            self.projectiles.remove(r)

    def render_frame(self):
        self.screen.delete('game_image')

        # Player Rendering
        player_img,player_pos = self.player.get_image()
        self.player_img = ImageTk.PhotoImage(player_img)
        self.screen.create_image(self.get_render_coords(player_pos),image=self.player_img,tag='game_image')

        # Enemy Rendering
        for enemy in self.enemies:
            enemy_img, enemy_pos = enemy.get_image()
            self.enemy_img = ImageTk.PhotoImage(enemy_img)
            self.screen.create_image(self.get_render_coords(enemy_pos), image=self.enemy_img, tag='game_image')

        for proj in self.projectiles:
            proj.draw_image(self.screen,self.get_render_coords)

    def get_render_coords(self,pos):
        pixel_pos = Coords.world_to_pixel_coords(pos)
        pixel_pos-=self.camera_pos
        pixel_pos+=Vec(self.screen_width,self.screen_height)/2
        return pixel_pos.tuple()
    def get_world_mpos(self):
        self.world_mpos = self.inp.get_mpos()
        self.world_mpos-=Vec(self.screen_width,self.screen_height)/2
        self.world_mpos+=self.camera_pos
        self.world_mpos = Coords.pixel_to_world_coords(self.world_mpos)

    def window_resize(self,nwidth,nheight):
        self.screen_width = nwidth
        self.screen_height = nheight
        self.screen.configure(width=self.screen_width,height=self.screen_height)