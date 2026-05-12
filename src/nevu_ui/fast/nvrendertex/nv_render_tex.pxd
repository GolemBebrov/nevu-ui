from nevu_ui.fast.nvvector2.nvvector2 cimport NvVector2
from nevu_ui.fast.nvrect.nvrect cimport NvRect
from nevu_ui.presentation.color import Color
from nevu_ui.core.annotations import Annotations  

cdef class NvRenderTexture:
    cdef public object render_texture 
    cdef public NvVector2 size
    cdef public bint loaded
    cdef void c_fast_blit(self, NvRenderTexture nv_texture, tuple dest, bint flip, tuple color)
    cdef void c_fast_blit_texture(self, object texture, tuple dest, bint flip, tuple color)
    cdef void c_fast_clear(self, tuple color)
    cdef void c_clear(self, tuple color)
    cpdef void clear(self, tuple color)
    cpdef void fast_clear(self, tuple color)
    cpdef void fill(self, tuple color)
    cpdef void kill(self)
    cpdef NvRect get_rect(self)
    cpdef double get_height(self)
    cpdef double get_width(self)
    @staticmethod
    cdef NvRenderTexture new(NvVector2 size)