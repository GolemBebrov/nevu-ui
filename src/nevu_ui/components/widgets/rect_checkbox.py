import copy
from typing import Unpack

import nevu_ui.core.modules as md
from nevu_ui.fast.nvvector2 import NvVector2
from nevu_ui.components.nevuobj.nevuobj import NevuObject
from collections.abc import Callable
from nevu_ui.core.enums import EventType, RenderReturnType, RenderConfig
from nevu_ui.components.widgets import RectCheckBoxKwargs, Widget
from nevu_ui.core.size.units import SizeRule
from nevu_ui.presentation.style import Style, default_style
from nevu_ui.core.state import nevu_state
from nevu_ui.core import Annotations
from nevu_ui.components.nevuobj.typehints import nevu_object_globals

class RectCheckBox(Widget):
    function: Callable | None
    _active_rect_factor: float | int
    def __init__(self, size: Annotations.nevuobj_size | Annotations.size_item = None, style: Annotations.nevuobj_style = None, **constant_kwargs: Unpack[RectCheckBoxKwargs]):
        if size is None:
            size = nevu_object_globals.library.get('size')
        if isinstance(size, int | float):
            size = NvVector2([size, size])
        elif isinstance(size, SizeRule):
            size = (size, size)

        super().__init__(size, style, **constant_kwargs)
        
    def _init_booleans(self):
        super()._init_booleans()
        self._supports_tuple_borderradius = False
    
    def _lazy_init(self, size: NvVector2 | list):
        super()._lazy_init(size)
        if val := self.get_param_value("checkbox_group"):
            val.add_checkbox(self) # type: ignore        
    
    def _add_params(self):
        from nevu_ui.components.layouts.misc.checkbox_group import CheckBoxGroup
        super()._add_params()
        self._add_param("function", (type(None), Callable), None)
        self._add_param_link("on_toggle", "function")
        self._add_param("toggled", bool, False)
        self._add_param_link("active", "toggled")
        self._add_param("active_rect_factor", (float, int), 0.8)
        self._add_param_link("active_factor", "active_rect_factor")
        self._add_param("checkbox_group", type(None) | CheckBoxGroup, None)
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
            
            inner_radius = self._rsize_marg.x*2
            inner_radius = [inner_radius]*4
            br = self.style.border_radius
            if isinstance(br, int|float):
                br = [br]*4
            for i in range(len(inner_radius)):
                inner_radius[i] += br[i]
                inner_radius[i] = max(0, int(inner_radius[i]))
            
            #inner_surf = self.renderer._create_surf_base(active_size, True, self.relm(inner_radius), sdf=True)
            inner_surf = self.renderer.core.create_clear(active_size)
            color = self.subtheme_border
            if len(color) == 3: color = (*color, 255)
            self.renderer.run_base(
                key=RenderConfig.DrawL1,
                radius=inner_radius,
                override_color = color,
                size=active_size,
                modify_object=inner_surf,
                standstill=True,
                return_type=RenderReturnType.Modify
            )
            self.surface.blit(inner_surf, offset.get_int_tuple())
            if nevu_state.window.is_dtype.raylib:
                md.rl.set_texture_filter(inner_surf.texture, md.rl.TextureFilter.TEXTURE_FILTER_BILINEAR) #type: ignore
                #with self.surface: #type: ignore
                    #nevu_state.window.display.blit_rect_vec(inner_surf.texture, offset.get_int_tuple(), mode = md.rl.BlendMode.BLEND_ALPHA) #type: ignore
                #return
            #self.surface.blit(inner_surf, offset) #type: ignore
            #self.clear_texture()
            
    def _on_click_system(self):
        self.toggled = not self.toggled
        super()._on_click_system()
    
    def _create_clone(self):
        self.constant_kwargs['events'] = self.get_param_strict("events").value.copy()
        return self.__class__(self._template['size'], copy.deepcopy(self.style), **self.constant_kwargs) # type: ignore
    
    def _on_copy_system(self, clone: NevuObject): # type: ignore
        super()._on_copy_system(clone, no_cache=True)
        self._event_cycle(EventType.OnCopy, clone)