import pygame
import pyray as rl
from typing import Unpack

from nevu_ui.fast.nvvector2 import NvVector2
from nevu_ui.utils import mouse
from nevu_ui.presentation.color import Color
from nevu_ui.components.widgets.progress_bar import ProgressBar
from nevu_ui.core.state import nevu_state
from nevu_ui.core.enums import Align, ConstantLayer
from nevu_ui.presentation.color import TupleColorRole, PairColorRole
from nevu_ui.components.widgets import Widget, SliderKwargs
from nevu_ui.fast.nvrect import NvRect
from nevu_ui.presentation.style import Style, default_style

class Slider(Widget):
    progress_style: Style
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
        if nevu_state.window.is_dtype.raylib:
            with self.progress_bar.surface: #type: ignore
                nevu_state.window.display.clear(Color.Blank)
        else:
            self.progress_bar.surface.fill((0,0,0,0))
            self._create_surf()
    
    def create_progress_bar(self):
        assert self.surface
        
        progress_style = self.progress_style or self.style
        self.progress_bar = ProgressBar(self.size, progress_style, min_value = self.start, max_value = self.end, value = self.current_value, alt = self.alt, role=self.bar_pair_role, z=-999)
        
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
        
    def _on_hover_system(self):
        super()._on_hover_system()
        self.progress_bar._hover()
        self._create_surf()
    def _on_unhover_system(self):
        super()._on_unhover_system()
        self.progress_bar._unhover()
        self._create_surf()
    def _on_click_system(self):
        super()._on_click_system()
        self.dragging = True
        self.progress_bar._click()
        self._create_surf()
    def _on_keyup_system(self):
        super()._on_keyup_system()
        self.dragging = False
        self.progress_bar._kup()
    def _on_keyup_abandon_system(self):
        super()._on_keyup_abandon_system()
        self.dragging = False
        self.progress_bar._kup_abandon()
    
    def _add_params(self):
        super()._add_params()
        self._add_param("start", (int, float), 0)
        self._add_param("end", (int, float), 100)
        self._add_param("step", (int, float), 1)
        self._add_param("current_value", (int, float), 0, layer=ConstantLayer.Lazy)
        self._add_param("progress_style", (Style, type(None)), None)
        self._add_param("padding_x", int, 10)
        self._add_param("padding_y", int, 10)
        self._add_param("tuple_role", TupleColorRole, TupleColorRole.INVERSE_PRIMARY)
        self._add_param("bar_pair_role", PairColorRole, PairColorRole.BACKGROUND)
    
    @property
    def start(self): return self.get_param_strict("start").value
    @property
    def end(self): return self.get_param_strict("end").value
    @property
    def step(self): return self.get_param_strict("step").value
    
    def _on_style_change_additional(self):
        super()._on_style_change_additional()
        if hasattr(self, "progress_bar") and self.progress_bar: self.progress_bar._changed = True
        
    @property
    def current_value(self) -> float | int:
        return self.progress_bar.value if hasattr(self, "progress_bar") and self.progress_bar else 0
    @current_value.setter
    def current_value(self, new_value: float | int):
        if hasattr(self, "progress_bar") and self.progress_bar: 
            self.progress_bar.set_progress_by_value(new_value)
            self._changed = True
        else:
            self._constant_current_val = new_value
    
    def _logic_update(self):
        super()._logic_update()
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
            
    def _primary_draw(self): pass
    
    def _create_surf(self):
        assert self.surface and self.progress_bar.surface
        args = self._create_font()
        self.clear_texture()
        self.adjust_text_rect()
        if nevu_state.window.is_dtype.raylib:
            display = nevu_state.window.display
            assert nevu_state.window.is_raylib(display)
            with self.surface: #type: ignore
                display.clear(Color.Blank)
                display.blit_rect_vec(self.progress_bar.surface.texture, (0,0), mode=rl.BlendMode.BLEND_ALPHA) #type: ignore
                nvrect = NvRect(args[2]) #type: ignore
                nvrect = self.adjust_text_rect(nvrect)
                args = list(args) #type: ignore
                args[2] = nvrect.get_int_tuple()[0:2] #type: ignore
                rl.draw_text_ex(*args) #type: ignore
        else:
            self.surface.fill((0,0,0,0)) 
            self.surface.blit(self.progress_bar.surface, (0,0)) #type: ignore
            self.surface.blit(self._text_surface, self._text_rect) #type: ignore
        
    def _create_font(self):
        ext_kwargs = {}
        if nevu_state.window.is_dtype.raylib:
            ext_kwargs["render"] = False
        args = self.renderer.bake_text(str(round(self.current_value)), style=self.progress_bar.style, color=self.style.colortheme.get_tuple(self.tuple_role), **ext_kwargs)
        return args
     
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
            self._create_surf()
    
    def adjust_text_rect(self, rect = None):
        result_rect = rect or self._text_rect
        result_rect = NvRect(result_rect)
        if self.style.align_x == Align.CENTER and self.style.align_y == Align.CENTER: return rect
        
        padx = 0
        pady = 0
        
        border_size = self._rsize_marg / 2
        
        match self.style.align_x:
            case Align.LEFT:
                padx = self.padding_x + border_size.x
            case Align.RIGHT: 
                padx = -self.padding_x - border_size.x
        
        match self.style.align_y:
            case Align.TOP:
                pady = self.padding_y + border_size.y
            case Align.BOTTOM: 
                pady = -self.padding_y - border_size.y
        
        if isinstance(result_rect, tuple):
            result_rect = NvRect(*result_rect)
        result_rect.move_ip(padx, pady)
        if rect is None:
            self._text_rect = result_rect
        else:
            return result_rect
    
    def _resize(self, resize_ratio: NvVector2):
        super()._resize(resize_ratio)
        assert self.surface
        self._create_font()
        self.progress_bar._resize(resize_ratio)