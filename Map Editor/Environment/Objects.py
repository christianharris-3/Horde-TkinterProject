import pygame,json
pygame.init()

from Environment.Environment_Data import Data
from Utility_functions import *



class Object:
    def __init__(self,x,y,angle,name):
        self.name = name
        self.stats = Data.objects[self.name]['Stats']
        self.width = self.stats['Width']
        self.height = self.stats['Height']
        self.mass = self.stats['Mass']
        self.health = self.stats['Health']

        self.x = x
        self.y = y
        self.angle = angle

        self.base_image = Data.objects[self.name]['Image'].copy()
        self.image = pygame.transform.scale(self.base_image,(self.width,self.height))
        self.image = pygame.transform.rotate(self.image,self.angle)
        

    def render_surf(self):
        return self.image

    def get_hitboxes(self):
        return [(self.x-self.width/2,self.y-self.height/2,self.width,self.height)]

    def get_collide(self,obj):
        return list_obj_collide(self.get_hitboxes(),obj)

    def take_damage(damage,impact_vel=-1,knockback=0):
        if self.immunity_frames<0:
            if impact_vel != -1:
                self.velocity+=(impact_vel*knockback)/self.mass
            self.immunity_frames = 1
            self.health-=damage


class Box(Object):
    def __init__(self,x,y,angle=0):
        super().__init__(x,y,angle,'Box')
        
