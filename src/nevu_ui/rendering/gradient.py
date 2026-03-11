from nevu_ui.core.state import nevu_state
from nevu_ui.rendering.pygame.gradient import GradientPygame
from nevu_ui.rendering.raylib.gradient import GradientRaylib
from nevu_ui.presentation.color.color import is_rgb_like
from nevu_ui.core import Annotations
from nevu_ui.core import (
    LinearSide, GradientType, GradientConfig
)

def Gradient(colors: list[Annotations.rgb_like_color | tuple[Annotations.rgb_like_color, int]], type: GradientType = GradientType.Linear, direction: GradientConfig = LinearSide.Right, transparency = None):
    if nevu_state.window.is_dtype.raylib:
        return GradientRaylib(colors, type, direction, transparency=transparency)
    return GradientPygame(colors, type, direction, transparency)

def gradient_queue(*colors: Annotations.rgb_like_color | tuple[Annotations.rgb_like_color, int]):
    new_colors = []
    for item in colors:
        if is_rgb_like(item):
            new_colors.append(item)
        elif isinstance(item, tuple):
            new_colors.extend((item[0],)*item[1])
    return new_colors