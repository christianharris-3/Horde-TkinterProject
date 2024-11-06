import time
from src.Utiles import Vec


class Input:
    def __init__(self,window):
        self.kprs = set()
        self.mpos = Vec()
        window.bind('<KeyPress>',self.key_press)
        window.bind('<KeyRelease>', self.key_release)
        window.bind('<ButtonPress>', self.button_press)
        window.bind('<ButtonRelease>', self.button_release)
        window.bind('<Motion>',self.mouse_move)

    def key_press(self,event):
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

# Function to create a game loop with delta time
def game_looper(loop_function, window, target_fps=60):
    __game_loop(loop_function, window, target_fps, time.perf_counter())

def __game_loop(loop_function, window, target_fps, tick_start_time):
    time_stamp = time.perf_counter()
    delta_time = (time_stamp - tick_start_time) * target_fps
    tick_start_time = time_stamp

    if not loop_function(delta_time):
        window.after(1,__game_loop, loop_function, window, target_fps, tick_start_time)

