import colorsys
import random
from typing import TypeGuard

class ColorAnnotation():
    RGBColor = tuple[int, int, int]
    RGBAColor = tuple[int, int, int, int]
    RGBLikeColor = RGBColor | RGBAColor
    HSLColor = tuple[float, float, float]
    HEXColor = str
    AnyColor = RGBLikeColor | HSLColor | HEXColor
    
    @staticmethod
    def is_rgb(color) -> TypeGuard['RGBColor']:
        return isinstance(color, tuple) and len(color) == 3 and all(isinstance(c, int) and 0 <= c <= 255 for c in color)
    
    @staticmethod
    def is_rgba(color) -> TypeGuard['RGBAColor']:
        return isinstance(color, tuple) and len(color) == 4 and all(isinstance(c, int) and 0 <= c <= 255 for c in color)
    
    @staticmethod
    def is_rgb_like(color) -> TypeGuard['RGBLikeColor']:
        return ColorAnnotation.is_rgb(color) or ColorAnnotation.is_rgba(color)
    
    @staticmethod
    def is_hsl(color) -> TypeGuard['HSLColor']:
        return isinstance(color, tuple) and len(color) == 3 and all(isinstance(c, float) and 0 <= c <= 1 for c in color)
    
    @staticmethod
    def is_hex(color) -> TypeGuard['HEXColor']:
        return isinstance(color, str) and color.startswith('#')
    
