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

    def get_hitbox(self):
        return CircleHitbox(self.x, self.y, self.radius)

    def physics(self,delta_time):
        self.vel+=self.target_move*self.move_acceleration*delta_time
        self.vel*=self.move_drag**delta_time
        self.x+=self.vel[0]*delta_time
        self.y+=self.vel[1]*delta_time