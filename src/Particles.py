from src.Utiles import Vec, CircleHitbox, Coords
from PIL import Image, ImageTk
import tkinter as tk
import math, random


class Particle:
    def __init__(self, x, y, angle, speed):
        self.x = x
        self.y = y
        self.angle = angle
        self.vel = Vec.make_from_angle(angle) * speed
        self.radius = 0.1
        self.move_drag = 0.9

        self.shape = 'Circle'
        self.col = 'grey'
        self.outline_col = 'black'

        self.prev_x = self.x
        self.prev_y = self.y

    def draw_image(self, screen, coord_mapper):
        if self.shape == 'Circle':
            screen.create_oval(*coord_mapper(Vec(self.x - self.radius, self.y - self.radius)),
                               *coord_mapper(Vec(self.x + self.radius, self.y + self.radius)),
                               fill=self.col, outline=self.outline_col, tag='game_image')
        elif self.shape == 'Line':
            screen.create_line(coord_mapper(Vec(self.x, self.y)), coord_mapper(Vec(self.prev_x, self.prev_y)),
                               fill=self.col, tag='game_image', capstyle=tk.ROUND,
                               width=Coords.world_to_pixel(self.radius))

    def physics(self, delta_time):
        self.prev_x = self.x
        self.prev_y = self.y
        self.vel *= self.move_drag ** delta_time
        self.x += self.vel[0] * delta_time
        self.y += self.vel[1] * delta_time

    def get_dead(self):
        return self.vel.length() < 0.01

class Blood_Particle(Particle):
    def __init__(self,x,y,angle,speed, size):
        super().__init__(x, y, angle, speed)
        self.radius = size
        self.col = "red"
        self.outline_col = "red3"

class Bullet_Hit_Particle(Particle):
    def __init__(self,x,y,angle,speed):
        super().__init__(x, y, angle, speed)
        self.radius = 0.04
        self.shape = 'Line'