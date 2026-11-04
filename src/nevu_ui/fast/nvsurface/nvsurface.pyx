# cython: language_level=3
# cython: boundscheck=False
# cython: wraparound=False
# cython: cdivision=True
# cython: initializedcheck=False
# cython: nonecheck=False

from __future__ import annotations

cimport cython
from typing import Any
from libc.stdint cimport uint16_t, uint32_t, uint8_t, uintptr_t, uint64_t
from libc.string cimport memcpy, memset
from cpython.object cimport PyObject
import numpy as np
import nevu_ui.core.modules as md
from nevu_ui.core.annotations import Annotations
from nevu_ui.fast.nvvector2.nvvector2 cimport NvVector2, nv_vector2_t, nv_vector2_new
from nevu_ui.core.state import nevu_state
from nevu_ui.presentation.color import Color
from nevu_ui.fast.raylib.nevu_raylib cimport (
    RenderTexture2D,
    Texture2D,
    c_clear_background,
    c_draw_texture_pro,
    c_draw_texture_vec,
    begin_texture_mode_raw,
    end_texture_mode,
    get_c_render_texture,
    get_c_texture,
    begin_blend_mode,
    c_draw_texture_maxopt,
    end_blend_mode
)

cdef extern from *:
    """
    #include <Python.h>
    typedef struct {
        PyObject_HEAD
        void *c_type;
        void *c_data;
    } FastCData;
    """
    ctypedef struct FastCData:
        void *c_type
        void *c_data

cdef object _TYPE_RENDER_TEXTURE = None
cdef object _TYPE_TEXTURE = None
cdef void* _PTR_RENDER_TEXTURE = NULL
cdef void* _PTR_TEXTURE = NULL
cdef object _CDATA_BASE = None
cdef bint _rl_types_inited = False

cdef inline bint _ensure_rl_types() noexcept:
    global _TYPE_RENDER_TEXTURE, _TYPE_TEXTURE, _PTR_RENDER_TEXTURE, _PTR_TEXTURE, _CDATA_BASE, _rl_types_inited
    if _rl_types_inited:
        return True
    if md.rl is None:
        return False
    try:
        ffi = md.rl.ffi
        _CDATA_BASE = ffi.CData
        _TYPE_RENDER_TEXTURE = ffi.typeof("RenderTexture")
        _TYPE_TEXTURE = ffi.typeof("Texture")
        _PTR_RENDER_TEXTURE = <void*><PyObject*>_TYPE_RENDER_TEXTURE
        _PTR_TEXTURE = <void*><PyObject*>_TYPE_TEXTURE
        _rl_types_inited = True
        return True
    except Exception:
        return False

cdef object _pg_Surface = None
cdef int _SRCALPHA = 0

cdef inline object _get_pg_surface_cls():
    global _pg_Surface, _SRCALPHA
    if _pg_Surface is None:
        if md.pygame is not None:
            _pg_Surface = md.pygame.Surface
            _SRCALPHA = <int>md.pygame.SRCALPHA
    return _pg_Surface

cdef _NvSurfBase _active_context = None

cdef inline bint is_context_active(_NvSurfBase item) noexcept:
    return _active_context is item

cdef inline bint is_other_context_active(_NvSurfBase item) noexcept:
    return _active_context is not None and not (_active_context is item)

cdef inline tuple _to_color_tuple(color):
    return tuple(color)

