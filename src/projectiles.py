import math, random
import tkinter as tk
from src.utiles import ListHitbox, Vec, CircleHitbox, resourcepath
from src.particles import Particle, Bullet_Hit_Particle, Explosion, Grenade_Fragment
from PIL import Image, ImageTk


class Projectile(Particle):
    """
    Projectile object inherites from Particle in src/particle.py
    it manages:
    - collision with an entities
    """
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
        damage = 0
        if self.get_hitbox().Get_Collide(entity.get_hitbox()) and self.team != entity.team and not self.get_dead():
            particles += entity.take_hit(self)
            damage += self.damage
            self.hits_to_live -= 1
            for _ in range(round(min(self.damage * 2, entity.max_health))):
                particles.append(Bullet_Hit_Particle(self.x,self.y,
                                                     random.gauss(self.angle,0.2),
                                        max(random.gauss(self.vel.length(),0.2),0.1)))

        return particles, damage

### All following clases are all the different projectiles, each storing different:
###  - radii
###  - damage
###  - colour

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
    """
    Damage can only be dealt through projectiles, so this class is created to act as a projectile
    it deals damage for grenades and for melee hits by zombies
    """
    def __init__(self, kb, angle, damage, stuns=False):
        self.knockback = kb
        self.angle = angle
        self.damage = damage
        self.stuns = stuns


class Grenade:
    """
    Grenade class uses polymorphism to act as a projectile
    The grenade physics works so that when the projectile finishes it is exactly where the player clicked
    it cant follow the same physics as normal projectiles as this would not work with them.
    This class manages:
    - grenade physics
    - drawing
    - exploding: creating particle effects and dealing damage
    """
    def __init__(self, x, y, target_x, target_y, team):
        self.x = x
        self.y = y
        self.team = team
        self.angle = 0
        self.radius = 0.1
        self.time_alive = 0
        self.time_kill_cutoff = 0.15 * ((target_x - x) ** 2 + (target_y - y) ** 2) ** 0.5

        self.acceleration = 20
        self.vel = Vec((target_x - x) / self.time_kill_cutoff,
                       (target_y - y) / self.time_kill_cutoff - (self.acceleration / 2 * self.time_kill_cutoff))

        self.damage = 10
        self.range = 3
        self.knockback = 1

        self.grenade_image_base = Image.open(resourcepath('Sprites/Grenade.png')).convert("RGBA").resize((18, 18),
                                                                                           resample=Image.Resampling.BOX)

    def physics(self, delta_time):
        self.time_alive += delta_time / 60

        self.x += self.vel.x * delta_time / 60
        self.y += self.vel.y * delta_time / 60
        self.vel.y += self.acceleration * delta_time / 60

        self.angle += 0.4

    def get_hitbox(self):
        return CircleHitbox(self.x, self.y, self.radius)

    def draw_image(self, screen, coord_mapper):
        self.image = ImageTk.PhotoImage(self.grenade_image_base.rotate(self.angle))
        screen.create_image(*coord_mapper(Vec(self.x, self.y)), anchor=tk.CENTER, image=self.image)

    def get_dead(self,_):
        return self.time_alive > self.time_kill_cutoff

    def explode(self, entities):
        particles = [Explosion(self.x,self.y,1)]
        particles += [Grenade_Fragment(self.x,self.y,random.random()*math.pi*2,max(random.gauss(0.5,0.1),0.1)) for _ in range(25)]
        damage = 0
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
                    damage+=dmg
        return particles, damage

    def detect_hit(self, _):
        return [], 0
