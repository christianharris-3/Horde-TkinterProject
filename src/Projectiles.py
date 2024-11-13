from src.Utiles import ListHitbox, Vec, CircleHitbox
from src.Particles import Particle, Bullet_Hit_Particle, Explosion, Grenade_Fragment
from PIL import Image, ImageTk
import tkinter as tk
import math, random


class Projectile(Particle):
    def __init__(self, x, y, angle, speed, team):
        super().__init__(x, y, angle, speed)
        self.team = team
        self.hits_to_live = 1

        self.damage = 1
        self.knockback = 0.1
        self.stuns = False

    def get_hitbox(self):
        steps = 4
        dx = self.prev_x - self.x
        dy = self.prev_y - self.y
        return ListHitbox([(self.x - dx * a / steps, self.y - dy * a / steps, self.radius) for a in range(steps)])

    def get_dead(self, collision_hash=None):
        if collision_hash:
            ownhitbox = CircleHitbox(self.x,self.y,self.radius)
            for code in ownhitbox.colcodes:
                if code in collision_hash:
                    for t in collision_hash[code]:
                        if ownhitbox.Get_Collide(t.get_hitbox()) and t.tile_type != 'Shop':
                            return True
        return self.vel.length() < 0.05 or self.hits_to_live <= 0

    def detect_hit(self, entity):
        particles = []
        if self.get_hitbox().Get_Collide(entity.get_hitbox()) and self.team != entity.team and not self.get_dead():
            particles += entity.take_hit(self)
            self.hits_to_live -= 1
            particles += [Bullet_Hit_Particle(self.x,self.y,random.gauss(self.angle,0.2),
                                        max(random.gauss(self.vel.length(),0.2),0.1)) for _ in range(round(self.damage*2))]

        return particles


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
        super().__init__(x, y, angle, speed, team)
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
    def __init__(self, kb, angle, damage, stuns=False):
        self.knockback = kb
        self.angle = angle
        self.damage = damage
        self.stuns = stuns


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
        self.total_life = 0.15 * ((self.target_x - self.start_x) ** 2 + (self.target_y - self.start_y) ** 2) ** 0.5

        self.acceleration = 20
        self.x_vel = (self.target_x - self.start_x) / self.total_life
        self.y_vel = (self.target_y - self.start_y) / self.total_life - (self.acceleration / 2 * self.total_life)

        self.damage = 10
        self.range = 3
        self.knockback = 1

        self.grenade_image_base = Image.open('Sprites/Grenade.png').convert("RGBA").resize((18, 18),
                                                                                           resample=Image.Resampling.BOX)

    def physics(self, delta_time):
        self.t += delta_time / 60

        self.x += self.x_vel * delta_time / 60
        self.y += self.y_vel * delta_time / 60
        self.y_vel += self.acceleration * delta_time / 60

        self.angle += 0.4

    def get_hitbox(self):
        return CircleHitbox(self.x, self.y, self.radius)

    def draw_image(self, screen, coord_mapper):
        self.image = ImageTk.PhotoImage(self.grenade_image_base.rotate(self.angle))
        screen.create_image(*coord_mapper(Vec(self.x, self.y)), anchor=tk.CENTER, image=self.image)

    def get_dead(self,_):
        return self.t > self.total_life

    def explode(self, entities):
        particles = [Explosion(self.x,self.y,1)]
        particles += [Grenade_Fragment(self.x,self.y,random.random()*math.pi*2,max(random.gauss(0.5,0.1),0.1)) for _ in range(25)]
        for e in entities:
            if e.team != self.team:
                dx = e.x - self.x
                dy = e.y - self.y
                dis = (dx ** 2 + dy ** 2) ** 0.5
                if dis < self.range:
                    dmg = self.damage / max(dis, 1)
                    kb = self.knockback / max(dis, 1)
                    angle = math.atan2(dy, dx)
                    particles += e.take_hit(KB_Obj(kb, angle, dmg))
        return particles

    def detect_hit(self, _):
        return []