cdef inline void _c_raw_blit(uint8_t *dst_base, int dst_pitch, int dw, int dh,
                             const uint8_t *src_base, int src_pitch, int sw, int sh,
                             int dx, int dy) noexcept nogil:
    cdef int sx = 0
    cdef int sy = 0

    if dx < 0:
        sx = -dx
        sw += dx
        dx = 0
    if dy < 0:
        sy = -dy
        sh += dy
        dy = 0

    if dx + sw > dw:
        sw = dw - dx
    if dy + sh > dh:
        sh = dh - dy

    if sw <= 0 or sh <= 0:
        return

    cdef const uint8_t *src_p = src_base + sy * src_pitch + (sx << 2)
    cdef uint8_t *dst_p = dst_base + dy * dst_pitch + (dx << 2)
    cdef size_t row_bytes = <size_t>(sw << 2)

    if dx == 0 and sx == 0 and sw == dw and <size_t>src_pitch == row_bytes and <size_t>dst_pitch == row_bytes:
        memcpy(dst_p, src_p, <size_t>sh * row_bytes)
        return

    cdef int y
    if sw == 1:
        for y in range(sh):
            (<uint32_t*>dst_p)[0] = (<const uint32_t*>src_p)[0]
            src_p += src_pitch
            dst_p += dst_pitch
        return
    elif sw == 2:
        for y in range(sh):
            (<uint64_t*>dst_p)[0] = (<const uint64_t*>src_p)[0]
            src_p += src_pitch
            dst_p += dst_pitch
        return

    for y in range(sh):
        memcpy(dst_p, src_p, row_bytes)
        src_p += src_pitch
        dst_p += dst_pitch


cdef class _NvSurfBase:
    cdef void on_begin(self): ...
    cdef void on_end(self): ...

    def __init__(self, size: Annotations.dest_like_v):
        raise NotImplementedError

    def __enter__(self) -> _NvSurfBase:
        global _active_context
        if _active_context is not None:
            raise RuntimeError("Cannot nest surface contexts")
        if not self._loaded:
            raise RuntimeError("Surface is killed")
        _active_context = self
        self.on_begin()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        global _active_context
        _active_context = None
        self.on_end()

    cpdef void blit(self, object source, dest: Annotations.dest_like_v):
        raise NotImplementedError

    cpdef void clear(self, object color):
        raise NotImplementedError

    cpdef void fill(self, object color):
        self.clear(color)

    cpdef void kill(self):
        pass

    cpdef NvVector2 get_size(self):
        return NvVector2.cfrom_xy(self._width, self._height)

    cpdef int get_width(self): return self._width
    cpdef int get_height(self): return self._height

    @property
    def size(self) -> NvVector2:
        return NvVector2.cfrom_xy(self._width, self._height)

    @property
    def width(self) -> int: return self._width
    @property
    def height(self) -> int: return self._height

    @property
    def native(self) -> Any:
        return self._native

    @property
    def loaded(self) -> bool:
        return self._loaded

    def copy(self):
        raise NotImplementedError

    def __repr__(self) -> str:
        return f"NvSurface<{self.width}x{self.height}>"

    def __str__(self) -> str:
        return self.__repr__()


