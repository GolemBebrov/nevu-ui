import copy

from nevu_ui.nevuobj import NevuObject
from nevu_ui.fast.nvvector2 import NvVector2 
from nevu_ui.layouts import Grid

from nevu_ui.style import (
    Style, default_style
)

class Column(Grid):
    def __init__(self, size: NvVector2 | list, style: Style = default_style, content: dict[int , NevuObject] | None = None, **constant_kwargs):
        super().__init__(size, style, None, **constant_kwargs)
        self._lazy_kwargs = {'size': size, 'content': content}
        
    def _add_constants(self):
        super()._add_constants()
        self._block_constant("column")
        
    def _lazy_init(self, size: NvVector2 | list, content: dict[int , NevuObject] | None = None): # type: ignore
        super()._lazy_init(size)
        self.cell_height = self.size[1] / self.row
        self.cell_width = self.size[0] / self.column
        if not content:
            return
        for ycoord, item in content.items():
            self.add_item(item, ycoord)
            
    def add_item(self, item: NevuObject, y: int): # type: ignore
        return super().add_item(item, 1, y)
    
    def get_item(self, y: int) -> NevuObject | None: # type: ignore
        return super().get_item(1, y)
    def clone(self):
        return Column(self._lazy_kwargs['size'], copy.deepcopy(self.style), self._lazy_kwargs['content'], **self.constant_kwargs)
