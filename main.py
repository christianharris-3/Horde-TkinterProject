import tkinter as tk
import src.TkinterController as TC
from src.Game import Game


class Main:
    def __init__(self):
        self.done = False
        self.window_width = 600
        self.window_height = 600

        self.window = tk.Tk()
        self.window.geometry(f'{self.window_width}x{self.window_height}')
        self.input = TC.Input(self.window)

        self.game_active = True
        self.game = Game(self.window,self.input,self.window_width,self.window_height)

        self.window.bind('<Configure>', self.window_resize)
        TC.game_looper(self.game_loop, self.window)

    def game_loop(self, delta_time):
        self.game.gameloop(delta_time)
        self.game.render_frame()
        return self.done

    def exit(self):
        self.done = True
        self.window.destroy()

    def window_resize(self,event):
        self.window_width = event.width
        self.window_height = event.height
        if self.game_active:
            self.game.window_resize(self.window_width,self.window_height)


if __name__ == "__main__":
    main = Main()
    main.window.mainloop()
