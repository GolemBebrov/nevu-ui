import copy
from typing import Unpack, Callable

from nevu_ui.fast.nvvector2 import NvVector2
from nevu_ui.components.widgets import Label, ButtonKwargs
from nevu_ui.presentation.style import Style, default_style

class Button(Label):
    def __init__(self, function: Callable, text: str, size: NvVector2 | list, style: Style = default_style, **constant_kwargs: Unpack[ButtonKwargs]):
        super().__init__(text, size, style, **constant_kwargs)
        self.function = function
        
    def _init_booleans(self):
        super()._init_booleans()
    
    def _add_params(self):
        super()._add_params()
        self._add_param("is_active", bool, True)
        self._add_param("throw_errors", bool, False)
        self._change_param_default("hoverable", True)
        self._change_param_default("clickable", True)

    def _on_click_system(self):
        super()._on_click_system()
        if self.function and self.is_active:
            try: self.function()
            except Exception as e:
                if self.throw_errors: raise e
                else: print(e)
                
    def _create_clone(self): return Button(self.function, self._template['text'], self._template['size'], copy.deepcopy(self.style), **self.constant_kwargs)
