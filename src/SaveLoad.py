from src.Enemy import Slow_Zombie, Fast_Zombie, Big_Zombie, Demon_Zombie, Chonk_Zombie
from src.Player import Player
from src.TileMap import Tilemap
from src.Projectiles import Bullet, SMG_Bullet, Shotgun_Shell, LMG_Bullet, Grenade
from src.Particles import Blood_Splat, Blood_Particle, Bullet_Hit_Particle, Grenade_Fragment, Explosion, Force_Push_Effect
from src.Utiles import Vec, get_now
import json, copy, os, time

### Player
### Shop data
### game stats
### entities
# Projectiles
# Particles?
# Tilemap

class Save:
    entity_type_map = {Slow_Zombie: 'Slow_Zombie',
                       Fast_Zombie: 'Fast_Zombie',
                       Big_Zombie: 'Big_Zombie',
                       Demon_Zombie: 'Demon_Zombie',
                       Chonk_Zombie: 'Chonk_Zombie',
                       Player: 'Player'}
    particle_type_map = {Bullet: 'Bullet', SMG_Bullet: 'SMG_Bullet', Shotgun_Shell: 'Shotgun_Shell',
                         LMG_Bullet: 'LMG_Bullet', Grenade: 'Grenade',
                         Blood_Splat: "Blood_Splat", Blood_Particle: "Blood_Particle",
                         Bullet_Hit_Particle: "Bullet_Hit_Particle",
                         Grenade_Fragment: "Grenade_Fragment", Explosion: "Explosion",
                         Force_Push_Effect: "Force_Push_Effect"}

    @staticmethod
    def save(filename, player,enemies,tilemap,projectiles,particles,shop_data,game_stats, camera_pos, wave_data,
             cheat_info):
        shop_data = copy.copy(shop_data)
        shop_data["Player_Object"] = None
        data = {"player":Save.player(player),"enemies":[Save.entity(e) for e in enemies],
                "game_stats":game_stats,"shop_data":shop_data, "projectiles":[Save.particle(e) for e in projectiles],
                "particles":[Save.particle(e) for e in particles],"tilemap":Save.tilemap(tilemap),
                "camera_pos":camera_pos.tuple(), "filename":filename, "wave_data":Save.wave_data(wave_data),
                'save_timestamp':{'date':get_now()[0], 'time':get_now()[1], 'unix_time':time.time()},'cheat_info':cheat_info}
        with open(f'Data/Game Saves/{filename}.json','w') as f:
            json.dump(data,f)

    @staticmethod
    def entity(e):
        data = {"x": e.x, "y": e.y, "vel": e.vel.tuple(), "health": e.health, "class": Save.entity_type_map[type(e)]}
        return data

    @staticmethod
    def player(e):
        data = Save.entity(e)
        data.update({"shield":e.shield, "weapon":e.active_weapon, "ammo_left":e.ammo_left, "reloading":e.reloading,
                     "reload_timer":e.reload_timer})
        return data

    @staticmethod
    def particle(e):
        data = {"x":e.x,"y":e.y,"vel":e.vel.tuple(),"time_alive":e.time_alive,"radius":e.radius,
                "class":Save.particle_type_map[type(e)],"team":e.team,"time_kill_cutoff":e.time_kill_cutoff}
        return data

    @staticmethod
    def tilemap(e):
        return {"map_name":e.map_name}

    @staticmethod
    def wave_data(dat):
        dat = copy.copy(dat)
        new_zombies = []
        for a in range(len(dat["Zombies"])):
            new_zombies.append({'Num':dat["Zombies"][a]["Num"],
                                'Class':Save.entity_type_map[dat["Zombies"][a]["Class"]]})
        dat["Zombies"] = new_zombies
        return dat


class Load:
    @staticmethod
    def load(filename,control_map, screen_width, screen_height):
        filepath = f'Data/Game Saves/{filename}.json'
        if os.path.isfile(filepath):
            with open(filepath,'r') as f:
                data = json.load(f)
        else:
            print('Failed to Load',filepath)
            return None
        cheat_info = data["cheat_info"]
        player = Load.player(data["player"],control_map, cheat_info, screen_width, screen_height)
        enemies = [Load.enemy(e) for e in data["enemies"]]
        shop_data = data["shop_data"]
        shop_data["Player_Object"] = player
        game_stats = data["game_stats"]
        projectiles = [Load.particle(e,True) for e in data["projectiles"]]
        particles = [Load.particle(e) for e in data["particles"]]
        tilemap = Load.tilemap(data["tilemap"])
        camera_pos = Vec(*data["camera_pos"])
        wave_data = Load.wave_data(data["wave_data"])
        return player,enemies,tilemap,projectiles,particles,shop_data,game_stats,camera_pos,wave_data,cheat_info


    @staticmethod
    def enemy(data):
        for typ in Save.entity_type_map:
            if Save.entity_type_map[typ] == data["class"]:
                if data["class"] != 'Player':
                    e = typ(data["x"],data["y"])
                    e.vel = Vec(*data["vel"])
                    e.health = data["health"]
                    return e
        return False

    @staticmethod
    def player(data, control_map, cheat_info, screen_width, screen_height):
        e = Player(data["x"],data["y"], control_map, cheat_info, screen_width, screen_height)
        e.vel = Vec(*data["vel"])
        e.shield = data["shield"]
        e.set_weapon(data["weapon"])
        e.reloading = data["reloading"]
        e.reload_timer = data["reload_timer"]
        e.ammo_left = data["ammo_left"]
        return e

    @staticmethod
    def particle(data,projectile=False):
        data["vel"] = Vec(*data["vel"])
        for typ in Save.particle_type_map:
            if Save.particle_type_map[typ] == data["class"]:
                if projectile:
                    if typ == Grenade:
                        e = typ(data["x"],data["y"],0,0,data["team"])
                    else:
                        e = typ(data["x"],data["y"],data["vel"].angle(),data["vel"].length(),data["team"])
                else:
                    if typ in [Force_Push_Effect,Explosion]:
                        e = typ(data["x"],data["y"],data["vel"].length())
                    elif typ in [Blood_Particle,Blood_Splat]:
                        e = typ(data["x"],data["y"],data["vel"].angle(),data["vel"].length(),data["radius"])
                    else:
                        e = typ(data["x"], data["y"], data["vel"].angle(), data["vel"].length())
                e.vel = data["vel"]
                e.time_alive = data["time_alive"]
                e.radius = data["radius"]
                e.time_kill_cutoff = data["time_kill_cutoff"]
        return e

    @staticmethod
    def tilemap(data):
        tilemap = Tilemap(data["map_name"])
        return tilemap

    @staticmethod
    def wave_data(data):
        for a in data["Zombies"]:
            for typ in Save.entity_type_map:
                if Save.entity_type_map[typ] == a["Class"]:
                    a["Class"] = typ
        return data