from src.Entity import Entity
from PIL import Image
from src.Utiles import Coords, Vec


class Enemy(Entity):
    def __init__(self, x, y):
        super().__init__(x,y)
        self.team = 'Enemy'

        self.radius = 0.8

        self.image_base = Image.open('Sprites/Enemy.png').resize(
            Coords.world_to_pixel_coords((self.radius * 2, self.radius * 2)).tuple(True),resample=Image.Resampling.BOX)

    def get_image(self):
        image = Image.new("RGBA", (100, 100), (0, 0, 0, 0))
        image.paste(self.image_base, (int(50 - self.image_base.width / 2), int(50 - self.image_base.height / 2)))

        return image,Vec(self.x,self.y)

    def control(self,inp):
        self.target_move = Vec()

