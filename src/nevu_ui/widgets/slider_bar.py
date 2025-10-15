import copy
import pygame

from nevu_ui.fast.nvvector2 import NvVector2
from nevu_ui.widgets import Widget, Button, WidgetKwargs
from nevu_ui.utils import mouse
from nevu_ui.core_types import Align
from nevu_ui.widgets.progress_bar import ProgressBar
from nevu_ui.color import TupleColorRole, PairColorRole

from typing import Any, TypedDict, NotRequired, Unpack, Union

from nevu_ui.style import (
    Style, default_style
)

class SliderKwargs(WidgetKwargs):
    start: NotRequired[Union[int, float]]
    end: NotRequired[Union[int, float]]
    step: NotRequired[Union[int, float]]
    current_value: NotRequired[Any]
    progress_style: NotRequired[Style | None]
    padding_x: NotRequired[int]
    padding_y: NotRequired[int]
    tuple_role: NotRequired[TupleColorRole]
    bar_pair_role: NotRequired[PairColorRole]

class Slider(Widget):
    progress_style: Style
    start: float | int
    end: float | int
    step: float | int
    padding_x: int
    padding_y: int
    tuple_role: TupleColorRole
    bar_pair_role: PairColorRole
    def __init__(self, size: NvVector2 | list, style: Style = default_style, **constant_kwargs: Unpack[SliderKwargs]):
        self._constant_current_val = None
        super().__init__(size, style, **constant_kwargs)    
    
    def _lazy_init(self, size: NvVector2 | list):
        super()._lazy_init(size)
        self.create_progress_bar()
    
    def create_progress_bar(self):
        progress_style = self.progress_style or self.style
        self.progress_bar = ProgressBar(self.size, progress_style, min_value = self.start, max_value = self.end, value = self.current_value, inline=True, alt = self.alt, color_pair_role=self.bar_pair_role, role=self.bar_pair_role)
        self.progress_bar.surface = self.surface
        self.progress_bar._init_start()
        self.progress_bar.booted = True
        self.progress_bar._boot_up()
    
    def _init_numerical(self):
        super()._init_numerical()
    
    def _init_booleans(self):
        super()._init_booleans()
        self.dragging = False 
    
    def _on_click_system(self):
        super()._on_click_system()
        self.dragging = True
    def _on_keyup_system(self):
        super()._on_keyup_system()
        self.dragging = False
    def _on_keyup_abandon_system(self):
        super()._on_keyup_abandon_system()
        self.dragging = False
    
    def _add_constants(self):
        super()._add_constants()
        self._add_constant("start", (int, float), 0)
        self._add_constant("end", (int, float), 100)
        self._add_constant("step", (int, float), 1)
        self._add_free_constant("current_value", 0)
        self._add_constant("progress_style", (Style, type(None)), None)
        self._add_constant("padding_x", int, 10)
        self._add_constant("padding_y", int, 10)
        self._add_constant("tuple_role", TupleColorRole, TupleColorRole.INVERSE_PRIMARY)
        self._add_constant("bar_pair_role", PairColorRole, PairColorRole.BACKGROUND)
     
    def _on_style_change_additional(self):
        super()._on_style_change_additional()
        self.progress_bar._changed = True

    @property
    def current_value(self) -> float | int:
        return self.progress_bar.value if hasattr(self, "progress_bar") else 0

    @current_value.setter
    def current_value(self, new_value: float | int):
        if hasattr(self, "progress_bar"): 
            self.progress_bar.set_progress_by_value(new_value)
            self._changed = True
        else:
            self._constant_current_val = new_value
    
    def secondary_update(self):
        super().secondary_update()
        if not self.active: return
        if self._constant_current_val and hasattr(self, "progress_bar"):
            self.current_value = self._constant_current_val
            self._constant_current_val = None
            
        self.progress_bar.update()
        if self.dragging:
            self._on_drag()

    def _on_drag(self):
        relative_x = mouse.pos.x - self.master_coordinates.x
        
        slider_pos = max(self._rsize_marg.x / 2, min(self._rsize.x, relative_x))
        slider_perc = ((slider_pos - self._rsize_marg.x/2) / (self._rsize.x - self._rsize_marg.x/2))
        
        value = slider_perc * (self.end - self.start) + self.start
        if value % self.step != 0:
            value = round(value / self.step) * self.step
        value = max(self.start, min(self.end, value))
        
        if value != self.current_value:
            self.current_value = value
            
    def primary_draw(self):
        if self._changed:
            self.surface.fill((0,0,0,0))
    
    def secondary_draw_content(self):
        super().secondary_draw_content()
        if not self.visible: return
        self.progress_bar.draw()
        self.progress_bar.coordinates = NvVector2()
        
        if self._changed:
            self.bake_text(str(round(self.progress_bar.progress*100)), alignx = self.style.text_align_x, aligny = self.style.text_align_y, color=self.style.colortheme.get_tuple(self.tuple_role))
            assert self._text_surface and self._text_rect
            
            self.adjust_text_rect()
            
            self.surface.blit(self._text_surface, self._text_rect)
    
    def adjust_text_rect(self):
        assert self._text_rect
        if self.style.text_align_x == Align.CENTER and self.style.text_align_y == Align.CENTER: return
        
        padx = 0
        pady = 0
        
        border_size = self._rsize_marg.x / 2
        
        match self.style.text_align_x:
            case Align.LEFT:
                padx = self.padding_x + border_size
            case Align.RIGHT: 
                padx = -self.padding_x - border_size
        
        match self.style.text_align_y:
            case Align.TOP:
                pady = self.padding_y + border_size
            case Align.BOTTOM: 
                pady = -self.padding_y - border_size
        
        
        self._text_rect.move_ip(padx, pady)
    
    def resize(self, resize_ratio: NvVector2):
        super().resize(resize_ratio)
        self.progress_bar.resize(resize_ratio)
        self.progress_bar.surface = self.surface
    
    def clone(self):
        return Slider(self._lazy_kwargs['size'], copy.deepcopy(self.style), **self.constant_kwargs)