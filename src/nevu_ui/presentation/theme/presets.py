from dataclasses import dataclass

from . import ColorPair, ColorSubTheme, ColorTheme


class TrackThemeNamesMeta(type):
    def __new__(cls, name, bases, namespace):
        theme_names = [key for key in namespace.keys() if not key.startswith("_")]
        namespace["_names"] = theme_names
        return super().__new__(cls, name, bases, namespace)


@dataclass
class ColorThemeLibrary(metaclass=TrackThemeNamesMeta):
    material3_light = ColorTheme(
        name="Material3 Light",
        primary=ColorSubTheme(
            color=(103, 80, 164),
            on_color=(255, 255, 255),
            container=(234, 221, 255),
            on_container=(33, 0, 93),
        ),
        secondary=ColorSubTheme(
            color=(98, 91, 113),
            on_color=(255, 255, 255),
            container=(232, 222, 248),
            on_container=(29, 25, 43),
        ),
        tertiary=ColorSubTheme(
            color=(125, 82, 96),
            on_color=(255, 255, 255),
            container=(255, 216, 228),
            on_container=(49, 17, 29),
        ),
        error=ColorSubTheme(
            color=(179, 38, 30),
            on_color=(255, 255, 255),
            container=(249, 222, 220),
            on_container=(65, 14, 11),
        ),
        background=ColorPair(color=(255, 251, 254), on_color=(28, 27, 31)),
        surface=ColorPair(color=(255, 251, 254), on_color=(28, 27, 31)),
        surface_variant=ColorPair(color=(231, 224, 236), on_color=(73, 69, 79)),
        outline=(121, 116, 126),
        inverse_surface=ColorPair(color=(49, 48, 51), on_color=(244, 239, 244)),
        inverse_primary=(208, 188, 255),
    )

    material3_dark = ColorTheme(
        name="Material3 Dark",
        primary=ColorSubTheme(
            color=(208, 188, 255),
            on_color=(56, 30, 114),
            container=(79, 55, 139),
            on_container=(234, 221, 255),
        ),
        secondary=ColorSubTheme(
            color=(204, 194, 220),
            on_color=(51, 45, 65),
            container=(74, 68, 88),
            on_container=(232, 222, 248),
        ),
        tertiary=ColorSubTheme(
            color=(239, 184, 200),
            on_color=(75, 34, 52),
            container=(100, 57, 72),
            on_container=(255, 216, 228),
        ),
        error=ColorSubTheme(
            color=(242, 184, 181),
            on_color=(96, 20, 16),
            container=(140, 29, 24),
            on_container=(249, 222, 220),
        ),
        background=ColorPair(color=(28, 27, 31), on_color=(230, 225, 229)),
        surface=ColorPair(color=(28, 27, 31), on_color=(230, 225, 229)),
        surface_variant=ColorPair(color=(73, 69, 79), on_color=(202, 196, 208)),
        outline=(147, 143, 153),
        inverse_surface=ColorPair(color=(230, 225, 229), on_color=(49, 48, 51)),
        inverse_primary=(103, 80, 164),
    )

    material3_blue = ColorTheme(
        name="Material3 Blue Dark",
        primary=ColorSubTheme(
            color=(168, 199, 250),
            on_color=(15, 48, 84),
            container=(30, 73, 118),
            on_container=(215, 227, 255),
        ),
        secondary=ColorSubTheme(
            color=(164, 203, 221),
            on_color=(14, 50, 64),
            container=(36, 75, 91),
            on_container=(194, 232, 250),
        ),
        tertiary=ColorSubTheme(
            color=(208, 188, 255),
            on_color=(56, 30, 114),
            container=(79, 55, 139),
            on_container=(234, 221, 255),
        ),
        error=ColorSubTheme(
            color=(255, 180, 171),
            on_color=(105, 0, 5),
            container=(147, 0, 10),
            on_container=(255, 218, 214),
        ),
        background=ColorPair(color=(26, 28, 30), on_color=(227, 226, 230)),
        surface=ColorPair(color=(26, 28, 30), on_color=(227, 226, 230)),
        surface_variant=ColorPair(color=(67, 71, 78), on_color=(195, 198, 207)),
        outline=(141, 145, 153),
        inverse_surface=ColorPair(color=(227, 226, 230), on_color=(47, 48, 51)),
        inverse_primary=(10, 85, 168),
    )

    material3_green = ColorTheme(
        name="Material3 Green Dark",
        primary=ColorSubTheme(
            color=(138, 216, 176),
            on_color=(0, 56, 34),
            container=(0, 81, 51),
            on_container=(165, 245, 204),
        ),
        secondary=ColorSubTheme(
            color=(181, 204, 186),
            on_color=(33, 53, 38),
            container=(55, 75, 59),
            on_container=(209, 232, 213),
        ),
        tertiary=ColorSubTheme(
            color=(164, 205, 219),
            on_color=(7, 53, 64),
            container=(36, 76, 88),
            on_container=(191, 233, 248),
        ),
        error=ColorSubTheme(
            color=(255, 180, 171),
            on_color=(105, 0, 5),
            container=(147, 0, 10),
            on_container=(255, 218, 214),
        ),
        background=ColorPair(color=(26, 28, 27), on_color=(226, 227, 223)),
        surface=ColorPair(color=(26, 28, 27), on_color=(226, 227, 223)),
        surface_variant=ColorPair(color=(66, 73, 64), on_color=(194, 200, 189)),
        outline=(140, 147, 136),
        inverse_surface=ColorPair(color=(226, 227, 223), on_color=(47, 49, 47)),
        inverse_primary=(0, 108, 70),
    )

    material3_orange = ColorTheme(
        name="Material3 Orange Dark",
        primary=ColorSubTheme(
            color=(255, 183, 124),
            on_color=(80, 43, 0),
            container=(112, 59, 0),
            on_container=(255, 220, 190),
        ),
        secondary=ColorSubTheme(
            color=(227, 193, 165),
            on_color=(66, 44, 25),
            container=(90, 66, 45),
            on_container=(255, 221, 191),
        ),
        tertiary=ColorSubTheme(
            color=(205, 206, 165),
            on_color=(51, 51, 19),
            container=(74, 74, 39),
            on_container=(232, 234, 191),
        ),
        error=ColorSubTheme(
            color=(255, 180, 171),
            on_color=(105, 0, 5),
            container=(147, 0, 10),
            on_container=(255, 218, 214),
        ),
        background=ColorPair(color=(31, 27, 24), on_color=(234, 225, 221)),
        surface=ColorPair(color=(31, 27, 24), on_color=(234, 225, 221)),
        surface_variant=ColorPair(color=(82, 68, 59), on_color=(215, 194, 182)),
        outline=(159, 141, 130),
        inverse_surface=ColorPair(color=(234, 225, 221), on_color=(50, 47, 44)),
        inverse_primary=(143, 78, 0),
    )

    material3_teal = ColorTheme(
        name="Material3 Teal Dark",
        primary=ColorSubTheme(
            color=(128, 213, 219),
            on_color=(0, 55, 58),
            container=(0, 79, 83),
            on_container=(158, 240, 247),
        ),
        secondary=ColorSubTheme(
            color=(177, 203, 206),
            on_color=(27, 52, 55),
            container=(50, 75, 78),
            on_container=(204, 232, 235),
        ),
        tertiary=ColorSubTheme(
            color=(189, 199, 236),
            on_color=(39, 49, 82),
            container=(62, 71, 106),
            on_container=(218, 227, 255),
        ),
        error=ColorSubTheme(
            color=(255, 180, 171),
            on_color=(105, 0, 5),
            container=(147, 0, 10),
            on_container=(255, 218, 214),
        ),
        background=ColorPair(color=(25, 28, 29), on_color=(225, 227, 227)),
        surface=ColorPair(color=(25, 28, 29), on_color=(225, 227, 227)),
        surface_variant=ColorPair(color=(63, 72, 74), on_color=(191, 200, 202)),
        outline=(137, 146, 148),
        inverse_surface=ColorPair(color=(225, 227, 227), on_color=(46, 49, 49)),
        inverse_primary=(0, 106, 111),
    )

    one_dark = ColorTheme(
        name="Atom One Dark",
        primary=ColorSubTheme(
            color=(97, 175, 239),
            on_color=(40, 44, 52),
            container=(33, 56, 77),
            on_container=(209, 233, 255),
        ),
        secondary=ColorSubTheme(
            color=(198, 120, 221),
            on_color=(40, 44, 52),
            container=(65, 40, 73),
            on_container=(243, 218, 251),
        ),
        tertiary=ColorSubTheme(
            color=(152, 195, 121),
            on_color=(40, 44, 52),
            container=(42, 60, 33),
            on_container=(224, 245, 209),
        ),
        error=ColorSubTheme(
            color=(224, 108, 117),
            on_color=(30, 20, 22),
            container=(80, 30, 35),
            on_container=(255, 214, 218),
        ),
        background=ColorPair(color=(40, 44, 52), on_color=(171, 178, 191)),
        surface=ColorPair(color=(33, 37, 43), on_color=(171, 178, 191)),
        surface_variant=ColorPair(color=(44, 50, 60), on_color=(171, 178, 191)),
        outline=(92, 99, 112),
        inverse_surface=ColorPair(color=(171, 178, 191), on_color=(40, 44, 52)),
        inverse_primary=(97, 175, 239),
    )

    one_light = ColorTheme(
        name="Atom One Light",
        primary=ColorSubTheme(
            color=(44, 98, 216),
            on_color=(255, 255, 255),
            container=(220, 234, 255),
            on_container=(16, 48, 128),
        ),
        secondary=ColorSubTheme(
            color=(148, 28, 146),
            on_color=(255, 255, 255),
            container=(248, 220, 248),
            on_container=(68, 10, 67),
        ),
        tertiary=ColorSubTheme(
            color=(46, 125, 45),
            on_color=(255, 255, 255),
            container=(220, 245, 220),
            on_container=(15, 60, 15),
        ),
        error=ColorSubTheme(
            color=(205, 52, 40),
            on_color=(255, 255, 255),
            container=(255, 225, 222),
            on_container=(92, 16, 10),
        ),
        background=ColorPair(color=(250, 250, 250), on_color=(56, 58, 66)),
        surface=ColorPair(color=(240, 240, 241), on_color=(56, 58, 66)),
        surface_variant=ColorPair(color=(229, 230, 232), on_color=(105, 108, 117)),
        outline=(160, 161, 167),
        inverse_surface=ColorPair(color=(56, 58, 66), on_color=(250, 250, 250)),
        inverse_primary=(44, 98, 216),
    )

    monokai_pro = ColorTheme(
        name="Monokai Pro",
        primary=ColorSubTheme(
            color=(255, 216, 102),
            on_color=(45, 42, 46),
            container=(80, 65, 25),
            on_container=(255, 236, 179),
        ),
        secondary=ColorSubTheme(
            color=(120, 220, 232),
            on_color=(45, 42, 46),
            container=(30, 65, 70),
            on_container=(205, 245, 250),
        ),
        tertiary=ColorSubTheme(
            color=(171, 157, 242),
            on_color=(45, 42, 46),
            container=(55, 48, 85),
            on_container=(230, 222, 255),
        ),
        error=ColorSubTheme(
            color=(255, 97, 136),
            on_color=(45, 42, 46),
            container=(85, 25, 40),
            on_container=(255, 205, 218),
        ),
        background=ColorPair(color=(45, 42, 46), on_color=(252, 252, 250)),
        surface=ColorPair(color=(34, 31, 34), on_color=(252, 252, 250)),
        surface_variant=ColorPair(color=(64, 60, 65), on_color=(193, 192, 192)),
        outline=(114, 112, 114),
        inverse_surface=ColorPair(color=(252, 252, 250), on_color=(45, 42, 46)),
        inverse_primary=(255, 216, 102),
    )

    rose_pine = ColorTheme(
        name="Rosé Pine",
        primary=ColorSubTheme(
            color=(196, 167, 231),
            on_color=(25, 23, 36),
            container=(65, 52, 82),
            on_container=(235, 220, 252),
        ),
        secondary=ColorSubTheme(
            color=(235, 188, 186),
            on_color=(25, 23, 36),
            container=(75, 50, 50),
            on_container=(250, 225, 224),
        ),
        tertiary=ColorSubTheme(
            color=(156, 207, 216),
            on_color=(25, 23, 36),
            container=(42, 65, 70),
            on_container=(215, 242, 247),
        ),
        error=ColorSubTheme(
            color=(235, 111, 146),
            on_color=(25, 23, 36),
            container=(80, 28, 45),
            on_container=(255, 205, 220),
        ),
        background=ColorPair(color=(25, 23, 36), on_color=(224, 222, 244)),
        surface=ColorPair(color=(31, 29, 46), on_color=(224, 222, 244)),
        surface_variant=ColorPair(color=(38, 35, 58), on_color=(144, 140, 170)),
        outline=(110, 106, 134),
        inverse_surface=ColorPair(color=(224, 222, 244), on_color=(25, 23, 36)),
        inverse_primary=(196, 167, 231),
    )

    rose_pine_dawn = ColorTheme(
        name="Rosé Pine Dawn",
        primary=ColorSubTheme(
            color=(118, 93, 145),
            on_color=(255, 255, 255),
            container=(235, 225, 248),
            on_container=(55, 38, 75),
        ),
        secondary=ColorSubTheme(
            color=(165, 80, 104),
            on_color=(255, 255, 255),
            container=(250, 225, 232),
            on_container=(75, 25, 40),
        ),
        tertiary=ColorSubTheme(
            color=(46, 116, 128),
            on_color=(255, 255, 255),
            container=(215, 240, 245),
            on_container=(15, 50, 58),
        ),
        error=ColorSubTheme(
            color=(170, 55, 85),
            on_color=(255, 255, 255),
            container=(250, 220, 225),
            on_container=(80, 20, 35),
        ),
        background=ColorPair(color=(250, 244, 237), on_color=(87, 82, 121)),
        surface=ColorPair(color=(255, 253, 251), on_color=(87, 82, 121)),
        surface_variant=ColorPair(color=(242, 233, 222), on_color=(121, 117, 147)),
        outline=(152, 147, 165),
        inverse_surface=ColorPair(color=(87, 82, 121), on_color=(250, 244, 237)),
        inverse_primary=(118, 93, 145),
    )

    kanagawa_wave = ColorTheme(
        name="Kanagawa Wave",
        primary=ColorSubTheme(
            color=(126, 156, 216),
            on_color=(31, 31, 40),
            container=(42, 58, 88),
            on_container=(210, 226, 255),
        ),
        secondary=ColorSubTheme(
            color=(149, 127, 184),
            on_color=(31, 31, 40),
            container=(52, 45, 68),
            on_container=(225, 212, 245),
        ),
        tertiary=ColorSubTheme(
            color=(118, 148, 106),
            on_color=(31, 31, 40),
            container=(40, 58, 38),
            on_container=(205, 235, 195),
        ),
        error=ColorSubTheme(
            color=(195, 64, 67),
            on_color=(255, 252, 245),
            container=(78, 28, 30),
            on_container=(255, 200, 202),
        ),
        background=ColorPair(color=(31, 31, 40), on_color=(220, 215, 186)),
        surface=ColorPair(color=(22, 22, 29), on_color=(220, 215, 186)),
        surface_variant=ColorPair(color=(42, 42, 55), on_color=(197, 194, 174)),
        outline=(114, 113, 105),
        inverse_surface=ColorPair(color=(220, 215, 186), on_color=(31, 31, 40)),
        inverse_primary=(126, 156, 216),
    )

    kanagawa_lotus = ColorTheme(
        name="Kanagawa Lotus",
        primary=ColorSubTheme(
            color=(77, 105, 155),
            on_color=(255, 255, 255),
            container=(220, 232, 252),
            on_container=(25, 42, 75),
        ),
        secondary=ColorSubTheme(
            color=(98, 94, 122),
            on_color=(255, 255, 255),
            container=(230, 228, 240),
            on_container=(35, 32, 50),
        ),
        tertiary=ColorSubTheme(
            color=(65, 105, 62),
            on_color=(255, 255, 255),
            container=(222, 240, 220),
            on_container=(24, 48, 22),
        ),
        error=ColorSubTheme(
            color=(185, 45, 65),
            on_color=(255, 255, 255),
            container=(255, 220, 225),
            on_container=(80, 15, 25),
        ),
        background=ColorPair(color=(242, 236, 222), on_color=(84, 84, 109)),
        surface=ColorPair(color=(248, 244, 233), on_color=(84, 84, 109)),
        surface_variant=ColorPair(color=(229, 222, 206), on_color=(113, 110, 131)),
        outline=(160, 154, 142),
        inverse_surface=ColorPair(color=(84, 84, 109), on_color=(242, 236, 222)),
        inverse_primary=(77, 105, 155),
    )

    everforest_dark = ColorTheme(
        name="Everforest Dark",
        primary=ColorSubTheme(
            color=(167, 192, 128),
            on_color=(45, 53, 59),
            container=(55, 75, 48),
            on_container=(215, 238, 185),
        ),
        secondary=ColorSubTheme(
            color=(127, 187, 179),
            on_color=(45, 53, 59),
            container=(45, 72, 70),
            on_container=(195, 238, 232),
        ),
        tertiary=ColorSubTheme(
            color=(219, 188, 127),
            on_color=(45, 53, 59),
            container=(78, 65, 40),
            on_container=(248, 228, 185),
        ),
        error=ColorSubTheme(
            color=(230, 126, 128),
            on_color=(45, 53, 59),
            container=(85, 38, 40),
            on_container=(255, 210, 212),
        ),
        background=ColorPair(color=(45, 53, 59), on_color=(211, 198, 170)),
        surface=ColorPair(color=(52, 63, 68), on_color=(211, 198, 170)),
        surface_variant=ColorPair(color=(61, 72, 77), on_color=(180, 170, 145)),
        outline=(122, 132, 120),
        inverse_surface=ColorPair(color=(211, 198, 170), on_color=(45, 53, 59)),
        inverse_primary=(167, 192, 128),
    )

    everforest_light = ColorTheme(
        name="Everforest Light",
        primary=ColorSubTheme(
            color=(102, 122, 0),
            on_color=(255, 255, 255),
            container=(235, 245, 205),
            on_container=(45, 55, 0),
        ),
        secondary=ColorSubTheme(
            color=(42, 120, 160),
            on_color=(255, 255, 255),
            container=(215, 240, 252),
            on_container=(10, 48, 70),
        ),
        tertiary=ColorSubTheme(
            color=(145, 98, 0),
            on_color=(255, 255, 255),
            container=(255, 240, 200),
            on_container=(75, 50, 0),
        ),
        error=ColorSubTheme(
            color=(205, 50, 45),
            on_color=(255, 255, 255),
            container=(255, 225, 224),
            on_container=(95, 18, 16),
        ),
        background=ColorPair(color=(253, 246, 227), on_color=(92, 106, 114)),
        surface=ColorPair(color=(244, 240, 217), on_color=(92, 106, 114)),
        surface_variant=ColorPair(color=(230, 225, 200), on_color=(92, 106, 114)),
        outline=(165, 160, 140),
        inverse_surface=ColorPair(color=(92, 106, 114), on_color=(253, 246, 227)),
        inverse_primary=(102, 122, 0),
    )

    ayu_mirage = ColorTheme(
        name="Ayu Mirage",
        primary=ColorSubTheme(
            color=(255, 204, 102),
            on_color=(31, 36, 48),
            container=(75, 60, 32),
            on_container=(255, 232, 175),
        ),
        secondary=ColorSubTheme(
            color=(92, 207, 230),
            on_color=(31, 36, 48),
            container=(28, 62, 70),
            on_container=(195, 242, 250),
        ),
        tertiary=ColorSubTheme(
            color=(212, 191, 255),
            on_color=(31, 36, 48),
            container=(65, 55, 85),
            on_container=(238, 228, 255),
        ),
        error=ColorSubTheme(
            color=(242, 135, 121),
            on_color=(31, 36, 48),
            container=(80, 35, 32),
            on_container=(255, 215, 210),
        ),
        background=ColorPair(color=(31, 36, 48), on_color=(204, 202, 194)),
        surface=ColorPair(color=(36, 41, 54), on_color=(204, 202, 194)),
        surface_variant=ColorPair(color=(47, 53, 69), on_color=(190, 190, 190)),
        outline=(108, 115, 130),
        inverse_surface=ColorPair(color=(204, 202, 194), on_color=(31, 36, 48)),
        inverse_primary=(255, 204, 102),
    )

    ayu_light = ColorTheme(
        name="Ayu Light",
        primary=ColorSubTheme(
            color=(195, 85, 15),
            on_color=(255, 255, 255),
            container=(255, 230, 212),
            on_container=(90, 42, 10),
        ),
        secondary=ColorSubTheme(
            color=(22, 115, 180),
            on_color=(255, 255, 255),
            container=(218, 238, 255),
            on_container=(12, 52, 85),
        ),
        tertiary=ColorSubTheme(
            color=(82, 120, 0),
            on_color=(255, 255, 255),
            container=(232, 248, 190),
            on_container=(42, 60, 0),
        ),
        error=ColorSubTheme(
            color=(210, 45, 35),
            on_color=(255, 255, 255),
            container=(255, 224, 222),
            on_container=(92, 20, 16),
        ),
        background=ColorPair(color=(250, 250, 250), on_color=(92, 97, 102)),
        surface=ColorPair(color=(243, 244, 245), on_color=(92, 97, 102)),
        surface_variant=ColorPair(color=(230, 232, 235), on_color=(92, 97, 102)),
        outline=(175, 180, 185),
        inverse_surface=ColorPair(color=(92, 97, 102), on_color=(250, 250, 250)),
        inverse_primary=(195, 85, 15),
    )

    catppuccin_latte = ColorTheme(
        name="Catppuccin Latte",
        primary=ColorSubTheme(
            color=(136, 57, 239),
            on_color=(255, 255, 255),
            container=(234, 221, 255),
            on_container=(28, 0, 80),
        ),
        secondary=ColorSubTheme(
            color=(234, 118, 203),
            on_color=(76, 79, 105),
            container=(255, 216, 240),
            on_container=(76, 79, 105),
        ),
        tertiary=ColorSubTheme(
            color=(30, 102, 245),
            on_color=(255, 255, 255),
            container=(218, 230, 255),
            on_container=(0, 37, 105),
        ),
        error=ColorSubTheme(
            color=(210, 15, 57),
            on_color=(255, 255, 255),
            container=(249, 222, 220),
            on_container=(65, 0, 10),
        ),
        background=ColorPair(color=(239, 241, 245), on_color=(76, 79, 105)),
        surface=ColorPair(color=(204, 208, 218), on_color=(76, 79, 105)),
        surface_variant=ColorPair(color=(220, 224, 232), on_color=(92, 95, 119)),
        outline=(156, 160, 176),
        inverse_surface=ColorPair(color=(49, 50, 68), on_color=(239, 241, 245)),
        inverse_primary=(186, 187, 241),
    )

    catppuccin_mocha = ColorTheme(
        name="Catppuccin Mocha",
        primary=ColorSubTheme(
            color=(203, 166, 247),
            on_color=(30, 30, 46),
            container=(70, 48, 119),
            on_container=(220, 189, 255),
        ),
        secondary=ColorSubTheme(
            color=(245, 194, 231),
            on_color=(49, 50, 68),
            container=(90, 60, 80),
            on_container=(248, 208, 238),
        ),
        tertiary=ColorSubTheme(
            color=(137, 220, 235),
            on_color=(30, 30, 46),
            container=(40, 90, 100),
            on_container=(180, 240, 250),
        ),
        error=ColorSubTheme(
            color=(243, 139, 168),
            on_color=(49, 50, 68),
            container=(140, 27, 23),
            on_container=(249, 222, 220),
        ),
        background=ColorPair(color=(30, 30, 46), on_color=(205, 214, 244)),
        surface=ColorPair(color=(49, 50, 68), on_color=(205, 214, 244)),
        surface_variant=ColorPair(color=(88, 91, 112), on_color=(205, 214, 244)),
        outline=(147, 153, 178),
        inverse_surface=ColorPair(color=(205, 214, 244), on_color=(49, 50, 68)),
        inverse_primary=(137, 180, 250),
    )

    github_light = ColorTheme(
        name="GitHub Light",
        primary=ColorSubTheme(
            color=(9, 105, 218),
            on_color=(255, 255, 255),
            container=(221, 235, 252),
            on_container=(0, 28, 58),
        ),
        secondary=ColorSubTheme(
            color=(110, 118, 129),
            on_color=(255, 255, 255),
            container=(232, 234, 237),
            on_container=(36, 41, 47),
        ),
        tertiary=ColorSubTheme(
            color=(47, 129, 34),
            on_color=(255, 255, 255),
            container=(216, 243, 212),
            on_container=(0, 33, 4),
        ),
        error=ColorSubTheme(
            color=(207, 34, 46),
            on_color=(255, 255, 255),
            container=(255, 218, 220),
            on_container=(65, 0, 5),
        ),
        background=ColorPair(color=(255, 255, 255), on_color=(31, 35, 40)),
        surface=ColorPair(color=(246, 248, 250), on_color=(31, 35, 40)),
        surface_variant=ColorPair(color=(234, 238, 242), on_color=(87, 96, 106)),
        outline=(208, 215, 222),
        inverse_surface=ColorPair(color=(31, 35, 40), on_color=(240, 246, 252)),
        inverse_primary=(88, 166, 255),
    )

    github_dark = ColorTheme(
        name="GitHub Dark",
        primary=ColorSubTheme(
            color=(88, 166, 255),
            on_color=(13, 17, 23),
            container=(21, 53, 94),
            on_container=(221, 235, 252),
        ),
        secondary=ColorSubTheme(
            color=(139, 148, 158),
            on_color=(13, 17, 23),
            container=(52, 58, 67),
            on_container=(232, 234, 237),
        ),
        tertiary=ColorSubTheme(
            color=(63, 185, 80),
            on_color=(13, 17, 23),
            container=(15, 61, 23),
            on_container=(216, 243, 212),
        ),
        error=ColorSubTheme(
            color=(248, 131, 131),
            on_color=(13, 17, 23),
            container=(114, 21, 24),
            on_container=(255, 218, 220),
        ),
        background=ColorPair(color=(13, 17, 23), on_color=(201, 209, 217)),
        surface=ColorPair(color=(22, 27, 34), on_color=(201, 209, 217)),
        surface_variant=ColorPair(color=(33, 38, 45), on_color=(139, 148, 158)),
        outline=(48, 54, 61),
        inverse_surface=ColorPair(color=(201, 209, 217), on_color=(13, 17, 23)),
        inverse_primary=(9, 105, 218),
    )

    github_dimmed = ColorTheme(
        name="GitHub Dimmed",
        primary=ColorSubTheme(
            color=(83, 155, 245),
            on_color=(28, 33, 40),
            container=(33, 51, 71),
            on_container=(205, 217, 229),
        ),
        secondary=ColorSubTheme(
            color=(87, 171, 90),
            on_color=(28, 33, 40),
            container=(28, 61, 35),
            on_container=(205, 217, 229),
        ),
        tertiary=ColorSubTheme(
            color=(118, 131, 144),
            on_color=(28, 33, 40),
            container=(45, 51, 59),
            on_container=(173, 186, 199),
        ),
        error=ColorSubTheme(
            color=(244, 112, 103),
            on_color=(28, 33, 40),
            container=(76, 35, 33),
            on_container=(255, 219, 218),
        ),
        background=ColorPair(color=(34, 39, 46), on_color=(173, 186, 199)),
        surface=ColorPair(color=(28, 33, 40), on_color=(173, 186, 199)),
        surface_variant=ColorPair(color=(45, 51, 59), on_color=(173, 186, 199)),
        outline=(68, 76, 86),
        inverse_surface=ColorPair(color=(173, 186, 199), on_color=(28, 33, 40)),
        inverse_primary=(83, 155, 245),
    )

    github_high_contrast = ColorTheme(
        name="GitHub High Contrast",
        primary=ColorSubTheme(
            color=(64, 158, 255),
            on_color=(1, 4, 9),
            container=(10, 40, 80),
            on_container=(220, 240, 255),
        ),
        secondary=ColorSubTheme(
            color=(63, 185, 80),
            on_color=(1, 4, 9),
            container=(20, 70, 30),
            on_container=(220, 255, 220),
        ),
        tertiary=ColorSubTheme(
            color=(240, 246, 252),
            on_color=(1, 4, 9),
            container=(48, 54, 61),
            on_container=(255, 255, 255),
        ),
        error=ColorSubTheme(
            color=(255, 107, 107),
            on_color=(1, 4, 9),
            container=(100, 10, 10),
            on_container=(255, 200, 200),
        ),
        background=ColorPair(color=(1, 4, 9), on_color=(255, 255, 255)),
        surface=ColorPair(color=(10, 12, 16), on_color=(255, 255, 255)),
        surface_variant=ColorPair(color=(33, 38, 45), on_color=(240, 246, 252)),
        outline=(126, 134, 144),
        inverse_surface=ColorPair(color=(255, 255, 255), on_color=(1, 4, 9)),
        inverse_primary=(9, 105, 218),
    )

    tokyo_night = ColorTheme(
        name="Tokyo Night",
        primary=ColorSubTheme(
            color=(122, 162, 247),
            on_color=(26, 27, 38),
            container=(61, 89, 161),
            on_container=(192, 202, 245),
        ),
        secondary=ColorSubTheme(
            color=(187, 154, 247),
            on_color=(26, 27, 38),
            container=(52, 59, 88),
            on_container=(219, 203, 245),
        ),
        tertiary=ColorSubTheme(
            color=(115, 218, 202),
            on_color=(26, 27, 38),
            container=(36, 68, 84),
            on_container=(167, 254, 235),
        ),
        error=ColorSubTheme(
            color=(247, 118, 142),
            on_color=(26, 27, 38),
            container=(90, 30, 45),
            on_container=(255, 189, 189),
        ),
        background=ColorPair(color=(26, 27, 38), on_color=(192, 202, 245)),
        surface=ColorPair(color=(36, 40, 59), on_color=(192, 202, 245)),
        surface_variant=ColorPair(color=(52, 59, 88), on_color=(169, 177, 214)),
        outline=(68, 75, 106),
        inverse_surface=ColorPair(color=(192, 202, 245), on_color=(26, 27, 38)),
        inverse_primary=(122, 162, 247),
    )

    dracula = ColorTheme(
        name="Dracula",
        primary=ColorSubTheme(
            color=(189, 147, 249),
            on_color=(40, 42, 54),
            container=(74, 55, 106),
            on_container=(216, 189, 255),
        ),
        secondary=ColorSubTheme(
            color=(255, 121, 198),
            on_color=(40, 42, 54),
            container=(90, 42, 70),
            on_container=(255, 184, 225),
        ),
        tertiary=ColorSubTheme(
            color=(139, 233, 253),
            on_color=(40, 42, 54),
            container=(45, 85, 95),
            on_container=(165, 245, 255),
        ),
        error=ColorSubTheme(
            color=(255, 85, 85),
            on_color=(40, 42, 54),
            container=(90, 35, 35),
            on_container=(255, 180, 180),
        ),
        background=ColorPair(color=(40, 42, 54), on_color=(248, 248, 242)),
        surface=ColorPair(color=(68, 71, 90), on_color=(248, 248, 242)),
        surface_variant=ColorPair(color=(57, 59, 73), on_color=(189, 147, 249)),
        outline=(98, 114, 164),
        inverse_surface=ColorPair(color=(248, 248, 242), on_color=(40, 42, 54)),
        inverse_primary=(189, 147, 249),
    )

    nord_dark = ColorTheme(
        name="Nord",
        primary=ColorSubTheme(
            color=(136, 192, 208),
            on_color=(46, 52, 64),
            container=(46, 75, 105),
            on_container=(236, 239, 244),
        ),
        secondary=ColorSubTheme(
            color=(129, 161, 193),
            on_color=(46, 52, 64),
            container=(67, 76, 94),
            on_container=(216, 222, 233),
        ),
        tertiary=ColorSubTheme(
            color=(143, 188, 187),
            on_color=(46, 52, 64),
            container=(59, 66, 82),
            on_container=(229, 233, 240),
        ),
        error=ColorSubTheme(
            color=(191, 97, 106),
            on_color=(46, 52, 64),
            container=(110, 52, 58),
            on_container=(236, 239, 244),
        ),
        background=ColorPair(color=(46, 52, 64), on_color=(216, 222, 233)),
        surface=ColorPair(color=(59, 66, 82), on_color=(229, 233, 240)),
        surface_variant=ColorPair(color=(67, 76, 94), on_color=(216, 222, 233)),
        outline=(76, 86, 106),
        inverse_surface=ColorPair(color=(216, 222, 233), on_color=(46, 52, 64)),
        inverse_primary=(136, 192, 208),
    )

    gruvbox_dark = ColorTheme(
        name="Gruvbox Dark",
        primary=ColorSubTheme(
            color=(131, 165, 152),
            on_color=(40, 40, 40),
            container=(50, 75, 76),
            on_container=(235, 219, 178),
        ),
        secondary=ColorSubTheme(
            color=(250, 189, 47),
            on_color=(40, 40, 40),
            container=(102, 92, 84),
            on_container=(251, 241, 199),
        ),
        tertiary=ColorSubTheme(
            color=(211, 134, 155),
            on_color=(40, 40, 40),
            container=(80, 55, 68),
            on_container=(235, 219, 178),
        ),
        error=ColorSubTheme(
            color=(251, 73, 52),
            on_color=(40, 40, 40),
            container=(100, 30, 25),
            on_container=(251, 241, 199),
        ),
        background=ColorPair(color=(40, 40, 40), on_color=(235, 219, 178)),
        surface=ColorPair(color=(60, 56, 54), on_color=(235, 219, 178)),
        surface_variant=ColorPair(color=(80, 73, 69), on_color=(189, 174, 147)),
        outline=(124, 111, 100),
        inverse_surface=ColorPair(color=(235, 219, 178), on_color=(40, 40, 40)),
        inverse_primary=(131, 165, 152),
    )

    gruvbox_light = ColorTheme(
        name="Gruvbox Light",
        primary=ColorSubTheme(
            color=(7, 102, 120),
            on_color=(251, 241, 199),
            container=(211, 222, 194),
            on_container=(40, 40, 40),
        ),
        secondary=ColorSubTheme(
            color=(181, 118, 20),
            on_color=(251, 241, 199),
            container=(254, 225, 168),
            on_container=(40, 40, 40),
        ),
        tertiary=ColorSubTheme(
            color=(143, 63, 113),
            on_color=(251, 241, 199),
            container=(241, 203, 216),
            on_container=(40, 40, 40),
        ),
        error=ColorSubTheme(
            color=(157, 0, 6),
            on_color=(251, 241, 199),
            container=(252, 195, 193),
            on_container=(40, 40, 40),
        ),
        background=ColorPair(color=(251, 241, 199), on_color=(60, 56, 54)),
        surface=ColorPair(color=(235, 219, 178), on_color=(60, 56, 54)),
        surface_variant=ColorPair(color=(213, 196, 161), on_color=(60, 56, 54)),
        outline=(168, 153, 132),
        inverse_surface=ColorPair(color=(60, 56, 54), on_color=(251, 241, 199)),
        inverse_primary=(7, 102, 120),
    )

    solarized_dark = ColorTheme(
        name="Solarized Dark",
        primary=ColorSubTheme(
            color=(38, 139, 210),
            on_color=(0, 43, 54),
            container=(7, 54, 66),
            on_container=(147, 161, 161),
        ),
        secondary=ColorSubTheme(
            color=(42, 161, 152),
            on_color=(0, 43, 54),
            container=(7, 54, 66),
            on_container=(131, 148, 150),
        ),
        tertiary=ColorSubTheme(
            color=(181, 137, 0),
            on_color=(0, 43, 54),
            container=(7, 54, 66),
            on_container=(147, 161, 161),
        ),
        error=ColorSubTheme(
            color=(220, 50, 47),
            on_color=(0, 43, 54),
            container=(50, 20, 20),
            on_container=(253, 246, 227),
        ),
        background=ColorPair(color=(0, 43, 54), on_color=(131, 148, 150)),
        surface=ColorPair(color=(7, 54, 66), on_color=(147, 161, 161)),
        surface_variant=ColorPair(color=(88, 110, 117), on_color=(238, 232, 213)),
        outline=(101, 123, 131),
        inverse_surface=ColorPair(color=(253, 246, 227), on_color=(0, 43, 54)),
        inverse_primary=(38, 139, 210),
    )

    ocean_light = ColorTheme(
        name="Ocean Light",
        primary=ColorSubTheme(
            color=(30, 95, 145),
            on_color=(255, 255, 255),
            container=(205, 230, 245),
            on_container=(10, 45, 75),
        ),
        secondary=ColorSubTheme(
            color=(32, 138, 122),
            on_color=(255, 255, 255),
            container=(195, 235, 225),
            on_container=(5, 55, 45),
        ),
        tertiary=ColorSubTheme(
            color=(140, 80, 25),
            on_color=(255, 255, 255),
            container=(250, 225, 195),
            on_container=(65, 30, 5),
        ),
        error=ColorSubTheme(
            color=(195, 40, 30),
            on_color=(255, 255, 255),
            container=(255, 220, 215),
            on_container=(80, 10, 5),
        ),
        background=ColorPair(color=(240, 248, 255), on_color=(30, 50, 60)),
        surface=ColorPair(color=(255, 255, 255), on_color=(30, 50, 60)),
        surface_variant=ColorPair(color=(215, 230, 240), on_color=(60, 80, 95)),
        outline=(120, 145, 160),
        inverse_surface=ColorPair(color=(30, 50, 60), on_color=(240, 248, 255)),
        inverse_primary=(80, 165, 225),
    )

    synthwave_dark = ColorTheme(
        name="Synthwave Dark",
        primary=ColorSubTheme(
            color=(255, 42, 162),
            on_color=(21, 2, 53),
            container=(99, 0, 57),
            on_container=(255, 192, 220),
        ),
        secondary=ColorSubTheme(
            color=(0, 255, 255),
            on_color=(21, 2, 53),
            container=(0, 77, 77),
            on_container=(127, 255, 212),
        ),
        tertiary=ColorSubTheme(
            color=(255, 230, 0),
            on_color=(21, 2, 53),
            container=(85, 75, 0),
            on_container=(255, 245, 180),
        ),
        error=ColorSubTheme(
            color=(255, 80, 40),
            on_color=(21, 2, 53),
            container=(120, 30, 10),
            on_container=(255, 210, 200),
        ),
        background=ColorPair(color=(21, 2, 53), on_color=(230, 230, 250)),
        surface=ColorPair(color=(36, 17, 68), on_color=(230, 230, 250)),
        surface_variant=ColorPair(color=(72, 61, 139), on_color=(216, 191, 216)),
        outline=(106, 90, 205),
        inverse_surface=ColorPair(color=(230, 230, 250), on_color=(21, 2, 53)),
        inverse_primary=(255, 0, 255),
    )

    neon_cyber_dark = ColorTheme(
        name="Neon Cyber Dark",
        primary=ColorSubTheme(
            color=(191, 0, 255),
            on_color=(255, 255, 255),
            container=(70, 0, 110),
            on_container=(235, 180, 255),
        ),
        secondary=ColorSubTheme(
            color=(0, 240, 255),
            on_color=(12, 12, 12),
            container=(0, 70, 90),
            on_container=(170, 245, 255),
        ),
        tertiary=ColorSubTheme(
            color=(255, 0, 180),
            on_color=(12, 12, 12),
            container=(80, 0, 50),
            on_container=(255, 190, 230),
        ),
        error=ColorSubTheme(
            color=(255, 50, 70),
            on_color=(12, 12, 12),
            container=(90, 15, 25),
            on_container=(255, 190, 195),
        ),
        background=ColorPair(color=(12, 12, 12), on_color=(235, 235, 245)),
        surface=ColorPair(color=(25, 25, 30), on_color=(235, 235, 245)),
        surface_variant=ColorPair(color=(45, 45, 55), on_color=(200, 200, 220)),
        outline=(90, 80, 130),
        inverse_surface=ColorPair(color=(235, 235, 245), on_color=(12, 12, 12)),
        inverse_primary=(191, 0, 255),
    )
