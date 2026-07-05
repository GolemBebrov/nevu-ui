from nevu_ui.components.layouts.stack.base import StackBase
from nevu_ui.components.nevuobj import NevuObject
from nevu_ui.core.enums import Align
from nevu_ui.fast.logic.fast_logic import py_get_item_abs_coords


class StackRow(StackBase):
    def _recalculate_size(self):
        if not hasattr(self, "size"):
            print("StackColumn not booted")
            return
        if any(x.booted == False for x in self.items):
            return
        self.size.x = (
            sum(item.size.x + self.spacing for item in self.items)
            if len(self.items) > 0
            else 0
        )
        self.size.y = max(x.size.y for x in self.items) if len(self.items) > 0 else 0

    def _set_align_coords(self, item: NevuObject, alignment: Align):
        match alignment:
            case Align.CENTER:
                item.coordinates.y = self.coordinates.y + self.rely(
                    (self.size.y - item.size.y) / 2
                )
            case Align.LEFT:
                item.coordinates.y = self.coordinates.y
            case Align.RIGHT:
                item.coordinates.y = self.coordinates.y + self.rely(
                    self.size.y - item.size.y
                )

    def _recalculate_widget_coordinates(self):
        if self.booted == False:
            return
        self.cached_coordinates = []
        m = self.relx(self.spacing)
        current_x = 0
        for i in range(len(self.items)):
            item, alignment = self.items[i], self.widgets_alignment[i]

            orig_coords = item.coordinates.copy()

            item.coordinates.x = self.coordinates.x + (current_x + m / 2)
            self._set_align_coords(item, alignment)
            new_coords = item.coordinates.copy()

            item.coordinates = orig_coords
            item.set_coordinates(new_coords)

            item.absolute_coordinates = py_get_item_abs_coords(self, item)
            current_x += self.relx(item.size.x + self.spacing)
            self.cached_coordinates.append(item.coordinates)
