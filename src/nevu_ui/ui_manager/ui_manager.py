import pygame
import sys

from nevu_ui.window import Window

class Manager:
    def __init__(self, window: Window | None = None):
        if window: self.window = window
        self.running = True
        self._dirty_mode = False
        self._force_quit = True
        self.background = (0, 0, 0)
        self.fps = 60

    @property
    def window(self):
        return self._window
    @window.setter
    def window(self, window: Window):
        if not isinstance(window, Window):
            raise ValueError("Unexpected window type!")
        self._window = window

    def _before_draw_loop(self):
        self.window.clear(self.background)
    def draw_loop(self):
        pass
    def _after_draw_loop(self):
        pass

    def __main_draw_loop(self):
        self._before_draw_loop()
        self.draw_loop()
        self._after_draw_loop()

    def _before_update_loop(self, events):
        pass
    def update_loop(self, events):
        pass
    def _after_update_loop(self, events):
        self.window.update(events, self.fps)

    def __main_update_loop(self):
        events = pygame.event.get()
        self._before_update_loop(events)
        self.update_loop(events)
        self._after_update_loop(events)
    
    def exit(self):
        self.running = False
    
    def on_start(self):
        pass
    
    def on_exit(self):
        pass 
    
    def _on_exit(self):
        self.on_exit()
        if self._force_quit:
            pygame.quit()
            sys.exit()
        
    def first_update(self):
        pass
    
    def first_draw(self):
        pass
    
    def __main_loop(self):
        self.on_start()
        self.first_update()
        self.first_draw()
        while self.running:
            self.__main_update_loop()
            self.__main_draw_loop()
            if self._dirty_mode:
                pygame.display.update(self.window._next_update_dirty_rects)
            else:
                pygame.display.update()
            self.window._next_update_dirty_rects = []
        self._on_exit()
        
    def run(self):
        self.__main_loop()
