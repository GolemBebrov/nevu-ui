from typing import Unpack

from nevu_ui.components.widgets import Element
from nevu_ui.components.widgets.widget import Widget
from nevu_ui.core.annotations import Annotations
from nevu_ui.core.classes import Elements

#TODO
#class Dropdown(Widget):
#    def __init__(
#        self,
#        elements: list[Element | list | str] | None = None,
#        size: Annotations.nevuobj_size = None,
#        style: Annotations.nevuobj_style = None,
#        **params#Unpack[_WidgetKwargs],
#    ):
#        super().__init__(size, style, **params)
#        self._elements = Elements.create(*(elements or []))
#
#    def _add_params(self):
#        super()._add_params()
#
