from .window import Window
from .utils import *
import pygame
import sys
class Manager:
    def __init__(self, window: Window = None):
        if window: self.window = window
        self.running = True
        self.background = (0, 0, 0)
        self.fps = 60
        
        self._dirty_mode = True
    @property
    def window(self):
        return self._window
    @window.setter
    def window(self, window: Window):
        if not isinstance(window, Window):
            raise TypeError("window must be a Window object")
        self._window = window
    def draw_loop(self):
        pass
    def _a_system_draw_loop(self):
        pass
    def exit(self):
        self.running = False
    def _b_system_draw_loop(self):
        self.window.clear(self.background)
    def __main_draw_loop(self):
        self._b_system_draw_loop()
        self.draw_loop()
        self._a_system_draw_loop()
    def update_loop(self, events):
        pass
    def _a_system_update_loop(self, events):
        self.window.update(events, self.fps)
    def _b_system_update_loop(self, events):
        pass
    def __main_update_loop(self):
        events = pygame.event.get()
        self._b_system_update_loop(events)
        self.update_loop(events)
        self._a_system_update_loop(events)
    def on_exit(self):
        pygame.quit()
        sys.exit()
    def first_update(self):
        pass
    def first_draw(self):
        pass
    def __main_loop(self):
        self.first_update()
        self.first_draw()
        while self.running:
            self.__main_update_loop()
            self.__main_draw_loop()
            if self._dirty_mode:
                #print(self.window._next_update_dirty_rects)
                pygame.display.update(self.window._next_update_dirty_rects)
                self.window._next_update_dirty_rects = []
            else:
                self.window._next_update_dirty_rects = []
                pygame.display.update()
        self.on_exit()
    def run(self):
        self.__main_loop()

        
