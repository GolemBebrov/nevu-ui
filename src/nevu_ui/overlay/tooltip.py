import pygame
import weakref

from nevu_ui.style import Style, default_style
from nevu_ui.core.classes import TooltipType
from nevu_ui.fast.nvvector2 import NvVector2
from typing import TYPE_CHECKING
if TYPE_CHECKING: from nevu_ui.nevuobj.nevuobj import NevuObject
from nevu_ui.utils import NevuEvent, mouse, time
from nevu_ui.core.enums import EventType, HoverState, Malign
from nevu_ui.overlay import overlay
from nevu_ui.color import SubThemeRole
from nevu_ui.rendering.background_renderer import BackgroundRenderer

class _TooltipBase:
    __slots__ = ('ratio', 'pos', 'size', 'style', 'title', '_cached_surf', 'initial_ratio')
    def __init__(self, title: str, style: Style = default_style):
        self.initial_ratio = NvVector2(1,1)
        self.ratio = NvVector2(1,1)
        self.pos = NvVector2()
        self.size = NvVector2()
        self.style = style
        self.title = title
        self._cached_surf = None
    def adapted_coords(self, master: NevuObject):
        add_coords = mouse.pos - master.absolute_coordinates
        pos = master.absolute_coordinates + add_coords
        return mouse.pos
    def get_surf(self, renderer: BackgroundRenderer): 
        if not self._cached_surf:
            self._cached_surf = self._get_surf_content(renderer)
        return self._cached_surf
    def resize(self, ratio: NvVector2): 
        self.ratio = ratio
        self._cached_surf = None
    def _get_surf_content(self, renderer: BackgroundRenderer):
        br = self.style.borderradius
        if isinstance(br, tuple|list):
            br = max(br)
        surf = renderer._create_surf_base(self._csize, radius = br, sdf=True, override_color=self.style.colortheme.get_subtheme(SubThemeRole.TERTIARY).oncontainer)
        title_surf, title_rect , _ = renderer.bake_text(self.title, alignx = self.style.text_align_x, aligny = self.style.text_align_y, size = self._csize, outside=True, outside_rect = surf.get_rect()) #type: ignore
        surf.blit(title_surf, title_rect)
        return surf
    @property
    def _csize(self): return self.size * self.ratio

class _ExtendedTooltipBase(_TooltipBase):
    __slots__ = tuple(list(_TooltipBase.__slots__) + ["content"])
    def __init__(self, title: str, content, style: Style = default_style):
        super().__init__(title, style)
        self.content = content 
    def _get_surf_content(self, renderer: BackgroundRenderer):
        br = self.style.borderradius
        if isinstance(br, tuple|list):
            br = max(br)
        surf = renderer._create_surf_base(self._csize, radius = br, sdf=True, override_color=self.style.colortheme.get_subtheme(SubThemeRole.TERTIARY).oncontainer)
        title_size = self._csize - NvVector2(0, self._csize.y / 1.3)
        content_size = self._csize - NvVector2(0, title_size.y)
        title_rect = pygame.Rect(0,0,*title_size)
        content_rect = pygame.Rect(0,0,*content_size)
        title_surf, title_rect , _ = renderer.bake_text(self.title, alignx = self.style.text_align_x, aligny = Malign.Center, size = title_size, outside=True, outside_rect = title_rect) #type: ignore
        content_surf, content_rect, _ = renderer.bake_text(self.content, alignx = self.style.text_align_x, aligny = Malign.Center, size = content_size, outside=True, outside_rect = content_rect) #type: ignore
        content_rect.top+=title_size.y
        surf.blit(title_surf, title_rect)
        surf.blit(content_surf, content_rect)
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
    def __init__(self, type: tooltip_type, style: Style = default_style):
        self.style = style
        self.type = type
        self.master: NevuObject | None = None
        self._data = self.unpack_type()
        self.get_surf = self._data.get_surf
        self._counter = 0
        self._counter_max = 1.5
        self._counter_max_opened = self._counter_max * 0.4
        self.old_coord = NvVector2()

    def adapted_coords(self): 
        assert self.master, "Tooltip is not connected to NevuObject!"
        return self._data.adapted_coords(self.master)
        
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
        overlay.remove_element(self)
        
    def _on(self, *args):
        assert self.master and self.master.renderer, "Tooltip is not connected to NevuObject!"
        overlay.change_element(self, self.get_surf(self.master.renderer), self.adapted_coords(), 2, strict=False)
    
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
        