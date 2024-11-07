import tkinter as tk
from PIL import ImageTk
from src.Player import Player
from src.Enemy import Enemy
from src.Utiles import Coords, Vec
import random, math


class Game:
    def __init__(self, window, inp, screen_width, screen_height):
        self.window = window
        self.inp = inp
        self.screen_width = screen_width
        self.screen_height = screen_height

        self.screen = tk.Canvas(self.window, width=self.screen_width, height=self.screen_height, bg="green")
        self.screen.place(x=0,y=0)

        self.control_map = {'Left': {'Key': 'a', 'continuous': True},
                            'Right': {'Key': 'd', 'continuous': True},
                            'Up': {'Key': 'w', 'continuous': True},
                            'Down': {'Key': 's', 'continuous': True},
                            'Shoot': {'Key': 1, 'continuous': False}}

        self.player = Player(0, 0, self.control_map, self.screen_width, self.screen_height)
        self.enemies = [Enemy(5, a * 2) for a in range(5)]
        self.projectiles = []

        self.player_dead = False

        self.camera_pos = Vec()
        self.camera_target_pos = Vec()
        self.camera_vel = Vec()
        self.camera_acceleration = 0.03
        self.camera_shake_timer = 0
        self.camera_shake_intensity = 0.1
        self.camera_shake_offset = Vec()

        self.player_img = 0
        self.enemy_img = 0
        self.world_mpos = Vec()

        self.debug_info = False
        self.fps = 0
        self.window.bind('<F3>', self.toggle_debug)

    def gameloop(self, delta_time):
        self.fps = 60 / delta_time
        self.get_world_mpos()
        self.generate_enemies()

        # Player Physics and Input control
        self.projectiles += self.player.control(self.inp, self.world_mpos)
        self.player.physics(delta_time)
        if self.player.get_dead():
            self.player_dead = True
            return True

        # Enemy Physics, AI control and deletion
        rem = []
        for enem in self.enemies:
            enem.control(self.player)
            enem.physics(delta_time)
            if enem.get_dead():
                rem.append(enem)
        for r in rem:
            self.enemies.remove(r)

        # Player + Entity Collision
        entities = self.enemies + [self.player]
        for entity in entities:
            entity.entity_collision(entities, self.shake_camera)

        # Projectile Physics and deletion
        rem = []
        for proj in self.projectiles:
            proj.physics(delta_time)
            for entity in entities:
                proj.detect_hit(entity)
            if proj.get_dead():
                rem.append(proj)
        for r in rem:
            self.projectiles.remove(r)

        # Camera movement
        self.camera_physics(delta_time)

        return False

    def render_frame(self):
        self.screen.delete('game_image')

        # Player Rendering
        player_img, player_pos = self.player.get_image()
        self.player_img = ImageTk.PhotoImage(player_img)
        self.screen.create_image(self.get_render_coords(player_pos), image=self.player_img, tag='game_image')

        # Enemy Rendering
        self.enemy_images = []
        for enemy in self.enemies:
            enemy_img, enemy_pos = enemy.get_image()
            self.enemy_images.append(ImageTk.PhotoImage(enemy_img))
            self.screen.create_image(self.get_render_coords(enemy_pos), image=self.enemy_images[-1], tag='game_image')

        for proj in self.projectiles:
            proj.draw_image(self.screen, self.get_render_coords)

        # UI Rendering
        self.player.draw_ui(self.screen)

        if self.debug_info:
            self.screen.create_text(10, 100, text=f'FPS: {int(self.fps)}\nKeys Pressed: {self.inp.kprs}', anchor=tk.NW,
                                    tag='game_image')

    def generate_enemies(self):
        if random.random() < 0.01:
            angle = math.pi * (random.random() * 2 - 1)
            dis = 10
            self.enemies.append(Enemy(self.player.x + math.cos(angle) * dis,
                                      self.player.y + math.sin(angle) * dis))

    def shake_camera(self):
        self.camera_shake_timer = 0.1

    def camera_physics(self, delta_time):
        self.camera_target_pos = Vec(self.player.x, self.player.y)

        self.camera_vel += (self.camera_target_pos - self.camera_pos) * delta_time * self.camera_acceleration
        self.camera_pos += self.camera_vel
        self.camera_vel *= 0.8

        self.camera_shake_timer -= delta_time / 60
        if self.camera_shake_timer > 0:
            self.camera_shake_offset = Vec(random.gauss(0, self.camera_shake_intensity),
                                           random.gauss(0, self.camera_shake_intensity))

    def get_render_coords(self, pos):
        pixel_pos = Coords.world_to_pixel_coords(pos - self.camera_pos - self.camera_shake_offset)
        pixel_pos += Vec(self.screen_width, self.screen_height) / 2
        return pixel_pos.tuple()

    def get_world_mpos(self):
        self.world_mpos = self.inp.get_mpos()
        self.world_mpos -= Vec(self.screen_width, self.screen_height) / 2
        self.world_mpos = Coords.pixel_to_world_coords(self.world_mpos) + self.camera_pos + self.camera_shake_offset

    def window_resize(self, nwidth, nheight):
        self.screen_width = nwidth
        self.screen_height = nheight
        self.screen.configure(width=self.screen_width, height=self.screen_height)
        self.player.screen_resize(self.screen_width, self.screen_height)

    def toggle_debug(self, event):
        self.debug_info = not self.debug_info
