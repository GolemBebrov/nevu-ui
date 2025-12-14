import copy

from nevu_ui.nevuobj import NevuObject
from nevu_ui.fast.nvvector2 import NvVector2 
from nevu_ui.layouts import Grid
from nevu_ui.style import Style, default_style

class Row(Grid):
    content_type = dict[Grid.any_number, NevuObject]
    def __init__(self, size: NvVector2 | list, style: Style = default_style, content: content_type | None = None, **constant_kwargs):
        super().__init__(size, style, None, **constant_kwargs)
        self._lazy_kwargs = {'size': size, 'content': content}
        
    def _add_constants(self):
        super()._add_constants()
        self._block_constant("row")
        
    def _lazy_init(self, size: NvVector2 | list, content: content_type | None = None): # type: ignore
        super()._lazy_init(size)
        self.add_items(content)
        
    def add_items(self, content: content_type | None): # type: ignore
        if not content: return
        for xcoord, item in content.items():
            self.add_item(item, xcoord)
            
    def add_item(self, item: NevuObject, x: Grid.any_number): # type: ignore
        return super().add_item(item, x, 1)
    
    def get_item(self, x: Grid.any_number) -> NevuObject | None: # type: ignore
        return super().get_item(x, 1)
