import random, math
from src.Utiles import CircleHitbox, Vec, RectHitbox
from src.Particles import Blood_Particle, Blood_Splat
from src.Projectiles import KB_Obj


class Entity:
    def __init__(self, x, y):
        self.team = 'Neutral'
        self.x = x
        self.y = y
        self.vel = Vec()
        self.angle = 0
        self.move_drag = 0.9
        self.target_move = Vec()
        self.i_frames = -1
        self.damage_taken = 0

        self.knockback_resistance = 0.5

        self.stunned = False
        self.stun_timer = 0
        self.passive_ai_wait_timer = 0
        self.passive_ai_move_timer = 0

    def get_hitbox(self,circle=False):
        if circle:
            return CircleHitbox(self.x, self.y, self.radius)
        else:
            f = 1.4
            return RectHitbox(self.x-self.radius/2*f,self.y-self.radius/2*f,self.radius*f,self.radius*f)

    def physics(self, delta_time, tilemap_collision_hash):
        self.target_move.normalize()
        if not self.stunned:
            self.vel += self.target_move * self.move_acceleration * delta_time
        self.vel *= self.move_drag ** delta_time

        self.x += self.vel[0] * delta_time
        if self.tilemap_collision(tilemap_collision_hash):
            self.x -= self.vel[0] * delta_time

        self.y += self.vel[1] * delta_time
        if self.tilemap_collision(tilemap_collision_hash):
            self.y -= self.vel[1] * delta_time

        self.stun_timer -= delta_time / 60
        if self.stun_timer<0:
            self.stunned = False

        self.passive_ai_move_timer -= delta_time / 60
        self.passive_ai_wait_timer -= delta_time / 60

    def entity_collision(self, collision_hash, shake_camera):
        particles = []
        ownhitbox = self.get_hitbox()
        for code in ownhitbox.colcodes:
            if code in collision_hash:
                for e in collision_hash[code]:
                    if not (e is self) and ownhitbox.Get_Collide(e.get_hitbox()):
                        if self.team == "Enemy" and e.team == "Player":
                            if not(e.cheat_info["immortal"]):
                                # Deal Damage to Player
                                e.vel -= Vec(self.x - e.x, self.y - e.y).normalized() / 100
                                dmg = self.damage
                                kb = 0
                                angle = math.atan2(e.y-self.y, e.x-self.x)
                                particles += e.take_hit(KB_Obj(kb, angle, dmg))
                                shake_camera(self.damage/100)
                        else:
                            e.vel -= Vec(self.x - e.x, self.y - e.y).normalized() / 100
        return particles

    def tilemap_collision(self, collision_hash):
        ownhitbox = self.get_hitbox()
        self.can_open_shop = False
        for code in ownhitbox.colcodes:
            if code in collision_hash:
                for t in collision_hash[code]:
                    if ownhitbox.Get_Collide(t.get_hitbox()):
                        if t.tile_type == 'Shop':
                            if self.team == "Player":
                                self.can_open_shop = True
                                self.closest_shop = t
                        else:
                            return True
        return False

    def take_hit(self, projectile):
        particles = []
        if self.i_frames<0:
            if projectile.stuns:
                self.stunned = True
                self.stun_timer = 2
            self.vel += Vec.make_from_angle(projectile.angle, projectile.knockback * self.knockback_resistance)
            self.take_damage(projectile.damage)
            particle_num = round(min(projectile.damage,self.max_health)*2)
            if self.get_dead():
                particle_num*=4
                particles += [Blood_Splat(self.x+(random.random()*1.4-0.7)*self.radius,
                                          self.y+(random.random()*1.4-0.7)*self.radius,
                                          random.gauss(projectile.angle,0.2), max(random.gauss(0,0.1),0.01),
                                          random.random()/10+0.01)
                              for _ in range(round(self.radius*10))]
            particles += [Blood_Particle(random.gauss(self.x,self.radius/3),random.gauss(self.y,self.radius/3),
                                   random.gauss(projectile.angle,0.3),
                                   max(random.gauss(projectile.knockback*self.knockback_resistance,0.4),0.1),
                                   random.random()/15+0.01) for a in range(particle_num)]
        return particles

    def take_damage(self, damage):
        self.health -= damage
        self.damage_taken += damage

    def get_dead(self):
        return self.health <= 0
