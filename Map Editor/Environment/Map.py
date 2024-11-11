import pygame
pygame.init()

from Environment.Environment_Data import Data
from Utility_functions import *



class Tile:
    def __init__(self,name,grid_x,grid_y,cell_size,tilemap_x,tilemap_y):
        self.set_name(name)
        self.grid_x = grid_x
        self.grid_y = grid_y
        self.tilemap_x = tilemap_x
        self.tilemap_y = tilemap_y
        self.cell_size = cell_size
        if self.name != 'None':
            self.image = Data.data[self.name]['Image'].copy()
        else:
            self.image = None
        self.hitboxes = Data.data[self.name]['Hitbox'][:]
    def get_image(self):
        if self.image:
            return self.image
        else:
            return pygame.Surface((1,1))
    def set_name(self,name):
        self.name = name
    def refresh(self,grid,tilemap_x,tilemap_y):
        self.tilemap_x = tilemap_x
        self.tilemap_y = tilemap_y
        if self.name != 'None':
            self.image = Data.data[self.name]['Image'].copy()
        else:
            self.image = None

    def compare_overlay_list(self,overlay_list,overlay_string,tile):
        for i in range(len(overlay_list)):
            if overlay_string[i] != 'a':
                if overlay_string[i] == 't' and overlay_list[i] != tile:
                    return False
                elif overlay_string[i] == 'n' and overlay_list[i] == tile:
                    return False
        return True
        
        
    def get_collide(self,hitbox):
        if type(hitbox) == list:
            return list_list_collide(self.hitboxes,hitbox)
        else:
            return list_obj_collide(self.hitboxes,hitbox)
    
