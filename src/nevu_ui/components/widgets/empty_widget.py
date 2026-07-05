from typing import Unpack

from nevu_ui.components.widgets.typehints import WidgetKwargs
from nevu_ui.components.widgets.widget import Widget
from nevu_ui.core import Annotations
from nevu_ui.presentation.style import default_style


class EmptyWidget(Widget):
    def __init__(
        self,
        size: Annotations.nevuobj_size = None,
        **constant_kwargs: Unpack[WidgetKwargs],
    ):
        super().__init__(size, default_style, **constant_kwargs)

    def draw(self):
        if self._changed:
            self.surface.fill((0, 0, 0, 0))

    def clone(self):
        return EmptyWidget(self._template["size"], **self.constant_kwargs)
