import copy

from nevu_ui.nevuobj import NevuObject
from nevu_ui.fast.nvvector2 import NvVector2 
from nevu_ui.layouts import Grid

from nevu_ui.style import (
    Style, default_style
)

class Row(Grid):
    def __init__(self, size: NvVector2 | list, style: Style = default_style, content: dict[int , NevuObject] | None = None, **constant_kwargs):
        super().__init__(size, style, None, **constant_kwargs)
        self._lazy_kwargs = {'size': size, 'content': content}
        
    def _add_constants(self):
        super()._add_constants()
        self._block_constant("row")
        
    def _lazy_init(self, size: NvVector2 | list, content: dict[int , NevuObject] | None = None): # type: ignore
        super()._lazy_init(size)
        self.cell_height = self.size[1] / self.row
        self.cell_width = self.size[0] / self.column
        if not content:
            return
        for xcoord, item in content.items():
            self.add_item(item, xcoord)
    def clone(self):
        return Row(self._lazy_kwargs['size'], copy.deepcopy(self.style), self._lazy_kwargs['content'], **self.constant_kwargs)
            
    def add_item(self, item: NevuObject, x: int): # type: ignore
        return super().add_item(item, x, 1)
    
    def get_item(self, x: int) -> NevuObject | None: # type: ignore
        return super().get_item(x, 1)
