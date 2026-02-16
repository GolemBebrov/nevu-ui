from nevu_ui.fast.nvvector2.nvvector2 cimport NvVector2

cdef class NvRect:
    cdef public float x
    cdef public float y
    cdef public float w
    cdef public float h
    
    @staticmethod
    cdef NvRect new(float x, float y, float w, float h)

    cdef NvRect _add(self, NvRect other)
    cdef NvRect _sub(self, NvRect other)
    cdef NvRect _mul_scalar(self, float val)
    cdef NvRect _mul_rect(self, NvRect other)
    cdef NvRect _iadd(self, NvRect other)
    cdef NvRect _isub(self, NvRect other)
    cdef NvRect _imul(self, NvRect other)
    cpdef NvRect union(self, NvRect other)
    @staticmethod
    cdef NvRect from_nvvector(NvVector2 pos, NvVector2 size)
    cpdef bint collide_rect(self, NvRect other)