import colorsys
import random
from typing import TypeGuard
from nevu_ui.core import Annotations
    
def is_rgb(color) -> TypeGuard[Annotations.rgb_color]:
    return isinstance(color, tuple) and len(color) == 3 and all(isinstance(c, int) and 0 <= c <= 255 for c in color)

def is_rgba(color) -> TypeGuard[Annotations.rgba_color]:
    return isinstance(color, tuple) and len(color) == 4 and all(isinstance(c, int) and 0 <= c <= 255 for c in color)

def is_rgb_like(color) -> TypeGuard[Annotations.rgb_like_color]:
    return is_rgb(color) or is_rgba(color)

def is_hsl(color) -> TypeGuard[Annotations.hsl_color]:
    return isinstance(color, tuple) and len(color) == 3 and all(isinstance(c, float) and 0 <= c <= 1 for c in color)

def is_hex(color) -> TypeGuard[Annotations.hex_color]:
    return isinstance(color, str) and color.startswith('#')
    
class Color:
    AliceBlue = (240, 248, 255, 255)
    AntiqueWhite = (250, 235, 215, 255)
    Aqua = (0, 255, 255, 255)
    Aquamarine = (127, 255, 212, 255)
    Azure = (240, 255, 255, 255)
    Beige = (245, 245, 220, 255)
    Bisque = (255, 228, 196, 255)
    Black = (0, 0, 0, 255)
    BlanchedAlmond = (255, 235, 205, 255)
    Blue = (0, 0, 255, 255)
    BlueViolet = (138, 43, 226, 255)
    Brown = (165, 42, 42, 255)
    BurlyWood = (222, 184, 135, 255)
    CadetBlue = (95, 158, 160, 255)
    Chartreuse = (127, 255, 0, 255)
    Chocolate = (210, 105, 30, 255)
    Coral = (255, 127, 80, 255)
    CornflowerBlue = (100, 149, 237, 255)
    Cornsilk = (255, 248, 220, 255)
    Crimson = (220, 20, 60, 255)
    Cyan = (0, 255, 255, 255)
    DarkBlue = (0, 0, 139, 255)
    DarkCyan = (0, 139, 139, 255)
    DarkGoldenrod = (184, 134, 11, 255)
    DarkGray = (169, 169, 169, 255)
    DarkGrey = (169, 169, 169, 255)
    DarkGreen = (0, 100, 0, 255)
    DarkKhaki = (189, 183, 107, 255)
    DarkMagenta = (139, 0, 139, 255)
    DarkOliveGreen = (85, 107, 47, 255)
    DarkOrange = (255, 140, 0, 255)
    DarkOrchid = (153, 50, 204, 255)
    DarkRed = (139, 0, 0, 255)
    DarkSalmon = (233, 150, 122, 255)
    DarkSeaGreen = (143, 188, 143, 255)
    DarkSlateBlue = (72, 61, 139, 255)
    DarkSlateGray = (47, 79, 79, 255)
    DarkSlateGrey = (47, 79, 79, 255)
    DarkTurquoise = (0, 206, 209, 255)
    DarkViolet = (148, 0, 211, 255)
    DeepPink = (255, 20, 147, 255)
    DeepSkyBlue = (0, 191, 255, 255)
    DimGray = (105, 105, 105, 255)
    DimGrey = (105, 105, 105, 255)
    DodgerBlue = (30, 144, 255, 255)
    FireBrick = (178, 34, 34, 255)
    FloralWhite = (255, 250, 240, 255)
    ForestGreen = (34, 139, 34, 255)
    Fuchsia = (255, 0, 255, 255)
    Gainsboro = (220, 220, 220, 255)
    GhostWhite = (248, 248, 255, 255)
    Gold = (255, 215, 0, 255)
    Goldenrod = (218, 165, 32, 255)
    Gray = (128, 128, 128, 255)
    Grey = (128, 128, 128, 255)
    Green = (0, 128, 0, 255)
    GreenYellow = (173, 255, 47, 255)
    Honeydew = (240, 255, 240, 255)
    HotPink = (255, 105, 180, 255)
    IndianRed = (205, 92, 92, 255)
    Indigo = (75, 0, 130, 255)
    Ivory = (255, 255, 240, 255)
    Khaki = (240, 230, 140, 255)
    Lavender = (230, 230, 250, 255)
    LavenderBlush = (255, 240, 245, 255)
    LawnGreen = (124, 252, 0, 255)
    LemonChiffon = (255, 250, 205, 255)
    LightBlue = (173, 216, 230, 255)
    LightCoral = (240, 128, 128, 255)
    LightCyan = (224, 255, 255, 255)
    LightGoldenrodYellow = (250, 250, 210, 255)
    LightGray = (211, 211, 211, 255)
    LightGrey = (211, 211, 211, 255)
    LightGreen = (144, 238, 144, 255)
    LightPink = (255, 182, 193, 255)
    LightSalmon = (255, 160, 122, 255)
    LightSeaGreen = (32, 178, 170, 255)
    LightSkyBlue = (135, 206, 250, 255)
    LightSlateGray = (119, 136, 153, 255)
    LightSlateGrey = (119, 136, 153, 255)
    LightSteelBlue = (176, 196, 222, 255)
    LightYellow = (255, 255, 224, 255)
    Lime = (0, 255, 0, 255)
    LimeGreen = (50, 205, 50, 255)
    Linen = (250, 240, 230, 255)
    Magenta = (255, 0, 255, 255)
    Maroon = (176, 48, 96, 255)
    MediumAquamarine = (102, 205, 170, 255)
    MediumBlue = (0, 0, 205, 255)
    MediumForestGreen = (50, 129, 75, 255)
    MediumOrchid = (219, 112, 219, 255)
    MediumPurple = (147, 112, 219, 255)
    MediumSeaGreen = (66, 170, 113, 255)
    MediumSlateBlue = (127, 255, 212, 255)
    MediumSpringGreen = (60, 179, 113, 255)
    MediumTurquoise = (112, 219, 219, 255)
    MediumVioletRed = (199, 21, 133, 255)
    MidnightBlue = (25, 25, 112, 255)
    MintCream = (245, 255, 250, 255)
    MistyRose = (255, 228, 225, 255)
    Moccasin = (255, 228, 181, 255)
    NavajoWhite = (255, 222, 173, 255)
    Navy = (0, 0, 128, 255)
    NavyBlue = (0, 0, 128, 255)
    OldLace = (253, 245, 230, 255)
    Olive = (128, 128, 0, 255)
    OliveDrab = (107, 142, 35, 255)
    Orange = (255, 165, 0, 255)
    OrangeRed = (255, 69, 0, 255)
    Orchid = (218, 112, 214, 255)
    PaleGoldenrod = (238, 232, 170, 255)
    PaleGreen = (152, 251, 152, 255)
    PaleTurquoise = (175, 238, 238, 255)
    PaleVioletRed = (219, 112, 147, 255)
    PapayaWhip = (255, 239, 213, 255)
    PeachPuff = (255, 218, 185, 255)
    Peru = (205, 133, 63, 255)
    Pink = (255, 192, 203, 255)
    Plum = (221, 160, 221, 255)
    PowderBlue = (176, 224, 230, 255)
    Purple = (160, 32, 240, 255)
    RebeccaPurple = (102, 51, 153, 255)
    Red = (255, 0, 0, 255)
    RosyBrown = (188, 143, 143, 255)
    RoyalBlue = (65, 105, 225, 255)
    SaddleBrown = (139, 69, 19, 255)
    Salmon = (250, 128, 114, 255)
    SandyBrown = (244, 164, 96, 255)
    SeaGreen = (46, 139, 87, 255)
    Seashell = (255, 245, 238, 255)
    Sienna = (160, 82, 45, 255)
    Silver = (192, 192, 192, 255)
    SkyBlue = (135, 206, 235, 255)
    SlateBlue = (106, 90, 205, 255)
    SlateGray = (112, 128, 144, 255)
    SlateGrey = (112, 128, 144, 255)
    Snow = (255, 250, 250, 255)
    SpringGreen = (0, 255, 127, 255)
    SteelBlue = (70, 130, 180, 255)
    Tan = (210, 180, 140, 255)
    Teal = (0, 128, 128, 255)
    Thistle = (216, 191, 216, 255)
    Tomato = (255, 99, 71, 255)
    Turquoise = (64, 224, 208, 255)
    Violet = (238, 130, 238, 255)
    VioletRed = (208, 32, 144, 255)
    Wheat = (245, 222, 179, 255)
    White = (255, 255, 255, 255)
    WhiteSmoke = (245, 245, 245, 255)
    Yellow = (255, 255, 0, 255)
    YellowGreen = (154, 205, 50, 255)
    
    _COLOR_MAP = None
    
    @classmethod
    def _get_map(cls):
        if cls._COLOR_MAP is None:
            cls._COLOR_MAP = {k.lower(): v for k, v in cls.__dict__.items() if isinstance(v, tuple)}
        return cls._COLOR_MAP

    @classmethod
    def __getitem__(cls, key: str) -> Annotations.rgb_color | None:
        return cls._get_map().get(key.lower())


    @staticmethod
    def hex_to_rgb(hex_color: str) -> Annotations.rgb_color:
        """Converts HEX string to RGB tuple."""
        assert is_hex(hex_color), "Invalid HEX color format."
        hex_color = hex_color.lstrip('#')
        if len(hex_color) != 6: raise ValueError("Invalid HEX color format. Use #RRGGBB.")
        return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4)) # type: ignore

    @staticmethod
    def hsl_to_rgb(color: Annotations.hsl_color) -> Annotations.rgb_color:
        """Converts HSL (0-1) to RGB (0-255)."""
        assert is_hsl(color), "Invalid HSL color format."
        h, l, s = color
        r, g, b = colorsys.hls_to_rgb(h, l, s)
        return (round(r * 255), round(g * 255), round(b * 255))

    @staticmethod
    def rgb_to_hsl(color: Annotations.rgb_color) -> Annotations.hsl_color:
        """Converts RGB (0-255) to HSL (0-1)."""
        assert is_rgb(color), "Invalid RGB color format."
        r, g, b = color
        h, l, s = colorsys.rgb_to_hls(r / 255, g / 255, b / 255)
        return (h, l, s)

    @staticmethod
    def invert(color: Annotations.any_color) -> Annotations.any_color:
        """Inverts the color (makes negative)."""
        if is_rgb_like(color): return Color._invert_rgb(color)
        elif is_hsl(color): return Color.invert_hsl(color)
        elif is_hex(color): raise NotImplementedError("Hex color inversion is not implemented yet.")
        raise ValueError("Invalid color format.")

    @staticmethod
    def _invert_rgb(color: Annotations.rgb_like_color) -> Annotations.rgb_like_color:
        result = tuple(255 - c for c in color)
        assert is_rgb_like(result)
        return result

    @staticmethod
    def invert_hsl(color: Annotations.hsl_color) -> Annotations.hsl_color:
        assert is_hsl(color), "Invalid HSL color format."
        h, l, s = color
        inverted_h = (h + 0.5) % 1.0
        inverted_l = 1.0 - l
        return (inverted_h, inverted_l, s)
    
    @staticmethod
    def lighten(color: Annotations.rgb_color, amount: float = 0.2) -> Annotations.rgb_color:
        """
        Lightens the color.
        amount: from 0.0 (no change) to 1.0 (completely white).
        """
        if not (0.0 <= amount <= 1.0): raise ValueError("The 'amount' value should be between 0.0 and 1.0.")
        h, l, s = Color.rgb_to_hsl(color)
        l = l + (1 - l) * amount
        return Color.hsl_to_rgb((h, l, s))

    @staticmethod
    def darken(color: Annotations.rgb_color, amount: float = 0.2) -> Annotations.rgb_color:
        """
        Makes the color darker.
        amount: from 0.0 (no change) to 1.0 (completely black).
        """
        if not (0.0 <= amount <= 1.0):
            raise ValueError("The 'amount' value should be between 0.0 and 1.0.")
        h, l, s = Color.rgb_to_hsl(color)
        l = l * (1 - amount)
        return Color.hsl_to_rgb((h, l, s))

    @staticmethod
    def random_rgb() -> Annotations.rgb_color:
        """Returns a random RGB color."""
        return (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))
    
    @staticmethod
    def random_hsl() -> Annotations.hsl_color:
        """Returns a random HSL color."""
        return (random.uniform(0, 1), random.uniform(0, 1), random.uniform(0, 1))
    
    @staticmethod
    def text_color_for_bg(bg_color: Annotations.rgb_like_color) -> Annotations.rgb_like_color:
        """
        Determines which text color (black or white) will be better readable
        on a given background color.
        """
        if is_rgba(bg_color):
            r, g, b, a = bg_color
        elif is_rgb(bg_color):
            r, g, b = bg_color
        else:
            raise ValueError(f"Invalid color format: {bg_color}")
        luminance = (0.299 * r + 0.587 * g + 0.114 * b) / 255
        return Color.Black if luminance > 0.5 else Color.White
    
    @staticmethod
    def with_float_alpha(color: Annotations.rgb_like_color, alpha: float) -> Annotations.rgba_color:
        return Color.with_alpha(color, round(alpha * 255))
    
    @staticmethod
    def with_alpha(color: Annotations.rgb_like_color, alpha: int) -> Annotations.rgba_color:
        return (color[0], color[1], color[2], alpha)
    
    @staticmethod
    def mix(*colors) -> Annotations.rgb_color:
        """
        Mixes several colors together.
        Takes colors in RGB-tuple, HEX-string or color name from the Color class.
        """
        final_color_list = []
        for color in colors:
            if isinstance(color, str):
                if is_hex(color):
                    color = Color.hex_to_rgb(color)
                else:
                    try:
                        color = getattr(Color, color.upper())
                    except AttributeError as e:
                        raise ValueError(f"Unknown color name: {color}") from e
                    
            elif is_hsl(color): color = Color.hsl_to_rgb(color)
                
            elif not is_rgb_like(color):
                raise TypeError(f"Invalid color format for: {color}")

            final_color_list.append(color)

        if not final_color_list: return (0, 0, 0)

        r, g, b = (sum(c) // len(final_color_list) for c in zip(*final_color_list))
        return (r, g, b)
    
    @classmethod
    def get_color(cls, color: str, default=None):
        return cls._get_map().get(color.lower(), default)