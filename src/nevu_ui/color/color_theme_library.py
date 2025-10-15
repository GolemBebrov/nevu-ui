from .color_theme import ColorTheme, ColorSubTheme, ColorPair
from .color import Color

class ColorThemeLibrary:
    material3_light = ColorTheme(
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

    material3_dark = ColorTheme(
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

    ocean_light = ColorTheme(
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

    synthwave_dark = ColorTheme(
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

    catppuccin_latte = ColorTheme(
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

    catppuccin_mocha = ColorTheme(
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

    github_light= ColorTheme(
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

    github_dark = ColorTheme(
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

    gruvbox_light = ColorTheme(
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

    gruvbox_dark = ColorTheme(
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

    pastel_rose_light = ColorTheme(
        primary=ColorSubTheme(color=Color.ROYALBLUE, oncolor=Color.WHITE, container=Color.LIGHTSTEELBLUE, oncontainer=Color.DARKBLUE),
        secondary=ColorSubTheme(color=Color.MEDIUMPURPLE, oncolor=Color.WHITE, container=Color.PLUM, oncontainer=Color.DARKVIOLET),
        tertiary=ColorSubTheme(color=Color.SEAGREEN, oncolor=Color.WHITE, container=Color.MEDIUMSEAGREEN, oncontainer=Color.DARKGREEN),
        error=ColorSubTheme(color=Color.CRIMSON, oncolor=Color.WHITE, container=Color.LIGHTPINK, oncontainer=Color.DARKRED),
        background=ColorPair(color=Color.WHITESMOKE, oncolor=Color.BLACK),
        surface=ColorPair(color=Color.GHOSTWHITE, oncolor=Color.BLACK),
        surface_variant=ColorPair(color=Color.LIGHTGRAY, oncolor=Color.DARKSLATEGRAY),
        outline=Color.SLATEGRAY,
        inverse_surface=ColorPair(color=Color.DARKSLATEGRAY, oncolor=Color.WHITESMOKE),
        inverse_primary=Color.CORNFLOWERBLUE,
    )
    
    neon_cyber_dark = ColorTheme(
        primary=ColorSubTheme(color=(191, 0, 255), oncolor=(255, 255, 255), container=(138, 0, 255), oncontainer=(223, 0, 255)),
        secondary=ColorSubTheme(color=(0, 255, 255), oncolor=(0, 0, 0), container=(0, 204, 255), oncontainer=(0, 0, 0)),
        tertiary=ColorSubTheme(color=(255, 0, 204), oncolor=(0, 0, 0), container=(255, 61, 148), oncontainer=(0, 0, 0)),
        error=ColorSubTheme(color=(255, 0, 0), oncolor=(255, 255, 255), container=(207, 34, 46), oncontainer=(255, 255, 255)),
        background=ColorPair(color=(12, 12, 12), oncolor=(230, 230, 250)),
        surface=ColorPair(color=(28, 28, 28), oncolor=(230, 230, 250)),
        surface_variant=ColorPair(color=(40, 40, 40), oncolor=(216, 191, 216)),
        outline=(106, 90, 205),
        inverse_surface=ColorPair(color=(230, 230, 250), oncolor=(12, 12, 12)),
        inverse_primary=(138, 43, 226)
    )