import pygame
from PIL import Image

from nevu_ui.fast.nvvector2 import NvVector2
from nevu_ui.widgets import Widget
from nevu_ui.utils import time

from nevu_ui.style import (
    Style, default_style
)

class Gif(Widget):
    def __init__(self,size,gif_path=None,style:Style=default_style,frame_duration=100):
        super().__init__(size,style)
        self.gif_path = gif_path
        self.frames = []
        self.frame_index = 0
        self.frame_duration = frame_duration
        self.last_frame_time = 0
        self.original_size = size
        self._load_gif()
        self.current_time = 0
        self.scaled_frames = None
        self.resize(self._resize_ratio)
        
    def _load_gif(self):
        if not self.gif_path: return
        
        try:
            gif = Image.open(self.gif_path)
            for i in range(gif.n_frames):
                gif.seek(i)
                frame_rgb = gif.convert('RGB')
                frame_surface = pygame.image.frombuffer(frame_rgb.tobytes(), frame_rgb.size, 'RGB')
                self.frames.append(frame_surface)
            
        except FileNotFoundError:
            print(f"Error: GIF file not found at {self.gif_path}")
        except Exception as e:
            print(f"Error loading GIF: {e}")

    def resize(self, resize_ratio: NvVector2):
        super().resize(resize_ratio)
        if self.frames:
            self.scaled_frames = [pygame.transform.scale(frame,[self.size[0]*self._resize_ratio[0],self.size[1]*self._resize_ratio[1]]) for frame in self.frames]
        self._changed = True

    def draw(self):
        super().draw()
        if not self.visible:
            return
        if not self.frames:
            return
        
        self.current_time += 1*time.delta_time*100
        
        if self.current_time > self.frame_duration:
             self.frame_index = (self.frame_index + 1) % len(self.frames)
             self.current_time = 0
             self._changed = True
             
        if len(self.frames) == 0:
            self._changed = False
            
        if isinstance(self, Gif) and self._changed:
            self._changed = False
            if self.scaled_frames:
                frame_to_draw = self.scaled_frames[self.frame_index] if hasattr(self,"scaled_frames") else self.frames[self.frame_index]
                self.surface.blit(frame_to_draw,(0,0))
