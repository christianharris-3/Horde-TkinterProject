from src.Utiles import CircleHitbox, Vec
import math


class Projectile:
    def __init__(self, x, y, angle, speed, team):
        self.team = team
        self.x = x
        self.y = y
        self.angle = angle
        self.vel = Vec(math.cos(angle) * speed, math.sin(angle) * speed)
        self.radius = 0.1
        self.move_drag = 0.9
        self.time_to_live = 100

    def get_hitbox(self):
        return CircleHitbox(self.x, self.y, self.radius)

    def draw_image(self, screen, coord_mapper):
        screen.create_oval(*coord_mapper(Vec(self.x - self.radius, self.y - self.radius)),
                           *coord_mapper(Vec(self.x + self.radius, self.y + self.radius)), fill=self.col,
                           tag='game_image')

    def physics(self, delta_time):
        self.vel *= self.move_drag ** delta_time
        self.x += self.vel[0] * delta_time
        self.y += self.vel[1] * delta_time

    def get_dead(self):
        return self.vel.length() < 0.05


class Bullet(Projectile):
    def __init__(self, x, y, angle, speed, team):
        super().__init__(x, y, angle, speed, team)
        self.col = 'grey'
