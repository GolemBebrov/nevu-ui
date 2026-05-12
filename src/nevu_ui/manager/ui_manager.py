import sys

import nevu_ui.core.modules as md 
from nevu_ui.window import Window

class Manager:
    __slots__ = ("_window", "running", "force_quit", "background", "fps")
    def __init__(self, window: Window | None = None):
        if window: self.window = window
        self.running = True
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

    def on_draw(self): pass

    def on_update(self): pass
    
    def exit(self): self.running = False
    def on_start(self): pass
    def on_exit(self): pass 
    
    def _on_exit(self):
        self.on_exit()
        if self.force_quit:
            if self.window.is_dtype.pygame or self.window.is_dtype.sdl:
                md.pygame.quit()
            sys.exit()
        
    def first_update(self): pass
    def first_draw(self): pass
    
    def __main_loop(self):
        begin_frame = self.window.display.begin_frame
        end_frame = self.window.display.end_frame
        w_update = self.window.display.update
        
        on_update = self.on_update
        on_draw = self.on_draw
        
        window = self.window
        
        begin_frame()
        self.on_start()
        self.first_update()
        self.first_draw()
        end_frame()
        
        while self.running:
            begin_frame()
            window.clear(self.background)
            
            on_update()
            window.update(None, self.fps)
        
            on_draw()
            
            w_update()
            
            end_frame()
            
        self._on_exit()
        
    def run(self): self.__main_loop()
