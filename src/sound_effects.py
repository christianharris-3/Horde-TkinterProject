import pygame, random
from src.utiles import resourcepath

pygame.mixer.init()

class SFX:
    sound_effect_map = {'shotgun_fire': {'file': 'shotgun_fire.wav'},
                        'LMG_fire': {'file': 'LMG_fire.wav', 'volume': 0.5},
                        'SMG_fire': {'file': 'SMG_fire.wav'},
                        'shoot': {'file': 'Shoot.wav'},
                        'player_move': {},
                        'player_hurt': [{'file':'playerhurt1.wav'},{'file':'playerhurt2.wav'}],
                        'enemy_hurt': {},
                        'reload': {},
                        'cant_shoot': {'file':'cant_shoot.wav'},
                        'menu_click': {},
                        'throw_grenade': {},
                        'explosion': [{'file':'explosion.wav'},{'file':'boom.wav'}],
                        'force_push': {},
                        'open_shop': {'file':'open_shop.wav'},
                        'close_shop': {'file':'byebye.wav'},
                        'enemy_die': [{'file': 'enemy_dead.wav'},{'file':'death.wav'},{'file':'enemydeath1.wav'},{'file':'enemydeath2.wav'}],
                        'player_die': {'file': 'NOOO.wav'}}

    for sound in sound_effect_map:
        if isinstance(sound_effect_map[sound],dict):
            sound_effect_map[sound] = [sound_effect_map[sound]]
        for info in sound_effect_map[sound]:
            if 'file' in info:
                path = resourcepath('sfx\\' + info['file'])
                info['sound'] = pygame.mixer.Sound(path)
                if 'volume' in info:
                    info['sound'].set_volume(info['volume'])

    @staticmethod
    def play_sound(name):
        if name not in SFX.sound_effect_map:
            print(f'ERROR: no sound named {name}')
        info = random.choice(SFX.sound_effect_map[name])

        if 'file' not in info:
            print(f'no sound for {name}')
        else:
            info['sound'].play()

    @staticmethod
    def player_shoot(weapon):
        if weapon == 'Shotgun':
            SFX.play_sound('shotgun_fire')
        elif weapon == 'LMG':
            SFX.play_sound('LMG_fire')
        elif weapon == 'SMG':
            SFX.play_sound('SMG_fire')
        else:
            SFX.play_sound('shoot')

    @staticmethod
    def player_cant_shoot(weapon):
        SFX.play_sound('cant_shoot')

    @staticmethod
    def player_move():
        SFX.play_sound('player_move')

    @staticmethod
    def menu_button_click():
        SFX.play_sound('menu_click')

    @staticmethod
    def take_damage(entity_type):
        if entity_type == 'Player':
            SFX.play_sound('player_hurt')
        else:
            SFX.play_sound('enemy_hurt')

    @staticmethod
    def explosion():
        SFX.play_sound('explosion')

    @staticmethod
    def reload(weapon):
        SFX.play_sound('reload')

    @staticmethod
    def force_push():
        SFX.play_sound('force_push')

    @staticmethod
    def open_shop():
        SFX.play_sound('open_shop')

    @staticmethod
    def close_shop():
        SFX.play_sound('close_shop')

    @staticmethod
    def player_dead():
        SFX.play_sound('player_die')

    @staticmethod
    def zombie_dead(zombie):
        # SFX.play_sound('explosion')
        SFX.play_sound('enemy_die')