import pygame
import copy
import numpy as np

from .color import (
    Color_Type, Color, ColorThemeLibrary, ColorTheme, SubThemeRole
)
from .core_types import (
    Align, LinearSide, RadialPosition, GradientType, GradientConfig
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
        y, x = np.indices((height, width), dtype = np.float32)

        w_m = width - 1 if width > 1 else 1
        h_m = height - 1 if height > 1 else 1

        progress = self._get_linear_gradient_progress(x, y, w_m, h_m)
        self._blit_numpy_gradient(surface, progress)

    def _get_linear_gradient_progress(self, x, y, w_m, h_m):
        dir_map = {
            LinearSide.Right: x / w_m,
            LinearSide.Left: 1.0 - (x / w_m),
            LinearSide.Bottom: y / h_m,
            LinearSide.Top: 1.0 - (y / h_m),
            LinearSide.BottomRight: (x / w_m + y / h_m) / 2,
            LinearSide.TopLeft: 1.0 - (x / w_m + y / h_m) / 2,
            LinearSide.TopRight: ((x / w_m) + (1.0 - y / h_m)) / 2,
            LinearSide.BottomLeft: ((1.0 - x / w_m) + (y / h_m)) / 2
        }
        progress = dir_map.get(self.direction)
        if progress is None:
            raise ValueError(f"Unsupported gradient direction: {self.direction}")
        return progress
    def _apply_radial_gradient(self, surface):
        width, height = surface.get_size()
        center_x, center_y = self._get_radial_center(width, height)
        
        y, x = np.indices((height, width), dtype=np.float32)
        
        distance = np.sqrt((x - center_x)**2 + (y - center_y)**2)
        
        corners = [(0, 0), (width - 1, 0), (0, height - 1), (width - 1, height - 1)]
        max_radius = max(np.sqrt((cx - center_x)**2 + (cy - center_y)**2) for cx, cy in corners)
        
        if max_radius == 0:
            surface.fill(self.colors[0])
            return

        progress = distance / max_radius
        self._blit_numpy_gradient(surface, progress)

    def _blit_numpy_gradient(self, surface, progress):
        progress = np.clip(progress, 0.0, 1.0)
        stops = np.linspace(0, 1, len(self.colors))

        r, g, b = self._interpolate_channels(progress, stops)

        gradient_array = np.stack((r.T, g.T, b.T), axis=-1)

        pygame.surfarray.blit_array(surface, gradient_array)

    def _interpolate_channels(self, progress, stops):
        colors_array = np.array(self.colors)
        r = np.interp(progress, stops, colors_array[:, 0])
        g = np.interp(progress, stops, colors_array[:, 1])
        b = np.interp(progress, stops, colors_array[:, 2])
        return r, g, b

    def _stack_gradient_array(self, r, g, b):
        return np.stack([r, g, b], axis=-1).astype(np.uint8)

    def _get_radial_center(self, width, height):
        w_m, h_m = width - 1, height - 1
        center_map = {
            RadialPosition.Center: (w_m / 2, h_m / 2),
            RadialPosition.TopCenter: (w_m / 2, 0),
            RadialPosition.TopLeft: (0, 0),
            RadialPosition.TopRight: (w_m, 0),
            RadialPosition.BottomCenter: (w_m / 2, h_m),
            RadialPosition.BottomLeft: (0, h_m),
            RadialPosition.BottomRight: (w_m, h_m)
        }
        return center_map.get(self.direction, (w_m / 2, h_m / 2))

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
                except (AttributeError, ValueError):
                    raise ValueError(f"Unsupported color name: '{color}'.")
            elif isinstance(color, (tuple, list)) and len(color) == 3 and all(isinstance(c, int) and 0 <= c <= 255 for c in color):
                validated_colors.append(tuple(color))
            else:
                raise ValueError("Each color must be a tuple of 3 integers (RGB) or a valid color name.")

        return validated_colors

    def invert(self, new_direction=None):
        if new_direction is None:
            if self.type == 'linear':
                mapping = {
                    LinearSide.Right: LinearSide.Left, LinearSide.Left: LinearSide.Right,
                    LinearSide.Top: LinearSide.Bottom, LinearSide.Bottom: LinearSide.Top,
                    LinearSide.TopRight: LinearSide.BottomLeft, LinearSide.BottomLeft: LinearSide.TopRight,
                    LinearSide.TopLeft: LinearSide.BottomRight, LinearSide.BottomRight: LinearSide.TopLeft
                }
                new_direction = mapping.get(self.direction)
            elif self.type == GradientType.Radial:
                mapping = {
                    RadialPosition.Center: RadialPosition.Center,
                    RadialPosition.TopCenter: RadialPosition.BottomCenter, RadialPosition.BottomCenter: RadialPosition.TopCenter,
                    RadialPosition.TopLeft: RadialPosition.BottomRight, RadialPosition.BottomRight: RadialPosition.TopLeft,
                    RadialPosition.TopRight: RadialPosition.BottomLeft, RadialPosition.BottomLeft: RadialPosition.TopRight
                }
                new_direction = mapping.get(self.direction)

            if new_direction is None:
                raise ValueError(f"Inversion for direction '{self.direction}' is not supported.")
                
        return Gradient(list(reversed(self.colors)), self.type, new_direction, self.transparency)
class Style:
    def __init__(self,**kwargs):
        self.colortheme = copy.copy(ColorThemeLibrary.material3_dark_color_theme)
        self.borderwidth = 1
        self.borderradius = 0
        self._kwargs_for_copy = kwargs
        self.fontname = "Arial"
        self.fontsize = 20
        self.text_align_x = Align.CENTER
        self.text_align_y = Align.CENTER
        self.transparency = None
        self.bgimage = None
        self.gradient = None

        self.kwargs_dict = {}
        self.add_style_parameter("textcolor", "fontcolor", lambda value:self.parse_color(value, can_be_gradient=False, can_be_trasparent=False))
        self.add_style_parameter("fontcolor", "fontcolor", lambda value:self.parse_color(value, can_be_gradient=False, can_be_trasparent=False))
        self.add_style_parameter("borderradius", "borderradius", lambda value:self.parse_int(value, min_restriction=0))
        self.add_style_parameter("borderwidth", "borderwidth", lambda value:self.parse_int(value, min_restriction=-1))
        self.add_style_parameter("fontsize", "fontsize", lambda value:self.parse_int(value, min_restriction=1))
        self.add_style_parameter("fontname", "fontname", lambda value:self.parse_str(value))
        self.add_style_parameter("text_align_x", "text_align_x", lambda value:self.parse_int(value))
        self.add_style_parameter("text_align_y", "text_align_y", lambda value:self.parse_int(value))
        self.add_style_parameter("transparency", "transparency", lambda value:self.parse_int(value, max_restriction=255, min_restriction=0))
        self.add_style_parameter("bgimage", "bgimage", lambda value:self.parse_str(value))
        self.add_style_parameter("colortheme", "colortheme", lambda value:self.parse_class_type(value, ColorTheme))
        self.add_style_parameter("gradient", "gradient", lambda value:self.parse_class_type(value, Gradient))
        self._kwargs_handler(**kwargs)
        
    def add_style_parameter(self, name, attribute_name: str, checker_lambda):
        self.kwargs_dict[name] = (attribute_name, checker_lambda)
        
    def parse_color(self, value, can_be_gradient: bool = False, can_be_trasparent: bool = False, can_be_string: bool = False) -> tuple[bool, tuple|None]:
        if isinstance(value, Gradient) and can_be_gradient:
            return True, None

        elif isinstance(value, (tuple, list)) and (len(value) == 3 or len(value) == 4) and all(isinstance(c, int) for c in value):
            for item in value:
                if item < 0 or item > 255:
                    return False, None
            return True, None

        elif isinstance(value, str) and can_be_string:
            try:
                color_value = Color[value]
            except KeyError:
                return False, None
            else:
                assert isinstance(color_value, tuple)
                return True, color_value

        elif value == Color_Type.TRANSPARENT and can_be_trasparent:
            return True, None
        
        return False, None
    def parse_int(self, value: int, max_restriction: int|None = None, min_restriction: int|None = None) -> tuple[bool, None]:
        if isinstance(value, int):
            if max_restriction is not None and value > max_restriction:
                return False, None
            if min_restriction is not None and value < min_restriction:
                return False, None
            return True, None
        return False, None
    def parse_str(self, value: str) -> tuple[bool, None]:
        return self.parse_class_type(value, str)
    def parse_class_type(self, value: str, type: type|tuple) -> tuple[bool, None]:
        return (True, None) if isinstance(value, type) else (False, None)
    def _kwargs_handler(self, raise_errors: bool = False, **kwargs):
        for item_name, item_value in kwargs.items():
            dict_value = self.kwargs_dict.get(item_name.lower(), None)
            if dict_value is None:
                continue
            attribute_name, checker = dict_value
            checker_result, checker_value = checker(item_value)
            if checker_result:
                end_value = checker_value if checker_value is not None else item_value
                setattr(self, attribute_name, end_value)
            elif raise_errors:
                raise ValueError(f"Некорректное значение {item_name}")

    def __call__(self ,**kwargs):
        style = copy.copy(self)
        style._kwargs_handler(**kwargs)
        return style
    
default_style = Style()

