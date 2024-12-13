import pygame, random, time
from src.utiles import resourcepath

pygame.mixer.init()

class SFX:
    sound_data = {'not_pausable_sounds':['open_shop','close_shop','menu_click'],
                  'sound_cooldown':{'player_move':0.2}}
    sound_cooldown_tracker = {}

    base_sound_map = {'shotgun_fire': {'file': 'shotgun_fire.wav'},
                      'shotgun_reload':{'file': 'shotgun reload.wav'},
                      'LMG_fire': {'file': 'LMG_fire.wav','volume':0.4},
                      'LMG_reload': {'file': 'LMG_reload.wav'},
                      'SMG_fire': {'file': 'SMG_fire.wav','volume':0.4},
                      'SMG_reload':{'file': 'SMG_reload.wav'},
                      'pistol_fire':{'file': 'pistol_fire.wav'},
                      'pistol_reload':{'file': 'pistol_reload.wav'},
                      'cant_shoot': {'file': 'cant_shoot.wav'},
                      'player_move_1': {'file': 'player_move3.wav', 'volume':0.4},
                      'player_move_2': {'file': 'player_move4.wav', 'volume':0.4},
                      'player_hurt': [{'file':'player_hurt1.wav'},{'file':'player_hurt2.wav'},{'file':'player_hurt3.wav'},{'file':'player_hurt4.wav'}],
                      'player_die': {'file':'player_die.wav'},
                      'enemy_hurt': [{'file': 'zombie_hurt1.wav'}, {'file': 'zombie_hurt2.wav'}, {'file': 'zombie_hurt3.wav'}],
                      'menu_click': {'file': 'menu_press.wav', 'volume':0.4},
                      'throw_grenade': {'file': 'throw_grenade.wav', 'volume':0.5},
                      'explosion': {'file': 'explosion.wav'},
                      'force_push': {'file': 'force_push.wav'},
                      'open_shop': {'file': 'menu_press.wav', 'volume':0.4},
                      'close_shop': {'file': 'menu_press.wav', 'volume':0.4},
                      'enemy_die': [{'file':'enemy_death.wav'},{'file':'enemy_death2.wav'},{'file':'enemy_death3.wav'}],
                      }

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

    use_eight_bit_sounds = False
    use_improved_sounds = False

    paused = False
    paused_queue = []
    pygame.mixer.set_num_channels(20)
    game_sound = [pygame.mixer.Channel(a) for a in range(1,20)]
    game_sound_index = 0
    paused_sound = pygame.mixer.Channel(0)

    volume = 1

    walk_toggle = False

    for sound_map in [base_sound_map]+[eight_bit_sounds]*use_eight_bit_sounds+[improved_sounds]*use_improved_sounds:
        for sound in sound_map:
            if isinstance(sound_map[sound],dict):
                sound_map[sound] = [sound_map[sound]]
            for info in sound_map[sound]:
                if 'file' in info:
                    path = resourcepath('sfx\\' + info['file'])
                    info['sound'] = pygame.mixer.Sound(path)
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
            # Manage sound cooldown
            if not SFX.get_cooldown(name):
                return

            # Set sounds volume
            vol = SFX.volume
            if 'volume' in info:
                vol = info['volume'] * SFX.volume
            info['sound'].set_volume(vol)

            # Play sound using different sound channels for pausable sounds that can play ontop of each other
            if name in SFX.sound_data['not_pausable_sounds']:
                SFX.paused_sound.play(info['sound'])
            else:
                SFX.game_sound[SFX.game_sound_index].play(info['sound'])
                SFX.game_sound_index = (SFX.game_sound_index+1)%len(SFX.game_sound)

    @staticmethod
    def get_cooldown(name):
        if name in SFX.sound_data['sound_cooldown']:
            if name in SFX.sound_cooldown_tracker:
                if time.perf_counter() > SFX.sound_cooldown_tracker[name] + SFX.sound_data['sound_cooldown'][name]:
                    SFX.sound_cooldown_tracker.pop(name)
                return False
            else:
                SFX.sound_cooldown_tracker[name] = time.perf_counter()
        return True

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
        match weapon:
            case 'LMG': SFX.play_sound('LMG_fire')
            case 'SMG': SFX.play_sound('SMG_fire')
            case 'Pistol': SFX.play_sound('pistol_fire')
            case 'Shotgun': SFX.play_sound('shotgun_fire')

    @staticmethod
    def player_cant_shoot(weapon):
        SFX.play_sound('cant_shoot')

    @staticmethod
    def player_move():
        if not SFX.get_cooldown('player_move'):
            return
        SFX.walk_toggle = not SFX.walk_toggle
        if SFX.walk_toggle:
            SFX.play_sound('player_move_1')
        else:
            SFX.play_sound('player_move_2')

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
        match weapon:
            case 'LMG': SFX.play_sound('LMG_reload')
            case 'SMG': SFX.play_sound('SMG_reload')
            case 'Pistol': SFX.play_sound('pistol_reload')
            case 'Shotgun': SFX.play_sound('shotgun_reload')

    @staticmethod
    def force_push():
        SFX.play_sound('force_push')

    @staticmethod
    def throw_grenade():
        SFX.play_sound('throw_grenade')

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
        SFX.play_sound('enemy_die')
