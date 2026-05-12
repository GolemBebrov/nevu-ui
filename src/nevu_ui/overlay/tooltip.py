from __future__ import annotations
import weakref

import nevu_ui.core.modules as md
from nevu_ui.presentation.style import Style, default_style
from nevu_ui.core.classes import TooltipType
from nevu_ui.fast.nvvector2 import NvVector2
from nevu_ui.fast.nvrect import NvRect
from nevu_ui.core.state import nevu_state
from typing import TYPE_CHECKING
if TYPE_CHECKING: from nevu_ui.components.nevuobj import NevuObject
from nevu_ui.utils import NevuEvent, mouse, time
from nevu_ui.core.enums import EventType, HoverState, Malign, CacheType, RenderReturnType, RenderConfig
from nevu_ui.overlay import overlay
from nevu_ui.presentation.color import SubThemeRole, TupleColorRole
from nevu_ui.rendering.base_renderer import BaseRenderer
from nevu_ui.fast.nevucache import Cache

#include <brain.h>
#include <not bugs.h>
#include <stability.h>
#define GurrenLagann

class _TooltipBase:
    __slots__ = ('ratio', 'pos', 'size', 'style', 'title', '_cached_surf', 'initial_ratio', 'cache')
    def __init__(self, title: str, style: Style = default_style):
        self.initial_ratio = NvVector2(1,1)
        self.ratio = NvVector2(1,1)
        self.pos = NvVector2()
        self.size = NvVector2()
        self.style = style
        self.title = title
        self.cache = Cache()
        self._cached_surf = None
    
    def _clear_rl_specific(self):
        assert nevu_state.window
        
        if self.cache.get(CacheType.RlFont): md.rl.unload_font(self.cache.get(CacheType.RlFont)) #type: ignore
        if self.cache.get(CacheType.Scaled_Image): md.rl.unload_texture(self.cache.get(CacheType.Scaled_Image)) #type: ignore
        
    def clear_all(self):
        if nevu_state.window.is_dtype.raylib: 
            self._clear_rl_specific()
        self.cache.clear()
        
    def clear_surfaces(self):
        if nevu_state.window.is_dtype.raylib: 
            self._clear_rl_specific()
        self.cache.clear_selected(whitelist = [CacheType.Scaled_Image, CacheType.Image, CacheType.Scaled_Gradient, CacheType.Surface, CacheType.Borders, CacheType.Scaled_Borders, CacheType.Scaled_Background, CacheType.Background, CacheType.Texture, CacheType.RlFont, CacheType.TextArgs, CacheType.ClickTexture], blacklist = [])
    
    def adapted_coords(self): return mouse.pos
    
    def get_surf(self, renderer: BaseRenderer, alt):
        if not self._cached_surf:
            self._cached_surf = self._get_surf_content(renderer, alt)
        return self._cached_surf
    
    def resize(self, ratio: NvVector2): 
        self.ratio = ratio
        self._cached_surf = None
        self.clear_all()
        
    def _get_surf_content(self, renderer: BaseRenderer, alt):
        br = self.style.border_radius
        if isinstance(br, tuple|list):
            br = max(br)
        title_rect = NvRect(0,0,*self._csize)
        surf = renderer.run_base(RenderConfig.DrawL1, size = self._csize, radius = br, override_color=self.style.colortheme.get_subtheme(SubThemeRole.TERTIARY).oncontainer, return_type=RenderReturnType.CreateNew)
        _, title_surf = renderer.run_text(RenderConfig.DrawL3, text = self.title, override_font_size=self.style.font_size*self.ratio.y, override_color=self.style.colortheme.get_tuple(TupleColorRole.INVERSE_PRIMARY), return_type=RenderReturnType.CreateNew, max_size=self._csize) 
        tx = title_surf.width
        title_rect[0] += self._csize.x / 2 - tx / 2
        if nevu_state.window.is_dtype.raylib:
            with surf:
                md.rl.begin_blend_mode(md.rl.BlendMode.BLEND_ALPHA_PREMULTIPLY)
                nevu_state.window.display.fast_blit(title_surf.texture, title_rect.get_int_tuple())
                md.rl.end_blend_mode()
        else:
            surf.blit(title_surf, title_rect.get_int_tuple())
        return surf
    
    @property
    def _csize(self): return self.size * self.ratio

class _ExtendedTooltipBase(_TooltipBase):
    __slots__ = tuple(list(_TooltipBase.__slots__) + ["content"])
    def __init__(self, title: str, content, style: Style = default_style):
        super().__init__(title, style)
        self.content = content 
        
    def _get_surf_content(self, renderer, alt = False):
        br = self.style.border_radius
        if isinstance(br, tuple|list):
            br = max(br)
        surf = renderer.run_base(RenderConfig.DrawL1, size = self._csize, radius = br, override_color=self.style.colortheme.get_subtheme(SubThemeRole.TERTIARY).oncontainer, return_type=RenderReturnType.CreateNew)
        title_size = self._csize - NvVector2(0, self._csize.y / 1.3)
        content_size = self._csize - NvVector2(0, title_size.y)
        title_rect = NvRect(0,0,*title_size)
        content_rect = NvRect(0,title_rect.h, *content_size)
        
        _, title_surf = renderer.run_text(RenderConfig.DrawL3,override_font_size=self.style.font_size*self.ratio.y, text = self.title, override_color=self.style.colortheme.get_tuple(TupleColorRole.INVERSE_PRIMARY),return_type=RenderReturnType.CreateNew, max_size=title_size) 
        _, content_surf = renderer.run_text(RenderConfig.DrawL3,override_font_size=self.style.font_size*self.ratio.y,text = self.content, override_color=self.style.colortheme.get_tuple(TupleColorRole.INVERSE_PRIMARY), return_type=RenderReturnType.CreateNew, max_size=content_size) 
        tx = title_surf.width
        cx = content_surf.width
        title_rect[0] += title_size.x / 2 - tx / 2
        content_rect[0] += content_size.x / 2 - cx / 2
        surf.blit(title_surf, title_rect.get_int_tuple())
        surf.blit(content_surf, content_rect.get_int_tuple())
        return surf

