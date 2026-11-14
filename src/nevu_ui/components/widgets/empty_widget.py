from typing import Unpack

from nevu_ui.components._typehints import _WidgetKwargs
from nevu_ui.components.widgets.widget import Widget
from nevu_ui.core import Annotations
from nevu_ui.presentation import color
from nevu_ui.presentation.style import Style


class EmptyWidget(Widget):
    def __init__(self, size: Annotations.nevuobj_size = None, **params: Unpack[_WidgetKwargs]):
        super().__init__(size, Style(), **params)

    def draw(self):
        if not self._visible or self._wait_mode or self._dead or not self.surface:
            return
        self._changed = False
        self.surface.clear(color.Blank)

    def _create_clone(self):
        return self.__class__(self._template["size"], **self.kwargs)