class TileMap:
    def __init__(self,grid,cell_size,x,y):
        self.x = x
        self.y = y
        self.grid_h = len(grid)
        self.grid_w = len(grid[0])
        self.cell_size = cell_size
        
        self.grid = []
        for y in range(self.grid_h):
            self.grid.append([])
            for x in range(self.grid_w):
                self.grid[-1].append(Tile(grid[y][x],x,y,self.cell_size,self.x,self.y))
        self.refresh()

        self.marked_hitbox = []
        
    def render(self,Surf,subsurf_rect):
        Surf.fill((0,128,0))
        min_x = max(subsurf_rect.x//self.cell_size,0)
        min_y = max(subsurf_rect.y//self.cell_size,0)
        max_x = min((subsurf_rect.x+subsurf_rect.w)//self.cell_size,self.grid_w-1)
        max_y = min((subsurf_rect.y+subsurf_rect.h)//self.cell_size,self.grid_h-1)
        for y in range(min_y,max_y+1):
            for x in range(min_x,max_x+1):
                if self.grid[y][x].name != 'None':
                    Surf.blit(self.grid[y][x].get_image(),(x*self.cell_size-subsurf_rect.x,y*self.cell_size-subsurf_rect.y))
        return Surf
                
    def check_collisions(self,obj):
        if len(obj) == 3:
            top_left = self.world_pos_to_grid_pos((obj[0]-obj[2],obj[1]-obj[2]))
            bottom_right = self.world_pos_to_grid_pos((obj[0]+obj[2],obj[1]+obj[2]))
        else:
            top_left = self.world_pos_to_grid_pos((obj[0],obj[1]))
            bottom_right = self.world_pos_to_grid_pos((obj[0]+obj[2],obj[1]+obj[3]))
        
        for y in range(top_left[1],bottom_right[1]+1):
            for x in range(top_left[0],bottom_right[0]+1):
                if self.check_in_grid((x,y)) and self.grid[y][x].get_collide(obj):
                    return True
        return False
    def world_pos_to_grid_pos(self,pos):
        grid_pos = [int((pos[0]-self.x)//self.cell_size),int((pos[1]-self.y)//self.cell_size)]
        return grid_pos
    def check_in_grid(self,grid_pos):
        return grid_pos[0]>-1 and grid_pos[1]>-1 and grid_pos[0]<self.grid_w and grid_pos[1]<self.grid_h  
        
    def get_width(self):
        return self.grid_w
    def get_height(self):
        return self.grid_h

    def set_tile(self,x_pos,y_pos,tile_name):
        if self.check_in_grid((x_pos,y_pos)):
            self.grid[y_pos][x_pos].set_name(tile_name)
            for y in range(y_pos-1,y_pos+2):
                for x in range(x_pos-1,x_pos+2):
                    if self.check_in_grid((x,y)):
                        self.grid[y][x].refresh(self.grid,self.x,self.y)
        else:
            self.extend_grid(x_pos,y_pos)
    def extend_grid(self,x,y):
        self.default_tile = 'None'
        if x<0:
            for a in range(abs(x)):
                for b in self.grid:
                    b.insert(0,Tile(self.default_tile,0,0,self.cell_size,0,0))
                self.x-=self.cell_size
                self.grid_w+=1
        elif x>=self.grid_w:
            for a in range(x-self.grid_w+1):
                for b in self.grid:
                    b.append(Tile(self.default_tile,0,0,self.cell_size,0,0))
                self.grid_w+=1
        if y<0:
            for a in range(abs(y)):
                self.grid.insert(0,[Tile(self.default_tile,0,0,self.cell_size,0,0) for a in range(self.grid_w)])
                self.y-=self.cell_size
        elif y>=self.grid_h:
            for a in range(y-self.grid_h+1):
                self.grid.append([Tile(self.default_tile,0,0,self.cell_size,0,0) for a in range(self.grid_w)])
        self.refresh()
    def refresh(self):
        self.refresh_grid_poses()
        self.refresh_tiles()
    def refresh_grid_poses(self):
        for y,row in enumerate(self.grid):
            for x,tile in enumerate(row):
                tile.grid_x = x
                tile.grid_y = y
        self.grid_h = len(self.grid)
        self.grid_w = len(self.grid[0])
    def refresh_tiles(self):
        for y in self.grid:
            for x in y:
                x.refresh(self.grid,self.x,self.y)
                    
                    
        
        

class Map:
    def __init__(self,ui,cell_size=32,map_name=''):
        self.cell_size = cell_size

        self.map_name = map_name
        self.load_map(map_name)
##        self.tilemap = TileMap(self.grid,cell_size)

    def render_surf(self,subsurf_rect,objects):
        Surf = pygame.Surface((subsurf_rect.w,subsurf_rect.h))
        Surf = self.tilemap.render(Surf,subsurf_rect)

        for o in objects:
            if o.get_collide(subsurf_rect):
                o.active = True
                if o.name != 'None':
                    object_surf = o.render_surf()
                    Surf.blit(object_surf,(o.x-subsurf_rect.x-object_surf.get_width()/2-self.tilemap.x,
                                           o.y-subsurf_rect.y-object_surf.get_height()/2-self.tilemap.y))
            else:
                o.active = False
            

        return Surf

    def check_collisions(self,obj):
        return self.tilemap.check_collisions(obj)
    def get_grid(self):
        self.grid = []
        for y in self.tilemap.grid:
            self.grid.append([])
            for x in y:
                self.grid[-1].append(x.name)
    def get_storable_map(self):
        self.get_grid()
        return {'tilemap':self.grid,
                'pos':[self.tilemap.x/64,self.tilemap.y/64]}

    def load_map(self,info,pos=[0,0]):
        if type(info) == str:
            name = info
            if name == '':
                dat = {'map':{'tilemap':[['Grass']],'pos':[0,0]},
                       'entities':{}}
            else:
                if not '.json' in name:
                    name  = resourcepath('Maps\\'+name+'.json')
                with open(name,'r') as f:
                    dat = json.load(f)
            grid = dat['map']['tilemap']
            pos = dat['map']['pos']
            self.entity_data = dat['entities']
        else:
            grid = info
        self.tilemap = TileMap(grid,self.cell_size,pos[0],pos[1])






    
