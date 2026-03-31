import copy
from typing import Unpack

import nevu_ui.core.modules as md
from nevu_ui.fast.nvvector2 import NvVector2
from nevu_ui.components.nevuobj.nevuobj import NevuObject
from collections.abc import Callable
from nevu_ui.core.enums import EventType
from nevu_ui.components.widgets import RectCheckBoxKwargs, Widget
from nevu_ui.presentation.style import Style, default_style
from nevu_ui.core.state import nevu_state

class RectCheckBox(Widget):
    function: Callable | None
    _active_rect_factor: float | int
    def __init__(self, size: int, style: Style = default_style, **constant_kwargs: Unpack[RectCheckBoxKwargs]):
        super().__init__(NvVector2([size, size]), style, **constant_kwargs)
        
    def _init_booleans(self):
        super()._init_booleans()
        self._supports_tuple_borderradius = False
        
    def _add_params(self):
        super()._add_params()
        self._add_param("function", (type(None), Callable), None)
        self._add_param_link("on_toggle", "function")
        self._add_param("toggled", bool, False)
        self._add_param_link("active", "toggled")
        self._add_param("active_rect_factor", (float, int), 0.8)
        self._add_param_link("active_factor", "active_rect_factor")
        self._change_param_default("hoverable", True)

    @property
    def active_rect_factor(self):
        return self.get_param_strict("active_rect_factor").value
    
    @active_rect_factor.setter
    def active_rect_factor(self, value: float | int):
        self.set_param_value("active_rect_factor", value)
        self._changed = True

    def _change(self):
        self._on_style_change()
    
    @property
    def toggled(self):
        return self.get_param_strict("toggled").value
    
    @toggled.setter
    def toggled(self,value: bool):
        self.set_param_value("toggled", value)
        self._changed = True
        self.clear_surfaces()
        if self.function: self.function(value)
        if hasattr(self, "cache"):
            self.clear_texture()
        
    def secondary_draw_content(self):
        super().secondary_draw_content()
        if self._changed and self.toggled:
            margin = (self._csize * (1 - self.active_rect_factor))
            margin.to_round()
            offset = NvVector2(margin.x, margin.y)
            self.clear_texture()
            active_size = self._csize - (offset * 2)
            
            active_size.x = max(1, int(active_size.x))
            active_size.y = max(1, int(active_size.y))
            
            inner_radius = (self.style.border_radius - self.relm(self.style.border_width / 2))
            
            ext_kwargs = {}
            if nevu_state.window.is_dtype.raylib:
                ext_kwargs["blitmode"] = md.rl.BlendMode.BLEND_ALPHA
            
            inner_surf = self.renderer._create_surf_base(active_size, True, self.relm(inner_radius), sdf=True, **ext_kwargs)
            
            if nevu_state.window.is_dtype.raylib:
                md.rl.set_texture_filter(inner_surf.texture, md.rl.TextureFilter.TEXTURE_FILTER_BILINEAR) #type: ignore
                with self.surface: #type: ignore
                    nevu_state.window.display.blit_rect_vec(inner_surf.texture, offset.get_int_tuple(), mode = md.rl.BlendMode.BLEND_ALPHA) #type: ignore
                return
            self.surface.blit(inner_surf, offset) #type: ignore
            self.clear_texture()
            
    def _on_click_system(self):
        self.toggled = not self.toggled
        super()._on_click_system()
        
    
    def _create_clone(self):
        self.constant_kwargs['events'] = self.get_param_strict("events").value.copy()
        return self.__class__(self._template['size'].x, copy.deepcopy(self.style), **self.constant_kwargs) # type: ignore
    
    def _on_copy_system(self, clone: NevuObject): # type: ignore
        super()._on_copy_system(clone, no_cache=True)
        self._event_cycle(EventType.OnCopy, clone)