class _SmallTooltip(_TooltipBase): 
    def __init__(self, title: str, style: Style = default_style):
        super().__init__(title, style)
        self.initial_ratio = NvVector2(0.2, 0.2)

class _MediumTooltip(_ExtendedTooltipBase): 
    def __init__(self, title: str, content, style: Style = default_style):
        super().__init__(title, content, style)
        self.initial_ratio = NvVector2(0.4, 0.3)
        
class _LargeTooltip(_ExtendedTooltipBase): 
    def __init__(self, title: str, content, style: Style = default_style):
        super().__init__(title, content, style)
        self.initial_ratio = NvVector2(0.6, 0.4)
        
class _CustomTooltip(_TooltipBase):
    def __init__(self, ratio: NvVector2, title: str, style: Style = default_style):
        super().__init__(title, style)
        self.initial_ratio = ratio

class _BigCustomTooltip(_ExtendedTooltipBase):
    def __init__(self, ratio: NvVector2, title: str, content: str, style: Style = default_style):
        super().__init__(title, content, style)
        self.initial_ratio = ratio

#faputa solo sosu
class Tooltip():
    tooltip_type = TooltipType.Large | TooltipType.Medium | TooltipType.Small | TooltipType.Custom | TooltipType.BigCustom
    def __init__(self, type: tooltip_type, style: Style = default_style, alt: bool = False):
        self.style = style
        self.type = type
        self.master: NevuObject | None = None
        self._data = self.unpack_type()
        self.get_surf = self._data.get_surf
        self._counter = 0
        self._counter_max = 1.5
        self._counter_max_opened = self._counter_max * 0.4
        self.old_coord = NvVector2()
        self.alt = alt

    def adapted_coords(self): 
        assert self.master, "Tooltip is not connected to NevuObject!"
        return self._data.adapted_coords()
        
    @property
    def size(self): return self._data.size
    @size.setter
    def size(self, size: NvVector2): self._data.size = size
    
    def resize(self, resize_ratio: NvVector2): self._data.resize(resize_ratio)
    
    def unpack_type(self):
        if isinstance(self.type, TooltipType.Small):
            return _SmallTooltip(self.type.title, self.style)
        elif isinstance(self.type, TooltipType.Medium):
            return _MediumTooltip(self.type.title, self.type.content, self.style)
        elif isinstance(self.type, TooltipType.Large):
            return _LargeTooltip(self.type.title, self.type.content, self.style)
        elif isinstance(self.type, TooltipType.Custom):
            return _CustomTooltip(self.type.ratio, self.type.title, self.style)
        elif isinstance(self.type, TooltipType.BigCustom):
            return _BigCustomTooltip(self.type.ratio, self.type.title, self.type.content, self.style)
        raise ValueError("Invalid tooltip type!")
    
    def _off(self, *args):
        if overlay.has_element(self):
            overlay.remove_element(self)
    def _on(self, *args):
        assert self.master and self.master.renderer, "Tooltip is not connected to NevuObject!"
        overlay.change_element(self, self.get_surf(self.master.renderer, self.alt), self.adapted_coords(), 2, strict=False)
    
    def _adjust_size(self):
        assert self.master, "Tooltip is not connected to NevuObject!"
        self.size = self.master.size * self._data.initial_ratio
        
    def _update(self, *args):
        assert self.master, "Tooltip is not connected to NevuObject!"
        if self.master.hover_state == HoverState.UN_HOVERED and overlay.has_element(self):
            self._off()
            self._counter = 0
        elif self.master.hover_state in [HoverState.HOVERED, HoverState.CLICKED]:
            new_pos = mouse.pos
            if new_pos != self.old_coord:
                self._counter += 1*time.dt
                if overlay.has_element(self) and self._counter >= self._counter_max_opened:
                    self._move_to_mouse(new_pos)
                elif self._counter >= self._counter_max:
                    self._move_to_mouse(new_pos)

    def _move_to_mouse(self, new_pos):
        self._on()
        self._counter = 0
        self.old_coord = new_pos
    
    def connect_to_master(self, master: NevuObject):
        self.master = weakref.proxy(master)
        assert self.master, "Tooltip is not connected to NevuObject!"
        self.master.add_first_update_action(self._adjust_size)
        self.master.subscribe(NevuEvent(self, self._off, EventType.OnUnhover))
        self.master.subscribe(NevuEvent(self, self._update, EventType.Update))