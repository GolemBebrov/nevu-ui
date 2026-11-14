import math

import numpy as np

import nevu_ui.core.modules as md
from nevu_ui.core import (
    Annotations,
    GradientConfig,
    GradientType,
    LinearSide,
    RadialPosition,
)
from nevu_ui.presentation import color as nv_color

_gradient_invert_dict = {
    LinearSide.Right: LinearSide.Left,
    LinearSide.Left: LinearSide.Right,
    LinearSide.Top: LinearSide.Bottom,
    LinearSide.Bottom: LinearSide.Top,
    LinearSide.TopRight: LinearSide.BottomLeft,
    LinearSide.BottomLeft: LinearSide.TopRight,
    LinearSide.TopLeft: LinearSide.BottomRight,
    LinearSide.BottomRight: LinearSide.TopLeft,
    RadialPosition.Center: RadialPosition.Center,
    RadialPosition.TopCenter: RadialPosition.BottomCenter,
    RadialPosition.BottomCenter: RadialPosition.TopCenter,
    RadialPosition.TopLeft: RadialPosition.BottomRight,
    RadialPosition.BottomRight: RadialPosition.TopLeft,
    RadialPosition.TopRight: RadialPosition.BottomLeft,
    RadialPosition.BottomLeft: RadialPosition.TopRight,
}
_gradient_radial_value_dict = {
    RadialPosition.Center: (0.5, 0.5),
    RadialPosition.TopCenter: (0.5, 0),
    RadialPosition.BottomCenter: (0.5, 1),
    RadialPosition.TopLeft: (0, 0),
    RadialPosition.BottomRight: (1, 1),
    RadialPosition.TopRight: (1, 0),
    RadialPosition.BottomLeft: (0, 1),
}


