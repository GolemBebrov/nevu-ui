# cython: language_level=3
# cython: boundscheck=False
# cython: wraparound=False
# cython: cdivision=True
# cython: initializedcheck=False
# cython: nonecheck=False

from __future__ import annotations
cimport cython

import nevu_ui.core.modules as md
from nevu_ui.assets.base_font import FontLibrary
from nevu_ui.core.annotations import Annotations
from nevu_ui.core.state import nevu_state
from nevu_ui.presentation.color import Color

from nevu_ui.fast.nvvector2.nvvector2 cimport NvVector2
from nevu_ui.fast.nvsurface.nvsurface cimport _NvSurfBase, _NvSurfPygame, _NvSurfRaylib

__pos_default = NvVector2.new(0, 0)


cdef object _pg_Font = None

cdef inline tuple _to_color_tuple(color):
    return tuple(color)


cdef inline object _get_pg_font_cls():
    global _pg_Font
    if _pg_Font is None:
        if md.pygame is None:
            raise RuntimeError("pygame module is not initialized")
        pg_font = getattr(md.pygame, "font", None)
        if pg_font is None:
            import pygame.font as pg_font
        if not pg_font.get_init():
            pg_font.init()
        _pg_Font = pg_font.Font
    return _pg_Font


cdef class _NvFontBase:
    def __init__(self, int size, str path = FontLibrary.InterRegular):
        raise NotImplementedError()

    @property
    def size(self) -> int: return self.get_size()

    @property
    def native(self): return self._native

    @property
    def loaded(self) -> bool: return self._loaded

    def __repr__(self) -> str:
        return f"NvFont<{self._size}>"

    def __str__(self) -> str:
        return self.__repr__()

    cpdef void kill(self):
        raise NotImplementedError()

    cpdef NvVector2 measure(self, str text):
        raise NotImplementedError()

    cpdef void render(
        self,
        str text,
        _NvSurfBase surface_like = None,
        NvVector2 pos = __pos_default,
        tuple color = Color.White,
    ):
        raise NotImplementedError()

    cpdef _NvSurfBase get_rendered(self, str text, tuple color = Color.White):
        raise NotImplementedError()

    cdef inline int get_size(self): return self._size

    cdef inline void _check_loaded(self) except *:
        if not self._loaded:
            raise RuntimeError("Font is killed")


cdef class _NvFontRaylib(_NvFontBase):
    def __init__(self, int size, str path = FontLibrary.InterRegular):
        Annotations.window_check()
        if md.rl is None:
            raise RuntimeError("raylib module is not initialized")
        if size <= 0:
            raise ValueError(f"Font size must be positive, got {size}")

        cdef list codepoints = list(range(32, 127)) + list(range(1024, 1104)) + [1025, 1105]
        cdef int glyph_count = len(codepoints)
        cdef object c_array = md.rl.ffi.new("int[]", codepoints)
        cdef object c_ptr = md.rl.ffi.cast("int *", c_array)

        self._native = md.rl.load_font_ex(path, size, c_ptr, glyph_count)
        if self._native.glyphCount == 0:
            raise ValueError(f"Font {path} not found")

        self._size = size
        self._loaded = True

    cpdef void kill(self):
        if self._loaded:
            md.rl.unload_font(self._native)
            self._loaded = False

    def __dealloc__(self):
        if self._loaded:
            if md.rl is not None and md.rl.is_window_ready():
                md.rl.unload_font(self._native)
            self._loaded = False

    cpdef NvVector2 measure(self, str text):
        self._check_loaded()
        cdef object result = md.rl.measure_text_ex(self._native, text, <float>self._size, 0)
        return NvVector2.cfrom_xy(result.x, result.y)

    cpdef void render(
        self,
        str text,
        _NvSurfBase surface_like = None,
        NvVector2 pos = __pos_default,
        tuple color = Color.White,
    ):
        self._check_loaded()

        if surface_like is None:
            md.rl.draw_text_ex(
                self._native, text,
                (round(pos.data.x), round(pos.data.y)),
                <float>self._size, 0, _to_color_tuple(color),
            )
            return

        cdef _NvSurfBase rendered = None
        try:
            rendered = self.get_rendered(text, color)
        except RuntimeError as e:
            raise RuntimeError(
                "render() failed: an active NvSurface context blocks offscreen text rendering. "
                "To draw into the currently active surface, call "
                "render(text, None, pos, color) inside the 'with surface:' block."
            ) from e
        surface_like.blit(rendered, (pos.data.x, pos.data.y))

    cpdef _NvSurfBase get_rendered(self, str text, tuple color = Color.White):
        self._check_loaded()

        cdef NvVector2 text_size = self.measure(text)
        cdef int w = <int>text_size.x + 1
        cdef int h = <int>text_size.y + 1
        if w < 1: w = 1
        if h < 1: h = 1

        cdef _NvSurfRaylib surface = _NvSurfRaylib((w, h))
        surface.clear(Color.Blank)

        cdef tuple color_tuple = _to_color_tuple(color)
        if len(color_tuple) == 3:
            color_tuple = (*color_tuple, 255)

        with surface:
            md.rl.draw_text_ex(self._native, text, (0, 0), <float>self._size, 0, color_tuple)
        return surface


