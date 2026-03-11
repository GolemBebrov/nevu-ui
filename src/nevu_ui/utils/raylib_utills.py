import pyray as rl
import pygame
from nevu_ui.core.state import nevu_state
def load_image_texture(path: str, manipulation_func = None) -> rl.Texture:
    image = rl.load_image(path)
    if manipulation_func:
        manipulation_func(image)
    texture = rl.load_texture_from_image(image)
    rl.unload_image(image)
    return texture

def load_image(path: str, manipulation_func = None) -> rl.Image:
    image = rl.load_image(path)
    if manipulation_func:
        manipulation_func(image)
    return image

def _load_font_with_cyrillic(name, size):
    codepoints = list(range(32, 127)) + list(range(1024, 1104)) + [1025, 1105]
    glyph_count = len(codepoints)
    c_array = rl.ffi.new("int[]", codepoints)
    c_ptr = rl.ffi.cast("int *", c_array)
    return rl.load_font_ex(name, round(size), c_ptr, glyph_count)

def load_font(name, size):
    if nevu_state.window.is_dtype.raylib:
        return _load_font_with_cyrillic(name, size*1.25)
    return pygame.Font(name, size)