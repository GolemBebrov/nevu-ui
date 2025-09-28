import copy

from nevu_ui.core_types import Align
from nevu_ui.layouts import StackBase

class StackColumn(StackBase):
    def _recalculate_size(self):
        self.size[1] = sum(item.size[1] + self.spacing for item in self.items) if len(self.items) > 0 else 0
        self.size[0] = max(x.size[0] for x in self.items) if len(self.items) > 0 else 0
        
    def _recalculate_widget_coordinates(self):
        if self.booted == False: return
        self.cached_coordinates = []
        m = self.rely(self.spacing)
        current_y = 0
        for i in range(len(self.items)):
            item = self.items[i]
            alignment = self.widgets_alignment[i]
            widget_local_y = current_y + m
            item.coordinates[1] = self.coordinates[1] + widget_local_y 
            if alignment == Align.CENTER:
                item.coordinates[0] = self.coordinates[0] + self.relx(self.size[0] / 2 - item.size[0] / 2)
            elif alignment == Align.LEFT:
                item.coordinates[0] = self.coordinates[0]
            elif alignment == Align.RIGHT:
                item.coordinates[0] = self.coordinates[0] + self.relx(self.size[0] - item.size[0])
            item.master_coordinates = self._get_item_master_coordinates(item)
            current_y += self.rely(item.size[1] + self.spacing)
            self.cached_coordinates.append(item.coordinates)
            
    def clone(self):
        return StackColumn(copy.deepcopy(self.style), self._lazy_kwargs['content'], **self.constant_kwargs)
    
