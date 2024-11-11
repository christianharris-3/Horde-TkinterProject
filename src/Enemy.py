from src.Entity import Entity
from PIL import Image, ImageDraw
from src.Utiles import Coords, Vec


class Enemy(Entity):
    def __init__(self, x, y, image_path):
        super().__init__(x, y)
        self.team = 'Enemy'

        self.image_base = Image.open(image_path).resize(
            Coords.world_to_pixel_coords((self.radius * 2, self.radius * 2)).tuple(True), resample=Image.Resampling.BOX)

    def get_image(self):
        img_s = int(3.5*Coords.scale_factor)
        image = Image.new("RGBA", (img_s, img_s), (0, 0, 0, 0))
        enemy_image = self.image_base
        if self.target_move[0] > 0:
            enemy_image = enemy_image.transpose(Image.FLIP_LEFT_RIGHT)
        image.paste(enemy_image,
                    (int(img_s / 2 - self.image_base.width / 2), int(img_s / 2 - self.image_base.height / 2)))

        # Draw health bar
        drawer = ImageDraw.Draw(image)
        drawer.rectangle((img_s / 2 - self.image_base.width * 0.6, img_s / 2 - self.image_base.height * 0.7,
                          img_s / 2 + self.image_base.width * 0.6, img_s / 2 - self.image_base.height * 0.55),
                         fill=(100, 100, 100))
        drawer.rectangle((img_s / 2 - self.image_base.width * 0.6 + 1, img_s / 2 - self.image_base.height * 0.7 + 1,
                          img_s / 2 - self.image_base.width * 0.6 + 1 + (self.image_base.width * 1.2 - 2) * (
                                  self.health / self.max_health), img_s / 2 - self.image_base.height * 0.55 - 1),
                         fill=(200, 0, 0))

        return image, Vec(self.x, self.y)

    def control(self, player):
        self.target_move = Vec(player.x - self.x, player.y - self.y)


class Slow_Zombie(Enemy):
    def __init__(self, x, y):
        self.image_path = 'Sprites/Slow_Zombie.png'
        self.radius = 0.4
        super().__init__(x, y, self.image_path)
        self.max_health = 8
        self.health = self.max_health
        self.radius = 0.4
        self.move_acceleration = 0.005
        self.damage = 2
        self.coin_value = 1

class Fast_Zombie(Enemy):
    def __init__(self, x, y):
        self.image_path = 'Sprites/Fast_Zombie.png'
        self.radius = 0.35
        super().__init__(x, y, self.image_path)
        self.max_health = 4
        self.health = self.max_health
        self.radius = 0.35
        self.move_acceleration = 0.008
        self.damage = 1
        self.knockback_resistance = 0.8
        self.coin_value = 2

class Big_Zombie(Enemy):
    def __init__(self, x, y):
        self.image_path = 'Sprites/Big_Zombie.png'
        self.radius = 0.48
        super().__init__(x, y, self.image_path)
        self.max_health = 16
        self.health = self.max_health
        self.radius = 0.48
        self.move_acceleration = 0.003
        self.damage = 5
        self.knockback_resistance = 0.05
        self.coin_value = 5