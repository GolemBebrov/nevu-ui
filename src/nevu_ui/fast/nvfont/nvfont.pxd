cimport cython

from nevu_ui.fast.nvvector2.nvvector2 cimport NvVector2
from nevu_ui.fast.nvsurface.nvsurface cimport _NvSurfBase
from nevu_ui.presentation.color import Color

cdef NvVector2 __pos_default

cdef class _NvFontBase:
    cdef int _size
    cdef object _native
    cdef bint _loaded

    cdef inline int get_size(self)
    cdef inline void _check_loaded(self) except *
    cpdef void kill(self)
    cpdef NvVector2 measure(self, str text)
    cpdef void render(
        self,
        str text,
        _NvSurfBase surface_like = ?,
        NvVector2 pos = ?,
        tuple color = ?,
    )
    cpdef _NvSurfBase get_rendered(self, str text, tuple color = ?)

cdef class _NvFontRaylib(_NvFontBase):
    pass

cdef class _NvFontPygame(_NvFontBase):
    pass
