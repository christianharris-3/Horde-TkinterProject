import pygame
pygame.init()

from Utility_functions import *

class Data:
    # overlay string: n = not this tile, a = any tile, t = this tile
    
    data = {'None':{'File':'','Hitbox':()},
            'Grass':{'File':'Sprites/Grass.png','Hitbox':()},
            'Rock':{'File':'Sprites/Rock.png','Hitbox':(0.1,0.4,0.8,0.6)},
            'Mossy_Rock': {'File': 'Sprites/Mossy_Rock.png', 'Hitbox': (0.1, 0.2, 0.8, 0.8)},
            'Cobble':{'File':'Sprites/Cobble2.png','Hitbox':(0,0,1,1)},
            'Shop':{'File':'Sprites/Shop.png','Hitbox':(0.5,0.5,0.5)},
            'Tree': {'File': 'Sprites/Tree.png', 'Hitbox': (0.3, 0.5, 0.4, 0.5)},
            'Flowers1': {'File': 'Sprites/Flowers1.png', 'Hitbox': ()},
            'Flowers2': {'File': 'Sprites/Flowers2.png', 'Hitbox': ()},
            'Flowers3': {'File': 'Sprites/Flowers3.png', 'Hitbox': ()}
            }


    for obj in data:
        if obj!='None':
            data[obj]['Image'] = pygame.transform.scale(pygame.image.load(resourcepath(data[obj]['File'])).convert_alpha(),(64,64))
    
    
    

