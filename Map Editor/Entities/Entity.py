from Entities.Utiles import CircleHitbox, Vec
import pygame

class Entity:
    def __init__(self, x, y):
        self.team = 'Neutral'
        self.x = x
        self.y = y
        self.vel = Vec()
        self.angle = 0
        self.move_drag = 0.9
        self.target_move = Vec()

        self.i_frames = 0
        self.auto_fire_cooldown = 0
        self.reload_timer = 0

        self.knockback_resistance = 0.5
        self.PYGAME_IMAGE = pygame.image.load("Sprites/Player.png")
    def render_surf(self):
        return self.PYGAME_IMAGE
    def render_hud(self,_):
        pass

    def get_hitbox(self):
        return CircleHitbox(self.x, self.y, self.radius)

    def physics(self, delta_time, tilemap_collision_hash):
        self.target_move.normalize()
        self.vel += self.target_move * self.move_acceleration * delta_time
        self.vel *= self.move_drag ** delta_time

        self.x += self.vel[0] * delta_time
        if self.tilemap_collision(tilemap_collision_hash):
            self.x -= self.vel[0] * delta_time

        self.y += self.vel[1] * delta_time
        if self.tilemap_collision(tilemap_collision_hash):
            self.y -= self.vel[1] * delta_time

        self.i_frames -= delta_time / 60
        self.auto_fire_cooldown -= delta_time / 60
        self.reload_timer -= delta_time / 60

    def entity_collision(self, collision_hash, shake_camera):
        ownhitbox = self.get_hitbox()
        for code in ownhitbox.colcodes:
            if code in collision_hash:
                for e in collision_hash[code]:
                    if not (e is self) and ownhitbox.Get_Collide(e.get_hitbox()):
                        self.vel += Vec(self.x - e.x, self.y - e.y).normalized() / 100
                        if self.team == "Enemy" and e.team == "Player":
                            e.take_damage(self.damage)
                            if e.team == "Player":
                                shake_camera(self.damage/100)
    def tilemap_collision(self, collision_hash):
        ownhitbox = self.get_hitbox()
        for code in ownhitbox.colcodes:
            if code in collision_hash:
                for t in collision_hash[code]:
                    if ownhitbox.Get_Collide(t.get_hitbox()):
                        return True
        return False

    def take_hit(self, projectile):
        self.vel += Vec.make_from_angle(projectile.angle, projectile.knockback * self.knockback_resistance)
        self.take_damage(projectile.damage)

    def take_damage(self, damage):
        if self.i_frames < 0:
            self.health -= damage
            if self.team == "Player": self.i_frames = 0.3
            self.hurt_frames_counter = 3

    def get_dead(self):
        return self.health <= 0
