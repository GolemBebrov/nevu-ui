import copy
import pygame

from nevu_ui.fast.nvvector2 import NvVector2
from nevu_ui.widgets import Widget, WidgetKwargs
from nevu_ui.utils import mouse
from nevu_ui.widgets.progress_bar import ProgressBar
from nevu_ui.core.enums import Align, ConstantLayer
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
        self.booted = False
        self._constant_current_val = None
        super().__init__(size, style, **constant_kwargs) 
    
    def _lazy_init(self, size: NvVector2 | list):
        super()._lazy_init(size)
        self.create_progress_bar()
        self.add_first_update_action(self._first_progressbar_update)
    
    def _first_progressbar_update(self):
        self._on_progress_bar_change()
        self._create_font()
    
    def _on_progress_bar_change(self):
        self.progress_bar.surface.fill((0,0,0,0))
        self._create_surf()
    
    def create_progress_bar(self):
        assert self.surface
        self.progress_bar_surf = self.surface.copy()
        progress_style = self.progress_style or self.style
        self.progress_bar = ProgressBar(self.size, progress_style, min_value = self.start, max_value = self.end, value = self.current_value, inline=True, alt = self.alt, role=self.bar_pair_role, z=-999)
        self.progress_bar.surface = self.progress_bar_surf
        self.progress_bar._on_change_system = self._on_progress_bar_change
        self.progress_bar._on_value_change_system = self._on_progress_bar_change
        self.progress_bar._init_start()
        self.progress_bar.booted = True
        self.progress_bar._boot_up()
    
    def _init_numerical(self):
        super()._init_numerical()
    
    def _init_flags(self):
        super()._init_flags()
        self.dragging = False 
        self._font_changed = False
    
    def _init_objects(self):
        super()._init_objects()
        self.progress_bar_surf = None
    
    def _on_click_system(self):
        super()._on_click_system()
        self.dragging = True
        self.progress_bar._click()
    def _on_keyup_system(self):
        super()._on_keyup_system()
        self.dragging = False
        self.progress_bar._kup()
    def _on_keyup_abandon_system(self):
        super()._on_keyup_abandon_system()
        self.dragging = False
        self.progress_bar._kup_abandon()
    
    def _add_constants(self):
        super()._add_constants()
        self._add_constant("start", (int, float), 0, layer = ConstantLayer.Top)
        self._add_constant("end", (int, float), 100, layer = ConstantLayer.Top)
        self._add_constant("step", (int, float), 1)
        self._add_constant("current_value", (int, float), 0, self.current_value_getter, self.current_value_setter, layer=ConstantLayer.Top)
        self._add_constant("progress_style", (Style, type(None)), None)
        self._add_constant("padding_x", int, 10)
        self._add_constant("padding_y", int, 10)
        self._add_constant("tuple_role", TupleColorRole, TupleColorRole.INVERSE_PRIMARY)
        self._add_constant("bar_pair_role", PairColorRole, PairColorRole.BACKGROUND)
     
    def _on_style_change_additional(self):
        super()._on_style_change_additional()
        if hasattr(self, "progress_bar"): self.progress_bar._changed = True
        
    def current_value_getter(self) -> float | int:
        return self.progress_bar.value if hasattr(self, "progress_bar") else 0

    def current_value_setter(self, new_value: float | int):
        if hasattr(self, "progress_bar"): 
            self.progress_bar.set_progress_by_value(new_value)
            self._changed = True
        else:
            self._constant_current_val = new_value
    
    def logic_update(self):
        super().logic_update()
        if not self.active: return
        if self._constant_current_val and hasattr(self, "progress_bar"):
            self.current_value = self._constant_current_val
            self.clear_texture()
            self._create_font()
            self._changed = True
            self._constant_current_val = None
            
    def secondary_update(self):
        super().secondary_update()
        self.progress_bar.update()
        if self.dragging:
            self._on_drag()

    def _on_drag(self):
        relative_x = mouse.pos.x - self.absolute_coordinates.x
        
        slider_pos = max(self._rsize_marg.x / 2, min(self._rsize.x, relative_x))
        slider_perc = ((slider_pos - self._rsize_marg.x/2) / (self._rsize.x - self._rsize_marg.x/2))
        
        value = slider_perc * (self.end - self.start) + self.start
        if value % self.step != 0:
            value = round(value / self.step) * self.step
        value = max(self.start, min(self.end, value))
        
        if abs(value - self.current_value) > 1e-9:
            self.current_value = value
            self._create_font()
            
    def primary_draw(self): pass
    
    def _create_surf(self):
        assert self.surface and self.progress_bar_surf
        if not (self._text_surface or self._text_rect):
            self._create_font()
        self.clear_texture()
        self.surface.fill((0,0,0,0))
        self.surface.blit(self.progress_bar_surf, (0,0))
        self.surface.blit(self._text_surface, self._text_rect)
        
    def _create_font(self):
        #print(self.style.colortheme.get_tuple(self.tuple_role))
        self.renderer.bake_text(str(round(self.progress_bar.progress*100)), style=self.progress_bar.style, color=self.style.colortheme.get_tuple(self.tuple_role))
    
    def _after_state_change_system(self):
        super()._after_state_change_system()
        self._create_font()
        self.adjust_text_rect()
        self._create_surf()
        
    def secondary_draw_content(self):
        super().secondary_draw_content()
        if not self.visible: return
        
        self.progress_bar.coordinates = NvVector2()
        if self._changed:
            self.progress_bar.draw()
            assert self.surface
            if not self._text_surface:
                self._create_font()
            assert self._text_surface and self._text_rect
            self.adjust_text_rect()
            self._create_surf()
    
    def adjust_text_rect(self):
        assert self._text_rect
        if self.style.text_align_x == Align.CENTER and self.style.text_align_y == Align.CENTER: return
        
        padx = 0
        pady = 0
        
        border_size = self._rsize_marg / 2
        
        match self.style.text_align_x:
            case Align.LEFT:
                padx = self.padding_x + border_size.x
            case Align.RIGHT: 
                padx = -self.padding_x - border_size.x
        
        match self.style.text_align_y:
            case Align.TOP:
                pady = self.padding_y + border_size.y
            case Align.BOTTOM: 
                pady = -self.padding_y - border_size.y
        
        assert isinstance(self._text_rect, pygame.Rect)
        self._text_rect.move_ip(padx, pady)
    
    def resize(self, resize_ratio: NvVector2):
        super().resize(resize_ratio)
        assert self.surface
        self._create_font()
        self.progress_bar_surf = self.surface.copy()
        self.progress_bar.resize(resize_ratio)
        self.progress_bar.surface = self.progress_bar_surf