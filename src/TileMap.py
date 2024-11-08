from src.Utiles import Vec, RectHitbox, Coords
from PIL import Image, ImageTk
import tkinter as tk
import random

class TileData:

    data = {'Grass':{'File':'Sprites/Grass.png','Hitbox':()},
            'Rock':{'File':'Sprites/Rock.png','Hitbox':(0.1,0.4,0.8,0.6)},
            'Cobble':{'File':'Sprites/Cobble.png','Hitbox':(0,0,1,1)}}

    @staticmethod
    def image_load():
        for t in TileData.data:
            image = Image.open(TileData.data[t]["File"]).resize((Coords.scale_factor,Coords.scale_factor),
                                                                resample=Image.Resampling.BOX)
            TileData.data[t]["Image"] = ImageTk.PhotoImage(image)

class Tile:
    def __init__(self, x, y, pixels_per_unit, tile_type):
        self.x = x
        self.y = y
        self.pixels_per_unit = pixels_per_unit
        self.hitbox = None
        self.team = "Tilemap"
        self.tile_type = tile_type

        self.image = TileData.data[self.tile_type]['Image']
        if len(TileData.data[self.tile_type]['Hitbox'])!=0:
            hb = TileData.data[self.tile_type]['Hitbox']
            self.hitbox = RectHitbox(self.x+hb[0],self.y+hb[1],hb[2],hb[3])
        else:
            self.hitbox = None

    def get_image(self):
        return self.image

    def get_hitbox(self):
        return self.hitbox

    def hit_by(self, *_):
        pass


class Tilemap:
    pos_value_convert = 100000

    def __init__(self, pixels_per_unit):
        self.pixels_per_unit = pixels_per_unit
        self.tiles = {}
        self.collision_hash = {}

        TileData.image_load()
        self.load_tiles()
        self.load_collision_hash()

    def load_tiles(self):
        self.tiles = {}
        self.tilemap_width = 40
        self.tilemap_height = 40
        self.outside_tile = Tile(-1,-1,self.pixels_per_unit,'Cobble')
        map_ = [[8 if (x==0 or x==39 or y==0 or y==39) else random.randint(0, 10) for x in range(self.tilemap_width)] for y in range(self.tilemap_height)]
        map_[1][1] = 0

        for y in range(len(map_)):
            for x in range(len(map_[0])):
                if map_[y][x] == 10:
                    self.tiles[Tilemap.vec_to_pos_value((x, y))] = Tile(x, y, self.pixels_per_unit, 'Grass')
                elif map_[y][x] == 9:
                    self.tiles[Tilemap.vec_to_pos_value((x, y))] = Tile(x, y, self.pixels_per_unit, 'Rock')
                elif map_[y][x] == 8:
                    self.tiles[Tilemap.vec_to_pos_value((x, y))] = Tile(x, y, self.pixels_per_unit, 'Cobble')

    def load_collision_hash(self):
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
                elif not self.get_inside_tilemap((x,y)):
                    display_canvas.create_image(*renderpos_func(Vec(x,y)),image=self.outside_tile.get_image(),tag='game_image',anchor=tk.NW)
    @staticmethod
    def pos_value_to_vec(pos_value):
        x = pos_value // Tilemap.pos_value_convert
        y = pos_value % Tilemap.pos_value_convert
        return Vec(x, y)

    @staticmethod
    def vec_to_pos_value(vec):
        return vec[0] * Tilemap.pos_value_convert + vec[1]

    def get_inside_tilemap(self,pos):
        return pos[0]>=0 and pos[0]<=self.tilemap_width-1 and pos[1]>=0 and pos[1]<=self.tilemap_height-1
