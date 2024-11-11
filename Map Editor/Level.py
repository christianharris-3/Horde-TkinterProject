from Entities.Player import Player
from Entities.Enemy import Enemy
from Entities.Objects import *
from Environment.Map_Editor import Map_Editor
from Camera import Camera
import pygame,random

from Environment.Map import Map
from Utility_functions import *
import PyUI as pyui

class Level:
    def __init__(self,ui,name='level 1'):
        self.ui = ui

        self.entity_collide_dict = {}
        self.load_level(name)
##        self.entities = [Player(ui,240,240,'Blue','Metal','Base')]
##                         Enemy(ui,240,360,'Blue','Blue'),
##                         Enemy(ui,400,360,'Blue','Red','Flamer')]
        self.objects = [Box(ui,random.gauss(0,50),random.gauss(0,50)) for i in range(5)]
        self.cameras = [Camera(self.entities[0],pygame.Rect(10,10,ui.screenw-20,ui.screenh-20))]
##        self.map = Map(ui,128,'level 1')

        self.projectiles = []
        self.particles = []

    def load_level(self,name):
        self.map = Map(self.ui,128,name)
        
        self.entities = [Map_Editor.make_spider(self.ui,info) for info in self.map.entity_data]
    def resize(self):
        self.cameras[0].set_display_rect(pygame.Rect(10,10,self.ui.screenw-20,self.ui.screenh-20))
    def game_tick(self,screen):
        screen.fill(pyui.Style.wallpapercol)
        self.calc_entity_collide_dict()
        
        for c in self.cameras:
            c.move()
            c.render(screen,self.map,self.entities,self.objects,self.projectiles,self.particles)

        remove_list = []
        for p in self.entities+self.objects:
            p.gametick(self.map,self.projectiles,self.entity_collide_dict,self.entities,self.ui.deltatime)
            if p.check_dead(self.particles):
                remove_list.append(p)
        for rem in remove_list:
            if rem in self.entities: self.entities.remove(rem)
            else: self.objects.remove(rem)

        for object_list in [self.projectiles,self.particles]:
            remove_list = []
            for p in object_list:
                p.move(self.map,self.entity_collide_dict,self.particles)
                if p.check_finished():
                    remove_list.append(p)
            for rem in remove_list:
                rem.finish(self.particles)
                object_list.remove(rem)
    def calc_entity_collide_dict(self):
        self.entity_collide_dict = {}
        for obj in self.entities+self.objects:
            obj.colgrid_IDs = set()
            for hitbox in obj.get_hitboxes():
                IDs = obj_to_colgrid_IDs(hitbox)
                for i in IDs:
                    if not i in self.entity_collide_dict:
                        self.entity_collide_dict[i] = set()
                    self.entity_collide_dict[i].add(obj)
                    obj.colgrid_IDs.add(i)
                    
            
