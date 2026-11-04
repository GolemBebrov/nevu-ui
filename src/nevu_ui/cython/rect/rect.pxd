from nevu_ui.cython.vector2.vector2 cimport Vector2, nv_vector2_t

cdef class Rect:
    cdef public float x
    cdef public float y
    cdef public float w
    cdef public float h

    @staticmethod
    cdef Rect new(float x, float y, float w, float h)

    cdef Rect _add(self, Rect other)
    cdef Rect _sub(self, Rect other)
    cdef Rect _mul_scalar(self, float val)
    cdef Rect _mul_rect(self, Rect other)
    cdef Rect _iadd(self, Rect other)
    cdef Rect _isub(self, Rect other)
    cdef Rect _imul(self, Rect other)
    cpdef Rect union(self, Rect other)
    @staticmethod
    cdef Rect from_nvvector(Vector2 pos, Vector2 size)
    @staticmethod
    cdef Rect from_nv_vector_t(nv_vector2_t pos, nv_vector2_t size)
    cpdef bint collide_rect(self, Rect other)
