"""
Nevu-UI Colors.

It contains:
    * huge library of RGBA colors.
    * color manipulation functions.
    * typeguards for RGB/RGBA/HSL/HSLA color formats.
"""

from __future__ import annotations

import colorsys
import random
from typing import Any, TypeGuard

from nevu_ui.core import Annotations

AliceBlue = (240, 248, 255, 255)
AntiqueWhite = (250, 235, 215, 255)
Aqua = (0, 255, 255, 255)
Aquamarine = (127, 255, 212, 255)
Azure = (240, 255, 255, 255)
Beige = (245, 245, 220, 255)
Bisque = (255, 228, 196, 255)
Black = (0, 0, 0, 255)
Blank = (0, 0, 0, 0)
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

def is_rgb(color: Any) -> TypeGuard[Annotations.rgb_color]:
    """Checks color for having RGB format.
    examples:
        * (255, 100, 25) -> True
        * (-2, 300, 14.2) -> False
        * (255, 0, 25, 255) -> False
    """
    if not isinstance(color, tuple) or len(color) != 3:
        return False
    return all(isinstance(it, int) and 0 <= it <= 255 for it in color)

def is_rgba(color: Any) -> TypeGuard[Annotations.rgba_color]:
    """Checks color for having RGBA format.
    examples:
        * (255, 0, 25, 14) -> True
        * (256, -1, 34, 78)  -> False
        * (360, 1, 0.5) -> False
    """
    if not isinstance(color, tuple) or len(color) != 4:
        return False
    return all(isinstance(it, int) and 0 <= it <= 255 for it in color)

def is_rgb_like(color: Any) -> TypeGuard[Annotations.rgb_like_color]:
    """Checks color for having RGB or RGBA formats.
    examples:
        * (255, 0, 25) -> True
        * (100, 100, 100, 40) -> True
        * (-1, 34, 78)   -> False
        * (360, 1, 0.5) -> False
    """
    return is_rgb(color) or is_rgba(color)

def is_hsl(color: Any) -> TypeGuard[Annotations.hsl_color]:
    """Checks color for having HSL format.
    examples:
        * (0.5, 0.3, 0.7) -> True
        * (0.8, 0.1, 0.2, 0.4) -> False
        * (-0.1, 0.6, 200) -> False
    """
    if not isinstance(color, tuple) or len(color) != 3:
        return False
    return all(isinstance(c, float) and 0 <= c <= 1 for c in color)

def is_hsla(color: Any) -> TypeGuard[Annotations.hsla_color]:
    """Checks color for having HSLA format.
    examples:
        * (0.5, 0.3, 0.7, 1.0) -> True
        * (-0.2, 0.6, 0.9, 0.4) -> False
        * (0.4, 0.5, 0.2)  -> False
    """
    if not isinstance(color, tuple) or len(color) != 4:
        return False
    return all(isinstance(c, float) and 0 <= c <= 1 for c in color)

def is_hsl_like(color: Any) -> TypeGuard[Annotations.hsl_like_color]:
    """Checks color for having HSL or HSLA formats.
    examples:
        * (0.4, 0.6, 0.8) -> True
        * (0.4, 0.6, 0.8, 1.0) -> True
        * (-0.1, 0.3, 0.7) -> False
    """
    return is_hsl(color) or is_hsla(color)

def hsl_like_to_rgb(color: Annotations.hsl_like_color) -> Annotations.rgb_color:
    """Converts HSL or HSLA to RGB."""
    if not is_hsl_like(color):
        raise ValueError(f"Invalid HSL color: {color}")
    hue, sat, lum, alpha = color if is_hsla(color) else (color[0], color[1], color[2], 1.0)
    red, green, blue = colorsys.hls_to_rgb(hue, lum, sat)
    return (round(red * 255), round(green * 255), round(blue * 255))

def rgb_like_to_hsl(color: Annotations.rgb_like_color) -> Annotations.hsl_color:
    """Converts RGB or RGBA to HSL."""
    if not is_rgb_like(color):
        raise ValueError(f"Invalid RGB color: {color}")
    red, green, blue, alpha = color if is_rgba(color) else (color[0], color[1], color[2], 255)
    hue, lum, sat = colorsys.rgb_to_hls(red / 255, green / 255, blue / 255)
    return hue, sat, lum

def invert(color: Annotations.any_color) -> Annotations.any_color:
    """Inverts RGB like or HSL like colors."""
    if is_rgb_like(color):
        return _invert_rgb(color)
    elif is_hsl_like(color):
        return _invert_hsl(color)
    raise ValueError("Invalid color format. color must be RGB like or HSL like.")

def _invert_rgb(color: Annotations.rgb_like_color) -> Annotations.rgb_like_color:
    has_alpha = is_rgba(color)
    result = (255 - color[0], 255 - color[1], 255 - color[2])
    if has_alpha:
        return result[0], result[1], result[2], color[3]
    return result

