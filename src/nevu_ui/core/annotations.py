from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from nevu_ui.presentation.style import Style
from nevu_ui.core.size.units import SizeRule
from nevu_ui.fast.nvvector2.nvvector2 import NvVector2


class Annotations:
    #=== size annotations ===
    any_number = float | int
    dest_like = tuple[any_number, any_number] | list[any_number]
    rect_like = tuple[any_number, any_number, any_number, any_number] | list[any_number]
    
    #=== color annotations ===
    rgb_color = tuple[int, int, int]
    rgba_color = tuple[int, int, int, int]
    rgb_like_color = rgb_color | rgba_color
    hsl_color = tuple[float, float, float]
    hsla_color = tuple[float, float, float, int]
    hex_color = str
    any_color = rgb_like_color | hsl_color | hex_color
    
    #=== NevuObject annotation ===
    size_item = int | SizeRule | float
    nevuobj_size = tuple[size_item, size_item] | list[size_item] | NvVector2 | None
    nevuobj_style = Any | str | None