cdef class _NvSurfRaylib(_NvSurfBase):
    cdef void on_begin(self):
        begin_texture_mode_raw(self.c_native)

    cdef void on_end(self):
        end_texture_mode()

    cpdef void clear(self, object color):
        cdef bint ctx_active = is_context_active(self)
        if is_other_context_active(self):
            raise RuntimeError("Cannot clear surface: another NvSurface context is active")
        if not ctx_active:
            self.on_begin()
        c_clear_background(_to_color_tuple(color))
        if not ctx_active:
            self.on_end()

    cpdef void blit(self, object source, dest: Annotations.dest_like_v):
        if source is None:
            raise TypeError("blit() source must be a NvSurface, not None")

        cdef bint ctx_active = is_context_active(self)
        if is_other_context_active(self):
            raise RuntimeError("Cannot blit onto surface: another NvSurface context is active")
        if not ctx_active:
            self.on_begin()

        cdef nv_vector2_t nv_vec_dest
        if type(dest) is NvVector2:
            nv_vec_dest = (<NvVector2>dest).data
        elif type(dest) is tuple:
            nv_vec_dest = nv_vector2_new((<tuple>dest)[0], (<tuple>dest)[1])
        else:
            nv_vec_dest = nv_vector2_new(dest[0], dest[1])

        cdef void* ctype_ptr

        if type(source) is _NvSurfRaylib:
            c_draw_texture_maxopt((<_NvSurfRaylib>source).c_native_texture, nv_vec_dest, True)
        elif _ensure_rl_types() and isinstance(source, _CDATA_BASE):
            ctype_ptr = (<FastCData*>source).c_type
            if ctype_ptr == _PTR_RENDER_TEXTURE:
                c_draw_texture_maxopt(<Texture2D>(get_c_texture(source.texture)), nv_vec_dest, True)
            elif ctype_ptr == _PTR_TEXTURE:
                c_draw_texture_maxopt(<Texture2D>(get_c_texture(source)), nv_vec_dest, True)
            else:
                if not ctx_active:
                    self.on_end()
                raise TypeError(
                    f"Cannot blit {type(source).__name__} onto raylib NvSurface, "
                    f"source must be a raylib NvSurface, pyray RenderTexture, or pyray Texture"
                )
        else:
            if not ctx_active:
                self.on_end()
            raise TypeError(
                f"Cannot blit {type(source).__name__} onto raylib NvSurface, "
                f"source must be a raylib NvSurface, pyray RenderTexture, or pyray Texture"
            )

        if not ctx_active:
            self.on_end()

    def __init__(self, size: Annotations.dest_like_v):
        global _TYPE_RENDER_TEXTURE, _TYPE_TEXTURE, _PTR_RENDER_TEXTURE, _PTR_TEXTURE, _CDATA_BASE, _rl_types_inited
        Annotations.window_check()
        _ensure_rl_types()
        self._native = md.rl.load_render_texture(int(size[0]), int(size[1]))

        if _PTR_RENDER_TEXTURE == NULL:
            _TYPE_RENDER_TEXTURE = md.rl.ffi.typeof(self._native)
            _TYPE_TEXTURE = md.rl.ffi.typeof(self._native.texture)
            _PTR_RENDER_TEXTURE = <void*><PyObject*>_TYPE_RENDER_TEXTURE
            _PTR_TEXTURE = <void*><PyObject*>_TYPE_TEXTURE
            _CDATA_BASE = md.rl.ffi.CData
            _rl_types_inited = True

        self.c_native = get_c_render_texture(self._native)
        self.c_native_texture = get_c_texture(self._native.texture)
        self._width = <uint16_t>self.c_native.texture.width
        self._height = <uint16_t>self.c_native.texture.height
        self._loaded = True

    cpdef void kill(self):
        if self._loaded:
            md.rl.unload_render_texture(self._native)
            self._loaded = False

    def copy(self):
        cdef _NvSurfRaylib new_surf
        if not self._loaded:
            raise RuntimeError("Surface is killed")
        new_surf = _NvSurfRaylib((self._width, self._height))
        new_surf.clear(Color.Blank)
        begin_blend_mode(md.rl.BlendMode.BLEND_ALPHA)
        new_surf.blit(self, (0, 0))
        end_blend_mode()
        return new_surf

    def __dealloc__(self):
        if self._loaded:
            if md.rl is not None and md.rl.is_window_ready():
                md.rl.unload_render_texture(self._native)
            self._loaded = False


