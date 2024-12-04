import json
import copy
import os
import time
from src.enemy import SlowZombie, FastZombie, BigZombie, DemonZombie, ChonkZombie
from src.player import Player
from src.tilemap import Tilemap
from src.projectiles import Bullet, SMG_Bullet, Shotgun_Shell, LMG_Bullet, Grenade
from src.particles import Blood_Splat, Blood_Particle, Bullet_Hit_Particle, Grenade_Fragment, Explosion, Force_Push_Effect, Text_Particle
from src.utiles import Vec, get_now, get_difficulty_data, resourcepath


class Save:
    """
    Save object takes lots of game variables and converts them to one dictionary to be store in json
    This object stores:
     - player data     : position, velocity, health, shield, weapon, current ammo, reload state/timer, time since hit
     - enemy data      : position, velocity, health, enemy type
     - projectile data : position, velocity, size, projectile type
     - particle data   : position, velocity, size, particle type
     - camera data     : position
     - game stats      : current stats about the game, e.g. score, damage dealt, current wave
     - shop data       : coins, what guns are owned, num of grenades/force pushes owned
     - cheat info      : immortal, inf ammo, inf abilities, damage/spawn time/speed of time multipler
     - current wave    : zombies left of each type in the current wave
     - level           : the current level being played
     - timestamp       : a timestamp of when the save occured

    --- import methods and attributes ---
    method    : save     The main and only method used externally to this class, used to store a gamestate
    """

    entity_type_map = {SlowZombie: 'Slow_Zombie',
                       FastZombie: 'Fast_Zombie',
                       BigZombie: 'Big_Zombie',
                       DemonZombie: 'Demon_Zombie',
                       ChonkZombie: 'Chonk_Zombie',
                       Player: 'Player'}
    particle_type_map = {Bullet: 'Bullet', SMG_Bullet: 'SMG_Bullet', Shotgun_Shell: 'Shotgun_Shell',
                         LMG_Bullet: 'LMG_Bullet', Grenade: 'Grenade',
                         Blood_Splat: "Blood_Splat", Blood_Particle: "Blood_Particle",
                         Bullet_Hit_Particle: "Bullet_Hit_Particle",
                         Grenade_Fragment: "Grenade_Fragment", Explosion: "Explosion",
                         Force_Push_Effect: "Force_Push_Effect",
                         Text_Particle: "Text_Particle"}

    @staticmethod
    def save(filename, player,enemies,tilemap,projectiles,particles,
             shop_data,game_stats, camera_pos, wave_data,
             cheat_info, score_add_timer):
        shop_data = copy.copy(shop_data)
        shop_data["Player_Object"] = None
        data = {"player":Save.player(player),"enemies":[Save.entity(e) for e in enemies],
                "game_stats":game_stats,"shop_data":shop_data, "projectiles":[Save.particle(e) for e in projectiles],
                "particles":[Save.particle(e) for e in particles],"camera_pos":camera_pos.tuple(),
                "filename":filename, "wave_data":Save.wave_data(wave_data),
                'save_timestamp':{'date':get_now()[0], 'time':get_now()[1], 'unix_time':time.time()},
                'cheat_info':cheat_info,'level':{'path':tilemap.level_path,'title':tilemap.level_title},
                'score_add_timer':score_add_timer}
        if not os.path.exists('Data/Game Saves'):
            os.makedirs('Data/Games Save')
        with open(f'Data\\Game Saves\\{filename}.json','w') as f:
            json.dump(data,f)

    @staticmethod
    def entity(e):
        data = {"x": e.x, "y": e.y, "vel": e.vel.tuple(), "health": e.health, "class": Save.entity_type_map[type(e)]}
        return data

    @staticmethod
    def player(e):
        data = Save.entity(e)
        data.update({"shield":e.shield, "weapon":e.active_weapon, "ammo_left":e.ammo_left, "reloading":e.reloading,
                     "reload_timer":e.reload_timer, "time_since_hit":e.time_since_hit})
        return data

    @staticmethod
    def particle(e):
        data = {"x":e.x,"y":e.y,"vel":e.vel.tuple(),"time_alive":e.time_alive,"radius":e.radius,
                "class":Save.particle_type_map[type(e)],"team":e.team,"time_kill_cutoff":e.time_kill_cutoff}
        if data["class"] == "Text_Particle":
            data["font"] = e.font
            data["text"] = e.shape
        return data

    @staticmethod
    def tilemap(e):
        return {"level_path":e.level_path}

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
    """
    Load object unpacks all of the info from a given json file and loads the gamestate
    Loads all data stored by Save class

    --- import methods and attributes ---
    function : load     The main and only method used externally to this class, used to load a gamestate
    """
    @staticmethod
    def load(filename,control_map, screen_width, screen_height):
        filepath = f'Data\\Game Saves\\{filename}.json'
        if os.path.isfile(filepath):
            with open(filepath,'r') as f:
                data = json.load(f)
        else:
            print('Failed to Load',filepath)
            return None
        cheat_info = data["cheat_info"]
        tilemap = Tilemap(data["level"]["path"])
        difficulty_data = get_difficulty_data(tilemap.difficulty)
        player = Load.player(data["player"],control_map, cheat_info, screen_width, screen_height)
        enemies = [Load.enemy(e,difficulty_data) for e in data["enemies"]]
        shop_data = data["shop_data"]
        shop_data["Player_Object"] = player
        game_stats = data["game_stats"]
        projectiles = [Load.particle(e,True) for e in data["projectiles"]]
        particles = [Load.particle(e) for e in data["particles"]]
        camera_pos = Vec(*data["camera_pos"])
        wave_data = Load.wave_data(data["wave_data"])
        score_add_timer = data["score_add_timer"]
        return player,enemies,tilemap,projectiles,particles,shop_data,game_stats,camera_pos,wave_data,cheat_info,score_add_timer


    @staticmethod
    def enemy(data,difficulty_data):
        for typ in Save.entity_type_map:
            if Save.entity_type_map[typ] == data["class"]:
                if data["class"] != 'Player':
                    e = typ(data["x"],data["y"],difficulty_data)
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
        e.time_since_hit = data["time_since_hit"]
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
                    elif typ in [Text_Particle]:
                        e = typ(data["x"], data["y"], data["vel"].length(), data["text"], data["font"])
                    else:
                        e = typ(data["x"], data["y"], data["vel"].angle(), data["vel"].length())
                e.vel = data["vel"]
                e.time_alive = data["time_alive"]
                e.radius = data["radius"]
                e.time_kill_cutoff = data["time_kill_cutoff"]
        return e

    @staticmethod
    def wave_data(data):
        for a in data["Zombies"]:
            for typ in Save.entity_type_map:
                if Save.entity_type_map[typ] == a["Class"]:
                    a["Class"] = typ
        return data