import copy

from nevu_ui.components.layouts.scrollable.base import ScrollableBase
from nevu_ui.components.nevuobj import NevuObject
from nevu_ui.core.enums import Align, ScrollBarType
from nevu_ui.core.state import nevu_state
from nevu_ui.fast.nvvector2 import NvVector2
from nevu_ui.utils import Keys


class ScrollableRow(ScrollableBase):
    def _main_coord(self, coordinates: NvVector2):
        return coordinates.x

    def _sec_coord(self, coordinates: NvVector2):
        return coordinates.y

    @property
    def _main_axis(self):
        return 0

    @property
    def _sec_axis(self):
        return 1

    def _add_params(self):
        super()._add_params()
        self._change_param_default("append_key", Keys.Left)
        self._change_param_default("descend_key", Keys.Right)
        self._change_param_default("basic_alignment", Align.TOP)

    def _parse_align(self, align: Align):
        return align in (Align.TOP, Align.BOTTOM, Align.CENTER)

    @property
    def _scrollbar_type(self) -> ScrollBarType:
        return ScrollBarType.Horizontal

    def _get_scrollbar_coordinates(self) -> NvVector2:
        return NvVector2(
            self.coordinates.x
            + self.relx(self.size.x - self.scroll_bar.size.x)
            / 100
            * self.scroll_bar.percentage,
            self.coordinates.y + self.rely(self.size.y - self.scroll_bar.size.y),
        )

    def _set_item_main(self, item: NevuObject, align: Align):
        container_height, widget_height = self._csize.y, item._csize.y
        padding = self.rely(self.get_param_strict("spacing").value)
        item_coords = item.coordinates

        value = 0
        if align == Align.TOP:
            value = self.coordinates.y + padding
        elif align == Align.BOTTOM:
            value = self.coordinates.y + container_height - widget_height - padding
        elif align == Align.CENTER:
            value = self.coordinates.y + container_height / 2 - widget_height / 2
        item_coords.y = value

    def _regenerate_max_values(self):
        assert nevu_state.window, "Window is not initialized"
        pad = self.relx(self.get_param_strict("spacing").value)
        total_content_width = pad
        for item in self.items:
            total_content_width += item._csize.x + pad

        visible_width = self._csize.x
        antirel = nevu_state.window.rel
        if antirel.x == 0:
            self.actual_max_main = 0
        else:
            self.actual_max_main = max(
                0, (total_content_width - visible_width) / antirel.x
            )

    def _update_offset(self):
        self._offset = NvVector2.from_xy(self.relx(self.get_offset()), 0)
