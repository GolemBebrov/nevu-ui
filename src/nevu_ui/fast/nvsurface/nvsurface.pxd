cimport cython
from libc.stdint cimport uint16_t, uint8_t
from nevu_ui.fast.nvvector2.nvvector2 cimport NvVector2
from nevu_ui.fast.raylib.nevu_raylib cimport RenderTexture2D, Texture2D

cdef class _NvSurfBase:
    cdef uint16_t _width
    cdef uint16_t _height
    cdef object _native
    cdef bint _loaded

    cdef void on_begin(self)
    cdef void on_end(self)
    cpdef void blit(self, object source, dest: Annotations.dest_like_v)
    cpdef void clear(self, object color)
    cpdef void fill(self, object color)
    cpdef void kill(self)
    cpdef NvVector2 get_size(self)
    cpdef int get_width(self)
    cpdef int get_height(self)

cdef class _NvSurfRaylib(_NvSurfBase):
    cdef RenderTexture2D c_native
    cdef public Texture2D c_native_texture

@cython.final
cdef class _NvSurfPygame(_NvSurfBase):
    cdef bint _use_pure_copy
    cdef uint8_t* _pixels_ptr
    cdef int _pitch

    cdef void _fast_zero_clear(self) noexcept nogil
    cdef void c_blit_fast(self, _NvSurfPygame src, int dx, int dy) noexcept
