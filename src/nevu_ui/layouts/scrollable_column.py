import pygame
import copy

from nevu_ui.nevuobj import NevuObject
from nevu_ui.fast.nvvector2 import NvVector2
from nevu_ui.layouts.scrollable_base import ScrollableBase
from nevu_ui.fast.logic.fast_logic import collide_vertical
from nevu_ui.state import nevu_state
from nevu_ui.style import Style

from nevu_ui.core_types import (
    Align, ScrollBarType
)

class ScrollableColumn(ScrollableBase):

    def _add_constants(self):
        super()._add_constants()
        self.append_key = pygame.K_UP
        self.descend_key = pygame.K_DOWN

    def _parse_align(self, align: Align): # type: ignore
        return align in (Align.LEFT, Align.RIGHT, Align.CENTER)

    def _create_scroll_bar(self) -> ScrollableBase.ScrollBar:
        return self.ScrollBar([self.size[0]/40,self.size[1]/20], self.style, ScrollBarType.Vertical, self)

    def _update_scroll_bar(self):
        track_start_y = self.master_coordinates[1]
        track_path_y = self.size[1]
        offset = NvVector2(self.first_parent_menu.window._crop_width_offset, self.first_parent_menu.window._crop_height_offset) if self.first_parent_menu.window else NvVector2(0,0)
        
        start_coords = NvVector2(self.coordinates[0] + self.relx(self.size[0] - self.scroll_bar.size[0]), track_start_y)
        track_path = NvVector2(0, track_path_y)
        
        self.scroll_bar.set_scroll_params(start_coords, track_path, offset / 2)

    def _get_scrollbar_coordinates(self) -> NvVector2: # type: ignore
        return NvVector2(self._coordinates.x + self.relx(self.size.x - self.scroll_bar.size.x), self.scroll_bar.coordinates.y)

    def _resize_scrollbar(self):
        self.scroll_bar.coordinates.y = self.rely(self.scroll_bar.size.y)

    def _set_item_main(self, item: NevuObject, align: Align):
        container_width = self.relx(self.size[0])
        widget_width = self.relx(item.size[0])
        padding = self.relx(self.padding)

        if align == Align.LEFT:
            item.coordinates.x = self._coordinates.x + padding
        elif align == Align.RIGHT:
            item.coordinates.x = self._coordinates.x + (container_width - widget_width - padding)
        elif align == Align.CENTER:
            item.coordinates.x = self._coordinates.x + (container_width / 2 - widget_width / 2)
    
    def base_light_update(self, items = None): # type: ignore
        offset = self.get_offset()
        super().base_light_update(0, -offset, items = items)

    def _regenerate_coordinates(self):
        self.cached_coordinates = []
        self._regenerate_max_values()
        padding_offset = self.padding
        for i, item in enumerate(self.items):
            align = self.widgets_alignment[i]
            
            self._set_item_main(item, align)
            item.coordinates.y = self._coordinates.y + padding_offset
            self.cached_coordinates.append(item.coordinates.copy())
            item.master_coordinates = self._get_item_master_coordinates(item)
            padding_offset += item._csize.y + self.padding
        super()._regenerate_coordinates()
        
    @property
    def _collide_function(self):
        return collide_vertical
        
    def _regenerate_max_values(self):
        total_content_height = self.padding
        for item in self.items:
            total_content_height += item._csize.y + self.padding
        visible_height = self._csize.y
        
        antirel = nevu_state.window.rel
        
        self.actual_max_main = max(0, (total_content_height - visible_height) / antirel.y)

    def _restart_coordinates(self):
        self.max_main = self.padding
        self.actual_max_main = 0
    
    def _apply_style_to_scroll_bar(self, style: Style):
        if hasattr(self, 'scroll_bar'):
            self.scroll_bar.style = style
            
    def get_relative_vector_offset(self) -> NvVector2:
        return NvVector2(0, self.rely(self.get_offset()))
    
    def add_item(self, item: NevuObject, alignment: Align = Align.LEFT):
        super().add_item(item, alignment)

    def clone(self):
        return ScrollableColumn(self._lazy_kwargs['size'], copy.deepcopy(self.style), self._lazy_kwargs['content'], **self.constant_kwargs)