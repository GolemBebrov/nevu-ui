import pygame
import sys

from nevu_ui.window import Window

class Manager:
    def __init__(self, window: Window | None = None):
        if window: self.window = window
        self.running = True
        self.dirty_mode = False
        self.force_quit = True
        self.background = (0, 0, 0)
        self.fps = 60

    @property
    def window(self): return self._window
    @window.setter
    def window(self, window: Window):
        if not isinstance(window, Window):
            raise ValueError("Unexpected window type!")
        self._window = window

    def _before_draw(self): self.window.clear(self.background)
    def on_draw(self): pass
    def _after_draw(self): pass
    
    def __main_draw_loop(self):
        self._before_draw()
        self.on_draw()
        self._after_draw()

    def _before_update(self, events): pass
    def on_update(self, events): pass
    def _after_update(self, events):
        self.window.update(events, self.fps)

    def __main_update_loop(self):
        events = None if self.window.is_dtype.raylib else pygame.event.get()
        self._before_update(events)
        self.on_update(events)
        self._after_update(events)
    
    def exit(self): self.running = False
    def on_start(self): pass
    def on_exit(self): pass 
    
    def _on_exit(self):
        self.on_exit()
        if self.force_quit:
            pygame.quit()
            sys.exit()
        
    def first_update(self): pass
    def first_draw(self): pass
    
    def __main_loop(self):
        self.window.display.begin_frame()
        self.on_start()
        self.first_update()
        self.first_draw()
        self.window.display.end_frame()
        while self.running:
            self.window.display.begin_frame()
            self.__main_update_loop()
            self.__main_draw_loop()
            self.window._next_update_dirty_rects = []
            self.window.display.update()
            self.window.display.end_frame()
        self._on_exit()
        
    def run(self): self.__main_loop()
