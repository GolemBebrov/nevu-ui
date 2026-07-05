from typing import TYPE_CHECKING

import nevu_ui.core.modules as md
from nevu_ui.core.state import nevu_state


def _load_font_with_cyrillic(name, size):
    codepoints = list(range(32, 127)) + list(range(1024, 1104)) + [1025, 1105]
    glyph_count = len(codepoints)
    c_array = md.rl.ffi.new("int[]", codepoints)
    c_ptr = md.rl.ffi.cast("int *", c_array)
    return md.rl.load_font_ex(name, round(size), c_ptr, glyph_count)


def load_font(name, size):
    if nevu_state.window.renderer_type.raylib:
        return _load_font_with_cyrillic(name, size * 1.25)
    return md.pygame.Font(name, size)
