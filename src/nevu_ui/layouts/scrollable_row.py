import pygame
import copy

from nevu_ui.nevuobj import NevuObject
from nevu_ui.fast.nvvector2 import NvVector2
from nevu_ui.layouts.scrollable_base import ScrollableBase
from nevu_ui.fast.logic.fast_logic import collide_horizontal
from nevu_ui.core.state import nevu_state
from nevu_ui.core.enums import Align, ScrollBarType

class ScrollableRow(ScrollableBase):
    def _main_coord(self, coordinates: NvVector2): return coordinates.x
    def _sec_coord(self, coordinates: NvVector2): return coordinates.y
    @property
    def _main_axis(self): return 0
    
    def _add_params(self):
        super()._add_params()
        self._change_param_default("append_key", pygame.K_LEFT)
        self._change_param_default("descend_key", pygame.K_RIGHT)
        self._change_param_default("basic_alignment", Align.TOP)

    def _parse_align(self, align: Align): return align in (Align.TOP, Align.BOTTOM, Align.CENTER)

    def _create_scroll_bar(self) -> ScrollableBase.ScrollBar: 
        if not self.scrollbar_perc:
            size = NvVector2(self.size[0]/20, self.size[1]/40)
        else: size = self.size/100*self.scrollbar_perc
        return self.ScrollBar(size, self.style, ScrollBarType.Horizontal, self)

    def _get_scrollbar_coordinates(self) -> NvVector2:
        return NvVector2(self.scroll_bar.coordinates.x, self._coordinates.y + self.rely(self.size.y - self.scroll_bar.size.y))
    
    @property
    def _collide_function(self): return collide_horizontal
        
    def _set_item_main(self, item: NevuObject, align: Align):
        container_height, widget_height = self.rely(self.size[1]), self.rely(item.size[1])
        padding = self.rely(self.get_param_strict("spacing").value)

        match align:
            case Align.TOP: item.coordinates.y = self._coordinates.y + padding
            case Align.BOTTOM: item.coordinates.y = self._coordinates.y + (container_height - widget_height - padding)
            case Align.CENTER: item.coordinates.y = self._coordinates.y + (container_height / 2 - widget_height / 2)

    def _base_light_update(self, items = None): # type: ignore
        super()._base_light_update(-self.get_offset(), 0, items = items)
        
    def _regenerate_max_values(self):
        assert nevu_state.window, "Window is not initialized"
        pad = self.relx(self.get_param_strict("spacing").value)
        total_content_width = pad
        for item in self.items:
            total_content_width += item._csize.x + pad
            
        visible_width = self._csize.x
        antirel = nevu_state.window.rel
        self.actual_max_main = max(0, (total_content_width - visible_width) / antirel.x)

    def get_relative_vector_offset(self) -> NvVector2: return NvVector2(self.relx(self.get_offset()), 0)

    def clone(self): return ScrollableRow(self._template['size'], copy.deepcopy(self.style), self._template['content'], **self.constant_kwargs)