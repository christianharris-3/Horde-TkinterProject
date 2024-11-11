import pygame
pygame.init()

from Utility_functions import *

class Data:
    # overlay string: n = not this tile, a = any tile, t = this tile
    
    data = {'None':{'File':'','Hitbox':()},
            'Grass':{'File':'Sprites\Grass.png','Hitbox':()},
            'Rock':{'File':'Sprites\Rock.png','Hitbox':(0.1,0.4,0.8,0.6)},
            'Cobble':{'File':'Sprites\Cobble2.png','Hitbox':(0,0,1,1)}}


    for obj in data:
        if obj!='None':
            data[obj]['Image'] = pygame.transform.scale(pygame.image.load(resourcepath(data[obj]['File'])).convert_alpha(),(64,64))
    
    
    

