import copy
import pygame

from nevu_ui.fast.nvvector2 import NvVector2
from nevu_ui.widgets import Widget, Button
from nevu_ui.utils import mouse
from nevu_ui.core_types import Align

from nevu_ui.style import (
    Style, default_style
)

class SliderBar(Widget):
    def __init__(self, begin_val: int, end_val: int, size, style, step: int = 1, freedom=False,default=-999.999123):
        self.button = Button(lambda: None, "", [size[1]/1.2, size[1]/1.2], style, active=False, freedom=False)
        super().__init__(size, style, freedom)
        self.begin_val = begin_val 
        self.end_val = end_val      
        self.step = step          
        self.current_value = begin_val 
        self.is_dragging = False    
        self.slider_pos = 0         
        if default!= -999.999123:
            self.current_value = default
        self._update_slider_position()  
    @property
    def style(self):
        return self._style()
    @style.setter
    def style(self,style:Style):
        self._update_image()
        self.cached_gradient = None
        self._changed = True
        self._style = copy.deepcopy(style)
        self.button.style = copy.deepcopy(style)
        
    def _update_slider_position(self):
        """Обновляет позицию ползунка на основе текущего значения"""
        range_val = self.end_val - self.begin_val
        if range_val == 0:
            self.slider_pos = 0
        else:
            self.slider_pos = (self.current_value - self.begin_val) / range_val * self.size[0]

    def _update_value_from_position(self):
        range_val = self.end_val - self.begin_val
        if range_val == 0:
            self.current_value = self.begin_val
        else:
            self.current_value = self.begin_val + (self.slider_pos / self.size[0]) * range_val
            self.current_value = round(self.current_value / self.step) * self.step
            self.current_value = max(self.begin_val, min(self.end_val, self.current_value))

    def secondary_update(self, *args):
        super().secondary_update(*args)
        if not self.active: return
        if mouse.left_down or mouse.left_fdown:
            if self.get_rect().collidepoint(mouse.pos): self.is_dragging = True
        else: self.is_dragging = False
        if self.is_dragging:
            self._changed = True
            relative_x = mouse.pos[0] - self.master_coordinates[0]
            self.slider_pos = max(0, min(self.size[0], relative_x))
            self._update_value_from_position()
            self._update_slider_position()
        self.button.coordinates = NvVector2()
        self.button.master_coordinates = NvVector2()
        self.button.update()
    def draw(self):
        if not self.visible:return
        super().draw()
        #pygame.draw.line(self.surface, self.style.bordercolor,(0, self.size[1] // 2), (self.size[0], self.size[1] // 2), 6)
        slider_rect = pygame.Rect(max(0,min(self.slider_pos - self.button.size[0]/2,self.size[0]-self.button.size[0])),(self.size[1]- self.button.size[1])/2,  self.button.size[0], self.button.size[1])
        #pygame.draw.rect(self.surface, self.style.secondarycolor, slider_rect)
        self.button.draw()
        self.surface.blit(self.button.surface, slider_rect)
        self.bake_text(str(self.current_value), alignx=Align.CENTER, aligny=Align.CENTER)
        assert self._text_surface is not None and self._text_rect is not None
        self.surface.blit(self._text_surface, self._text_rect)
        if self._changed:
            self._changed = False