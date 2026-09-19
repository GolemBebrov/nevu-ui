from nevu_ui.core import Annotations, GradientConfig, GradientType, LinearSide
from nevu_ui.core.state import nevu_state
from nevu_ui.rendering.pygame.gradient import GradientPygame
from nevu_ui.rendering.raylib.gradient import GradientRaylib


class Gradient:
    def __new__(
        cls,
        colors: list[Annotations.rgb_like_color | tuple[Annotations.rgb_like_color, int]],
        type: GradientType = GradientType.Linear,
        direction: GradientConfig | tuple[float, float] = LinearSide.Right,
        transparency = None,
    ) -> GradientRaylib | GradientPygame:
        if nevu_state.window.renderer_type.raylib:
            return GradientRaylib(colors, type, direction, transparency=transparency)
        elif nevu_state.window.renderer_type.pygame_like:
            return GradientPygame(colors, type, direction, transparency)
        else:
            raise NotImplementedError("Gradient is not implemented for this backend.")

__all__ = ["Gradient"]
