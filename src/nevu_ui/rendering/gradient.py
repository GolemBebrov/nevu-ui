import pygame
import numpy as np

from nevu_ui.color import Color

from nevu_ui.core import (
    LinearSide, RadialPosition, GradientType, GradientConfig
)

class Gradient:
    def __init__(self, colors: list[tuple[int, int, int]], type: GradientType = GradientType.Linear, direction: GradientConfig = LinearSide.Right, transparency = None):
        self.colors = self._validate_colors(colors)
        if len(self.colors) < 2:
            raise ValueError("Gradient must contain at least two colors.")
        self.type = type
        self.direction = direction
        self._validate_type_direction()
        self.transparency = transparency

    def _validate_type_direction(self):
        self._validate_gradient_type()
        if self.type == GradientType.Linear:
            self._validate_linear_direction()
        elif self.type == GradientType.Radial:
            self._validate_radial_direction()
        else:
            raise ValueError(f"Unrecognized gradient type: {self.type}")

    def _validate_gradient_type(self):
        if self.type not in GradientType:
            raise ValueError(f"Gradient type '{self.type}' is not supported. Choose linear or radial.")

    def _validate_linear_direction(self):
        if self.direction not in LinearSide:
            raise ValueError(f"Linear gradient direction '{self.direction}' is not supported.")

    def _validate_radial_direction(self):
        if self.direction not in RadialPosition:
            raise ValueError(f"Radial gradient direction '{self.direction}' is not supported.")

    def with_transparency(self, transparency):
        return Gradient(self.colors, self.type, self.direction, transparency)

    def apply_gradient(self, surface):
        gradient_surface = pygame.Surface(surface.get_size(), pygame.SRCALPHA)
        
        if self.type == GradientType.Linear:
            self._apply_linear_gradient(gradient_surface)
        elif self.type == GradientType.Radial:
            self._apply_radial_gradient(gradient_surface)
        
        if self.transparency is not None:
            gradient_surface.set_alpha(self.transparency)
        surface.blit(gradient_surface, (0, 0))
        return surface

    def _apply_linear_gradient(self, surface):
        width, height = surface.get_size()
        
        x_lin = np.linspace(0.0, 1.0, width, dtype=np.float32)
        y_lin = np.linspace(0.0, 1.0, height, dtype=np.float32)

        if self.direction == LinearSide.Right:
            progress = x_lin[:, np.newaxis]
        elif self.direction == LinearSide.Left:
            progress = 1.0 - x_lin[:, np.newaxis]
        elif self.direction == LinearSide.Bottom:
            progress = y_lin[np.newaxis, :]
        elif self.direction == LinearSide.Top:
            progress = 1.0 - y_lin[np.newaxis, :]
        elif self.direction == LinearSide.BottomRight:
            progress = (x_lin[:, np.newaxis] + y_lin[np.newaxis, :]) * 0.5
        elif self.direction == LinearSide.TopLeft:
            progress = 1.0 - (x_lin[:, np.newaxis] + y_lin[np.newaxis, :]) * 0.5
        elif self.direction == LinearSide.TopRight:
            progress = (x_lin[:, np.newaxis] + (1.0 - y_lin[np.newaxis, :])) * 0.5
        elif self.direction == LinearSide.BottomLeft:
            progress = ((1.0 - x_lin[:, np.newaxis]) + y_lin[np.newaxis, :]) * 0.5
        else:
            raise ValueError(f"Unsupported gradient direction: {self.direction}")

        self._blit_numpy_gradient(surface, progress)

    def _apply_radial_gradient(self, surface):
        width, height = surface.get_size()
        center_x, center_y = self._get_radial_center(width, height)
        
        y_grid, x_grid = np.ogrid[:height, :width]
        
        dist_sq = (x_grid - center_x)**2 + (y_grid - center_y)**2
        distance = np.sqrt(dist_sq).astype(np.float32)

        corners = np.array([(0, 0), (width - 1, 0), (0, height - 1), (width - 1, height - 1)], dtype=np.float32)
        corner_dists_sq = (corners[:, 0] - center_x)**2 + (corners[:, 1] - center_y)**2
        max_radius = np.sqrt(np.max(corner_dists_sq))
        
        if max_radius == 0:
            surface.fill(self.colors[0])
            return

        progress = distance.T / max_radius
        self._blit_numpy_gradient(surface, progress)

    def _blit_numpy_gradient(self, surface, progress):
        progress = np.clip(progress, 0.0, 1.0)
        
        stops = np.linspace(0.0, 1.0, len(self.colors), dtype=np.float32)
        colors_array = np.array(self.colors, dtype=np.float32)
        
        r = np.interp(progress, stops, colors_array[:, 0])
        g = np.interp(progress, stops, colors_array[:, 1])
        b = np.interp(progress, stops, colors_array[:, 2])

        if progress.ndim == 2: 
            gradient_array = np.dstack((r, g, b)).astype(np.uint8)
        else:
            gradient_array = np.stack((r, g, b), axis=-1).astype(np.uint8)
            gradient_array = np.broadcast_to(gradient_array, surface.get_size() + (3,))

        pygame.surfarray.blit_array(surface, gradient_array)

    def _get_radial_center(self, width, height):
        w_m, h_m = width - 1, height - 1
        center_map = {
            RadialPosition.Center: (w_m * 0.5, h_m * 0.5),
            RadialPosition.TopCenter: (w_m * 0.5, 0),
            RadialPosition.TopLeft: (0, 0),
            RadialPosition.TopRight: (w_m, 0),
            RadialPosition.BottomCenter: (w_m * 0.5, h_m),
            RadialPosition.BottomLeft: (0, h_m),
            RadialPosition.BottomRight: (w_m, h_m)
        }
        return center_map.get(self.direction, (w_m * 0.5, h_m * 0.5)) # type: ignore

    def _validate_colors(self, colors):
        if not isinstance(colors, (list, tuple)):
            raise ValueError("Gradient colors must be a list or tuple.")

        validated_colors = []
        for color in colors:
            if isinstance(color, str):
                try:
                    color_tuple = getattr(Color, color.upper())
                    if isinstance(color_tuple, tuple) and len(color_tuple) == 3:
                        validated_colors.append(color_tuple)
                    else:
                        raise ValueError()
                except (AttributeError, ValueError) as e:
                    raise ValueError(f"Unsupported color name: '{color}'.") from e
            elif isinstance(color, (tuple, list)) and len(color) == 3 and all(isinstance(c, int) and 0 <= c <= 255 for c in color):
                validated_colors.append(tuple(color))
            else:
                raise ValueError("Each color must be a tuple of 3 integers (RGB) or a valid color name.")

        return validated_colors

    def invert(self, new_direction=None):
        if new_direction is None:
            if self.type == GradientType.Linear:
                mapping = {
                    LinearSide.Right: LinearSide.Left, LinearSide.Left: LinearSide.Right,
                    LinearSide.Top: LinearSide.Bottom, LinearSide.Bottom: LinearSide.Top,
                    LinearSide.TopRight: LinearSide.BottomLeft, LinearSide.BottomLeft: LinearSide.TopRight,
                    LinearSide.TopLeft: LinearSide.BottomRight, LinearSide.BottomRight: LinearSide.TopLeft
                }
                new_direction = mapping.get(self.direction) # type: ignore
            elif self.type == GradientType.Radial:
                mapping = {
                    RadialPosition.Center: RadialPosition.Center,
                    RadialPosition.TopCenter: RadialPosition.BottomCenter, RadialPosition.BottomCenter: RadialPosition.TopCenter,
                    RadialPosition.TopLeft: RadialPosition.BottomRight, RadialPosition.BottomRight: RadialPosition.TopLeft,
                    RadialPosition.TopRight: RadialPosition.BottomLeft, RadialPosition.BottomLeft: RadialPosition.TopRight
                }
                new_direction = mapping.get(self.direction) # type: ignore

        if new_direction is None:
            raise ValueError(f"Inversion for direction '{self.direction}' is not supported.")

        return Gradient(list(reversed(self.colors)), self.type, new_direction, self.transparency)