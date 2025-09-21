import colorsys
from dataclasses import dataclass
from enum import StrEnum
import random

# Likely will be unused 8)
class Color_Type:
    TRANSPARENT = 101

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
    DARKTURQUOISE = (0, 206, 209)
    DARKVIOLET = (148, 0, 211)
    DEEPPINK = (255, 20, 147)
    DEEPSKYBLUE = (0, 191, 255)
    DIMGRAY = (105, 105, 105)
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
    LIGHTGREEN = (144, 238, 144)
    LIGHTPINK = (255, 182, 193)
    LIGHTSALMON = (255, 160, 122)
    LIGHTSEAGREEN = (32, 178, 170)
    LIGHTSKYBLUE = (135, 206, 250)
    LIGHTSLATEGRAY = (119, 136, 153)
    LIGHTSTEELBLUE = (176, 196, 222)
    LIGHTYELLOW = (255, 255, 224)
    LIME = (0, 255, 0)
    LIMEGREEN = (50, 205, 50)
    LINEN = (250, 240, 230)
    MAGENTA = (255, 0, 255)
    MAROON = (128, 0, 0)
    MEDIUMAQUAMARINE = (102, 205, 170)
    MEDIUMBLUE = (0, 0, 205)
    MEDIUMORCHID = (186, 85, 211)
    MEDIUMPURPLE = (147, 112, 219)
    MEDIUMSEAGREEN = (60, 179, 113)
    MEDIUMSLATEBLUE = (123, 104, 238)
    MEDIUMSPRINGGREEN = (0, 250, 154)
    MEDIUMTURQUOISE = (72, 209, 204)
    MEDIUMVIOLETRED = (199, 21, 133)
    MIDNIGHTBLUE = (25, 25, 112)
    MINTCREAM = (245, 255, 250)
    MISTYROSE = (255, 228, 225)
    MOCCASIN = (255, 228, 181)
    NAVAJOWHITE = (255, 222, 173)
    NAVY = (0, 0, 128)
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
    PURPLE = (128, 0, 128)
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
    SNOW = (255, 250, 250)
    SPRINGGREEN = (0, 255, 127)
    STEELBLUE = (70, 130, 180)
    TAN = (210, 180, 140)
    TEAL = (0, 128, 128)
    THISTLE = (216, 191, 216)
    TOMATO = (255, 99, 71)
    TURQUOISE = (64, 224, 208)
    VIOLET = (238, 130, 238)
    WHEAT = (245, 222, 179)
    WHITE = (255, 255, 255)
    WHITESMOKE = (245, 245, 245)
    YELLOW = (255, 255, 0)
    YELLOWGREEN = (154, 205, 50)
    Ukraine = "POOP" #Joke >W<
    @classmethod
    def __getitem__(cls, key: str) -> tuple:
        return getattr(cls, key.upper())

    @staticmethod
    def hex_to_rgb(hex_color: str) -> tuple[int, int, int]:
        """Converts HEX string to RGB tuple."""
        hex_color = hex_color.lstrip('#')
        if len(hex_color) != 6:
            raise ValueError("Invalid HEX color format. Use #RRGGBB.")
        return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))

    @staticmethod
    def hsl_to_rgb(hsl: tuple[float, float, float]) -> tuple[int, int, int]:
        """Converts HSL (0-1) to RGB (0-255)."""
        h, l, s = hsl
        r, g, b = colorsys.hls_to_rgb(h, l, s)
        return (round(r * 255), round(g * 255), round(b * 255))

    @staticmethod
    def rgb_to_hsl(rgb: tuple[int, int, int]) -> tuple[float, float, float]:
        """Converts RGB (0-255) to HSL (0-1)."""
        r, g, b = rgb
        h, l, s = colorsys.rgb_to_hls(r / 255, g / 255, b / 255)
        return (h, l, s)

    @staticmethod
    def invert(rgb: tuple[int, int, int]) -> tuple[int, int, int]:
        """Inverts the color (makes negative)."""
        assert len(rgb) == 3
        return tuple(255 - c for c in rgb)

    @staticmethod
    def lighten(rgb: tuple[int, int, int], amount: float = 0.2) -> tuple[int, int, int]:
        """
        Lightens the color.
        amount: from 0.0 (no change) to 1.0 (completely white).
        """
        if not (0.0 <= amount <= 1.0):
            raise ValueError("The 'amount' value should be between 0.0 and 1.0.")
        h, l, s = Color.rgb_to_hsl(rgb)
        l = l + (1 - l) * amount
        return Color.hsl_to_rgb((h, l, s))

    @staticmethod
    def darken(rgb: tuple[int, int, int], amount: float = 0.2) -> tuple[int, int, int]:
        """
        Makes the color darker.
        amount: from 0.0 (no change) to 1.0 (completely black).
        """
        if not (0.0 <= amount <= 1.0):
            raise ValueError("The 'amount' value should be between 0.0 and 1.0.")
        h, l, s = Color.rgb_to_hsl(rgb)
        l = l * (1 - amount)
        return Color.hsl_to_rgb((h, l, s))

    @staticmethod
    def random() -> tuple[int, int, int]:
        """Returns a random RGB color."""
        return (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))

    @staticmethod
    def text_color_for_bg(bg_rgb: tuple[int, int, int]) -> tuple[int, int, int]:
        """
        Determines which text color (black or white) will be better readable
        on a given background color.
        """
        r, g, b = bg_rgb
        luminance = (0.299 * r + 0.587 * g + 0.114 * b) / 255
        return Color.BLACK if luminance > 0.5 else Color.WHITE

    @staticmethod
    def mix(*colors) -> tuple[int, int, int]:
        """
        Mixes several colors together.
        Takes colors in RGB-tuple, HEX-string or color name from the Color class.
        """
        final_color_list = []
        for color in colors:
            if isinstance(color, str):
                if color.startswith('#'):
                    color = Color.hex_to_rgb(color)
                else:
                    try:
                        color = getattr(Color, color.upper())
                    except AttributeError:
                        raise ValueError(f"Unknown color name: {color}")
            
            if not isinstance(color, tuple):
                 raise TypeError(f"Invalid color format for: {color}")

            final_color_list.append(color)

        if not final_color_list:
            return (0, 0, 0)

        r, g, b = (sum(c) // len(final_color_list) for c in zip(*final_color_list))
        return (r, g, b)

class _RoleAncestor(StrEnum):
    pass

class SubThemeRole(_RoleAncestor):
    PRIMARY = "primary"
    SECONDARY = "secondary"
    TERTIARY = "tertiary"
    ERROR = "error"

class PairColorRole(_RoleAncestor):
    BACKGROUND = "background"
    SURFACE = "surface"
    SURFACE_VARIANT = "surface_variant"
    INVERSE_SURFACE = "inverse_surface"

class TupleColorRole(_RoleAncestor):
    OUTLINE = "outline"
    INVERSE_PRIMARY = "inverse_primary"
@dataclass
class ColorPair:
    """Представляет пару цветов (основной цвет и цвет контента на нем)."""
    color: tuple
    oncolor: tuple

@dataclass
class ColorSubTheme:
    """Представляет часть цветовой схемы, основанную на ролях Material Design 3."""
    color: tuple
    oncolor: tuple
    container: tuple
    oncontainer: tuple

@dataclass
class ColorTheme:
    """
    Представляет полную, структурированную цветовую схему,
    организованную по ролям Material Design 3.
    """
    primary: ColorSubTheme
    secondary: ColorSubTheme
    tertiary: ColorSubTheme
    error: ColorSubTheme
    background: ColorPair
    surface: ColorPair
    surface_variant: ColorPair
    outline: tuple
    inverse_surface: ColorPair
    inverse_primary: tuple

    def get_subtheme(self, role: SubThemeRole) -> ColorSubTheme:
        assert isinstance(role, SubThemeRole)
        return getattr(self, role.value)
    
    def get_pair(self, role: PairColorRole) -> ColorPair:
        assert isinstance(role, PairColorRole)
        return getattr(self, role.value)

    def get_tuple(self, role: TupleColorRole) -> tuple:
        assert isinstance(role, TupleColorRole)
        return getattr(self, role.value)
    
    def get(self, any_role) -> ColorSubTheme | ColorPair | tuple:
        assert isinstance(any_role, _RoleAncestor)
        return getattr(self, any_role.value)

class ColorThemeLibrary:
    material3_light_color_theme = ColorTheme(
        primary=ColorSubTheme(color=(103, 80, 164), oncolor=(255, 255, 255), container=(234, 221, 255), oncontainer=(33, 0, 93)),
        secondary=ColorSubTheme(color=(98, 91, 113), oncolor=(255, 255, 255), container=(232, 222, 248), oncontainer=(29, 25, 43)),
        tertiary=ColorSubTheme(color=(125, 82, 96), oncolor=(255, 255, 255), container=(255, 216, 228), oncontainer=(49, 17, 29)),
        error=ColorSubTheme(color=(179, 38, 30), oncolor=(255, 255, 255), container=(249, 222, 220), oncontainer=(65, 14, 11)),
        background=ColorPair(color=(255, 251, 254), oncolor=(28, 27, 31)),
        surface=ColorPair(color=(255, 251, 254), oncolor=(28, 27, 31)),
        surface_variant=ColorPair(color=(231, 224, 236), oncolor=(73, 69, 79)),
        outline=(121, 116, 126),
        inverse_surface=ColorPair(color=(49, 48, 51), oncolor=(244, 239, 244)),
        inverse_primary=(208, 188, 255)
    )

    material3_dark_color_theme = ColorTheme(
        primary=ColorSubTheme(color=(208, 188, 255), oncolor=(56, 30, 114), container=(79, 55, 139), oncontainer=(234, 221, 255)),
        secondary=ColorSubTheme(color=(204, 194, 220), oncolor=(51, 45, 65), container=(74, 68, 88), oncontainer=(232, 222, 248)),
        tertiary=ColorSubTheme(color=(239, 184, 200), oncolor=(75, 34, 52), container=(100, 57, 72), oncontainer=(255, 216, 228)),
        error=ColorSubTheme(color=(242, 184, 181), oncolor=(96, 20, 16), container=(140, 29, 24), oncontainer=(249, 222, 220)),
        background=ColorPair(color=(28, 27, 31), oncolor=(230, 225, 229)),
        surface=ColorPair(color=(28, 27, 31), oncolor=(230, 225, 229)),
        surface_variant=ColorPair(color=(73, 69, 79), oncolor=(202, 196, 208)),
        outline=(147, 143, 153),
        inverse_surface=ColorPair(color=(230, 225, 229), oncolor=(49, 48, 51)),
        inverse_primary=(103, 80, 164)
    )

    ocean_light_color_theme = ColorTheme(
        primary=ColorSubTheme(color=Color.STEELBLUE, oncolor=Color.WHITE, container=Color.LIGHTBLUE, oncontainer=Color.DARKSLATEBLUE),
        secondary=ColorSubTheme(color=Color.MEDIUMAQUAMARINE, oncolor=Color.BLACK, container=Color.PALEGREEN, oncontainer=Color.DARKGREEN),
        tertiary=ColorSubTheme(color=Color.SADDLEBROWN, oncolor=Color.BLACK, container=Color.WHEAT, oncontainer=Color.SADDLEBROWN),
        error=ColorSubTheme(color=Color.TOMATO, oncolor=Color.WHITE, container=Color.MISTYROSE, oncontainer=Color.DARKRED),
        background=ColorPair(color=Color.ALICEBLUE, oncolor=Color.DARKSLATEGRAY),
        surface=ColorPair(color=Color.WHITE, oncolor=Color.DARKSLATEGRAY),
        surface_variant=ColorPair(color=Color.POWDERBLUE, oncolor=Color.SLATEGRAY),
        outline=Color.LIGHTSLATEGRAY,
        inverse_surface=ColorPair(color=Color.DARKSLATEGRAY, oncolor=Color.WHITE),
        inverse_primary=Color.SKYBLUE
    )

    synthwave_dark_color_theme = ColorTheme(
        primary=ColorSubTheme(color=Color.DEEPPINK, oncolor=Color.WHITE, container=(99, 0, 57), oncontainer=Color.PINK),
        secondary=ColorSubTheme(color=Color.CYAN, oncolor=Color.BLACK, container=(0, 77, 77), oncontainer=Color.AQUAMARINE),
        tertiary=ColorSubTheme(color=Color.YELLOW, oncolor=Color.BLACK, container=(102, 91, 0), oncontainer=Color.LIGHTYELLOW),
        error=ColorSubTheme(color=Color.ORANGERED, oncolor=Color.WHITE, container=(150, 40, 0), oncontainer=Color.ALICEBLUE),
        background=ColorPair(color=(21, 2, 53), oncolor=Color.LAVENDER),
        surface=ColorPair(color=(36, 17, 68), oncolor=Color.LAVENDER),
        surface_variant=ColorPair(color=Color.DARKSLATEBLUE, oncolor=Color.THISTLE),
        outline=Color.SLATEBLUE,
        inverse_surface=ColorPair(color=Color.LAVENDER, oncolor=(21, 2, 53)),
        inverse_primary=Color.MAGENTA
    )

    catppuccin_latte_color_theme = ColorTheme(
        primary=ColorSubTheme(color=(136, 57, 239), oncolor=(255, 255, 255), container=(234, 221, 255), oncontainer=(28, 0, 80)),
        secondary=ColorSubTheme(color=(125, 95, 102), oncolor=(255, 255, 255), container=(255, 216, 221), oncontainer=(49, 25, 31)),
        tertiary=ColorSubTheme(color=(255, 125, 112), oncolor=(255, 255, 255), container=(255, 218, 185), oncontainer=(68, 25, 0)),
        error=ColorSubTheme(color=(210, 15, 57), oncolor=(255, 255, 255), container=(249, 222, 220), oncontainer=(65, 0, 10)),
        background=ColorPair(color=(239, 241, 245), oncolor=(76, 79, 105)),
        surface=ColorPair(color=(205, 214, 244), oncolor=(76, 79, 105)),
        surface_variant=ColorPair(color=(220, 224, 232), oncolor=(92, 95, 119)),
        outline=(116, 119, 141),
        inverse_surface=ColorPair(color=(49, 50, 68), oncolor=(244, 239, 244)),
        inverse_primary=(186, 187, 241)
    )

    catppuccin_mocha_color_theme = ColorTheme(
        primary=ColorSubTheme(color=(203, 166, 247), oncolor=(49, 50, 68), container=(70, 48, 119), oncontainer=(234, 221, 255)),
        secondary=ColorSubTheme(color=(245, 194, 231), oncolor=(49, 50, 68), container=(72, 64, 88), oncontainer=(232, 222, 248)),
        tertiary=ColorSubTheme(color=(243, 139, 168), oncolor=(49, 50, 68), container=(95, 61, 73), oncontainer=(255, 216, 228)),
        error=ColorSubTheme(color=(243, 139, 168), oncolor=(49, 50, 68), container=(140, 27, 23), oncontainer=(249, 222, 220)),
        background=ColorPair(color=(30, 30, 46), oncolor=(205, 214, 244)),
        surface=ColorPair(color=(30, 30, 46), oncolor=(205, 214, 244)),
        surface_variant=ColorPair(color=(69, 71, 90), oncolor=(186, 194, 222)),
        outline=(127, 132, 156),
        inverse_surface=ColorPair(color=(205, 214, 244), oncolor=(49, 50, 68)),
        inverse_primary=(137, 180, 250)
    )

    github_light_color_theme = ColorTheme(
        primary=ColorSubTheme(color=(9, 105, 218), oncolor=(255, 255, 255), container=(221, 235, 252), oncontainer=(0, 28, 58)),
        secondary=ColorSubTheme(color=(110, 118, 129), oncolor=(255, 255, 255), container=(232, 234, 237), oncontainer=(36, 41, 47)),
        tertiary=ColorSubTheme(color=(47, 129, 34), oncolor=(255, 255, 255), container=(216, 243, 212), oncontainer=(0, 33, 4)),
        error=ColorSubTheme(color=(207, 34, 46), oncolor=(255, 255, 255), container=(255, 218, 220), oncontainer=(65, 0, 5)),
        background=ColorPair(color=(255, 255, 255), oncolor=(31, 35, 40)),
        surface=ColorPair(color=(246, 248, 250), oncolor=(31, 35, 40)),
        surface_variant=ColorPair(color=(246, 248, 250), oncolor=(87, 96, 106)),
        outline=(208, 215, 222),
        inverse_surface=ColorPair(color=(31, 35, 40), oncolor=(240, 246, 252)),
        inverse_primary=(136, 189, 255)
    )

    github_dark_color_theme = ColorTheme(
        primary=ColorSubTheme(color=(88, 166, 255), oncolor=(13, 17, 23), container=(21, 53, 94), oncontainer=(221, 235, 252)),
        secondary=ColorSubTheme(color=(139, 148, 158), oncolor=(13, 17, 23), container=(52, 58, 67), oncontainer=(232, 234, 237)),
        tertiary=ColorSubTheme(color=(63, 185, 80), oncolor=(13, 17, 23), container=(15, 61, 23), oncontainer=(216, 243, 212)),
        error=ColorSubTheme(color=(248, 131, 131), oncolor=(13, 17, 23), container=(114, 21, 24), oncontainer=(255, 218, 220)),
        background=ColorPair(color=(13, 17, 23), oncolor=(201, 209, 217)),
        surface=ColorPair(color=(22, 27, 34), oncolor=(201, 209, 217)),
        surface_variant=ColorPair(color=(22, 27, 34), oncolor=(139, 148, 158)),
        outline=(48, 54, 61),
        inverse_surface=ColorPair(color=(201, 209, 217), oncolor=(13, 17, 23)),
        inverse_primary=(9, 105, 218)
    )

    gruvbox_light_color_theme = ColorTheme(
        primary=ColorSubTheme(color=(69, 133, 136), oncolor=(251, 241, 199), container=(211, 222, 194), oncontainer=(40, 40, 40)),
        secondary=ColorSubTheme(color=(215, 153, 33), oncolor=(40, 40, 40), container=(254, 225, 168), oncontainer=(40, 40, 40)),
        tertiary=ColorSubTheme(color=(177, 98, 134), oncolor=(251, 241, 199), container=(241, 203, 216), oncontainer=(40, 40, 40)),
        error=ColorSubTheme(color=(204, 36, 29), oncolor=(251, 241, 199), container=(252, 195, 193), oncontainer=(40, 40, 40)),
        background=ColorPair(color=(251, 241, 199), oncolor=(60, 56, 54)),
        surface=ColorPair(color=(235, 219, 178), oncolor=(60, 56, 54)),
        surface_variant=ColorPair(color=(211, 197, 162), oncolor=(92, 84, 78)),
        outline=(168, 153, 132),
        inverse_surface=ColorPair(color=(60, 56, 54), oncolor=(251, 241, 199)),
        inverse_primary=(131, 165, 152)
    )

    gruvbox_dark_color_theme = ColorTheme(
        primary=ColorSubTheme(color=(131, 165, 152), oncolor=(40, 40, 40), container=(69, 133, 136), oncontainer=(235, 219, 178)),
        secondary=ColorSubTheme(color=(250, 189, 47), oncolor=(40, 40, 40), container=(215, 153, 33), oncontainer=(40, 40, 40)),
        tertiary=ColorSubTheme(color=(211, 134, 155), oncolor=(40, 40, 40), container=(177, 98, 134), oncontainer=(235, 219, 178)),
        error=ColorSubTheme(color=(251, 73, 52), oncolor=(40, 40, 40), container=(204, 36, 29), oncontainer=(235, 219, 178)),
        background=ColorPair(color=(40, 40, 40), oncolor=(235, 219, 178)),
        surface=ColorPair(color=(60, 56, 54), oncolor=(235, 219, 178)),
        surface_variant=ColorPair(color=(80, 73, 69), oncolor=(189, 174, 147)),
        outline=(124, 111, 100),
        inverse_surface=ColorPair(color=(235, 219, 178), oncolor=(40, 40, 40)),
        inverse_primary=(69, 133, 136)
    )