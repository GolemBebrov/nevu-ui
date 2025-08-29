import pygame
from dataclasses import dataclass
from enum import StrEnum

# Likely will be unused
class Color_Type:
    TRANSPARENT = 101

class Color:
    BLACK = (0, 0, 0)
    WHITE = (255, 255, 255)
    RED = (255, 0, 0)
    GREEN = (0, 255, 0)
    BLUE = (0, 0, 255)
    MAGENTA = (255, 0, 255)
    CYAN = (0, 255, 255) 
    YELLOW = (255, 255, 0)
    GRAY = (128, 128, 128)
    PINK = (255, 192, 203)
    PURPLE = (128, 0, 128)
    ORANGE = (255, 165, 0)
    BROWN = (165, 42, 42)
    SILVER = (192, 192, 192)
    GOLD = (255, 215, 0)
    PALEGREEN = (152, 251, 152)
    NAVY = (0, 0, 128)
    MAROON = (128, 0, 0)
    OLIVE = (128, 128, 0)
    TEAL = (0, 128, 128)
    AQUA = (0, 255, 255)
    LAVENDER = (230, 230, 250)
    BEIGE = (245, 245, 220)
    IVORY = (255, 255, 240)
    LEMONCHIFFON = (255, 250, 205)
    LIGHTYELLOW = (255, 255, 224)
    LAVENDERBLUSH = (255, 240, 245)
    MISTYROSE = (255, 228, 225)
    ANTIQUEWHITE = (250, 235, 215)
    PAPAYAWHIP = (255, 239, 213)
    BLANCHEDALMOND = (255, 235, 205)
    BISQUE = (255, 228, 196)
    PEACHPUFF = (255, 218, 185)
    NAVAJOWHITE = (255, 222, 173)
    MOCCASIN = (255, 228, 181)
    CORAL = (255, 127, 80)
    TOMATO = (255, 99, 71)
    ORANGERED = (255, 69, 0)
    DARKORANGE = (255, 140, 0)
    CHOCOLATE = (210, 105, 30)
    SADDLEBROWN = (139, 69, 19)
    LIGHTGRAY = (211, 211, 211)
    DARKGRAY = (169, 169, 169)
    LIGHTBLACK = (105, 105, 105)
    ALICEBLUE = (240, 248, 255)
    AQUAMARINE = (127, 255, 212)
    AZURE = (240, 255, 255)
    BURLYWOOD = (222, 184, 135)
    CADETBLUE = (95, 158, 160)
    CHARTREUSE = (127, 255, 0)
    CORNFLOWERBLUE = (100, 149, 237)
    CORNSILK = (255, 248, 220)
    CRIMSON = (220, 20, 60)
    DARKBLUE = (0, 0, 139)
    DARKCYAN = (0, 139, 139)
    DARKGOLDENROD = (184, 134, 11)
    DARKGREEN = (0, 100, 0)
    DARKKHAKI = (189, 183, 107)
    DARKMAGENTA = (139, 0, 139)
    DARKOLIVEGREEN = (85, 107, 47)
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
    GOLDENROD = (218, 165, 32)
    GREENYELLOW = (173, 255, 47)
    HONEYDEW = (240, 255, 240)
    HOTPINK = (255, 105, 180)
    INDIANRED = (205, 92, 92)
    INDIGO = (75, 0, 130)
    KHAKI = (240, 230, 140)
    LAWNGREEN = (124, 252, 0)
    LIGHTBLUE = (173, 216, 230)
    LIGHTCORAL = (240, 128, 128)
    LIGHTCYAN = (224, 255, 255)
    LIGHTGOLDENRODYELLOW = (250, 250, 210)
    LIGHTGREEN = (144, 238, 144)
    LIGHTPINK = (255, 182, 193)
    LIGHTSALMON = (255, 160, 122)
    LIGHTSEAGREEN = (32, 178, 170)
    LIGHTSKYBLUE = (135, 206, 250)
    LIGHTSLATEGRAY = (119, 136, 153)
    LIGHTSTEELBLUE = (176, 196, 222)
    LIMEGREEN = (50, 205, 50)
    LINEN = (250, 240, 230)
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
    OLDLACE = (253, 245, 230)
    OLIVEDRAB = (107, 142, 35)
    ORCHID = (218, 112, 214)
    PALEGOLDENROD = (238, 232, 170)
    PALETURQUOISE = (175, 238, 238)
    PALEVIOLETRED = (219, 112, 147)
    PERU = (205, 133, 63)
    PLUM = (221, 160, 221)
    POWDERBLUE = (176, 224, 230)
    REBECCAPURPLE = (102, 51, 153)
    ROSYBROWN = (188, 143, 143)
    ROYALBLUE = (65, 105, 225)
    SEASHELL = (255, 245, 238)
    SIENNA = (160, 82, 45)
    SKYBLUE = (135, 206, 235)
    SLATEBLUE = (106, 90, 205)
    SLATEGRAY = (112, 128, 144)
    SNOW = (255, 250, 250)
    SPRINGGREEN = (0, 255, 127)
    STEELBLUE = (70, 130, 180)
    TAN = (210, 180, 140)
    THISTLE = (216, 191, 216)
    TURQUOISE = (64, 224, 208)
    VIOLET = (238, 130, 238)
    WHEAT = (245, 222, 179)
    WHITESMOKE = (245, 245, 245)
    YELLOWGREEN = (154, 205, 50)
    Ukraine = "POOP"
    @classmethod
    def __getitem__(cls, key: str) -> tuple:
        return getattr(cls, key.upper())