@cython.final
cdef class _NvSurfPygame(_NvSurfBase):
    cdef void on_begin(self): pass
    cdef void on_end(self): pass

    def __init__(self, size: Annotations.dest_like_v, bint use_pure_copy = False):
        cdef int w, h
        if type(size) is NvVector2:
            w = <int>(<NvVector2>size).x
            h = <int>(<NvVector2>size).y
        elif type(size) is tuple:
            w = <int>(<tuple>size)[0]
            h = <int>(<tuple>size)[1]
        else:
            w = <int>size[0]
            h = <int>size[1]

        cdef object surface_cls = _get_pg_surface_cls()
        if surface_cls is None:
            raise RuntimeError("pygame module is not initialized")

        self._native = surface_cls((w, h), flags=_SRCALPHA, depth=32)
        try:
            self._native = self._native.convert_alpha()
        except Exception:
            pass

        self._width = <uint16_t>w
        self._height = <uint16_t>h
        self._loaded = True
        self._use_pure_copy = use_pure_copy

        cdef object addr = getattr(self._native, "_pixels_address", None)
        if addr is not None:
            self._pixels_ptr = <uint8_t*><uintptr_t>addr
            self._pitch = self._native.get_pitch()
            self._fast_zero_clear()
        else:
            self._pixels_ptr = NULL
            self._pitch = 0
            self._native.fill((0, 0, 0, 0))

    cdef void _fast_zero_clear(self) noexcept nogil:
        if <size_t>self._pitch == (<size_t>self._width << 2):
            memset(self._pixels_ptr, 0, <size_t>self._pitch * self._height)
            return
        cdef int y
        cdef size_t row_bytes = <size_t>self._width << 2
        cdef uint8_t *ptr = self._pixels_ptr
        for y in range(self._height):
            memset(ptr, 0, row_bytes)
            ptr += self._pitch

    cpdef void clear(self, object color):
        if type(color) is tuple and len(<tuple>color) >= 4:
            if (<tuple>color)[0] == 0 and (<tuple>color)[1] == 0 and (<tuple>color)[2] == 0 and (<tuple>color)[3] == 0:
                if self._pixels_ptr != NULL:
                    with nogil:
                        self._fast_zero_clear()
                    return

        if type(color) is tuple:
            self._native.fill(color)
        else:
            self._native.fill(tuple(color))

    cpdef void blit(self, object source, dest: Annotations.dest_like_v):
        cdef _NvSurfPygame src = <_NvSurfPygame>source
        cdef int dx, dy

        if type(dest) is NvVector2:
            dx = <int>(<NvVector2>dest).x
            dy = <int>(<NvVector2>dest).y
        elif type(dest) is tuple:
            dx = <int>(<tuple>dest)[0]
            dy = <int>(<tuple>dest)[1]
        elif type(dest) is list:
            dx = <int>(<list>dest)[0]
            dy = <int>(<list>dest)[1]
        else:
            dx = <int>dest[0]
            dy = <int>dest[1]

        if type(source) is md.pygame.Surface:
            self._native.blit(source, (dx, dy))
            return
        elif type(source) is _NvSurfPygame:
            if self._use_pure_copy and self._pixels_ptr != NULL and src._pixels_ptr != NULL:
                _c_raw_blit(self._pixels_ptr, self._pitch, self._width, self._height, src._pixels_ptr, src._pitch, src._width, src._height, dx, dy)
                return

            self._native.blit(src._native, (dx, dy))
            return

        raise TypeError(
            f"Cannot blit {type(source).__name__} onto pygame NvSurface, "
            f"source must be a pygame NvSurface"
        )

    cdef void c_blit_fast(self, _NvSurfPygame src, int dx, int dy) noexcept:
        if self._use_pure_copy and self._pixels_ptr != NULL and src._pixels_ptr != NULL:
            with nogil:
                _c_raw_blit(self._pixels_ptr, self._pitch, self._width, self._height,
                            src._pixels_ptr, src._pitch, src._width, src._height,
                            dx, dy)
        else:
            self._native.blit(src._native, (dx, dy))

    cpdef void kill(self):
        self._pixels_ptr = NULL
        self._loaded = False

    def copy(self):
        cdef _NvSurfPygame new_surf = _NvSurfPygame.__new__(_NvSurfPygame)
        new_surf._native = self._native.copy()
        new_surf._width = self._width
        new_surf._height = self._height
        new_surf._loaded = True
        new_surf._use_pure_copy = self._use_pure_copy

        cdef object addr = getattr(new_surf._native, "_pixels_address", None)
        if addr is not None:
            new_surf._pixels_ptr = <uint8_t*><uintptr_t>addr
            new_surf._pitch = self._pitch
        else:
            new_surf._pixels_ptr = NULL
            new_surf._pitch = 0
        return new_surf


class _NvSurfaceMeta(type):
    def __instancecheck__(cls, instance):
        return isinstance(instance, _NvSurfBase)


class NvSurface(_NvSurfBase, metaclass=_NvSurfaceMeta):
    def __new__(cls, *args, **kwargs):
        Annotations.window_check()
        rtype = nevu_state.window.renderer_type

        if rtype.raylib:
            return _NvSurfRaylib(*args, **kwargs)
        if rtype.pygame_like:
            return _NvSurfPygame(*args, **kwargs)
        raise RuntimeError(
            f"NvSurface does not support backend '{nevu_state.window.backend}' >:() <- this is your face when you saw this."
        )
