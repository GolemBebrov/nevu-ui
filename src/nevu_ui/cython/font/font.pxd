cimport cython

from nevu_ui.cython.vector2.vector2 cimport Vector2
from nevu_ui.cython.surface.surface cimport _NvSurfBase
from nevu_ui.presentation.color import Color

cdef Vector2 __pos_default

cdef class _FontBase:
    cdef int _size
    cdef object _native
    cdef bint _loaded

    cdef inline int get_size(self)
    cdef inline void _check_loaded(self) except *
    cpdef void kill(self)
    cpdef Vector2 measure(self, str text)
    cpdef void render(
        self,
        str text,
        _NvSurfBase surface_like = ?,
        Vector2 pos = ?,
        tuple color = ?,
    )
    cpdef _NvSurfBase get_rendered(self, str text, tuple color = ?)

cdef class _FontRaylib(_FontBase):
    pass

cdef class _FontPygame(_FontBase):
    pass
