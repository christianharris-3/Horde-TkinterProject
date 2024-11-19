import random
import math
import copy
import json
import tkinter as tk
from PIL import ImageTk, Image, ImageDraw, ImageFont
from src.Player import Player
from src.TileMap import Tilemap
from src.Utiles import Coords, Vec, RectHitbox, get_difficulty_data
from src.Projectiles import Grenade
from src.SaveLoad import Save, Load



class Game:
    def __init__(self, window, inp, screen_width, screen_height,
                 control_map, menus, font, gamefile, level):
        self.window = window
        self.inp = inp
        self.menus = menus
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.font = font

        self.screen = tk.Canvas(self.window, width=self.screen_width,
                                height=self.screen_height, bg="green",
                                highlightthickness=0)
        self.screen.place(relx=0.5, rely=0.5, anchor=tk.CENTER)

        self.control_map = control_map
        self.cheat_info = {'immortal': False,
                           'infinite ammo': False,
                           'infinite abilities': False,
                           'damage multiplier': 1,
                           'spawn time multiplier':1,
                           'speed of time': 1}

        self.tilemap = Tilemap(level)
        self.allwaves_data = self.load_waves_data()
        self.difficulty = self.tilemap.difficulty
        self.difficulty_data = get_difficulty_data(self.difficulty)


        self.player = Player(self.tilemap.entity_data[0]["x_pos"],
                             self.tilemap.entity_data[0]["y_pos"],
                             self.control_map, self.cheat_info,
                             self.screen_width, self.screen_height)
        self.enemies = []
        self.projectiles = []
        self.particles = []

        self.coin_image = ImageTk.PhotoImage(
            image=Image.open('Sprites/Coin.png').convert("RGBA").resize((60, 60),
                                                                resample=Image.Resampling.BOX))
        self.shop_data = {'Owned_Guns': ['Pistol'],
                          'Temp_Upgrades': {'Heal': -1, 'Shield': 0, 'Grenade': 0, 'Force Push': 0},
                          'Player_Object': self.player,
                          'Coins': 0}
        self.game_stats = {'Zombie Kills': 0,
                           'Coins Earned': 0,
                           'Score': 0,
                           'Wave Reached': 'Wave 1',
                           'Rounds Fired': 0,
                           'Grenades Thrown': 0,
                           'Force Pushes Used': 0,
                           'Damage Dealt': 0,
                           'Damage Taken': 0,
                           'Level': self.tilemap.level_title}

        self.wave_index = 0
        self.wave_data = copy.deepcopy(self.allwaves_data[self.wave_index])
        self.wave_title_timer = 2
        self.inbetween_wave = False
        self.inbetween_wave_timer = 0
        self.inbetween_wave_timer_total = 1
        self.zombie_spawn_timer = 0
        self.zombies_in_wave = sum([a["Num"] for a in self.wave_data['Zombies']])
        self.zombies_left = -1
        self.zombies_killed_in_wave = 0

        self.player_dead = False

        self.combo = 0
        self.combo_timer = 0

        self.camera_pos = Vec(self.player.x, self.player.y)
        self.camera_target_pos = Vec()
        self.camera_vel = Vec()
        self.camera_acceleration = 0.03
        self.camera_shake_timer = 0
        self.camera_shake_intensity = 0.1
        self.camera_shake_offset = Vec()

        self.player_img = None
        self.enemy_img = None
        self.enemy_images = []
        self.image_cache = []
        self.collision_hash = {}
        self.world_mpos = Vec()

        self.debug_info = False
        self.fps = 0
        self.window.bind('<F3>', self.toggle_debug)

        self.gamefile = gamefile
        if gamefile:
            self.load_game(gamefile)
        else:
            # fruit names source
            # https://www.goodgoodgood.co/articles/list-of-fruits
            with open('Data/fruit_names.json', 'r') as f:
                fruit = random.choice(json.load(f))
            self.gamefile = fruit

    def load_game(self, filename):
        game_data = Load.load(filename, self.control_map, self.screen_width, self.screen_height)
        if game_data:
            self.player, self.enemies, self.tilemap, self.projectiles,self.particles = game_data[:5]
            self.shop_data, self.game_stats, self.camera_pos, wave_data, cheat_info = game_data[5:]
            self.allwaves_data = self.load_waves_data()
            titles = [a["Title"] for a in self.allwaves_data]
            wave_index = titles.index(self.game_stats["Wave Reached"])
            self.set_wave(wave_index)
            self.wave_data = wave_data
            self.cheat_info = cheat_info
            self.difficulty_data = get_difficulty_data(self.tilemap.difficulty)
    def save_game(self, filename=None):
        if filename:
            self.gamefile = filename
        else:
            filename = self.gamefile
        Save.save(filename, self.player, self.enemies, self.tilemap, self.projectiles,
                  self.particles, self.shop_data, self.game_stats, self.camera_pos,
                  self.wave_data, self.cheat_info)

    def load_waves_data(self):
        dat = self.tilemap.wave_data
        for wave in dat:
            for z in wave["Zombies"]:
                for typ in Save.entity_type_map:
                    if Save.entity_type_map[typ] == z["Class"]:
                        z["Class"] = typ
        return dat

    def gameloop(self, delta_time):
        self.fps = 60 / delta_time
        self.combo_timer -= delta_time / 60
        self.get_world_mpos()
        self.generate_enemies(delta_time)
        self.wave_manager(delta_time)
        self.get_collision_hash()


        # Player Physics and Input control
        open_shop = False
        if not self.player_dead:
            new_projectiles,new_particles,open_shop = self.player.control(self.inp, self.world_mpos,
                                                      self.shop_data, self.enemies, self.game_stats)
            if len(new_projectiles) > 0:
                self.game_stats['Rounds Fired'] += 1
            self.projectiles += new_projectiles
            self.particles += new_particles
            self.player.physics(delta_time, self.tilemap.collision_hash)
            self.player.manage_time(delta_time)
            self.game_stats["Damage Taken"] = self.player.damage_taken
            if self.player.get_dead():
                self.player_dead = True
                for e in self.enemies:
                    e.passive_ai_wait_timer = random.random() * 5 + 2
                return True, False

        # Enemy Physics, AI control and deletion
        rem = []
        for enem in self.enemies:
            enem.control(self.player)
            enem.physics(delta_time, self.tilemap.collision_hash)
            if enem.get_dead():
                rem.append(enem)
        for r in rem:
            self.zombies_killed_in_wave += 1
            self.game_stats['Zombie Kills'] += 1
            self.shop_data["Coins"] += r.coin_value*self.difficulty_data["Coin_Multiplier"]
            self.game_stats["Coins Earned"] += r.coin_value
            if self.combo_timer < 0:
                self.combo = 0
            else:
                self.combo += 1
            self.game_stats["Score"] += (10 + self.combo) * r.coin_value
            self.combo_timer = 1
            self.enemies.remove(r)

        # Player + Entity Collision
        entities = self.enemies + [self.player]
        for entity in entities:
            self.particles += entity.entity_collision(self.collision_hash, self.shake_camera)

        # Projectile Physics and deletion
        rem = []
        for proj in self.projectiles:
            proj.physics(delta_time)
            for entity in entities:
                new_particles, damage_dealt = proj.detect_hit(entity)
                self.particles += new_particles
                self.game_stats["Damage Dealt"] += damage_dealt
            if proj.get_dead(self.tilemap.collision_hash):
                if isinstance(proj,Grenade):
                    new_particles, damage_dealt = proj.explode(entities)
                    self.particles += new_particles
                    self.game_stats["Damage Dealt"] += damage_dealt
                rem.append(proj)
        for r in rem:
            self.projectiles.remove(r)

        # Particle Physics and deletion
        rem = []
        for par in self.particles:
            par.physics(delta_time)
            if par.get_dead():
                rem.append(par)
        for r in rem:
            self.particles.remove(r)

        # Camera movement
        self.camera_physics(delta_time)

        return False, open_shop

    def render_frame(self):
        self.screen.delete('game_image')

        # Tilemap Rendering
        tlx, tly = self.screen_to_world_pos(Vec()).tuple()
        brx, bry = self.screen_to_world_pos(Vec(self.screen_width, self.screen_height)).tuple()
        self.tilemap.render_tiles(self.screen, RectHitbox(tlx, tly,
                                                          round(brx - tlx), round(bry - tly)),
                                  self.get_render_coords)

        # Enemy Rendering
        self.enemy_images = []
        for enemy in self.enemies:
            enemy_img, enemy_pos = enemy.get_image()
            self.enemy_images.append(ImageTk.PhotoImage(enemy_img))
            self.screen.create_image(self.get_render_coords(enemy_pos),
                                     image=self.enemy_images[-1], tag='game_image')

        # Player Rendering
        if not self.player_dead:
            screen_hitbox = RectHitbox(*self.screen_to_world_pos(Vec()),
                                       *Coords.pixel_to_world_coords(Vec(self.screen_width,
                                                                         self.screen_height)))

            player_img, player_pos = self.player.get_image(self.enemies, screen_hitbox,
                                                           self.inbetween_wave)
            self.player_img = ImageTk.PhotoImage(player_img)
            self.screen.create_image(self.get_render_coords(player_pos),
                                     image=self.player_img, tag='game_image')

        # Projectile/Particle Rendering
        for par in self.projectiles + self.particles:
            par.draw_image(self.screen, self.get_render_coords)

        ### UI Rendering
        if not self.player_dead:
            self.player.draw_ui(self.screen, self.shop_data["Temp_Upgrades"], self.font)

        # Coins
        self.screen.create_image((10, 10), image=self.coin_image, tag='game_image',
                                 anchor=tk.NW)
        self.screen.create_text(80, 40, text=str(self.shop_data["Coins"]), anchor=tk.W,
                                tags='game_image', font=(self.font, 30))
        # Score
        self.screen.create_text(self.screen_width - 30, 10,
                                text=f"Score: {self.game_stats['Score']}", anchor=tk.NE,
                                tags='game_image', font=(self.font, 30))

        # Wave Title
        if self.wave_title_timer > 0 and not self.inbetween_wave:
            fade_progress = max(math.sin(min(self.wave_title_timer, 1) * math.pi / 2), 0)
            try:
                surf_s = 80
                scale_factor = 10 * fade_progress
                surf = Image.new('RGBA', (surf_s, surf_s), (255, 255, 255, 0))
                drawer = ImageDraw.Draw(surf)
                font = ImageFont.load_default()
                text_size = drawer.textsize(self.wave_data["Title"], font)
                drawer.text((surf_s / 2 - text_size[0] / 2, surf_s / 2 - text_size[1] / 2),
                            self.wave_data["Title"],
                            font=font, fill=(0, 0, 0, int(255 * fade_progress)), anchor=tk.S)
                self.image_cache = ImageTk.PhotoImage(
                    surf.resize((int(surf_s * scale_factor) + 1, int(surf_s * scale_factor) + 1),
                                resample=Image.Resampling.BOX))
                self.screen.create_image(self.screen_width / 2, self.screen_height / 2,
                                         image=self.image_cache,anchor=tk.CENTER, tags='game_image')
            except Exception as _:
                self.screen.create_text((self.screen_width / 2, self.screen_height / 2),
                                        text=self.wave_data["Title"],anchor=tk.CENTER,
                                      font=(self.font, int(80 * fade_progress)), tags='game_image')

        # Wave Progress Bar
        w = 300
        h = 30
        self.screen.create_rectangle(self.screen_width / 2 - w, 10, self.screen_width/2 + w, 10 + h,
                                     fill='#888', tags='game_image')
        if not self.inbetween_wave:
            first_bar = 2 * w * self.zombies_killed_in_wave / self.zombies_in_wave
            second_bar = 2 * w * len(self.enemies) / self.zombies_in_wave
        else:
            first_bar = 2 * w * (1-self.inbetween_wave_timer/self.inbetween_wave_timer_total)
            second_bar = 0
        if first_bar > 0:
            self.screen.create_rectangle(self.screen_width / 2 - w, 10,
                                         self.screen_width / 2 - w + first_bar, 10 + h,
                                         fill='#8255b9', tags='game_image')
        if second_bar > 0:
            self.screen.create_rectangle(self.screen_width / 2 - w + first_bar, 10,
                                         self.screen_width / 2 - w + first_bar + second_bar, 10 + h,
                                         fill='#8255b9', stipple='gray50', tags='game_image')
        self.screen.create_text(self.screen_width / 2, 10 + h / 2, text=self.wave_data["Title"],
                                anchor=tk.CENTER, font=(self.font, 12), tags='game_image')

        # Shop Prompt
        if self.inbetween_wave:
            self.screen.create_text(self.screen_width/2,self.screen_height-200,anchor=tk.CENTER,
                                    text='Spend Coins\nin the Shop!', font=(self.font, 30),
                                    fill='#254a21', tags='game_image')

        # Debug
        if self.debug_info:
            output = f"""
            FPS: {int(self.fps)}
            Keys Pressed: {self.inp.kprs}
            Zombies Alive: {len(self.enemies)}
            Zombies To Spawn: {'+'.join([str(a['Num']) for a in self.wave_data['Zombies']])}
            Particles: {len(self.particles)}
            Projectiles: {len(self.projectiles)}
            """
            game_stat_strs = [f"{stat}: {self.game_stats[stat]}" for stat in self.game_stats]
            output += '\n            '.join(game_stat_strs)
            self.screen.create_text(-30, 80, text=output, anchor=tk.NW, tags='game_image')

    def generate_enemies(self, delta_time):
        if self.wave_title_timer < 0 and self.inbetween_wave_timer < 0 and not self.player_dead:
            self.zombie_spawn_timer -= delta_time / 60
            if self.zombie_spawn_timer <= 0:
                # Slows down zombie spawns when more zombies are alive
                self.zombie_spawn_timer = self.wave_data['Spawn_Rate']
                self.zombie_spawn_timer*=max((len(self.enemies)*self.wave_data["Spawn_Slower"]+1),1)
                self.zombie_spawn_timer*=self.cheat_info["spawn time multiplier"]

                def make_zombie(z_class):
                    angle = math.pi * (random.random() * 2 - 1)
                    dis = 10
                    return z_class(self.player.x + math.cos(angle) * dis,
                                   self.player.y + math.sin(angle) * dis,
                                   self.difficulty_data)

                self.zombies_left = sum([a['Num'] for a in self.wave_data['Zombies']])
                if self.zombies_left > 0:
                    choice = random.randint(1, self.zombies_left)
                    for z in self.wave_data['Zombies']:
                        choice -= z['Num']
                        if choice <= 0:
                            new_enemy = make_zombie(z['Class'])
                            count = 0
                            while count < 100 and not (self.tilemap.get_inside_tilemap(
                                    Vec(new_enemy.x, new_enemy.y))) or new_enemy.tilemap_collision(
                                    self.tilemap.collision_hash):
                                count += 1
                                new_enemy = make_zombie(z['Class'])
                            if count < 100:
                                z['Num'] -= 1
                                self.enemies.append(new_enemy)
                                self.zombies_left-=1
                            break

    def wave_manager(self, delta_time):
        self.inbetween_wave_timer -= delta_time / 60
        if self.inbetween_wave_timer<0 and self.inbetween_wave:
            self.inbetween_wave = False
            self.wave_title_timer = 2

        if not self.inbetween_wave:
            self.wave_title_timer -= delta_time / 60
            if self.zombies_left == 0 and len(self.enemies) == 0:
                self.wave_index += 1
                while self.wave_index >= len(self.allwaves_data):
                    # Generates new wave if out of waves
                    new_wave = copy.deepcopy(self.allwaves_data[-1])
                    new_wave["Title"] = f"wave {len(self.allwaves_data)+1}"
                    new_wave["Spawn_Rate"] /= 2
                    new_wave["Spawn_Slower"] /= 2
                    for z in new_wave["Zombies"]:
                        z["Num"] = int(z["Num"]*1.5)
                    self.allwaves_data.append(new_wave)

                self.set_wave(self.wave_index)

    def set_wave(self,wave_index):
        self.wave_index = wave_index
        self.wave_data = copy.deepcopy(self.allwaves_data[wave_index])
        self.wave_title_timer = 2
        self.zombie_spawn_timer = 0
        self.zombies_left = -1
        numlist = [a["Num"] for a in self.wave_data['Zombies']]
        self.zombies_in_wave = sum(numlist)
        self.zombies_killed_in_wave = 0
        self.game_stats["Wave Reached"] = self.wave_data["Title"]

        self.inbetween_wave = True
        self.inbetween_wave_timer_total = self.zombies_in_wave*self.wave_data["Spawn_Rate"]/3/(
                                          self.wave_index+1)
        self.inbetween_wave_timer = self.inbetween_wave_timer_total


    def shake_camera(self, amplitude=0.1):
        self.camera_shake_timer = 0.1
        self.camera_shake_intensity = amplitude

    def camera_physics(self, delta_time):
        self.camera_target_pos = Vec(self.player.x, self.player.y)

        self.camera_vel += (self.camera_target_pos - self.camera_pos
                            ) * delta_time * self.camera_acceleration
        self.camera_pos += self.camera_vel
        self.camera_vel *= 0.8

        self.camera_shake_timer -= delta_time / 60
        if self.camera_shake_timer > 0:
            self.camera_shake_offset = Vec(random.gauss(0, self.camera_shake_intensity),
                                           random.gauss(0, self.camera_shake_intensity))

    def get_collision_hash(self):
        self.collision_hash = {}
        entities = self.enemies[:]
        if not self.player_dead:
            entities.append(self.player)
        for e in entities:
            for code in e.get_hitbox().colcodes:
                if code in self.collision_hash:
                    self.collision_hash[code].append(e)
                else:
                    self.collision_hash[code] = [e]

    def get_render_coords(self, pos):
        pixel_pos = Coords.world_to_pixel_coords(pos - self.camera_pos - self.camera_shake_offset)
        pixel_pos += Vec(self.screen_width, self.screen_height) / 2
        return pixel_pos.tuple()

    def screen_to_world_pos(self, pos):
        pos -= Vec(self.screen_width, self.screen_height) / 2
        return Coords.pixel_to_world_coords(pos) + self.camera_pos + self.camera_shake_offset

    def get_world_mpos(self):
        self.world_mpos = self.screen_to_world_pos(self.inp.get_mpos())

    def window_resize(self, nwidth, nheight):
        self.screen_width = nwidth
        self.screen_height = nheight
        self.screen.configure(width=self.screen_width, height=self.screen_height)
        self.player.screen_resize(self.screen_width, self.screen_height)

    def toggle_debug(self, _):
        self.debug_info = not self.debug_info
