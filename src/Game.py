import tkinter as tk
from PIL import ImageTk, Image
from src.Player import Player
from src.Enemy import Slow_Zombie, Fast_Zombie, Big_Zombie
from src.TileMap import Tilemap
from src.Utiles import Coords, Vec, RectHitbox
import random, math


class Game:
    def __init__(self, window, inp, screen_width, screen_height, control_map, menus):
        self.window = window
        self.inp = inp
        self.menus = menus
        self.screen_width = screen_width
        self.screen_height = screen_height

        self.screen = tk.Canvas(self.window, width=self.screen_width, height=self.screen_height, bg="green",
                                highlightthickness=0)
        self.screen.place(x=0, y=0)

        self.control_map = control_map

        self.tilemap = Tilemap(Coords.scale_factor)
        self.player = Player(self.tilemap.entity_data[0]["x_pos"], self.tilemap.entity_data[0]["y_pos"],
                             self.control_map, self.screen_width, self.screen_height)
        self.enemies = []
        self.projectiles = []

        self.coins = 0
        self.coin_image = ImageTk.PhotoImage(
            image=Image.open('Sprites/Coin.png').convert("RGBA").resize((60, 60), resample=Image.Resampling.BOX))

        self.player_dead = False

        self.camera_pos = Vec(self.player.x, self.player.y)
        self.camera_target_pos = Vec()
        self.camera_vel = Vec()
        self.camera_acceleration = 0.03
        self.camera_shake_timer = 0
        self.camera_shake_intensity = 0.1
        self.camera_shake_offset = Vec()

        self.player_img = 0
        self.enemy_img = 0
        self.world_mpos = Vec()

        self.debug_info = True
        self.fps = 0
        self.window.bind('<F3>', self.toggle_debug)

    def gameloop(self, delta_time):
        self.fps = 60 / delta_time
        self.get_world_mpos()
        self.generate_enemies()
        self.get_collision_hash()

        # Player Physics and Input control
        new_projectiles, open_shop = self.player.control(self.inp, self.world_mpos)
        self.projectiles+=new_projectiles
        self.player.physics(delta_time, self.tilemap.collision_hash)
        self.player.manage_time(delta_time)
        if self.player.get_dead():
            self.player_dead = True
            return True, False

        # Enemy Physics, AI control and deletion
        rem = []
        for enem in self.enemies:
            enem.control(self.player)
            enem.physics(delta_time, self.tilemap.collision_hash)
            if enem.get_dead():
                rem.append(enem)
        for r in rem:
            self.coins+=r.coin_value
            self.enemies.remove(r)

        # Player + Entity Collision
        entities = self.enemies + [self.player]
        for entity in entities:
            entity.entity_collision(self.collision_hash, self.shake_camera)

        # Projectile Physics and deletion
        rem = []
        for proj in self.projectiles:
            proj.physics(delta_time)
            for entity in entities:
                proj.detect_hit(entity)
            if proj.get_dead():
                rem.append(proj)
        for r in rem:
            self.projectiles.remove(r)

        # Camera movement
        self.camera_physics(delta_time)

        return False, open_shop

    def render_frame(self):
        self.screen.delete('game_image')

        # Tilemap Rendering
        tlx, tly = self.screen_to_world_pos(Vec()).tuple()
        brx, bry = self.screen_to_world_pos(Vec(self.screen_width, self.screen_height)).tuple()
        self.tilemap.render_tiles(self.screen, RectHitbox(tlx, tly, round(brx - tlx), round(bry - tly)),
                                  self.get_render_coords)

        # Player Rendering
        player_img, player_pos = self.player.get_image()
        self.player_img = ImageTk.PhotoImage(player_img)
        self.screen.create_image(self.get_render_coords(player_pos), image=self.player_img, tag='game_image')

        # Enemy Rendering
        self.enemy_images = []
        for enemy in self.enemies:
            enemy_img, enemy_pos = enemy.get_image()
            self.enemy_images.append(ImageTk.PhotoImage(enemy_img))
            self.screen.create_image(self.get_render_coords(enemy_pos), image=self.enemy_images[-1], tag='game_image')

        for proj in self.projectiles:
            proj.draw_image(self.screen, self.get_render_coords)

        # UI Rendering
        self.player.draw_ui(self.screen)

        # coins
        self.screen.create_image((10, self.screen_height - 10), image=self.coin_image, tag='game_image', anchor=tk.SW)
        self.screen.create_text(80, self.screen_height - 40, text=str(self.coins), anchor=tk.W, tags='game_image',
                                font=('Segoe Print', 30))

        # Debug
        if self.debug_info:
            output = f'''
            FPS: {int(self.fps)}
            Keys Pressed: {self.inp.kprs}
            Zombies: {len(self.enemies)}
                        '''
            self.screen.create_text(-30, 80, text=output, anchor=tk.NW, tags='game_image')

    def generate_enemies(self):
        if random.random() < 0.01:
            def make_zombie(z_class):
                angle = math.pi * (random.random() * 2 - 1)
                dis = 10
                return z_class(self.player.x + math.cos(angle) * dis, self.player.y + math.sin(angle) * dis)

            zombie_map = [{'Probability': 2, 'Class': Slow_Zombie},
                          {'Probability': 5, 'Class': Fast_Zombie},
                          {'Probability': 3, 'Class': Big_Zombie}]
            choice = random.randint(1, sum([a['Probability'] for a in zombie_map]))
            for z in zombie_map:
                choice -= z['Probability']
                if choice <= 0:
                    new_enemy = make_zombie(z['Class'])
                    while not (
                    self.tilemap.get_inside_tilemap(Vec(new_enemy.x, new_enemy.y))) or new_enemy.tilemap_collision(
                            self.tilemap.collision_hash):
                        new_enemy = make_zombie(z['Class'])
                    self.enemies.append(new_enemy)
                    break

    def shake_camera(self, amplitude=0.1):
        self.camera_shake_timer = 0.1
        self.camera_shake_intensity = amplitude

    def camera_physics(self, delta_time):
        self.camera_target_pos = Vec(self.player.x, self.player.y)

        self.camera_vel += (self.camera_target_pos - self.camera_pos) * delta_time * self.camera_acceleration
        self.camera_pos += self.camera_vel
        self.camera_vel *= 0.8

        self.camera_shake_timer -= delta_time / 60
        if self.camera_shake_timer > 0:
            self.camera_shake_offset = Vec(random.gauss(0, self.camera_shake_intensity),
                                           random.gauss(0, self.camera_shake_intensity))

    def get_collision_hash(self):
        self.collision_hash = {}
        for e in self.enemies + [self.player]:
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