cdef class _NvFontPygame(_NvFontBase):
    def __init__(self, int size, str path = FontLibrary.InterRegular):
        cdef object font_cls = _get_pg_font_cls()
        if size <= 0:
            raise ValueError(f"Font size must be positive, got {size}")

        self._native = font_cls(path, size)
        self._size = size
        self._loaded = True

    cpdef void kill(self):
        self._loaded = False
        self._native = None

    cpdef NvVector2 measure(self, str text):
        self._check_loaded()

        cdef list lines = text.split("\n")
        if len(lines) > 1:
            max_w = 0
            for line in lines:
                line_w = self._native.size(line)[0]
                if line_w > max_w:
                    max_w = line_w
            total_h = len(lines) * self._native.get_linesize()
            return NvVector2.cfrom_xy(max_w, total_h)

        cdef tuple result = self._native.size(text)
        return NvVector2.cfrom_ints(result[0], result[1])

    cpdef void render(
        self,
        str text,
        _NvSurfBase surface_like = None,
        NvVector2 pos = __pos_default,
        tuple color = Color.White,
    ):
        self._check_loaded()

        if surface_like is None:
            raise TypeError(
                "render() target surface must be a NvSurface for the pygame backend, not None"
            )

        cdef object rendered = self._native.render(text, True, color)
        try:
            rendered = rendered.convert_alpha()
        except Exception:
            pass

        cdef int w = rendered.get_width()
        cdef int h = rendered.get_height()
        if w > 0 and h > 0:
            surface_like.blit(rendered, (pos.data.x, pos.data.y))

    cpdef _NvSurfBase get_rendered(self, str text, tuple color = Color.White):
        self._check_loaded()

        cdef object rendered = self._native.render(text, True, color)
        cdef int w = rendered.get_width()
        cdef int h = rendered.get_height()

        cdef int sw = w if w > 1 else 1
        cdef int sh = h if h > 1 else 1

        cdef _NvSurfPygame surface = _NvSurfPygame((sw, sh))
        if w > 0 and h > 0:
            surface.blit(rendered, (0, 0))
        return surface


class _NvFontMeta(type):
    def __instancecheck__(cls, instance):
        return isinstance(instance, _NvFontBase)


class NvFont(_NvFontBase, metaclass=_NvFontMeta):
    def __new__(cls, *args, **kwargs):
        Annotations.window_check()
        rtype = nevu_state.window.renderer_type

        if rtype.raylib:
            return _NvFontRaylib(*args, **kwargs)
        if rtype.pygame_like:
            return _NvFontPygame(*args, **kwargs)
        raise RuntimeError(
            f"NvFont does not support backend '{nevu_state.window.backend}' >:() <- this is your face when you saw this."
        )
