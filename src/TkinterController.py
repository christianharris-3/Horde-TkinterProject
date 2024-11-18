import time
from src.Utiles import Vec


class Input:
    def __init__(self,window):
        self.kprs = set()
        self.mpos = Vec()
        self.window = window
        self.refresh_binding()

        self.cheat_code = 'god'
        self.cheat_code_progress = 0
        self.cheat_code_active = False

    def refresh_binding(self):
        self.window.bind('<KeyPress>',self.key_press)
        self.window.bind('<KeyRelease>', self.key_release)
        self.window.bind('<ButtonPress>', self.button_press)
        self.window.bind('<ButtonRelease>', self.button_release)
        self.window.bind('<Motion>',self.mouse_move)

    def key_press(self,event):
        if event.keysym == self.cheat_code[self.cheat_code_progress]:
            self.cheat_code_progress+=1
            if self.cheat_code_progress == len(self.cheat_code):
                self.cheat_code_active = True
                self.cheat_code_progress = 0
        else:
            self.cheat_code_progress = 0

        self.kprs.add(event.keysym)
    def key_release(self,event):
        self.kprs.discard(event.keysym)
    def button_press(self,event):
        self.kprs.add(event.num)
    def button_release(self,event):
        self.kprs.discard(event.num)
    def mouse_move(self,event):
        self.mpos = Vec(event.x, event.y)

    def get_pressed(self,key):
        return key in self.kprs
    def get_mpos(self):
        return self.mpos

    def get_cheatcode_active(self):
        if self.cheat_code_active:
            self.cheat_code_active = False
            return True
        return False

# Function to create a game loop with delta time
def game_looper(loop_function, window, target_fps):
    __game_loop(loop_function, window, target_fps, time.perf_counter())

def __game_loop(loop_function, window, target_fps, tick_start_time):
    time_stamp = time.perf_counter()
    delta_time = (time_stamp - tick_start_time) * target_fps[0]
    tick_start_time = time_stamp

    if not loop_function(delta_time):
        window.after(1,__game_loop, loop_function, window, target_fps, tick_start_time)