class GradientPygame:
    def __init__(
        self,
        colors: list[Annotations.rgb_like_color | tuple[Annotations.rgb_like_color, float]],
        direction: GradientConfig | tuple[float, float] | list[float] = LinearSide.Right,
        transparency=None,
    ):
        self.colors = self._validate_colors(colors)
        self.direction = direction
        self.type = self._detect_type(direction)
        self.transparency = transparency
        self._precompute_colors_and_stops()

    @staticmethod
    def _detect_type(direction) -> GradientType:
        if isinstance(direction, LinearSide):
            return GradientType.Linear
        if isinstance(direction, RadialPosition) or (
            isinstance(direction, (tuple, list)) and len(direction) == 2
        ):
            return GradientType.Radial
        if isinstance(direction, (int, float)) and not isinstance(direction, bool):
            raise NotImplementedError(
                "Arbitrary angle gradients are not supported in Pygame backend; use LinearSide."
            )
        raise ValueError(f"Gradient direction '{direction}' is not supported.")

    def _precompute_colors_and_stops(self):
        colors_only = [c[0] for c in self.colors]
        weights = [c[1] for c in self.colors]

        max_channels = max(len(c) for c in colors_only)
        self._has_alpha = max_channels == 4

        if self._has_alpha:
            colors_only = [c if len(c) == 4 else c + (255,) for c in colors_only]

        self._colors_array = np.array(colors_only, dtype=np.float32)

        stops = np.zeros(len(self.colors), dtype=np.float32)
        if len(self.colors) > 1:
            stops[1:] = np.cumsum(weights[:-1])
            if stops[-1] > 0:
                stops /= stops[-1]
            else:
                stops = np.linspace(0.0, 1.0, len(self.colors), dtype=np.float32)
        self._stops = stops

    def with_transparency(self, transparency):
        return GradientPygame(self.colors, self.direction, transparency)

    def apply_gradient(self, width, height):
        if self._has_alpha:
            gradient_surface = md.pygame.Surface((width, height), md.pygame.SRCALPHA)
        else:
            gradient_surface = md.pygame.Surface((width, height))

        if self.type == GradientType.Linear:
            self._apply_linear_gradient(gradient_surface)
        elif self.type == GradientType.Radial:
            self._apply_radial_gradient(gradient_surface)

        if self.transparency is not None:
            gradient_surface.set_alpha(self.transparency)

        return gradient_surface

    def _apply_linear_gradient(self, surface):
        width, height = surface.get_size()

        if self.direction in (LinearSide.Right, LinearSide.Left):
            progress = np.linspace(0.0, 1.0, width, dtype=np.float32)
            if self.direction == LinearSide.Left:
                progress = 1.0 - progress
            self._blit_numpy_gradient_1d(surface, progress, axis=0)

        elif self.direction in (LinearSide.Bottom, LinearSide.Top):
            progress = np.linspace(0.0, 1.0, height, dtype=np.float32)
            if self.direction == LinearSide.Top:
                progress = 1.0 - progress
            self._blit_numpy_gradient_1d(surface, progress, axis=1)

        else:
            x_lin = np.linspace(0.0, 1.0, width, dtype=np.float32)
            y_lin = np.linspace(0.0, 1.0, height, dtype=np.float32)

            match self.direction:
                case LinearSide.BottomRight:
                    progress = (x_lin[:, np.newaxis] + y_lin[np.newaxis, :]) * 0.5
                case LinearSide.TopLeft:
                    progress = 1.0 - (x_lin[:, np.newaxis] + y_lin[np.newaxis, :]) * 0.5
                case LinearSide.TopRight:
                    progress = (
                        x_lin[:, np.newaxis] + (1.0 - y_lin[np.newaxis, :])
                    ) * 0.5
                case LinearSide.BottomLeft:
                    progress = (
                        (1.0 - x_lin[:, np.newaxis]) + y_lin[np.newaxis, :]
                    ) * 0.5
                case _:
                    raise ValueError(
                        f"Unsupported gradient direction: {self.direction}"
                    )

            self._blit_numpy_gradient_2d(surface, progress)

    def _apply_radial_gradient(self, surface):
        width, height = surface.get_size()
        center_x, center_y = self._get_radial_center(width, height)

        w_m, h_m = width - 1, height - 1
        max_dx = max(center_x, w_m - center_x)
        max_dy = max(center_y, h_m - center_y)
        max_radius = math.hypot(max_dx, max_dy)

        if max_radius == 0:
            surface.fill(self.colors[0][0])
            return

        y_grid, x_grid = np.ogrid[:height, :width]
        dist_sq = (x_grid - center_x) ** 2 + (y_grid - center_y) ** 2
        distance = np.sqrt(dist_sq)

        progress = distance.T / max_radius
        self._blit_numpy_gradient_2d(surface, progress)

    def _blit_numpy_gradient_1d(self, surface, progress, axis: int):
        progress = np.clip(progress, 0.0, 1.0)
        stops = self._stops
        colors_array = self._colors_array

        r = np.interp(progress, stops, colors_array[:, 0])
        g = np.interp(progress, stops, colors_array[:, 1])
        b = np.interp(progress, stops, colors_array[:, 2])

        gradient_1d_rgb = np.empty((len(progress), 3), dtype=np.uint8)
        gradient_1d_rgb[:, 0] = r
        gradient_1d_rgb[:, 1] = g
        gradient_1d_rgb[:, 2] = b

        width, height = surface.get_size()
        if axis == 0:
            gradient_array_rgb = np.broadcast_to(
                gradient_1d_rgb[:, np.newaxis, :], (width, height, 3)
            )
        else:
            gradient_array_rgb = np.broadcast_to(
                gradient_1d_rgb[np.newaxis, :, :], (width, height, 3)
            )

        md.pygame.surfarray.blit_array(surface, gradient_array_rgb)

        if self._has_alpha:
            a = np.interp(progress, stops, colors_array[:, 3]).astype(np.uint8)
            if axis == 0:
                gradient_alpha = np.broadcast_to(a[:, np.newaxis], (width, height))
            else:
                gradient_alpha = np.broadcast_to(a[np.newaxis, :], (width, height))

            alpha_view = md.pygame.surfarray.pixels_alpha(surface)
            alpha_view[:, :] = gradient_alpha

    def _blit_numpy_gradient_2d(self, surface, progress):
        progress = np.clip(progress, 0.0, 1.0)
        stops = self._stops
        colors_array = self._colors_array

        r = np.interp(progress, stops, colors_array[:, 0])
        g = np.interp(progress, stops, colors_array[:, 1])
        b = np.interp(progress, stops, colors_array[:, 2])

        width, height = surface.get_size()

        gradient_array_rgb = np.empty((width, height, 3), dtype=np.uint8)
        gradient_array_rgb[..., 0] = r
        gradient_array_rgb[..., 1] = g
        gradient_array_rgb[..., 2] = b

        md.pygame.surfarray.blit_array(surface, gradient_array_rgb)

        if self._has_alpha:
            a = np.interp(progress, stops, colors_array[:, 3]).astype(np.uint8)
            alpha_view = md.pygame.surfarray.pixels_alpha(surface)
            alpha_view[:, :] = a

    def _get_radial_center(self, width: int, height: int) -> tuple[float, float]:
        w_m, h_m = width - 1, height - 1
        if isinstance(self.direction, RadialPosition):
            values = _gradient_radial_value_dict.get(self.direction, (0, 0))
        else:
            values = self.direction
        return w_m * values[0], h_m * values[1]

    def _validate_colors(self, colors):
        if not isinstance(colors, list | tuple):
            raise TypeError("Gradient colors type must be a list or tuple.")
        if len(colors) < 2:
            raise ValueError("Gradient colors must contain at least two colors.")
        correct_colors = []
        for item in colors:
            if not isinstance(item, list | tuple):
                raise TypeError(f"color {item} in gradient colors has invalid type.")
            if len(item) == 2 and 3 <= len(item[0]) <= 4:
                col, weight = item[0], item[1]
            elif 3 <= len(item) <= 4:
                col, weight = item, 1.0
            else:
                raise ValueError(f"Gradient color has invalid structure: {item}.")

            if isinstance(col, str):
                try:
                    color_tuple = getattr(nv_color, col.capitalize())
                except AttributeError:
                    raise ValueError(f"Unsupported color name: '{col}'.")
                correct_colors.append((color_tuple, weight))

            elif (
                isinstance(col, (tuple, list))
                and 3 <= len(col) <= 4
                and all(isinstance(c, int | float) and 0 <= c <= 255 for c in col)
            ):
                correct_colors.append((tuple(col), weight))
            else:
                raise ValueError(
                    "Each color must be a tuple of 3 or 4 integers (RGB/RGBA), a valid color name, or a tuple of (color, weight)."
                )
        return correct_colors

    def invert(self, new_direction=None):
        if new_direction is None:
            if isinstance(self.direction, (tuple, list)):
                new_direction = (1.0 - self.direction[0], 1.0 - self.direction[1])
            else:
                new_direction = _gradient_invert_dict.get(self.direction)
        if new_direction is None:
            raise ValueError(
                f"Inversion for direction '{self.direction}' is not supported."
            )
        return GradientPygame(
            list(reversed(self.colors)), new_direction, self.transparency
        )
