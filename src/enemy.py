import random
import math
from PIL import Image, ImageDraw
from src.entity import Entity
from src.utiles import Coords, Vec, resourcepath


class Enemy(Entity):
    """
    Enemy object inherites from Entity class in src/entity.py, it manages
     - enemy rendering, sprite and health bar
     - enemy ai
    """
    def __init__(self, x, y, zombie_type):
        super().__init__(x, y)
        self.team = 'Enemy'
        self.facing_left = True
        self.image_path = 'Sprites\\'+zombie_type+'.png'
        self.image_base = Image.open(resourcepath(self.image_path)).resize(
            Coords.world_to_pixel_coords((self.radius * 2, self.radius * 2)).tuple(True),
            resample=Image.Resampling.BOX)

    def get_image(self):
        img_s = int(3.5*Coords.scale_factor)
        image = Image.new("RGBA", (img_s, img_s), (0, 0, 0, 0))

        # Draw enemy Sprite
        enemy_image = self.image_base
        if self.facing_left:
            enemy_image = enemy_image.transpose(Image.FLIP_LEFT_RIGHT)
        if self.stunned and self.stun_timer>1:
            angle = ((self.stun_timer-1)**3)*360
            if self.facing_left:
                angle = 360-angle
            enemy_image = enemy_image.rotate(angle)
        image.paste(enemy_image,
                    (int(img_s / 2 - self.image_base.width / 2),
                     int(img_s / 2 - self.image_base.height / 2)))

        # Draw health bar
        drawer = ImageDraw.Draw(image)
        drawer.rectangle((img_s / 2 - self.image_base.width * 0.6,
                          img_s / 2 - self.image_base.height * 0.7,
                          img_s / 2 + self.image_base.width * 0.6,
                          img_s / 2 - self.image_base.height * 0.55),
                         fill=(100, 100, 100))
        health_terp = self.health / self.max_health
        if health_terp>0:
            drawer.rectangle((img_s / 2 - self.image_base.width * 0.6 + 1,
                              img_s / 2 - self.image_base.height * 0.7 + 1,
                            img_s / 2 - self.image_base.width * 0.6 + 1 + (
                                      self.image_base.width * 1.2 - 2) * (
                                    health_terp), img_s / 2 - self.image_base.height * 0.55 - 1),
                            fill=(200, 0, 0))

        return image, Vec(self.x, self.y)

    def control(self, player):
        if not player.get_dead():
            self.target_move = Vec(player.x - self.x, player.y - self.y)
            self.facing_left = self.target_move[0] > 0
        else:
            if self.passive_ai_wait_timer<0:
                self.target_move = Vec.make_from_angle(random.random()*math.pi*2)
                self.facing_left = self.target_move[0] > 0
                self.passive_ai_move_timer = random.random()+0.5
                self.passive_ai_wait_timer = 1000
            if self.passive_ai_move_timer<0:
                self.target_move = Vec()
                self.passive_ai_move_timer = 1000
                self.passive_ai_wait_timer = random.random()*4+0.5

    def apply_difficulty(self,difficulty_data):
        self.max_health *= difficulty_data["Zombie_Health"]
        self.health = self.max_health
        self.move_acceleration *= difficulty_data["Zombie_Speed"]
        self.damage *= difficulty_data["Zombie_Damage"]

### All following clases are all the different enemies, each storing different:
###  - radii
###  - damage
###  - max health
###  - move speed
###  - coin value
###  - knockback resistance
###  - Image file paths

class SlowZombie(Enemy):
    def __init__(self, x, y, difficulty_data):
        self.zombie_type = 'Slow_Zombie'
        self.radius = 0.4
        super().__init__(x, y, self.zombie_type)
        self.max_health = 5
        self.health = self.max_health
        self.radius = 0.4
        self.move_acceleration = 0.005
        self.damage = 2
        self.coin_value = 1
        self.apply_difficulty(difficulty_data)

class FastZombie(Enemy):
    def __init__(self, x, y, difficulty_data):
        self.zombie_type = 'Fast_Zombie'
        self.radius = 0.35
        super().__init__(x, y, self.zombie_type)
        self.max_health = 4
        self.health = self.max_health
        self.radius = 0.35
        self.move_acceleration = 0.008
        self.damage = 1
        self.knockback_resistance = 0.8
        self.coin_value = 2
        self.apply_difficulty(difficulty_data)

class BigZombie(Enemy):
    def __init__(self, x, y, difficulty_data):
        self.zombie_type = 'Big_Zombie'
        self.radius = 0.48
        super().__init__(x, y, self.zombie_type)
        self.max_health = 16
        self.health = self.max_health
        self.radius = 0.48
        self.move_acceleration = 0.003
        self.damage = 5
        self.knockback_resistance = 0.05
        self.coin_value = 3
        self.apply_difficulty(difficulty_data)

class DemonZombie(Enemy):
    def __init__(self, x, y, difficulty_data):
        self.zombie_type = 'Demon_Zombie'
        self.radius = 0.3
        super().__init__(x, y, self.zombie_type)
        self.max_health = 3
        self.health = self.max_health
        self.radius = 0.3
        self.move_acceleration = 0.011
        self.damage = 8
        self.knockback_resistance = 0.5
        self.coin_value = 3
        self.apply_difficulty(difficulty_data)

class ChonkZombie(Enemy):
    def __init__(self, x, y, difficulty_data):
        self.zombie_type = 'Chonk_Zombie'
        self.radius = 0.6
        super().__init__(x, y, self.zombie_type)
        self.max_health = 32
        self.health = self.max_health
        self.radius = 0.6
        self.move_acceleration = 0.0055
        self.damage = 10
        self.knockback_resistance = 0.001
        self.coin_value = 8
        self.apply_difficulty(difficulty_data)
