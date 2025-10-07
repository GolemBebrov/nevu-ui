import copy

from nevu_ui.fast.nvvector2 import NvVector2
from nevu_ui.widgets import WidgetKwargs, Widget
from collections.abc import Callable
from nevu_ui.core_types import EventType

from typing import Any, TypedDict, NotRequired, Unpack, Union


from nevu_ui.style import (
    Style, default_style
)

class RectCheckBoxKwargs(WidgetKwargs):
    function: NotRequired[Callable | None]
    on_toogle: NotRequired[Callable | None]
    toogled: NotRequired[bool]
    active: NotRequired[bool]
    active_rect_factor: NotRequired[Union[float, int]]
    active_factor: NotRequired[Union[float, int]]

class RectCheckBox(Widget):
    function: Callable | None
    _active_rect_factor: float | int
    def __init__(self, size: int, style: Style = default_style, **constant_kwargs: Unpack[RectCheckBoxKwargs]):
        super().__init__(NvVector2([size, size]), style, **constant_kwargs)
        
    def _init_booleans(self):
        super()._init_booleans()
        self._toogled = False
        
    def _add_constants(self):
        super()._add_constants()
        self._add_constant("function", (type(None), Callable), None)
        self._add_constant_link("on_toogle", "function")
        self._add_constant("toogled", bool, False)
        self._add_constant_link("active", "toogled")
        self._add_constant("active_rect_factor", (float, int), 0.8)
        self._add_constant_link("active_factor", "active_rect_factor")

    @property
    def active_rect_factor(self):
        return self._active_rect_factor
    
    @active_rect_factor.setter
    def active_rect_factor(self, value: float | int):
        self._active_rect_factor = value
        self._changed = True

    @property
    def toogled(self):
        return self._toogled
    
    @toogled.setter
    def toogled(self,value: bool):
        self._toogled = value
        self._changed = True
        if self.function: self.function(value)
        
    def secondary_draw_content(self):
        super().secondary_draw_content()
        if self._changed and self._toogled:
            margin = (self._csize * (1 - self.active_rect_factor)) / 2
            margin.to_round()
            offset = NvVector2(margin.x, margin.y)
            
            active_size = self._csize - (offset * 2)
            
            active_size.x = max(1, int(active_size.x))
            active_size.y = max(1, int(active_size.y))
            
            inner_radius = (self.style.borderradius - self.relm(self.style.borderwidth / 2))
            
            inner_surf = self.renderer._create_surf_base(
                active_size, 
                True, 
                self.relm(inner_radius)
            )
            
            self.surface.blit(inner_surf, offset)
            
    def _on_click_system(self):
        self.toogled = not self.toogled
        super()._on_click_system()
          
    def clone(self):
        self.constant_kwargs['events'] = self._events
        selfcopy = RectCheckBox(self._lazy_kwargs['size'].x, copy.deepcopy(self.style), **self.constant_kwargs) # type: ignore
        self._event_cycle(EventType.OnCopy, selfcopy)
        return selfcopy