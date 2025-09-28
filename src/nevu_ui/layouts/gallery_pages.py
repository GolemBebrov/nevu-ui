from nevu_ui.fast.nvvector2 import NvVector2

from nevu_ui.layouts import (
    Grid, Pages
)
from nevu_ui.widgets import (
    Widget, Image, Gif
)

class Gallery_Pages(Pages):
    def __init__(self, size: NvVector2 | list):
        super().__init__(size)
        
    def add_item(self, item: Widget): # type: ignore
        if self.is_layout(item): raise ValueError("Widget must not be Layout, layout creates automatically")
        if isinstance(item, (Image, Gif)):
            g = Grid(self.size)
            g.add_item(item, 1, 1)
            super().add_item(g)