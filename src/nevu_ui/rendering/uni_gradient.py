from typing import Any, Callable

from nevu_ui.core import Annotations, GradientConfig, GradientType, LinearSide
from nevu_ui.core.state import nevu_state
from nevu_ui.rendering.pygame.gradient import GradientPygame
from nevu_ui.rendering.raylib.gradient import GradientRaylib


def Gradient(
    colors: list[Annotations.rgb_like_color | tuple[Annotations.rgb_like_color, int]],
    type: GradientType = GradientType.Linear,
    direction: GradientConfig = LinearSide.Right,
    transparency=None,
):
    if nevu_state.window.renderer_type.raylib:
        return GradientRaylib(colors, type, direction, transparency=transparency)
    return GradientPygame(colors, type, direction, transparency)
