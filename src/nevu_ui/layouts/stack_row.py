import copy

from nevu_ui.core_types import Align
from nevu_ui.layouts import StackBase

class StackRow(StackBase):
    def _recalculate_size(self):
        self.size.x = sum(item.size[0] + self.spacing for item in self.items) if len(self.items) > 0 else 0
        self.size.y = max(x.size[1] for x in self.items) if len(self.items) > 0 else 0

    def _recalculate_widget_coordinates(self):
        if self.booted == False: return
        self.cached_coordinates = []
        m = self.relx(self.spacing)
        current_x = 0 
        for i in range(len(self.items)):
            item = self.items[i]
            alignment = self.widgets_alignment[i]
            widget_local_x = current_x + m / 2
            item.coordinates[0] = self.coordinates[0] + widget_local_x 
            if alignment == Align.CENTER:
                item.coordinates[1] = self.coordinates[1] + self.rely(self.size[1] / 2 - item.size[1] / 2)
            elif alignment == Align.LEFT:
                item.coordinates[1] = self.coordinates[1]
            elif alignment == Align.RIGHT:
                item.coordinates[1] = self.coordinates[1] + self.rely(self.size[1] - item.size[1])
            item.master_coordinates = self._get_item_master_coordinates(item)
            current_x += self.relx(item.size[0] + self.spacing)
            self.cached_coordinates.append(item.coordinates)
            
    def clone(self):
        return StackRow(copy.deepcopy(self.style), self._lazy_kwargs['content'], **self.constant_kwargs)
