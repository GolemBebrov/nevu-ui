from typing import Unpack

from nevu_ui.fast.nvvector2.nvvector2 import NvVector2
from nevu_ui.style import default_style
from nevu_ui.widgets import Widget, WidgetKwargs

class EmptyWidget(Widget):
    def __init__(self, size: NvVector2 | list, **constant_kwargs: Unpack[WidgetKwargs]):
        super().__init__(size, default_style, **constant_kwargs)
    def draw(self): pass
    def clone(self): return EmptyWidget(self._lazy_kwargs['size'], **self.constant_kwargs)