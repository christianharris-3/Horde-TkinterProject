from src.Entity import Entity
import tkinter as tk
from PIL import Image, ImageTk, ImageDraw
from src.Utiles import Coords, Vec
from src.Projectiles import Bullet, SMG_Bullet, LMG_Bullet
from src.TileMap import Tile
import math


class WeaponData:
    data = {"Pistol": {"File": "Sprites/Pistol.png", "Render_Size": 1, "Render_Distance": 1, "Projectile": Bullet,
                       "Bullet_Speed": 0.5, "Shoot_CD": 0.1, "Semi_Auto": False, "Clip_Size": 5, "Reload_Time": 0.5},
            "SMG": {"File": "Sprites/SMG.png", "Render_Size": 1.2, "Render_Distance": 1, "Projectile": SMG_Bullet,
                    "Bullet_Speed": 0.6, "Shoot_CD": 0.1, "Semi_Auto": True, "Clip_Size": 20, "Reload_Time": 0.8},
            "LMG": {"File": "Sprites/LMG.png", "Render_Size": 2, "Render_Distance": 1.5, "Projectile": LMG_Bullet,
                    "Bullet_Speed": 0.8, "Shoot_CD": 0.06, "Semi_Auto": True, "Clip_Size": 30, "Reload_Time": 1.5},
            }


class Player(Entity):
    def __init__(self, x, y, control_map, screen_width, screen_height):
        super().__init__(x, y)
        self.team = 'Player'
        self.radius = 0.45
        self.move_acceleration = 0.01
        self.max_health = 20
        self.health = self.max_health

        self.control_map = control_map

        self.weapon_data = WeaponData.data["LMG"]
        self.control_map["Shoot"]["continuous"] = self.weapon_data["Semi_Auto"]
        self.ammo_left = self.weapon_data["Clip_Size"]
        self.reloading = True
        self.reload_timer = 0

        self.image_base = Image.open('Sprites/Player.png').convert("RGBA").resize(
            Coords.world_to_pixel_coords((self.radius * 2, self.radius * 2)).tuple(True), resample=Image.Resampling.BOX)

        self.weapon_image_base = Image.open(self.weapon_data["File"]).convert("RGBA").resize(
            (Coords.world_to_pixel_coords((self.radius, self.radius)) * self.weapon_data["Render_Size"]).tuple(True),
            resample=Image.Resampling.BOX)

        self.hurt_image = 0
        self.hurt_frames_counter = 0
        self.screen_resize(screen_width, screen_height)

        self.can_open_shop = False
        self.closest_shop = Tile(-1, -1, 40, "Shop")

        self.auto_fire_cooldown = 0
        self.reload_timer = 0

        self.buttons_down = []

    def screen_resize(self, w, h):
        hurt_image = Image.new("RGBA", (w, h), (255, 0, 0, 0))
        drawer = ImageDraw.Draw(hurt_image)
        drawer.rectangle((0, 0, w, h), (255, 0, 0, 100))
        self.hurt_image = ImageTk.PhotoImage(hurt_image)

    def manage_time(self,delta_time):
        self.i_frames -= delta_time / 60
        self.auto_fire_cooldown -= delta_time / 60
        self.reload_timer -= delta_time / 60

        self.closest_shop.can_be_opened = self.can_open_shop
        self.closest_shop.open_shop_text = f"Click {self.control_map['Shop']['Key'].upper()} To Open Shop"

    def get_image(self):
        img_s = int(3.5 * Coords.scale_factor)
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
        weapon_img = weapon_img.rotate(-self.angle / math.pi * 180, expand=True)
        image.paste(weapon_img, (
            int(img_s / 2 + math.cos(self.angle) * Coords.world_to_pixel(
                self.radius) * self.weapon_data["Render_Distance"] - weapon_img.width / 2),
            int(img_s / 2 + math.sin(self.angle) * Coords.world_to_pixel(
                self.radius) * self.weapon_data["Render_Distance"] - weapon_img.width / 2 - Coords.world_to_pixel(
                self.radius / 10))),
                    weapon_img)

        return image, Vec(self.x, self.y)

    def draw_ui(self, screen):
        screen.create_rectangle(10, 10, 210, 60, fill="#444444", outline="#444444", tag="game_image")
        screen.create_rectangle(12, 12, 12 + (196 * self.health / self.max_health), 58,
                                fill="#ff0000", outline="#ff0000", tag="game_image")

        if self.reloading:
            output = "Clip: Reloading"
            screen.create_rectangle(220, 55, 220 + max(self.reload_timer, 0) / self.weapon_data["Reload_Time"] * 300,
                                    60, fill="#803310", outline="#803310", tag="game_image")
        else:
            output = f"Clip: {self.ammo_left}/{self.weapon_data['Clip_Size']}"
        screen.create_text(220, 0, text=output, anchor=tk.NW, tags='game_image', font=('Segoe Print', 30))

        self.hurt_frames_counter -= 1
        if self.hurt_frames_counter >= 0:
            hurt_image = Image.new("RGBA", (screen.winfo_width(), screen.winfo_height()), (255, 0, 0, 0))
            drawer = ImageDraw.Draw(hurt_image)
            drawer.rectangle((0, 0, screen.winfo_width(), screen.winfo_height()), (255, 0, 0, 100))
            self.hurt_image = ImageTk.PhotoImage(hurt_image)
            screen.create_image(0, 0, anchor=tk.NW, image=self.hurt_image, tag="game_image")

    def control(self, inp, mpos):

        # Remove all not pressed buttons from buttons_down list
        rem = []
        for b in self.buttons_down:
            if not inp.get_pressed(b):
                rem.append(b)
        for r in rem:
            self.buttons_down.remove(r)

        # Movement
        self.target_move = Vec()
        if self.get_pressed(inp,"Left"):
            self.target_move[0] -= 1
        elif self.get_pressed(inp,"Right"):
            self.target_move[0] += 1
        if self.get_pressed(inp,"Up"):
            self.target_move[1] -= 1
        elif self.get_pressed(inp,"Down"):
            self.target_move[1] += 1

        # Reload
        if self.get_pressed(inp,"Reload"):
            self.reload()

        # Shop
        open_shop = False
        if self.get_pressed(inp,"Shop") and self.can_open_shop:
            open_shop = True

        # Shooting
        if self.reload_timer <= 0 and self.reloading:
            self.reloading = False
            self.ammo_left = self.weapon_data["Clip_Size"]
        new_projectiles = []
        if self.get_pressed(inp,"Shoot") and self.auto_fire_cooldown < 0:
            new_projectiles = self.shoot()
            self.auto_fire_cooldown = self.weapon_data["Shoot_CD"]

        self.angle = math.atan2(mpos[1] - self.y, mpos[0] - self.x)
        return new_projectiles, open_shop

    def get_pressed(self,inp,key):
        if inp.get_pressed(self.control_map[key]['Key']) and (self.control_map[key]['Key'] not in self.buttons_down):
            if not self.control_map[key]['continuous']:
                self.buttons_down.append(self.control_map[key]['Key'])
            return True
        return False

    def shoot(self):
        if self.ammo_left > 0 and not self.reloading:
            self.ammo_left -= 1
            if self.ammo_left == 0:
                self.reload()
            return [
                self.weapon_data["Projectile"](self.x, self.y, self.angle, self.weapon_data["Bullet_Speed"], self.team)]
        else:
            return []

    def reload(self):
        self.reloading = True
        self.reload_timer = self.weapon_data["Reload_Time"]
