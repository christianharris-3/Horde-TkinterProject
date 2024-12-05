import pygame, random
from src.utiles import resourcepath

pygame.mixer.init()

class SFX:
    sound_data = {'not_pausable_sounds':['open_shop','close_shop','menu_click']}

    base_sound_map = {'shotgun_fire': {},
                      'shotgun_reload':{'file': 'shotgun_reload.wav'},
                      'LMG_fire': {},
                      'LMG_reload': {'file': 'LMG_reload.wav'},
                      'SMG_fire': {},
                      'cant_shoot': {'file': 'cant_shoot.wav'},
                      'shoot': {},
                      'player_move': {},
                      'player_hurt': {},
                      'enemy_hurt': {},
                      'menu_click': {},
                      'throw_grenade': {},
                      'explosion': {},
                      'force_push': {},
                      'open_shop': {},
                      'close_shop': {},
                      'enemy_die': {},
                      'player_die': {}}

    eight_bit_sounds = {'explosion': {'file':'8bit/explosion.wav'},
                        'shotgun_fire': {'file': '8bit/shotgun_fire.wav'},
                        'LMG_fire': {'file': '8bit/LMG_fire.wav', 'volume': 0.5},
                        'SMG_fire': {'file': '8bit/SMG_fire.wav'},
                        'shoot': {'file': '8bit/Shoot.wav'},
                        }

    improved_sounds = {'player_hurt': [{'file':'bs/playerhurt1.wav'},{'file':'bs/playerhurt2.wav'}],
                       'enemy_die': [{'file': 'bs/enemy_dead.wav'},{'file':'bs/death.wav'},{'file':'bs/enemydeath1.wav'},{'file':'bs/enemydeath2.wav'}],
                       'explosion': [{'file':'bs/boom.wav'}],
                       'player_die': {'file': 'bs/NOOO.wav'},
                       'open_shop': {'file': 'bs/open_shop.wav'},
                       'close_shop': {'file': 'bs/byebye.wav'},
                       'menu_click': [{'file': 'bs/menu_sound.wav'},{'file':'bs/menu_sound2.wav'}],
                       }

    use_eight_bit_sounds = True
    use_improved_sounds = True

    paused = False
    paused_queue = []
    game_sound = [pygame.mixer.Channel(a) for a in range(1,8)]
    game_sound_index = 0
    paused_sound = pygame.mixer.Channel(0)

    for sound_map in [base_sound_map,eight_bit_sounds,improved_sounds]:
        for sound in sound_map:
            if isinstance(sound_map[sound],dict):
                sound_map[sound] = [sound_map[sound]]
            for info in sound_map[sound]:
                if 'file' in info:
                    path = resourcepath('sfx\\' + info['file'])
                    info['sound'] = pygame.mixer.Sound(path)
                    if 'volume' in info:
                        info['sound'].set_volume(info['volume'])
                    # if sound_map is improved_sounds:
                        # info['sound'].set_volume(0.01)

    @staticmethod
    def set_sound_loading(eight_bit=False,improved_sounds=False):
        SFX.use_eight_bit_sounds = eight_bit
        SFX.use_improved_sounds = improved_sounds

    @staticmethod
    def play_sound(name):
        if SFX.paused and (name not in SFX.sound_data['not_pausable_sounds']):
            print(name,SFX.sound_data['not_pausable_sounds'])
            SFX.paused_queue.append(name)
            return

        if name in SFX.improved_sounds and SFX.use_improved_sounds:
            info = random.choice(SFX.improved_sounds[name])
        elif name in SFX.eight_bit_sounds and SFX.use_eight_bit_sounds:
            info = random.choice(SFX.eight_bit_sounds[name])
        elif name in SFX.base_sound_map:
            info = random.choice(SFX.base_sound_map[name])
        else:
            print(f'ERROR: no sound named {name}')
            return

        if 'file' not in info:
            print(f'no sound for {name}')
        else:
            if name in SFX.sound_data['not_pausable_sounds']:
                SFX.paused_sound.play(info['sound'])
            else:
                SFX.game_sound[SFX.game_sound_index].play(info['sound'])
                SFX.game_sound_index = (SFX.game_sound_index+1)%len(SFX.game_sound)

    @staticmethod
    def set_paused(paused):
        SFX.paused = paused
        if SFX.paused:
            for game_sound in SFX.game_sound:
                game_sound.pause()
        else:
            for game_sound in SFX.game_sound:
                game_sound.unpause()
            for name in SFX.paused_queue:
                SFX.play_sound(name)
            SFX.paused_queue = []

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
    def menu_button_click(button_typ):
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
        if weapon == 'LMG':
            SFX.play_sound('LMG_reload')
        elif weapon == 'Shotgun':
            SFX.play_sound('shotgun_reload')
        else:
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