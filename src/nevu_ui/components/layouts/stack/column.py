from nevu_ui.components.layouts.stack.base import StackBase
from nevu_ui.components.nevuobj import NevuObject
from nevu_ui.core.enums import Align
from nevu_ui.fast.logic.fast_logic import py_get_item_abs_coords, rl_predraw_widgets


class StackColumn(StackBase):
    def _recalculate_size(self):
        if not hasattr(self, "size"):
            print("StackColumn not booted")
            return
        if any(x.booted == False for x in self.items):
            return
        self.size[1] = (
            sum(item.size[1] + self.spacing for item in self.items)
            if len(self.items) > 0
            else 0
        )
        self.size[0] = max(x.size[0] for x in self.items) if len(self.items) > 0 else 0

    def _set_align_coords(self, item: NevuObject, alignment: Align):
        match alignment:
            case Align.CENTER:
                item.coordinates.x = self.coordinates.x + self.relx(
                    (self.size.x - item.size.x) / 2
                )
            case Align.LEFT:
                item.coordinates.x = self.coordinates.x
            case Align.RIGHT:
                item.coordinates.x = self.coordinates.x + self.relx(
                    self.size.x - item.size.x
                )

    def _recalculate_widget_coordinates(self):
        if self.booted == False:
            return
        self.cached_coordinates = []
        m = self.rely(self.spacing)
        spacing = self.rely(self.spacing)
        current_y = 0
        for i in range(len(self.items)):
            item, alignment = self.items[i], self.widgets_alignment[i]

            orig_coords = item.coordinates.copy()

            item.coordinates.y = self.coordinates.y + (current_y + m / 2)
            self._set_align_coords(item, alignment)
            new_coords = item.coordinates.copy()

            item.coordinates = orig_coords
            item.set_coordinates(new_coords)

            item.absolute_coordinates = py_get_item_abs_coords(self, item)
            current_y += item.get_actual_size().y
            current_y += spacing
            self.cached_coordinates.append(item.coordinates)
