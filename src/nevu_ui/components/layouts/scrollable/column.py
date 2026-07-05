import copy

from nevu_ui.components.layouts.scrollable.base import ScrollableBase
from nevu_ui.components.nevuobj import NevuObject
from nevu_ui.core.enums import Align, ScrollBarType
from nevu_ui.core.state import nevu_state
from nevu_ui.fast.nvvector2 import NvVector2
from nevu_ui.utils import Keys


class ScrollableColumn(ScrollableBase):
    def _main_coord(self, coordinates: NvVector2):
        return coordinates.y

    def _sec_coord(self, coordinates: NvVector2):
        return coordinates.x

    @property
    def _main_axis(self):
        return 1

    @property
    def _sec_axis(self):
        return 0

    def _add_params(self):
        super()._add_params()
        self._change_param_default("append_key", Keys.Up)
        self._change_param_default("descend_key", Keys.Down)
        self._change_param_default("basic_alignment", Align.LEFT)

    def _parse_align(self, align: Align):
        return align in (Align.LEFT, Align.RIGHT, Align.CENTER)

    @property
    def _scrollbar_type(self) -> ScrollBarType:
        return ScrollBarType.Vertical

    def _get_scrollbar_coordinates(self) -> NvVector2:
        return NvVector2(
            self.coordinates.x + self.relx(self.size.x - self.scroll_bar.size.x),
            self.coordinates.y
            + self.rely(self.size.y - self.scroll_bar.size.y)
            / 100
            * self.scroll_bar.percentage,
        )

    def _set_item_main(self, item: NevuObject, align: Align):
        container_width, widget_width = self._csize.x, item._csize.x
        padding = self.relx(self.get_param_strict("spacing").value)
        item_coords = item.coordinates

        value = 0
        match align:
            case Align.LEFT:
                value = self.coordinates.x + padding
            case Align.RIGHT:
                value = self.coordinates.x + container_width - widget_width - padding
            case Align.CENTER:
                value = self.coordinates.x + container_width / 2 - widget_width / 2
        item_coords.x = value

    def _regenerate_max_values(self):
        assert nevu_state.window, "Window is not initialized"
        pad = self.rely(self.get_param_strict("spacing").value)
        total_content_height = pad
        for item in self.items:
            total_content_height += item._csize.y + pad

        visible_height = self._csize.y
        antirel = nevu_state.window.rel
        if antirel.y == 0:
            self.actual_max_main = 0
        else:
            self.actual_max_main = max(
                0, (total_content_height - visible_height) / antirel.y
            )

    def _update_offset(self):
        self._offset = NvVector2.from_xy(0, self.rely(self.get_offset()))
