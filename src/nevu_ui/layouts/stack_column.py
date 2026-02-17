from nevu_ui.nevuobj import NevuObject
from nevu_ui.core.enums import Align
from nevu_ui.layouts import StackBase

class StackColumn(StackBase):
    def _recalculate_size(self):
        if not hasattr(self, "size"): print("StackColumn not booted") ; return
        if any(x.booted == False for x in self.items): return
        self.size[1] = sum(item.size[1] + self.spacing for item in self.items) if len(self.items) > 0 else 0
        self.size[0] = max(x.size[0] for x in self.items) if len(self.items) > 0 else 0

    def _set_align_coords(self, item: NevuObject, alignment: Align):
        match alignment:
            case Align.CENTER: item.coordinates.x = self.coordinates.x + self.relx((self.size.x - item.size.x)/2)
            case Align.LEFT: item.coordinates.x = self.coordinates.x
            case Align.RIGHT: item.coordinates.x = self.coordinates.x + self.relx(self.size.x - item.size.x)

    def _recalculate_widget_coordinates(self):
        if self.booted == False: return
        self.cached_coordinates = []
        m = self.rely(self.spacing)
        current_y = 0
        for i in range(len(self.items)):
            item, alignment = self.items[i], self.widgets_alignment[i]
            item.coordinates.y = self.coordinates.y + (current_y + m / 2)
            self._set_align_coords(item, alignment)
            item.absolute_coordinates = self._get_item_abs_coords(item)
            current_y += self.rely(item.size.y + self.spacing)
            self.cached_coordinates.append(item.coordinates)