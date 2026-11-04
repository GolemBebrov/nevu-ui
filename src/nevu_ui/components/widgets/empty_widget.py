from typing import Unpack

from nevu_ui.components._typehints import _WidgetKwargs
from nevu_ui.components.widgets.widget import Widget
from nevu_ui.core import Annotations
from nevu_ui.presentation.color import Color
from nevu_ui.presentation.style import default_style


class EmptyWidget(Widget):
    def __init__(
        self,
        size: Annotations.nevuobj_size = None,
        **params: Unpack[_WidgetKwargs],
    ):
        super().__init__(size, default_style, **params)

    def draw(self):
        self.surface.clear(Color.Blank)

    def _create_clone(self):
        return EmptyWidget(self._template["size"], **self.kwargs)
