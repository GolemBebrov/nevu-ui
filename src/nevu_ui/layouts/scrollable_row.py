import pygame
import copy

from nevu_ui.nevuobj import NevuObject
from nevu_ui.fast.nvvector2 import NvVector2
from nevu_ui.layouts.scrollable_base import ScrollableBase
from nevu_ui.fast.logic.fast_logic import collide_horizontal
from nevu_ui.core.state import nevu_state
from nevu_ui.core.enums import Align, ScrollBarType

class ScrollableRow(ScrollableBase):
    def _add_constants(self):
        super()._add_constants()
        self.append_key = pygame.K_LEFT
        self.descend_key = pygame.K_RIGHT

    def _parse_align(self, align: Align): return align in (Align.TOP, Align.BOTTOM, Align.CENTER)

    def _create_scroll_bar(self) -> ScrollableBase.ScrollBar: return self.ScrollBar([self.size[0]/20,self.size[1]/40], self.style, ScrollBarType.Horizontal, self)

    def _update_scroll_bar(self):
        track_start_x, track_path_x = self.absolute_coordinates[0], self.size[0]
        offset = NvVector2(self.first_parent_menu.window._crop_width_offset, self.first_parent_menu.window._crop_height_offset) if self.first_parent_menu.window else NvVector2(0,0)
        
        start_coords = NvVector2(track_start_x, self.coordinates[1] + self.rely(self.size[1] - self.scroll_bar.size[1]))
        track_path = NvVector2(track_path_x, 0)
        
        self.scroll_bar.set_scroll_params(start_coords, track_path, offset / 2)

    def _get_scrollbar_coordinates(self) -> NvVector2:
        return NvVector2(self.scroll_bar.coordinates.x, self._coordinates.y + self.rely(self.size.y - self.scroll_bar.size.y))

    def _resize_scrollbar(self): self.scroll_bar.coordinates.x = self.relx(self.scroll_bar.size.x)
        
    @property
    def _collide_function(self): return collide_horizontal
        
    def _set_item_main(self, item: NevuObject, align: Align):
        container_height, widget_height = self.rely(self.size[1]), self.rely(item.size[1])
        padding = self.rely(self.padding)

        match align:
            case Align.TOP: item.coordinates.y = self._coordinates.y + padding
            case Align.BOTTOM: item.coordinates.y = self._coordinates.y + (container_height - widget_height - padding)
            case Align.CENTER: item.coordinates.y = self._coordinates.y + (container_height / 2 - widget_height / 2)

    def base_light_update(self, items = None): # type: ignore
        super().base_light_update(-self.get_offset(), 0, items = items)

    def _regenerate_coordinates(self):
        self.cached_coordinates = []
        self._regenerate_max_values()
        pad = self.relx(self.padding)
        padding_offset = pad
        for i, item in enumerate(self.items):
            align = self.widgets_alignment[i]
            self._set_item_main(item, align)
            item.coordinates.x = self._coordinates.x + padding_offset
            self.cached_coordinates.append(item.coordinates.copy())
            item.absolute_coordinates = self._get_item_master_coordinates(item)
            padding_offset += item._csize.x + pad
        super()._regenerate_coordinates()
        
    def _regenerate_max_values(self):
        assert nevu_state.window, "Window is not initialized"
        pad = self.relx(self.padding)
        total_content_width = pad
        for item in self.items:
            total_content_width += item._csize.x + pad
            
        visible_width = self._csize.x
        antirel = nevu_state.window.rel
        self.actual_max_main = max(0, (total_content_width - visible_width) / antirel.x)

    def _restart_coordinates(self):
        self.max_main = self.padding
        self.actual_max_main = 0

    def get_relative_vector_offset(self) -> NvVector2: return NvVector2(self.relx(self.get_offset()), 0)

    def add_item(self, item: NevuObject, alignment: Align = Align.TOP): super().add_item(item, alignment)

    def clone(self): return ScrollableRow(self._lazy_kwargs['size'], copy.deepcopy(self.style), self._lazy_kwargs['content'], **self.constant_kwargs)