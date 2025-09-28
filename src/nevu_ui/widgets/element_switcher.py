import copy
import pygame
import numpy as np

from nevu_ui.fast.nvvector2 import NvVector2
from nevu_ui.widgets import Widget
from nevu_ui.utils import mouse

from nevu_ui.style import (
    Style, default_style
)

class ElementSwitcher(Widget):
    def __init__(self, size, elements, style: Style = default_style,on_change_function=None):
        super().__init__(size, style)
        self.elements = elements
        self.current_index = 0
        self.button_padding = 10
        self.arrow_width = 10
        self.bake_text(self.current_element_text())
        self.on_change_function = on_change_function
    def current_element_text(self):
        if not self.elements: return ""
        return f"{self.elements[self.current_index]}"
    def next_element(self):
        self.current_index = (self.current_index + 1) % len(self.elements)
        self.bake_text(self.current_element_text())
        if self.on_change_function: self.on_change_function(self.current_element_text())
    def previous_element(self):
        self.current_index = (self.current_index - 1) % len(self.elements)
        self.bake_text(self.current_element_text())
        if self.on_change_function: self.on_change_function(self.current_element_text())
    def set_index(self,index:int):
        self.current_index = index
        self.bake_text(self.current_element_text())
        if self.on_change_function: self.on_change_function(self.current_element_text())
    @property
    def hovered(self):
        return self._hovered
    @hovered.setter
    def hovered(self,value:bool):
        if hasattr(self, "_hovered") and self.hovered == value:
            return
        self._hovered = value
        if not hasattr(self, "elements"):
            self.add_on_first_update(lambda: self.bake_text(self.current_element_text()))
            return
        self.bake_text(self.current_element_text())

    def update(self, *args):
        super().update(*args)
        if not self.active:
            return
        if mouse.left_up and self.hovered:
            click_pos_relative = np.array(mouse.pos) - self.master_coordinates
            center_x = self.surface.get_width() / 2
            button_width = self._text_rect.width / 2 + self.button_padding + self.arrow_width * 2
            if click_pos_relative[0] < center_x - button_width / 2: self.previous_element()
            elif click_pos_relative[0] > center_x + button_width / 2: self.next_element()

    def draw(self):
        super().draw()
        if not self.visible:
            return
        text_center_x = self.surface.get_width() / 2
        text_center_y = self.surface.get_height() / 2
        left_button_center_x = text_center_x - self._text_rect.width / 2 - self.button_padding - self.arrow_width
        right_button_center_x = text_center_x + self._text_rect.width / 2 + self.button_padding + self.arrow_width

        button_center_y = text_center_y
        arrow_color = self.style.fontcolor

        pygame.draw.polygon(self.surface, arrow_color, [
            (left_button_center_x - self.arrow_width, button_center_y),
            (left_button_center_x, button_center_y - self.arrow_width / 2),
            (left_button_center_x, button_center_y + self.arrow_width / 2)])
        pygame.draw.polygon(self.surface, arrow_color, [
            (right_button_center_x + self.arrow_width, button_center_y),
            (right_button_center_x, button_center_y - self.arrow_width / 2),
            (right_button_center_x, button_center_y + self.arrow_width / 2)])

        self.surface.blit(self._text_surface, self._text_rect)
