import pygame
import copy

from nevu_ui.nevuobj import NevuObject
from nevu_ui.fast.nvvector2 import NvVector2
from nevu_ui.layouts.scrollable_base import ScrollableBase
from nevu_ui.fast.logic.fast_logic import collide_vertical
from nevu_ui.core.state import nevu_state
from nevu_ui.core.enums import Align, ScrollBarType

class ScrollableColumn(ScrollableBase):
    def _main_coord(self, coordinates: NvVector2): return coordinates.y
    def _sec_coord(self, coordinates: NvVector2): return coordinates.x
    @property
    def _main_axis(self): return 1
    
    def _add_constants(self):
        super()._add_constants()
        self.append_key = pygame.K_UP
        self.descend_key = pygame.K_DOWN
        self._change_constant_default("basic_alignment", Align.LEFT)

    def _parse_align(self, align: Align): return align in (Align.LEFT, Align.RIGHT, Align.CENTER)

    def _create_scroll_bar(self) -> ScrollableBase.ScrollBar:
        if not self.scrollbar_perc:
            size = NvVector2(self.size[0]/40, self.size[1]/20)
        else: size = self.size / 100 * self.scrollbar_perc
        return self.ScrollBar(size, self.style, ScrollBarType.Vertical, self)

    def _get_scrollbar_coordinates(self) -> NvVector2:
        return NvVector2(self._coordinates.x + self.relx(self.size.x - self.scroll_bar.size.x), self.scroll_bar.coordinates.y)

    def _set_item_main(self, item: NevuObject, align: Align):
        container_width, widget_width = self._csize.x, item._csize.x
        padding = self.relx(self.padding)
        
        match align:
            case Align.LEFT: item.coordinates.x = self._coordinates.x + padding
            case Align.RIGHT: item.coordinates.x = self._coordinates.x + (container_width - widget_width - padding)
            case Align.CENTER: item.coordinates.x = self._coordinates.x + (container_width / 2 - widget_width / 2)
    
    def base_light_update(self, items = None): # type: ignore
        super().base_light_update(0, -self.get_offset(), items = items)

    def _regenerate_coordinates(self):
        self.cached_coordinates = []
        self._regenerate_max_values()
        pad = self.rely(self.padding)
        padding_offset = pad
        for i, item in enumerate(self.items):
            align = self.widgets_alignment[i]
            self._set_item_main(item, align)
            item.coordinates.y = self._coordinates.y + padding_offset
            self.cached_coordinates.append(item.coordinates.copy())
            item.absolute_coordinates = self._get_item_master_coordinates(item)
            padding_offset += item._csize.y + pad
        super()._regenerate_coordinates()
        
    @property
    def _collide_function(self): return collide_vertical
        
    def _regenerate_max_values(self):
        assert nevu_state.window, "Window is not initialized"
        pad = self.rely(self.padding)
        total_content_height = pad
        for item in self.items:
            total_content_height += item._csize.y + pad
            
        visible_height = self._csize.y
        antirel = nevu_state.window.rel
        self.actual_max_main = max(0, (total_content_height - visible_height) / antirel.y)

    def _restart_coordinates(self):
        self.max_main = self.padding
        self.actual_max_main = 0

    def get_relative_vector_offset(self) -> NvVector2: return NvVector2(0, self.rely(self.get_offset()))

    def clone(self): return ScrollableColumn(self._lazy_kwargs['size'], copy.deepcopy(self.style), self._lazy_kwargs['content'], **self.constant_kwargs)