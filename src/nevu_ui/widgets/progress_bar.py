import copy

from nevu_ui.fast.nvvector2 import NvVector2
from nevu_ui.widgets import Widget

from nevu_ui.style import (
    Style, default_style
)

class ProgressBar(Widget):
    min_value: int | float
    max_value: int | float
    _current_value: int | float
    def __init__(self, size: NvVector2 | list, style: Style = default_style,**constant_kwargs):
        super().__init__(size, style, **constant_kwargs)
        self.percentage_of_value = self.value
    def _add_constants(self):
        super()._add_constants()
        self._add_constant("min_value", (int, float), 0)
        self._add_constant("max_value", (int, float), 100)
        self._add_constant("value", (int, float), 0)
    @property
    def percentage(self):
        return self._percentage
    @percentage.setter
    def percentage(self,value):
        self._percentage = value
        self.value = self.min_value+(self.max_value-self.min_value)*self._percentage
    @percentage.setter
    def percentage_of_value(self,value):
        self._percentage = (value-self.min_value)/(self.max_value-self.min_value)
    @property
    def value(self):
        return self._current_value
    @value.setter
    def value(self,value):
        self._current_value = value
        self.percentage_of_value = value
    def secondary_draw(self):
        super().secondary_draw()
        surf = self.renderer._create_surf_base([int(self.relx(self.size[0]*self.percentage))-2,int(self.rely(self.size[1]))-2])
        self.surface.blit(surf,(0,0))
        