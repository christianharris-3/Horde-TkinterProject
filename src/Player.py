import math, random
import tkinter as tk
from PIL import Image, ImageTk, ImageDraw
from src.entity import Entity
from src.Utiles import Coords, Vec
from src.Projectiles import Bullet, SMG_Bullet, LMG_Bullet, Shotgun_Shell, Grenade, KB_Obj
from src.Particles import Force_Push_Effect
from src.TileMap import Tile


class WeaponData:
    data = {"Pistol": {"File": "Sprites/Pistol.png", "Render_Size": 1, "Render_Distance": 1, "Projectile": Bullet,
                       "Bullet_Speed": 0.5, "Shoot_CD": 0.2, "Semi_Auto": False, "Clip_Size": 5, "Reload_Time": 1,
                       "Spray_Count": 1, "Spread":0.05, "Speed_Ran":0.05, "Price": 0},
            "SMG": {"File": "Sprites/SMG.png", "Render_Size": 1.2, "Render_Distance": 1, "Projectile": SMG_Bullet,
                    "Bullet_Speed": 0.6, "Shoot_CD": 0.1, "Semi_Auto": True, "Clip_Size": 20, "Reload_Time": 0.8,
                    "Spray_Count": 1, "Spread":0.08, "Speed_Ran":0.05, "Price": 25},
            "Shotgun": {"File": "Sprites/Shotgun.png", "Render_Size": 1.8, "Render_Distance": 1.3, "Projectile": Shotgun_Shell,
                        "Bullet_Speed": 0.4, "Shoot_CD": 0.35, "Semi_Auto": False, "Clip_Size": 10, "Reload_Time": 1.5,
                        "Spray_Count": 8, "Spread":0.2, "Speed_Ran":0.1, "Price": 100},
            "LMG": {"File": "Sprites/LMG.png", "Render_Size": 2, "Render_Distance": 1.5, "Projectile": LMG_Bullet,
                    "Bullet_Speed": 0.65, "Shoot_CD": 0.06, "Semi_Auto": True, "Clip_Size": 30, "Reload_Time": 1.2,
                    "Spray_Count": 1, "Spread":0.03, "Speed_Ran":0.03, "Price": 150},
            }


