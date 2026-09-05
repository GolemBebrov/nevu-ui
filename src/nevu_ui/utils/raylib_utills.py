import nevu_ui.core.modules as md
from nevu_ui.core.state import nevu_state


def load_font_with_cyrillic(name: str, size: float):
    codepoints = list(range(32, 127)) + list(range(1024, 1104)) + [1025, 1105]
    glyph_count = len(codepoints)
    c_array = md.rl.ffi.new("int[]", codepoints)
    c_ptr = md.rl.ffi.cast("int *", c_array)
    return md.rl.load_font_ex(name, round(size), c_ptr, glyph_count)


def load_font(name: str, size: float):
    if nevu_state.window.renderer_type.raylib:
        return load_font_with_cyrillic(name, size)
    return md.pygame.Font(name, round(size))
