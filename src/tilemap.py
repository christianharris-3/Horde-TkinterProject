import json
import tkinter as tk
from src.utiles import Vec, RectHitbox, CircleHitbox, Coords
from PIL import Image, ImageTk

class TileData:
    """
    data class to store tiledata
    """
    data = {'Grass':{'File':'Sprites/Grass.png','Hitbox':()},
            'Rock':{'File':'Sprites/Rock.png','Hitbox':(0.1,0.4,0.8,0.6)},
            'Mossy_Rock': {'File': 'Sprites/Mossy_Rock.png', 'Hitbox': (0.1, 0.2, 0.8, 0.8)},
            'Cobble':{'File':'Sprites/Cobble2.png','Hitbox':(0,0,1,1)},
            'Shop':{'File':'Sprites/Shop.png','Hitbox':(0.5,0.5,0.5)},
            'Tree':{'File':'Sprites/Tree.png','Hitbox':(0.3,0.5,0.4,0.5)},
            'Flowers1': {'File': 'Sprites/Flowers1.png', 'Hitbox': ()},
            'Flowers2': {'File': 'Sprites/Flowers2.png', 'Hitbox': ()},
            'Flowers3': {'File': 'Sprites/Flowers3.png', 'Hitbox': ()}}

    @staticmethod
    def image_load():
        for t in TileData.data:
            image = Image.open(TileData.data[t]["File"]).resize((Coords.scale_factor,Coords.scale_factor),
                                                                resample=Image.Resampling.BOX)
            TileData.data[t]["Image"] = ImageTk.PhotoImage(image)

class Tile:
    """
    Tile class stores data about the tile, it stores:
    - position
    - hitbox
    - image
    - tile type
    - if it is a shop tile, data about shop

    """
    def __init__(self, x, y, pixels_per_unit, tile_type):
        self.x = x
        self.y = y
        self.pixels_per_unit = pixels_per_unit
        self.hitbox = None
        self.team = "Tilemap"
        self.tile_type = tile_type
        self.can_be_opened = False
        self.open_shop_text = ""

        self.image = TileData.data[self.tile_type]['Image']
        if len(TileData.data[self.tile_type]['Hitbox'])!=0:
            hb = TileData.data[self.tile_type]['Hitbox']
            if len(hb) == 4:
                self.hitbox = RectHitbox(self.x+hb[0],self.y+hb[1],hb[2],hb[3])
            else:
                self.hitbox = CircleHitbox(self.x + hb[0], self.y + hb[1], hb[2])
        else:
            self.hitbox = None

    def get_image(self):
        return self.image

    def get_hitbox(self):
        return self.hitbox

    def hit_by(self, *_):
        pass


class Tilemap:
    """
    Tilemap is a class to manage:
    - rendering the tilemap
    - generating a collision hash
    - loading a tilemap from a file
    """
    pos_value_convert = 100000

    def __init__(self,levelname):
        self.pixels_per_unit = Coords.scale_factor
        self.tiles = {}
        self.collision_hash = {}
        self.pos = Vec()
        self.entity_data = []

        TileData.image_load()

        self.load_map(f"Data/Maps/{levelname.removesuffix('.json').split('/')[-1]}.json")
        self.load_collision_hash()

    def load_map(self,level_path):
        self.tiles = {}
        self.level_path = level_path
        self.outside_tile = Tile(-1, -1, self.pixels_per_unit, 'Cobble')

        with open(level_path, 'r') as f:
            data = json.load(f)
        self.entity_data = data["entities"]
        self.pos = Vec(*data["map"]["pos"])
        self.tilemap_width = len(data["map"]["tilemap"][0])
        self.tilemap_height = len(data["map"]["tilemap"])
        self.wave_data = data["wave_data"]
        self.difficulty = data["difficulty"]
        self.level_title = data["level_title"]

        for y in range(self.tilemap_height):
            for x in range(self.tilemap_width):
                if data["map"]["tilemap"][y][x] != "None":
                    self.tiles[Tilemap.vec_to_pos_value(self.pos+Vec(x, y))] = Tile(x+self.pos[0], y+self.pos[1], self.pixels_per_unit, data["map"]["tilemap"][y][x])


    def load_collision_hash(self):
        """
        A collision hash is a dictionary that stores all the tiles by there "colcode",
        which is a unique int created from the (x,y) position of the tile. When collision is
        calculated the entity calculates its on colcode and then checks collisions with only tiles
        in the dictionary sharing that colcode. This greatly increases speed of collision detection.
        """
        self.collision_hash = {}
        for t in self.tiles:
            hitbox = self.tiles[t].get_hitbox()
            if hitbox:
                for code in hitbox.colcodes:
                    if code in self.collision_hash:
                        self.collision_hash[code].append(self.tiles[t])
                    else:
                        self.collision_hash[code] = [self.tiles[t]]

    def render_tiles(self, display_canvas, display_hitbox, renderpos_func):
        display_hitbox.set_ints()
        for x in range(display_hitbox.x-1, display_hitbox.x + display_hitbox.width + 1):
            for y in range(display_hitbox.y-1, display_hitbox.y + display_hitbox.height + 1):
                t = Tilemap.vec_to_pos_value((x, y))
                if t in self.tiles:
                    display_canvas.create_image(*renderpos_func(Vec(self.tiles[t].x, self.tiles[t].y)),
                                                image=self.tiles[t].get_image(), tag='game_image', anchor=tk.NW)
                    if self.tiles[t].can_be_opened:
                        display_canvas.create_text(*renderpos_func(Vec(self.tiles[t].x+0.5, self.tiles[t].y-0.2)),
                                                   text=self.tiles[t].open_shop_text,tags='game_image',font=('Segoe Print',15))
                elif not self.get_inside_tilemap(Vec(x,y)):
                    display_canvas.create_image(*renderpos_func(Vec(x,y)),image=self.outside_tile.get_image(),
                                                tag='game_image',anchor=tk.NW)
    @staticmethod
    def pos_value_to_vec(pos_value):
        x = pos_value // Tilemap.pos_value_convert
        y = pos_value % Tilemap.pos_value_convert
        return Vec(x, y)

    @staticmethod
    def vec_to_pos_value(vec):
        return vec[0] * Tilemap.pos_value_convert + vec[1]

    def get_inside_tilemap(self,pos):
        pos-=self.pos
        return pos[0]>=0 and pos[0]<=self.tilemap_width-1 and pos[1]>=0 and pos[1]<=self.tilemap_height-1
