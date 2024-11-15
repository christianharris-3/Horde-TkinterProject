from src.Enemy import Slow_Zombie, Fast_Zombie, Big_Zombie, Demon_Zombie
from src.Player import Player

# Player
# Shop data
### entities
# Projectiles
# Particles?
# Tilemap

class Save:
    entity_type_map = {Slow_Zombie: 'Slow_Zombie',
                       Fast_Zombie: 'Fast_Zombie',
                       Big_Zombie: 'Big_Zombie',
                       Demon_Zombie: 'Demon_Zombie',
                       Player: 'Player'}
    @staticmethod
    def entity(e):
        data = {"x": e.x, "y": e.y, "vel": e.vel, "health": e.health, "type": Save.entity_type_map[type(e)]}
        return data

    @staticmethod
    def player(e):
        data = Save.entity(e)
        data.update({"shield":e.shield, "weapon":e.active_weapon, "ammo_left":e.ammo_left, "reloading":e.reloading,
                     "reload_timer":e.reload_timer})
        return data


    def save(self,player,enemies,tilemap,projectiles,particles,shop_data):
        pass

class Load:
    @staticmethod
    def enemy(data):
        for typ in Save.entity_type_map:
            if Save.entity_type_map[typ] == data["type"]:
                if data["type"] != 'Player':
                    e = typ(data["x"],data["y"])
                    e.vel = data["vel"]
                    e.health = data["health"]
                    return e
        return False

    @staticmethod
    def player(data, control_map):
        e = Player(data["x"],data["y"],control_map, )