class Player(Entity):
    def __init__(self, x, y, control_map, cheat_info, screen_width, screen_height):
        super().__init__(x, y)
        self.team = 'Player'
        self.radius = 0.45
        self.move_acceleration = 0.01
        self.max_health = 20
        self.health = self.max_health
        self.recent_health = self.health
        self.shield = 0
        self.recent_shield = self.shield

        self.control_map = control_map
        self.cheat_info = cheat_info

        self.active_weapon = "Pistol"
        self.weapon_data = WeaponData.data[self.active_weapon]
        self.ammo_left = self.weapon_data["Clip_Size"]
        self.reloading = True
        self.weapon_image_base = None
        self.set_weapon(self.active_weapon)

        self.image_base = Image.open('Sprites/Player.png').convert("RGBA").resize(
            Coords.world_to_pixel_coords((self.radius * 2, self.radius * 2)).tuple(True), resample=Image.Resampling.BOX)

        self.grenade_image_base = ImageTk.PhotoImage(Image.open('Sprites/Grenade.png'
                                             ).convert("RGBA").resize((54,54),resample=Image.Resampling.BOX))
        self.push_image_base = ImageTk.PhotoImage(Image.open('Sprites/Force_Push.png'
                                                  ).convert("RGBA").resize((54, 54),resample=Image.Resampling.BOX))

        self.hurt_image = 0
        self.hurt_frames_counter = 0
        self.screen_resize(screen_width, screen_height)
        self.time_since_hit = 0

        self.can_open_shop = False
        self.closest_shop = Tile(-1, -1, 40, "Shop")
        self.closest_shop.team = None

        self.auto_fire_cooldown = 0
        self.reload_timer = 0
        self.recent_health_timer = 0

        self.buttons_down = []

    def set_weapon(self, new_weapon):
        self.weapon_data = WeaponData.data[new_weapon]
        self.active_weapon = new_weapon
        self.control_map["Shoot"]["continuous"] = self.weapon_data["Semi_Auto"]
        self.ammo_left = self.weapon_data["Clip_Size"]
        self.reloading = True
        self.reload_timer = self.weapon_data["Reload_Time"]

        self.weapon_image_base = Image.open(self.weapon_data["File"]).convert("RGBA")
        ratio = self.weapon_image_base.height / self.weapon_image_base.width
        self.weapon_image_base = self.weapon_image_base.resize(
            (Coords.world_to_pixel_coords((self.radius, self.radius * ratio)) * self.weapon_data["Render_Size"]).tuple(
                True),
            resample=Image.Resampling.BOX)
        size = max(self.weapon_image_base.height, self.weapon_image_base.width)
        square_surf = Image.new('RGBA', (size, size), (0, 0, 0, 0))
        square_surf.paste(self.weapon_image_base, (int(size / 2 - self.weapon_image_base.width / 2),
                                                   int(size / 2 - self.weapon_image_base.height / 2)))
        self.weapon_image_base = square_surf

    def screen_resize(self, w, h):
        hurt_image = Image.new("RGBA", (w, h), (255, 0, 0, 0))
        drawer = ImageDraw.Draw(hurt_image)
        drawer.rectangle((0, 0, w, h), (255, 0, 0, 100))
        self.hurt_image = ImageTk.PhotoImage(hurt_image)

    def manage_time(self, delta_time):
        self.i_frames -= delta_time / 60
        self.auto_fire_cooldown -= delta_time / 60
        self.reload_timer -= delta_time / 60
        self.time_since_hit += delta_time / 60

        self.closest_shop.can_be_opened = self.can_open_shop
        self.closest_shop.open_shop_text = f"Click {self.control_map['Shop']['Key'].upper()} To Open Shop"

    def get_image(self, enemies, screen_hitbox, inbetween_waves):
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

        # Function for drawing arrows
        def draw_arrow(target_x,target_y,surf,col):
            angle = math.atan2(target_y-self.y,target_x-self.x)
            dis = Coords.world_to_pixel(self.radius*2)
            draw = ImageDraw.Draw(surf)
            center = Vec(img_s/2,img_s/2)
            draw.polygon([(Vec.make_from_angle(angle)*dis+center).tuple(),
                          (Vec.make_from_angle(angle+0.1)*(dis-5)+center).tuple(),
                          (Vec.make_from_angle(angle-0.1)*(dis-5)+center).tuple()],fill=col)

        # Draw arrows to all off screen enemies
        for e in enemies:
            if not e.get_hitbox(True).Get_Collide(screen_hitbox):
                draw_arrow(e.x,e.y,image,'#f22')

        # Draw arrow to shop if a closest shop exists
        if inbetween_waves and self.closest_shop.team and not self.closest_shop.can_be_opened:
            draw_arrow(self.closest_shop.x+0.5,self.closest_shop.y+0.5,image,'#275384')

        return image, Vec(self.x, self.y)

    def draw_ui(self, screen, temp_upgrades, font):
        ## Health Bar
        if self.i_frames<0:
            self.recent_health = self.health
            self.recent_shield = self.shield
        w = 300
        # Main hp bar, 3 rects for border, recent health and health display
        screen.create_rectangle(screen.winfo_width()/2-w/2,screen.winfo_height()-80,
                                screen.winfo_width()/2+w/2-1,screen.winfo_height()-30-1,
                                fill="#444", outline="#666",tag='game_image')
        screen.create_rectangle(screen.winfo_width() / 2 - (w - 10) / 2 * (self.recent_health / self.max_health),screen.winfo_height() - 75,
                                screen.winfo_width() / 2 + (w - 10) / 2 * (self.recent_health / self.max_health),screen.winfo_height() - 35,
                                fill="#a44", outline="#b33", tag='game_image', width=4)
        screen.create_rectangle(screen.winfo_width()/2 - (w-10)/2*(self.health / self.max_health), screen.winfo_height() - 75,
                                screen.winfo_width()/2 + (w-10)/2*(self.health / self.max_health), screen.winfo_height() - 35,
                                fill="#f00", outline="#f22", tag='game_image',width=4)
        # Shield hp overlay, 2 rects recent shield and shield display
        if self.shield!=0:
            screen.create_rectangle(screen.winfo_width() / 2 - (w - 10) / 2 * (self.recent_shield / self.max_health),
                                    screen.winfo_height() - 75,
                                    screen.winfo_width() / 2 + (w - 10) / 2 * (self.recent_shield / self.max_health),
                                    screen.winfo_height() - 35,stipple="gray50",
                                    fill="#44a", outline="#33b", tag='game_image', width=4)
            screen.create_rectangle(screen.winfo_width() / 2 - (w - 10) / 2 * (self.shield / self.max_health),
                                    screen.winfo_height() - 75,
                                    screen.winfo_width() / 2 + (w - 10) / 2 * (self.shield / self.max_health),
                                    screen.winfo_height() - 35,stipple="gray50",
                                    fill="#00b", outline="#22b", tag='game_image', width=4)

        # Ammo Display
        ammo_x = (screen.winfo_width()+w) / 2+20
        ammo_y = screen.winfo_height()-55
        if self.reloading:
            output = "Clip: Reloading"
            screen.create_rectangle(ammo_x, ammo_y+20, ammo_x + max(self.reload_timer, 0) / self.weapon_data["Reload_Time"] * 300,
                                    ammo_y+25, fill="#803310", outline="#803310", tag="game_image")
        else:
            output = f"Clip: {self.ammo_left}/{self.weapon_data['Clip_Size']}"
        screen.create_text(ammo_x, ammo_y, text=output, anchor=tk.W, tags='game_image', font=(font, 30))

        # Grenade/Force Push Display
        grenade_x = (screen.winfo_width() - w) / 2 - 150
        grenade_y = screen.winfo_height() - 55
        output = f"{temp_upgrades['Grenade']}/10"
        screen.create_text(grenade_x, grenade_y, text=output, anchor=tk.W, tags='game_image', font=(font, 30))
        screen.create_image(grenade_x-10, grenade_y, image=self.grenade_image_base,anchor=tk.E ,tags='game_image')

        push_x = (screen.winfo_width() - w) / 2 - 360
        push_y = screen.winfo_height() - 55
        output = f"{temp_upgrades['Force Push']}/10"
        screen.create_text(push_x, push_y, text=output, anchor=tk.W, tags='game_image', font=(font, 30))
        screen.create_image(push_x - 10, push_y, image=self.push_image_base, anchor=tk.E, tags='game_image')

        # Damage tick
        self.hurt_frames_counter -= 1
        if self.hurt_frames_counter >= 0:
            hurt_image = Image.new("RGBA", (screen.winfo_width(), screen.winfo_height()), (255, 0, 0, 0))
            drawer = ImageDraw.Draw(hurt_image)
            drawer.rectangle((0, 0, screen.winfo_width(), screen.winfo_height()), (255, 0, 0, 100))
            self.hurt_image = ImageTk.PhotoImage(hurt_image)
            screen.create_image(0, 0, anchor=tk.NW, image=self.hurt_image, tag="game_image")

    def control(self, inp, mpos, shop_data, enemies, game_stats):

        # Remove all not pressed buttons from buttons_down list
        rem = []
        for b in self.buttons_down:
            if not inp.get_pressed(b):
                rem.append(b)
        for r in rem:
            self.buttons_down.remove(r)

        # Movement
        self.target_move = Vec()
        if self.get_pressed(inp, "Left"):
            self.target_move[0] -= 1
        elif self.get_pressed(inp, "Right"):
            self.target_move[0] += 1
        if self.get_pressed(inp, "Up"):
            self.target_move[1] -= 1
        elif self.get_pressed(inp, "Down"):
            self.target_move[1] += 1

        # Reload
        if self.get_pressed(inp, "Reload"):
            self.reload()

        # Shop
        open_shop = False
        if self.get_pressed(inp, "Shop") and self.can_open_shop:
            open_shop = True

        # Abilities
        new_projectiles = []
        new_particles = []
        if self.get_pressed(inp, "Grenade") and (shop_data["Temp_Upgrades"]["Grenade"]>0 or self.cheat_info['infinite abilities']):
            new_projectiles = [Grenade(self.x,self.y,*mpos.tuple(),self.team)]
            new_projectiles[-1].damage*=self.cheat_info['damage multiplier']
            if not self.cheat_info['infinite abilities']:
                shop_data["Temp_Upgrades"]["Grenade"]-=1
            game_stats["Grenades Thrown"]+=1

        if self.get_pressed(inp, "Force Push") and (shop_data["Temp_Upgrades"]["Force Push"]>0 or self.cheat_info['infinite abilities']):
            if not self.cheat_info['infinite abilities']:
                shop_data["Temp_Upgrades"]["Force Push"]-=1
            new_particles += self.force_push(enemies)
            game_stats["Force Pushes Used"] += 1


        # Shooting
        if self.reload_timer <= 0 and self.reloading:
            self.reloading = False
            self.ammo_left = self.weapon_data["Clip_Size"]
        out = self.get_pressed(inp, "Shoot")
        if out and self.auto_fire_cooldown < 0:
            new_projectiles = self.shoot()
            self.auto_fire_cooldown = self.weapon_data["Shoot_CD"]

        self.angle = math.atan2(mpos[1] - self.y, mpos[0] - self.x)
        return new_projectiles, new_particles, open_shop

    def get_pressed(self, inp, key):
        if inp.get_pressed(self.control_map[key]['Key']) and (self.control_map[key]['Key'] not in self.buttons_down):
            if not self.control_map[key]['continuous']:
                self.buttons_down.append(self.control_map[key]['Key'])
            return True
        return False

    def shoot(self):
        if self.ammo_left > 0 and not self.reloading:
            if not self.cheat_info['infinite ammo']:
                self.ammo_left -= 1
            if self.ammo_left == 0:
                self.reload()
            projectiles = []
            for b in range(self.weapon_data["Spray_Count"]):
                projectiles.append(self.weapon_data["Projectile"](self.x, self.y,
                                                                  random.gauss(self.angle, self.weapon_data["Spread"]),
                                                                  max(random.gauss(self.weapon_data["Bullet_Speed"],
                                                                  self.weapon_data["Speed_Ran"]), 0.1), self.team))
                projectiles[-1].damage*=self.cheat_info['damage multiplier']
            return projectiles
        else:
            return []

    def force_push(self,enemies):
        push_range = 6
        knockback = 1
        for e in enemies:
            dx = e.x - self.x
            dy = e.y - self.y
            dis = (dx ** 2 + dy ** 2) ** 0.5
            if dis < push_range:
                kb = knockback / max(dis, 1)/e.knockback_resistance
                angle = math.atan2(dy, dx)
                e.take_hit(KB_Obj(kb, angle, 0, True))
        return [Force_Push_Effect(self.x,self.y,1)]

    def reload(self):
        self.reloading = True
        self.reload_timer = self.weapon_data["Reload_Time"]

    def take_damage(self, damage):
        if self.i_frames <= 0 and not self.cheat_info['immortal']:
            self.damage_taken += damage
            if self.shield>damage:
                self.shield-=damage
                damage = 0
            else:
                damage-=self.shield
                self.shield = 0
            self.health-=damage
            if self.team == "Player":
                self.i_frames = 0.3
            self.hurt_frames_counter = 3
            self.time_since_hit = 0