def hex_to_rgb(hex_color: str) -> tuple[int, int, int]:
    hex_color = hex_color.lstrip('#')
    return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4)) #type: ignore
      
def mix(*colors) -> tuple[int, int, int]:
    final_color_list = []
    for color in colors:
        if isinstance(color, str):
            if color.startswith('#'):
                color = hex_to_rgb(color)
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

class SubThemeRole(StrEnum):
    PRIMARY = "primary"
    SECONDARY = "secondary"
    TERTIARY = "tertiary"
    ERROR = "error"

@dataclass
class ColorTheme:
    """Представляет полную цветовую схему, основанную на ролях Material Design 3."""
    primary: tuple
    on_primary: tuple
    primary_container: tuple
    on_primary_container: tuple
    secondary: tuple
    on_secondary: tuple
    secondary_container: tuple
    on_secondary_container: tuple
    tertiary: tuple
    on_tertiary: tuple
    tertiary_container: tuple
    on_tertiary_container: tuple
    error: tuple
    on_error: tuple
    error_container: tuple
    on_error_container: tuple
    background: tuple
    on_background: tuple
    surface: tuple
    on_surface: tuple
    surface_variant: tuple
    on_surface_variant: tuple
    outline: tuple
    inverse_surface: tuple
    inverse_on_surface: tuple
    inverse_primary: tuple

    def get_subtheme(self, role: SubThemeRole) -> 'ColorSubTheme':
        """
        Извлекает часть цветовой схемы в виде объекта ColorSubTheme.

        Args:
            role: Роль для извлечения (используйте SubThemeRole.PRIMARY и т.д.).

        Returns:
            Объект ColorSubTheme с соответствующими цветами.
        """
        role_name = role.value
        
        color = getattr(self, role_name)
        on_color = getattr(self, f"on_{role_name}")
        container = getattr(self, f"{role_name}_container")
        on_container = getattr(self, f"on_{role_name}_container")

        return ColorSubTheme(
            color=color,
            oncolor=on_color,
            container=container,
            oncontainer=on_container
        )

@dataclass
class ColorSubTheme:
    """Представляет часть цветовой схемы, основанную на ролях Material Design 3."""
    color: tuple
    oncolor: tuple
    container: tuple
    oncontainer: tuple


