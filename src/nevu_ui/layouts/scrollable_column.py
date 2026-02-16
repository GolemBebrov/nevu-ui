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
    
    def _add_params(self):
        super()._add_params()
        self._change_param_default("append_key", pygame.K_UP)
        self._change_param_default("descend_key", pygame.K_DOWN)
        self._change_param_default("basic_alignment", Align.LEFT)

    def _parse_align(self, align: Align): return align in (Align.LEFT, Align.RIGHT, Align.CENTER)

    def _create_scroll_bar(self) -> ScrollableBase.ScrollBar:
        if not self.scrollbar_perc:
            size = NvVector2(self.size[0]/40, self.size[1]/20)
        else: size = self.size / 100 * self.scrollbar_perc
        return self.ScrollBar(size, self.style, ScrollBarType.Vertical, self)

    def _get_scrollbar_coordinates(self) -> NvVector2:
        return NvVector2(self.coordinates.x + self.relx(self.size.x - self.scroll_bar.size.x), self.scroll_bar.coordinates.y)

    def _set_item_main(self, item: NevuObject, align: Align):
        container_width, widget_width = self._csize.x, item._csize.x
        padding = self.relx(self.get_param_strict("spacing").value)
        
        match align:
            case Align.LEFT: item.coordinates.x = self.coordinates.x + padding
            case Align.RIGHT: item.coordinates.x = self.coordinates.x + (container_width - widget_width - padding)
            case Align.CENTER: item.coordinates.x = self.coordinates.x + (container_width / 2 - widget_width / 2)
        item.coordinates.x += self.coordinates.x
    
    def _base_light_update(self, items = None): # type: ignore
        super()._base_light_update(0, -self.get_offset(), items = items)
        
    @property
    def _collide_function(self): return collide_vertical
        
    def _regenerate_max_values(self):
        assert nevu_state.window, "Window is not initialized"
        pad = self.rely(self.get_param_strict("spacing").value)
        total_content_height = pad
        for item in self.items:
            total_content_height += item._csize.y + pad
            
        visible_height = self._csize.y
        antirel = nevu_state.window.rel
        self.actual_max_main = max(0, (total_content_height - visible_height) / antirel.y)

    def get_relative_vector_offset(self) -> NvVector2: return self.coordinates + NvVector2(0, self.rely(self.get_offset()))

    def clone(self): return ScrollableColumn(self._template['size'], copy.deepcopy(self.style), self._template['content'], **self.constant_kwargs)