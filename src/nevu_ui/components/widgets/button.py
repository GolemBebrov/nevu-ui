from __future__ import annotations

import copy
from collections.abc import Callable
from typing import Unpack

from nevu_ui.components.widgets.label import Label
from nevu_ui.components.widgets.typehints import ButtonKwargs
from nevu_ui.core import Annotations
from nevu_ui.core.enums import BindType


class Button(Label):
    # === Params ===
    is_active: bool
    throw_errors: bool

    # ==============
    def __init__(
        self,
        function: Callable,
        text: str,
        size: Annotations.nevuobj_size = None,
        style: Annotations.nevuobj_style = None,
        **constant_kwargs: Unpack[ButtonKwargs],
    ):
        super().__init__(text, size, style, **constant_kwargs)
        self.function = function

    def _system_callback_binds(self):
        super()._system_callback_binds()
        self._system_callbacks.bind(BindType.KeyUp, _button_on_keyup)

    def _add_params(self):
        super()._add_params()
        self._add_param("is_active", bool, True)
        self._add_param("throw_errors", bool, False)
        self._change_param_default("hoverable", True)
        self._change_param_default("clickable", True)

    def _create_clone(self):
        return Button(
            self.function,
            self._template["text"],
            self._template["size"],
            copy.deepcopy(self.style),
            **self.constant_kwargs,
        )

# === NOT CLASS FUNCTIONS ===

def _button_on_keyup(self):
    if not ((func := self.function) and self.is_active):
        return
    try:
        func()
    except Exception as e:
        if self.throw_errors:
            raise e
        else:
            print(
                f"Error in Button(id = {self.id}, text = {self.text!r}) function: {e}"
            )
