import copy
import pygame

from nevu_ui.fast.nvvector2 import NvVector2
from nevu_ui.widgets import Widget

from nevu_ui.style import (
    Style, default_style
)

class Image(Widget):
    def __init__(self, size: NvVector2 | list, image_path: str, style: Style = default_style, **constant_kwargs):
        super().__init__(size, style, **constant_kwargs)
        self.image_path = image_path
        self._image_original = self.load_image
        self.image = self.image_orig
        self.resize(NvVector2())
        
    def resize(self, resize_ratio: NvVector2):
        super().resize(resize_ratio)
        self.image = pygame.transform.scale(self.image_orig, self._csize)
        
    def draw(self):
        super().draw()
        if not self.visible:
            return
        self.surface.blit(self.image,[0,0])
    
    def copy(self):
        return Image(self._lazy_kwargs['size'], self.image_path, copy.deepcopy(self.style), **self.constant_kwargs)