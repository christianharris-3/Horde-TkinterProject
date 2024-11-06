from src.Entity import Entity
from PIL import Image, ImageDraw
from src.Utiles import Coords, Vec


class Enemy(Entity):
    def __init__(self, x, y):
        super().__init__(x, y)
        self.team = 'Enemy'

        self.max_health = 5
        self.health = self.max_health
        self.radius = 0.8
        self.move_acceleration = 0.005

        self.image_base = Image.open('Sprites/Enemy.png').resize(
            Coords.world_to_pixel_coords((self.radius * 2, self.radius * 2)).tuple(True), resample=Image.Resampling.BOX)

    def get_image(self):
        img_s = 140
        image = Image.new("RGBA", (img_s, img_s), (0, 0, 0, 0))
        enemy_image = self.image_base
        if self.target_move[0]>0:
            enemy_image = enemy_image.transpose(Image.FLIP_LEFT_RIGHT)
        image.paste(enemy_image,
                    (int(img_s / 2 - self.image_base.width / 2), int(img_s / 2 - self.image_base.height / 2)))

        # Draw health bar
        drawer = ImageDraw.Draw(image)
        drawer.rectangle((img_s / 2 - self.image_base.width * 0.6, img_s / 2 - self.image_base.height * 0.7,
                          img_s / 2 + self.image_base.width * 0.6, img_s / 2 - self.image_base.height * 0.55),
                         fill=(100,100,100))
        drawer.rectangle((img_s / 2 - self.image_base.width * 0.6 + 1, img_s / 2 - self.image_base.height * 0.7 + 1,
                          img_s / 2 - self.image_base.width * 0.6 + 1 + (self.image_base.width * 1.2 - 2) * (
                                  self.health / self.max_health), img_s / 2 - self.image_base.height * 0.55 - 1),
                         fill=(200,0,0))

        return image, Vec(self.x, self.y)

    def control(self,player):
        self.target_move = Vec(player.x-self.x,player.y-self.y)
