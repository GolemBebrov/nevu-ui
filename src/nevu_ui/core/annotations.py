from __future__ import annotations

from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from nevu_ui.cython.vector2 import Vector2

from nevu_ui.core.size import _SizeRule
from nevu_ui.core.state import nevu_state

VERSION = "0.9.1"

class NevuNotInitializedError(RuntimeError): ...

class Annotations:
    # === size annotations ===
    type any_number = float | int
    type vec2_like = tuple[any_number, any_number] | list[any_number]
    type vec2_like_v = vec2_like | Vector2
    type vec2_like_srule = tuple[_SizeRule, _SizeRule] | list[_SizeRule]
    type vec2_all = vec2_like_v | vec2_like_srule
    type rect_like = tuple[any_number, any_number, any_number, any_number] | list[any_number]

    # === destination annotations ===
    type dest_like_v = vec2_like_v | rect_like

    # === radius annotations ===
    type normalized_radius = tuple[any_number, any_number, any_number, any_number]
    type rad_like = normalized_radius | float

    # === color annotations ===
    type rgb_color = tuple[int, int, int]
    type rgba_color = tuple[int, int, int, int]
    type rgb_like_color = rgb_color | rgba_color
    type hsl_color = tuple[float, float, float]
    type hsla_color = tuple[float, float, float, int]
    type hex_color = str
    type any_color = rgb_like_color | hsl_color | hex_color

    # === NevuObject annotation ===
    type size_item = _SizeRule | float
    type nevuobj_size = tuple[size_item, size_item] | list[size_item] | Any | None
    type nevuobj_style = Any | str | None

    @staticmethod
    def window_check():
        if nevu_state.window is None:
            raise NevuNotInitializedError(
                "Nevu UI window isnt initialized.\nPlease create Nevu UI window first "
            )

__all__ = ["Annotations"]