material3_light_color_theme = ColorTheme(
    primary=(103, 80, 164), on_primary=(255, 255, 255), primary_container=(234, 221, 255), on_primary_container=(33, 0, 93),
    secondary=(98, 91, 113), on_secondary=(255, 255, 255), secondary_container=(232, 222, 248), on_secondary_container=(30, 25, 43),
    tertiary=(125, 82, 96), on_tertiary=(255, 255, 255), tertiary_container=(255, 216, 228), on_tertiary_container=(55, 11, 30),
    error=(179, 38, 30), on_error=(255, 255, 255), error_container=(249, 222, 220), on_error_container=(65, 14, 11),
    background=(255, 251, 255), on_background=(28, 27, 31),
    surface=(255, 251, 255), on_surface=(28, 27, 31),
    surface_variant=(231, 224, 236), on_surface_variant=(73, 69, 79),
    outline=(121, 116, 126),
    inverse_surface=(49, 48, 51), inverse_on_surface=(244, 239, 244), inverse_primary=(208, 188, 255)
)

material3_dark_color_theme = ColorTheme(
    primary=(208, 188, 255), on_primary=(56, 30, 114), primary_container=(79, 55, 139), on_primary_container=(234, 221, 255),
    secondary=(204, 194, 220), on_secondary=(51, 45, 65), secondary_container=(74, 68, 88), on_secondary_container=(232, 222, 248),
    tertiary=(239, 184, 200), on_tertiary=(75, 34, 52), tertiary_container=(100, 57, 72), on_tertiary_container=(255, 216, 228),
    error=(242, 184, 181), on_error=(96, 20, 16), error_container=(140, 29, 24), on_error_container=(249, 222, 220),
    background=(28, 27, 31), on_background=(230, 225, 229),
    surface=(28, 27, 31), on_surface=(230, 225, 229),
    surface_variant=(73, 69, 79), on_surface_variant=(202, 196, 208),
    outline=(147, 143, 153),
    inverse_surface=(230, 225, 229), inverse_on_surface=(49, 48, 51), inverse_primary=(103, 80, 164)
)

ocean_light_color_theme = ColorTheme(
    primary=Color.STEELBLUE, on_primary=Color.WHITE, primary_container=Color.LIGHTBLUE, on_primary_container=Color.DARKSLATEBLUE,
    secondary=Color.MEDIUMAQUAMARINE, on_secondary=Color.BLACK, secondary_container=Color.PALEGREEN, on_secondary_container=Color.DARKGREEN,
    tertiary=Color.SADDLEBROWN, on_tertiary=Color.BLACK, tertiary_container=Color.WHEAT, on_tertiary_container=Color.SADDLEBROWN,
    error=Color.TOMATO, on_error=Color.WHITE, error_container=Color.MISTYROSE, on_error_container=Color.DARKRED,
    background=Color.ALICEBLUE, on_background=Color.DARKSLATEGRAY,
    surface=Color.WHITE, on_surface=Color.DARKSLATEGRAY,
    surface_variant=Color.POWDERBLUE, on_surface_variant=Color.SLATEGRAY,
    outline=Color.LIGHTSLATEGRAY,
    inverse_surface=Color.DARKSLATEGRAY, inverse_on_surface=Color.WHITE, inverse_primary=Color.SKYBLUE
)

synthwave_dark_color_theme = ColorTheme(
    primary=Color.DEEPPINK, on_primary=Color.WHITE, primary_container=(99, 0, 57), on_primary_container=Color.PINK,
    secondary=Color.CYAN, on_secondary=Color.BLACK, secondary_container=(0, 77, 77), on_secondary_container=Color.AQUAMARINE,
    tertiary=Color.YELLOW, on_tertiary=Color.BLACK, tertiary_container=(102, 91, 0), on_tertiary_container=Color.LIGHTYELLOW,
    error=Color.ORANGERED, on_error=Color.WHITE, error_container=(150, 40, 0), on_error_container=Color.ALICEBLUE,
    background=(21, 2, 53), on_background=Color.LAVENDER,
    surface=(36, 17, 68), on_surface=Color.LAVENDER,
    surface_variant=Color.DARKSLATEBLUE, on_surface_variant=Color.THISTLE,
    outline=Color.SLATEBLUE,
    inverse_surface=Color.LAVENDER, inverse_on_surface=(21, 2, 53), inverse_primary=Color.MAGENTA
)