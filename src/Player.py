from src.Entity import Entity
from PIL import Image
from src.Utiles import Coords, Vec
from src.Projectiles import Bullet
import math


class Player(Entity):
    def __init__(self, x, y, control_map):
        super().__init__(x, y)
        self.team = 'Player'

        self.control_map = control_map
        self.image_base = Image.open('Sprites/Player.png').convert("RGBA").resize(
            Coords.world_to_pixel_coords((self.radius * 2, self.radius * 2)).tuple(True), resample=Image.Resampling.BOX)

        self.weapon_image_base = Image.open('Sprites/Pistol.png').convert("RGBA").resize(
            Coords.world_to_pixel_coords((self.radius, self.radius)).tuple(True), resample=Image.Resampling.BOX)

        self.buttons_down = []

    def get_image(self):
        img_s = 140
        image = Image.new("RGBA", (img_s, img_s), (0, 0, 0, 0))


        # Check of player is pointing to left, then flip and weapon, else don't
        if abs(self.angle) > math.pi / 2:
            weapon_img = self.weapon_image_base.transpose(Image.FLIP_TOP_BOTTOM)
            player_img = self.image_base
        else:
            weapon_img = self.weapon_image_base
            player_img = self.image_base.transpose(Image.FLIP_LEFT_RIGHT)

        # Draw player image
        image.paste(player_img,
                    (int(img_s / 2 - self.image_base.width / 2), int(img_s / 2 - self.image_base.height / 2)),
                    player_img)

        # Draw weapon image
        weapon_img = weapon_img.rotate(-self.angle/math.pi*180,expand=True)
        distance_mul = 1
        image.paste(weapon_img, (
            int(img_s / 2 + math.cos(self.angle) * Coords.world_to_pixel(self.radius) * distance_mul - weapon_img.width / 2),
            int(img_s / 2 + math.sin(self.angle) * Coords.world_to_pixel(self.radius) * distance_mul - weapon_img.width / 2 - Coords.world_to_pixel(self.radius/10))),
                    weapon_img)

        return image, Vec(self.x, self.y)

    def control(self, inp, mpos):

        # Remove all not pressed buttons from buttons_down list
        rem = []
        for b in self.buttons_down:
            if not inp.get_pressed(b):
                rem.append(b)
        for r in rem:
            self.buttons_down.remove(r)

        self.target_move = Vec()
        if inp.get_pressed(self.control_map['Left']['Key']):
            self.target_move[0] -= 1
        elif inp.get_pressed(self.control_map['Right']['Key']):
            self.target_move[0] += 1
        if inp.get_pressed(self.control_map['Up']['Key']):
            self.target_move[1] -= 1
        elif inp.get_pressed(self.control_map['Down']['Key']):
            self.target_move[1] += 1

        new_projectiles = []
        if inp.get_pressed(self.control_map['Shoot']['Key']) and self.control_map['Shoot']['Key'] not in self.buttons_down:
            new_projectiles = self.shoot()
            self.buttons_down.append(self.control_map['Shoot']['Key'])

        self.angle = math.atan2(mpos[1] - self.y, mpos[0] - self.x)
        return new_projectiles

    def shoot(self):
        return [Bullet(self.x,self.y,self.angle,1,self.team)]