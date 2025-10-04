import copy

from nevu_ui.fast.nvvector2 import NvVector2
from nevu_ui.widgets import Label, LabelKwargs

from typing import Any, TypedDict, NotRequired, Unpack

from nevu_ui.style import (
    Style, default_style
)

class ButtonKwargs(LabelKwargs):
    is_active: NotRequired[bool]
    throw_errors: NotRequired[bool]

class Button(Label):
    throw_errors: bool
    is_active: bool
    
    def __init__(self, function, text: str, size: NvVector2 | list, style: Style = default_style, **constant_kwargs: Unpack[ButtonKwargs]):
        super().__init__(text, size, style, **constant_kwargs)
        self.function = function
        
    def _init_booleans(self):
        super()._init_booleans()
        self.clickable = True
        self.hoverable = True
        
    def _add_constants(self):
        super()._add_constants()
        self._add_constant("is_active", bool, True)
        self._add_constant("throw_errors", bool, False)

    def _on_click_system(self):
        super()._on_click_system()
        if self.function and self.is_active:
            try: self.function()
            except Exception as e:
                if self.throw_errors: raise e
                else: print(e)
                
    def clone(self):
        return Button(self.function, self._lazy_kwargs['text'], self._lazy_kwargs['size'], copy.deepcopy(self.style), **self.constant_kwargs)
