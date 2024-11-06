from src.Utiles import CircleHitbox, Vec

class Entity:
    def __init__(self, x, y):
        self.team = 'Neutral'
        self.x = x
        self.y = y
        self.vel = Vec()
        self.angle = 0
        self.radius = 1
        self.move_acceleration = 0.02
        self.move_drag = 0.9
        self.target_move = Vec()
        self.i_frames = 0

        self.max_health = 20
        self.health = self.max_health
        self.knockback_resistance = 0.5

    def get_hitbox(self):
        return CircleHitbox(self.x, self.y, self.radius)

    def physics(self, delta_time):
        self.target_move.normalize()
        self.vel += self.target_move * self.move_acceleration * delta_time
        self.vel *= self.move_drag ** delta_time
        self.x += self.vel[0] * delta_time
        self.y += self.vel[1] * delta_time

        self.i_frames-=delta_time/60

    def entity_collision(self,entities,shake_camera):
        for e in entities:
            if not(e is self):
                if self.get_hitbox().Get_Collide(e.get_hitbox()):
                    self.vel+=Vec(self.x-e.x,self.y-e.y).normalized()/100
                    if self.team == "Enemy" and e.team == "Player":
                        e.take_damage(1)
                        if e.team == "Player":
                            shake_camera()

    def take_hit(self, projectile):
        self.vel += Vec.make_from_angle(projectile.angle,projectile.knockback*self.knockback_resistance)
        self.take_damage(projectile.damage)

    def take_damage(self,damage):
        if self.i_frames<0:
            self.health -= damage
            self.i_frames = 0.3
            self.hurt_frames_counter = 3

    def get_dead(self):
        return self.health <= 0
