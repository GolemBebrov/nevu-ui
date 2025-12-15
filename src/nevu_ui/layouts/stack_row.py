import copy

from nevu_ui.nevuobj import NevuObject
from nevu_ui.core_types import Align
from nevu_ui.layouts import StackBase

class StackRow(StackBase):
    def _recalculate_size(self):
        self.size.x = sum(item.size.x + self.spacing for item in self.items) if len(self.items) > 0 else 0
        self.size.y = max(x.size.y for x in self.items) if len(self.items) > 0 else 0

    def _set_align_coords(self, item: NevuObject, alignment: Align):
        match alignment:
            case Align.CENTER: item.coordinates.y = self.coordinates.y + self.rely((self.size.y - item.size.y)/2)
            case Align.LEFT: item.coordinates.y = self.coordinates.y
            case Align.RIGHT: item.coordinates.y = self.coordinates.y + self.rely(self.size.y - item.size.y)
    
    def _recalculate_widget_coordinates(self):
        if self.booted == False: return
        self.cached_coordinates = []
        m = self.relx(self.spacing)
        current_x = 0 
        for i in range(len(self.items)):
            item, alignment = self.items[i], self.widgets_alignment[i]
            item.coordinates.x = self.coordinates.x + (current_x + m / 2)
            self._set_align_coords(item, alignment)
            item.absolute_coordinates = self._get_item_master_coordinates(item)
            current_x += self.relx(item.size.x + self.spacing)
            self.cached_coordinates.append(item.coordinates)