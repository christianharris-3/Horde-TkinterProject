from src.Utiles import ListHitbox, Vec, CircleHitbox
from PIL import Image, ImageTk
import tkinter as tk
import math, random


class Projectile:
    def __init__(self, x, y, angle, speed, team):
        self.team = team
        self.x = x
        self.y = y
        self.angle = angle
        self.vel = Vec(math.cos(angle) * speed, math.sin(angle) * speed)
        self.radius = 0.1
        self.move_drag = 0.9
        self.hits_to_live = 1

        self.col = 'grey'
        self.damage = 1
        self.knockback = 0.1

        self.prev_x = self.x
        self.prev_y = self.y

    def get_hitbox(self):
        steps = 4
        dx = self.prev_x - self.x
        dy = self.prev_y - self.y
        return ListHitbox([(self.x - dx * a / steps, self.y - dy * a / steps, self.radius) for a in range(steps)])

    def draw_image(self, screen, coord_mapper):
        screen.create_oval(*coord_mapper(Vec(self.x - self.radius, self.y - self.radius)),
                           *coord_mapper(Vec(self.x + self.radius, self.y + self.radius)), fill=self.col,
                           tag='game_image')

    def physics(self, delta_time):
        self.prev_x = self.x
        self.prev_y = self.y
        self.vel *= self.move_drag ** delta_time
        self.x += self.vel[0] * delta_time
        self.y += self.vel[1] * delta_time

    def get_dead(self):
        return self.vel.length() < 0.05 or self.hits_to_live <= 0

    def detect_hit(self, entity):
        if self.get_hitbox().Get_Collide(entity.get_hitbox()) and self.team != entity.team and not self.get_dead():
            entity.take_hit(self)
            self.hits_to_live -= 1


class Bullet(Projectile):
    def __init__(self, x, y, angle, speed, team):
        super().__init__(x, y, angle, speed, team)


class SMG_Bullet(Projectile):
    def __init__(self, x, y, angle, speed, team):
        super().__init__(x, y, angle, speed, team)
        self.radius = 0.05
        self.col = '#555555'
        self.damage = 1


class Shotgun_Shell(Projectile):
    def __init__(self, x, y, angle, speed, team):
        super().__init__(x, y, angle + random.gauss(0, 0.2), max(speed + random.gauss(0, 0.15), 0.1), team)
        self.radius = 0.03
        self.col = '#444444'
        self.damage = 1


class LMG_Bullet(Projectile):
    def __init__(self, x, y, angle, speed, team):
        super().__init__(x, y, angle, speed, team)
        self.radius = 0.08
        self.col = '#333333'
        self.damage = 1.5

class KB_Obj:
    def __init__(self,kb,angle,damage):
        self.knockback = kb
        self.angle = angle
        self.damage = damage

class Grenade:
    def __init__(self, x, y, target_x, target_y, team):
        self.x = x
        self.y = y
        self.start_x = x
        self.start_y = y
        self.target_x = target_x
        self.target_y = target_y
        self.team = team
        self.angle = 0
        self.radius = 0.1
        self.t = 0
        self.total_life = 0.5

        self.acceleration = 10
        self.x_vel = (self.target_x-self.start_x)/self.total_life
        self.y_vel = (self.target_y-self.start_y)/self.total_life+self.acceleration/2*self.total_life

        self.damage = 10
        self.range = 4
        self.knockback = 1

        self.grenade_image_base = Image.open('Sprites/Grenade.png').convert("RGBA").resize((18, 18),
                                                                                         resample=Image.Resampling.BOX)

    def physics(self, delta_time):
        self.t += delta_time / 60

        self.x+=self.x_vel*delta_time / 60
        self.y+=self.y_vel*delta_time /60
        self.y_vel+=self.acceleration*delta_time / 60

        # if self.target_x<self.start_x: k = -1
        # else: k = 1
        # const = 1
        # m = self.target_x - self.start_x
        # n = self.target_y - self.start_y
        # c = (const * m)/(2*k)+(n/m)
        #
        # self.x = self.start_x + m * terp
        # self.y = self.start_y + k*(c/m-n/(m**2))*((m * terp)**2)+(n/m-k*(c-n/m))*(m * terp)

        # self.y = self.start_y + (self.target_y - self.start_y) * terp
        self.angle+=0.4

    def get_hitbox(self):
        return CircleHitbox(self.x,self.y,self.radius)


    def draw_image(self, screen, coord_mapper):
        self.image = ImageTk.PhotoImage(self.grenade_image_base.rotate(self.angle))
        screen.create_image(*coord_mapper(Vec(self.x,self.y)),anchor=tk.CENTER,image=self.image)

    def get_dead(self):
        return self.t>self.total_life

    def explode(self,entities):
        for e in entities:
            if e.team != self.team:
                dx = e.x-self.x
                dy = e.y-self.y
                dis = (dx**2+dy**2)**0.5
                if dis<self.range:
                    dmg = self.damage/max(dis,1)
                    kb = self.knockback/max(dis,1)
                    angle = math.atan2(dy,dx)
                    e.take_hit(KB_Obj(kb,angle,dmg))


    def detect_hit(self, _):
        pass