def _invert_hsl(color: Annotations.hsl_like_color) -> Annotations.hsl_like_color:
    has_alpha = is_hsla(color)
    hue, sat, lum = color[0], color[1], color[2]
    inverted_hue = (hue + 0.5) % 1.0
    inverted_lum = 1.0 - lum
    result = (inverted_hue, sat, inverted_lum)
    if has_alpha:
        return result[0], result[1], result[2], color[3]
    return result

def lighten(color: Annotations.rgb_like_color, amount: float = 0.2) -> Annotations.rgb_like_color:
    """
    Makes RGB like color lighter by amount.
    amount: from 0.0 to 1.0, 0 means no change and 1 means full white.
    """
    has_alpha = is_rgba(color)
    if has_alpha:
        alpha = color[3]
        color = color[:3]

    if not (0.0 <= amount <= 1.0):
        raise ValueError("Amount should be between 0.0 and 1.0.")

    hue, sat, lum = rgb_like_to_hsl(color)
    lum = lum + (1 - lum) * amount

    if has_alpha:
        return (*hsl_like_to_rgb((hue, sat, lum)), alpha) #type: ignore
    return hsl_like_to_rgb((hue, sat, lum))

def darken(color: Annotations.rgb_like_color, amount: float = 0.2) -> Annotations.rgb_like_color:
    """
    Makes RGB like color darker by amount.
    amount: from 0.0 to 1.0, 0 means no change and 1 means full black.
    """
    has_alpha = is_rgba(color)
    if has_alpha:
        alpha = color[3]
        color = color[:3]

    if not (0.0 <= amount <= 1.0):
        raise ValueError("Amount should be between 0.0 and 1.0.")

    hue, sat, lum = rgb_like_to_hsl(color)
    lum = lum * (1 - amount)

    if has_alpha:
        return (*hsl_like_to_rgb((hue, sat, lum)), alpha)  #type: ignore
    return hsl_like_to_rgb((hue, sat, lum))

def random_rgb(red: int | None = None, green: int | None = None, blue: int | None = None) -> Annotations.rgb_color:
    """Returns an RGB color with specified or random values."""
    red = red if red is not None else random.randint(0, 255)
    green = green if green is not None else random.randint(0, 255)
    blue = blue if blue is not None else random.randint(0, 255)
    result = red, green, blue
    if any(not(0 <= it <= 255) for it in result):
        raise ValueError(f"Incorrect RGB values specified: red={red}, green={green}, blue={blue}")
    return result

def random_rgba(red: int | None = None, green: int | None = None, blue: int | None = None, alpha: int | None = None) -> Annotations.rgba_color:
    """Returns an RGBA color with specified or random values."""
    red = red if red is not None else random.randint(0, 255)
    green = green if green is not None else random.randint(0, 255)
    blue = blue if blue is not None else random.randint(0, 255)
    alpha = alpha if alpha is not None else random.randint(0, 255)
    result = red, green, blue, alpha
    if any(not(0 <= it <= 255) for it in result):
        raise ValueError(f"Incorrect RGB values specified: red={red}, green={green}, blue={blue}, alpha={alpha}")
    return result

def random_hsl(hue: float | None = None, sat: float | None = None, lum: float | None = None) -> Annotations.hsl_color:
    """Returns an HSL color with specified or random values."""
    hue = hue if hue is not None else random.uniform(0, 1)
    sat = sat if sat is not None else random.uniform(0, 1)
    lum = lum if lum is not None else random.uniform(0, 1)
    result = hue, sat, lum
    if any(not(0 <= it <= 1) for it in result):
        raise ValueError(f"Incorrect HSL values specified: hue={hue}, sat={sat}, lum={lum}")
    return result

def random_hsla(hue: float | None = None, sat: float | None = None, lum: float | None = None, alpha: float | None = None) -> Annotations.hsla_color:
    """Returns an HSLA color with specified or random values."""
    hue = hue if hue is not None else random.uniform(0, 1)
    sat = sat if sat is not None else random.uniform(0, 1)
    lum = lum if lum is not None else random.uniform(0, 1)
    alpha = alpha if alpha is not None else random.uniform(0, 1)
    result = hue, sat, lum, alpha
    if any(not(0 <= it <= 1) for it in result):
        raise ValueError(f"Incorrect HSLA values specified: hue={hue}, sat={sat}, lum={lum}, alpha={alpha}")
    return result

def set_float_alpha(color: Annotations.rgb_like_color, alpha: float) -> Annotations.rgba_color:
    """Sets the alpha of a RGB like color from a float value."""
    if not (0 <= alpha <= 1):
        raise ValueError("Float alpha must be between 0 and 1.")
    return set_alpha(color, round(alpha * 255))

