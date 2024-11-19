import random
import tkinter as tk
from src.Utiles import Vec, CircleHitbox, Coords


class Particle:
    def __init__(self, x, y, angle, speed):
        self.team = "Neutral"
        self.x = x
        self.y = y
        self.start_x = x
        self.start_y = y
        self.angle = angle
        self.vel = Vec.make_from_angle(angle) * speed
        self.radius = 0.1
        self.move_drag = 0.9
        self.time_alive = 0
        self.velocity_kill_cutoff = 0.01
        self.time_kill_cutoff = 10


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
        elif self.shape == 'Ring_Expand':
            ring_rad = abs(self.x-self.start_x)
            screen.create_oval(*coord_mapper(Vec(self.start_x - ring_rad, self.start_y - ring_rad)),
                               *coord_mapper(Vec(self.start_x + ring_rad, self.start_y + ring_rad)),
                               outline=self.outline_col, width=int(self.vel.length()*self.radius) ,tag='game_image')

    def physics(self, delta_time):
        self.prev_x = self.x
        self.prev_y = self.y
        self.vel *= self.move_drag ** delta_time
        self.x += self.vel[0] * delta_time
        self.y += self.vel[1] * delta_time

        self.time_alive += delta_time/60

    def get_dead(self):
        return self.vel.length() < self.velocity_kill_cutoff or self.time_alive > self.time_kill_cutoff

class Blood_Particle(Particle):
    def __init__(self,x,y,angle,speed, size):
        super().__init__(x, y, angle, speed)
        self.radius = size
        self.col = "red"
        self.outline_col = "red3"

class Blood_Splat(Particle):
    def __init__(self,x,y,angle,speed, size):
        super().__init__(x, y, angle, speed)
        self.radius = size
        self.col = "red"
        self.outline_col = "red3"
        self.velocity_kill_cutoff = -1
        self.time_kill_cutoff = random.random()*2+1

class Bullet_Hit_Particle(Particle):
    def __init__(self,x,y,angle,speed):
        super().__init__(x, y, angle, speed)
        self.radius = 0.04
        self.shape = 'Line'

class Explosion(Particle):
    def __init__(self,x,y,speed):
        super().__init__(x, y, 0, speed)
        self.shape = 'Ring_Expand'
        self.radius = 40
        self.move_drag=0.78

class Grenade_Fragment(Particle):
    def __init__(self,x,y,angle,speed):
        super().__init__(x, y, angle, speed)
        self.shape = 'Circle'
        self.col = '#585858'
        self.outline_col = '#444'
        self.radius = 0.05
        self.velocity_kill_cutoff = 0.08

class Force_Push_Effect(Particle):
    def __init__(self,x,y,speed):
        super().__init__(x, y, 0, speed)
        self.shape = 'Ring_Expand'
        self.radius = 40
        self.outline_col = '#d6bad6'
        self.move_drag=0.78