class Color:
    ALICEBLUE = (240, 248, 255)
    ANTIQUEWHITE = (250, 235, 215)
    AQUA = (0, 255, 255)
    AQUAMARINE = (127, 255, 212)
    AZURE = (240, 255, 255)
    BEIGE = (245, 245, 220)
    BISQUE = (255, 228, 196)
    BLACK = (0, 0, 0)
    BLANCHEDALMOND = (255, 235, 205)
    BLUE = (0, 0, 255)
    BLUEVIOLET = (138, 43, 226)
    BROWN = (165, 42, 42)
    BURLYWOOD = (222, 184, 135)
    CADETBLUE = (95, 158, 160)
    CHARTREUSE = (127, 255, 0)
    CHOCOLATE = (210, 105, 30)
    CORAL = (255, 127, 80)
    CORNFLOWERBLUE = (100, 149, 237)
    CORNSILK = (255, 248, 220)
    CRIMSON = (220, 20, 60)
    CYAN = (0, 255, 255)
    DARKBLUE = (0, 0, 139)
    DARKCYAN = (0, 139, 139)
    DARKGOLDENROD = (184, 134, 11)
    DARKGRAY = (169, 169, 169)
    DARKGREY = (169, 169, 169)
    DARKGREEN = (0, 100, 0)
    DARKKHAKI = (189, 183, 107)
    DARKMAGENTA = (139, 0, 139)
    DARKOLIVEGREEN = (85, 107, 47)
    DARKORANGE = (255, 140, 0)
    DARKORCHID = (153, 50, 204)
    DARKRED = (139, 0, 0)
    DARKSALMON = (233, 150, 122)
    DARKSEAGREEN = (143, 188, 143)
    DARKSLATEBLUE = (72, 61, 139)
    DARKSLATEGRAY = (47, 79, 79)
    DARKSLATEGREY = (47, 79, 79)
    DARKTURQUOISE = (0, 206, 209)
    DARKVIOLET = (148, 0, 211)
    DEEPPINK = (255, 20, 147)
    DEEPSKYBLUE = (0, 191, 255)
    DIMGRAY = (105, 105, 105)
    DIMGREY = (105, 105, 105)
    DODGERBLUE = (30, 144, 255)
    FIREBRICK = (178, 34, 34)
    FLORALWHITE = (255, 250, 240)
    FORESTGREEN = (34, 139, 34)
    FUCHSIA = (255, 0, 255)
    GAINSBORO = (220, 220, 220)
    GHOSTWHITE = (248, 248, 255)
    GOLD = (255, 215, 0)
    GOLDENROD = (218, 165, 32)
    GRAY = (128, 128, 128)
    GREY = (128, 128, 128)
    GREEN = (0, 128, 0)
    GREENYELLOW = (173, 255, 47)
    HONEYDEW = (240, 255, 240)
    HOTPINK = (255, 105, 180)
    INDIANRED = (205, 92, 92)
    INDIGO = (75, 0, 130)
    IVORY = (255, 255, 240)
    KHAKI = (240, 230, 140)
    LAVENDER = (230, 230, 250)
    LAVENDERBLUSH = (255, 240, 245)
    LAWNGREEN = (124, 252, 0)
    LEMONCHIFFON = (255, 250, 205)
    LIGHTBLUE = (173, 216, 230)
    LIGHTCORAL = (240, 128, 128)
    LIGHTCYAN = (224, 255, 255)
    LIGHTGOLDENRODYELLOW = (250, 250, 210)
    LIGHTGRAY = (211, 211, 211)
    LIGHTGREY = (211, 211, 211)
    LIGHTGREEN = (144, 238, 144)
    LIGHTPINK = (255, 182, 193)
    LIGHTSALMON = (255, 160, 122)
    LIGHTSEAGREEN = (32, 178, 170)
    LIGHTSKYBLUE = (135, 206, 250)
    LIGHTSLATEGRAY = (119, 136, 153)
    LIGHTSLATEGREY = (119, 136, 153)
    LIGHTSTEELBLUE = (176, 196, 222)
    LIGHTYELLOW = (255, 255, 224)
    LIME = (0, 255, 0)
    LIMEGREEN = (50, 205, 50)
    LINEN = (250, 240, 230)
    MAGENTA = (255, 0, 255)
    MAROON = (176, 48, 96)
    MEDIUMAQUAMARINE = (102, 205, 170)
    MEDIUMBLUE = (0, 0, 205)
    MEDIUMFORESTGREEN = (50, 129, 75)
    MEDIUMORCHID = (219, 112, 219)
    MEDIUMPURPLE = (147, 112, 219)
    MEDIUMSEAGREEN = (66, 170, 113)
    MEDIUMSLATEBLUE = (127, 255, 212)
    MEDIUMSPRINGGREEN = (60, 179, 113)
    MEDIUMTURQUOISE = (112, 219, 219)
    MEDIUMVIOLETRED = (199, 21, 133)
    MIDNIGHTBLUE = (25, 25, 112)
    MINTCREAM = (245, 255, 250)
    MISTYROSE = (255, 228, 225)
    MOCCASIN = (255, 228, 181)
    NAVAJOWHITE = (255, 222, 173)
    NAVY = (0, 0, 128)
    NAVYBLUE = (0, 0, 128)
    OLDLACE = (253, 245, 230)
    OLIVE = (128, 128, 0)
    OLIVEDRAB = (107, 142, 35)
    ORANGE = (255, 165, 0)
    ORANGERED = (255, 69, 0)
    ORCHID = (218, 112, 214)
    PALEGOLDENROD = (238, 232, 170)
    PALEGREEN = (152, 251, 152)
    PALETURQUOISE = (175, 238, 238)
    PALEVIOLETRED = (219, 112, 147)
    PAPAYAWHIP = (255, 239, 213)
    PEACHPUFF = (255, 218, 185)
    PERU = (205, 133, 63)
    PINK = (255, 192, 203)
    PLUM = (221, 160, 221)
    POWDERBLUE = (176, 224, 230)
    PURPLE = (160, 32, 240)
    REBECCAPURPLE = (102, 51, 153)
    RED = (255, 0, 0)
    ROSYBROWN = (188, 143, 143)
    ROYALBLUE = (65, 105, 225)
    SADDLEBROWN = (139, 69, 19)
    SALMON = (250, 128, 114)
    SANDYBROWN = (244, 164, 96)
    SEAGREEN = (46, 139, 87)
    SEASHELL = (255, 245, 238)
    SIENNA = (160, 82, 45)
    SILVER = (192, 192, 192)
    SKYBLUE = (135, 206, 235)
    SLATEBLUE = (106, 90, 205)
    SLATEGRAY = (112, 128, 144)
    SLATEGREY = (112, 128, 144)
    SNOW = (255, 250, 250)
    SPRINGGREEN = (0, 255, 127)
    STEELBLUE = (70, 130, 180)
    TAN = (210, 180, 140)
    TEAL = (0, 128, 128)
    THISTLE = (216, 191, 216)
    TOMATO = (255, 99, 71)
    TURQUOISE = (64, 224, 208)
    VIOLET = (238, 130, 238)
    VIOLETRED = (208, 32, 144)
    WHEAT = (245, 222, 179)
    WHITE = (255, 255, 255)
    WHITESMOKE = (245, 245, 245)
    YELLOW = (255, 255, 0)
    YELLOWGREEN = (154, 205, 50)
    Ukraine = "POOP" #Joke >W<
    
    @classmethod
    def __getitem__(cls, key: str) -> ColorAnnotation.RGBColor | None:
        assert key.upper() != "UKRAINE", "its a joke >W<!!!"
        return getattr(cls, key.upper(), None)

    @staticmethod
    def hex_to_rgb(hex_color: str) -> ColorAnnotation.RGBColor:
        """Converts HEX string to RGB tuple."""
        assert ColorAnnotation.is_hex(hex_color), "Invalid HEX color format."
        hex_color = hex_color.lstrip('#')
        if len(hex_color) != 6:
            raise ValueError("Invalid HEX color format. Use #RRGGBB.")
        return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4)) # type: ignore

    @staticmethod
    def hsl_to_rgb(color: ColorAnnotation.HSLColor) -> ColorAnnotation.RGBColor:
        """Converts HSL (0-1) to RGB (0-255)."""
        assert ColorAnnotation.is_hsl(color), "Invalid HSL color format."
        h, l, s = color
        r, g, b = colorsys.hls_to_rgb(h, l, s)
        return (round(r * 255), round(g * 255), round(b * 255))

    @staticmethod
    def rgb_to_hsl(color: ColorAnnotation.RGBColor) -> ColorAnnotation.HSLColor:
        """Converts RGB (0-255) to HSL (0-1)."""
        assert ColorAnnotation.is_rgb(color), "Invalid RGB color format."
        r, g, b = color
        h, l, s = colorsys.rgb_to_hls(r / 255, g / 255, b / 255)
        return (h, l, s)

    @staticmethod
    def invert(color: ColorAnnotation.AnyColor) -> ColorAnnotation.AnyColor:
        """Inverts the color (makes negative)."""
        if ColorAnnotation.is_rgb_like(color):
            return Color._invert_rgb(color)
        elif ColorAnnotation.is_hsl(color):
            return Color.invert_hsl(color)
        elif ColorAnnotation.is_hex(color):
            raise NotImplementedError("Hex color inversion is not implemented yet.")
            #return Color._invert_rgb(Color.hex_to_rgb(color))
        raise ValueError("Invalid color format.")

    @staticmethod
    def _invert_rgb(color: ColorAnnotation.RGBLikeColor) -> ColorAnnotation.RGBLikeColor:
        result = tuple(255 - c for c in color)
        assert ColorAnnotation.is_rgb_like(result)
        return result

    @staticmethod
    def invert_hsl(color: ColorAnnotation.HSLColor) -> ColorAnnotation.HSLColor:
        assert ColorAnnotation.is_hsl(color), "Invalid HSL color format."
        h, l, s = color
        inverted_h = (h + 0.5) % 1.0
        inverted_l = 1.0 - l
        return (inverted_h, inverted_l, s)
    
    @staticmethod
    def lighten(color: ColorAnnotation.RGBColor, amount: float = 0.2) -> ColorAnnotation.RGBColor:
        """
        Lightens the color.
        amount: from 0.0 (no change) to 1.0 (completely white).
        """
        if not (0.0 <= amount <= 1.0):
            raise ValueError("The 'amount' value should be between 0.0 and 1.0.")
        h, l, s = Color.rgb_to_hsl(color)
        l = l + (1 - l) * amount
        return Color.hsl_to_rgb((h, l, s))

    @staticmethod
    def darken(color: ColorAnnotation.RGBColor, amount: float = 0.2) -> ColorAnnotation.RGBColor:
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
    def random_rgb() -> ColorAnnotation.RGBColor:
        """Returns a random RGB color."""
        return (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))
    
    @staticmethod
    def random_hsl() -> ColorAnnotation.HSLColor:
        """Returns a random HSL color."""
        return (random.uniform(0, 1), random.uniform(0, 1), random.uniform(0, 1))
    
    @staticmethod
    def text_color_for_bg(bg_color: ColorAnnotation.RGBColor) -> ColorAnnotation.RGBColor:
        """
        Determines which text color (black or white) will be better readable
        on a given background color.
        """
        r, g, b = bg_color
        luminance = (0.299 * r + 0.587 * g + 0.114 * b) / 255
        return Color.BLACK if luminance > 0.5 else Color.WHITE
    
    @staticmethod
    def mix(*colors) -> ColorAnnotation.RGBColor:
        """
        Mixes several colors together.
        Takes colors in RGB-tuple, HEX-string or color name from the Color class.
        """
        final_color_list = []
        for color in colors:
            if isinstance(color, str):
                if ColorAnnotation.is_hex(color):
                    color = Color.hex_to_rgb(color)
                else:
                    try:
                        color = getattr(Color, color.upper())
                    except AttributeError as e:
                        raise ValueError(f"Unknown color name: {color}") from e
                    
            elif ColorAnnotation.is_hsl(color):
                color = Color.hsl_to_rgb(color)
                
            elif not ColorAnnotation.is_rgb_like(color):
                raise TypeError(f"Invalid color format for: {color}")

            final_color_list.append(color)

        if not final_color_list:
            return (0, 0, 0)

        r, g, b = (sum(c) // len(final_color_list) for c in zip(*final_color_list))
        return (r, g, b)
    