def set_alpha(color: Annotations.rgb_like_color, alpha: int) -> Annotations.rgba_color:
    """Sets the alpha of a RGB like color from an int value."""
    if not (0 <= alpha <= 255):
        raise ValueError("Alpha must be between 0 and 255.")
    return (color[0], color[1], color[2], alpha)

def mix_rgb_like(*colors: Annotations.rgb_like_color) -> Annotations.rgba_color:
    """Merges RGB like colors into one RGBA color."""
    if len(colors) == 0:
        raise ValueError("At least one color must be present.")
    if any(not is_rgb_like(color) for color in colors):
        raise ValueError("All colors must have RGB like format.")
    final_colors = [set_alpha(color, color[3] if len(color) == 4 else 255) for color in colors]
    red, green, blue, alpha = (sum(color) // len(final_colors) for color in zip(*final_colors))
    return red, green, blue, alpha

__all__ = [
    "AliceBlue",
    "AntiqueWhite",
    "Aqua",
    "Aquamarine",
    "Azure",
    "Beige",
    "Bisque",
    "Black",
    "Blank",
    "BlanchedAlmond",
    "Blue",
    "BlueViolet",
    "Brown",
    "BurlyWood",
    "CadetBlue",
    "Chartreuse",
    "Chocolate",
    "Coral",
    "CornflowerBlue",
    "Cornsilk",
    "Crimson",
    "Cyan",
    "DarkBlue",
    "DarkCyan",
    "DarkGoldenrod",
    "DarkGray",
    "DarkGreen",
    "DarkGrey",
    "DarkKhaki",
    "DarkMagenta",
    "DarkOliveGreen",
    "DarkOrange",
    "DarkOrchid",
    "DarkRed",
    "DarkSalmon",
    "DarkSeaGreen",
    "DarkSlateBlue",
    "DarkSlateGray",
    "DarkSlateGrey",
    "DarkTurquoise",
    "DarkViolet",
    "DeepPink",
    "DeepSkyBlue",
    "DimGray",
    "DimGrey",
    "DodgerBlue",
    "FireBrick",
    "FloralWhite",
    "ForestGreen",
    "Fuchsia",
    "Gainsboro",
    "GhostWhite",
    "Gold",
    "Goldenrod",
    "Gray",
    "Green",
    "GreenYellow",
    "Grey",
    "Honeydew",
    "HotPink",
    "IndianRed",
    "Indigo",
    "Ivory",
    "Khaki",
    "Lavender",
    "LavenderBlush",
    "LawnGreen",
    "LemonChiffon",
    "LightBlue",
    "LightCoral",
    "LightCyan",
    "LightGoldenrodYellow",
    "LightGray",
    "LightGreen",
    "LightGrey",
    "LightPink",
    "LightSalmon",
    "LightSeaGreen",
    "LightSkyBlue",
    "LightSlateGray",
    "LightSlateGrey",
    "LightSteelBlue",
    "LightYellow",
    "Lime",
    "LimeGreen",
    "Linen",
    "Magenta",
    "Maroon",
    "MediumAquamarine",
    "MediumBlue",
    "MediumForestGreen",
    "MediumOrchid",
    "MediumPurple",
    "MediumSeaGreen",
    "MediumSlateBlue",
    "MediumSpringGreen",
    "MediumTurquoise",
    "MediumVioletRed",
    "MidnightBlue",
    "MintCream",
    "MistyRose",
    "Moccasin",
    "NavajoWhite",
    "Navy",
    "NavyBlue",
    "OldLace",
    "Olive",
    "OliveDrab",
    "Orange",
    "OrangeRed",
    "Orchid",
    "PaleGoldenrod",
    "PaleGreen",
    "PaleTurquoise",
    "PaleVioletRed",
    "PapayaWhip",
    "PeachPuff",
    "Peru",
    "Pink",
    "Plum",
    "PowderBlue",
    "Purple",
    "RebeccaPurple",
    "Red",
    "RosyBrown",
    "RoyalBlue",
    "SaddleBrown",
    "Salmon",
    "SandyBrown",
    "SeaGreen",
    "Seashell",
    "Sienna",
    "Silver",
    "SkyBlue",
    "SlateBlue",
    "SlateGray",
    "SlateGrey",
    "Snow",
    "SpringGreen",
    "SteelBlue",
    "Tan",
    "Teal",
    "Thistle",
    "Tomato",
    "Turquoise",
    "Violet",
    "VioletRed",
    "Wheat",
    "White",
    "WhiteSmoke",
    "Yellow",
    "YellowGreen",


    "darken",
    "hsl_like_to_rgb",
    "invert",
    "is_hsl",
    "is_hsla",
    "is_hsl_like",
    "is_rgb",
    "is_rgba",
    "is_rgb_like",
    "lighten",
    "mix_rgb_like",
    "random_hsl",
    "random_hsla",
    "random_rgb",
    "random_rgba",
    "rgb_like_to_hsl",
    "set_alpha",
    "set_float_alpha",
]
