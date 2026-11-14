from typing import Any

from nevu_ui.core import Annotations, GradientConfig, LinearSide
from nevu_ui.core.state import nevu_state
from nevu_ui.rendering.pygame.gradient import GradientPygame
from nevu_ui.rendering.raylib.gradient import GradientRaylib


class _GradientMeta(type):
    def __instancecheck__(cls, instance: Any) -> bool:
        return isinstance(instance, (GradientRaylib, GradientPygame))


class Gradient(metaclass=_GradientMeta):
    def __new__(
        cls,
        colors: list[Annotations.rgb_like_color | tuple[Annotations.rgb_like_color, float]],
        direction: GradientConfig | tuple[float, float] | float = LinearSide.Right,
        transparency=None,
    ) -> GradientRaylib | GradientPygame:
        rtype = nevu_state.window.renderer_type
        if rtype.raylib:
            return GradientRaylib(colors, direction, transparency=transparency)
        elif rtype.pygame_like:
            return GradientPygame(colors, direction, transparency)
        else:
            raise NotImplementedError("Gradient is not implemented for selected backend.")


__all__ = ["Gradient"]
