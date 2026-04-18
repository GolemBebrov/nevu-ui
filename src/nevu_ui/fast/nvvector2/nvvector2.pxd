cdef class NvVector2:
    cdef public double x
    cdef public double y
    
    @staticmethod
    cdef inline NvVector2 new(double x, double y)

    @staticmethod
    cdef inline NvVector2 cfrom_list(list other)
    
    @staticmethod
    cdef inline NvVector2 cfrom_ints(int x, int y)
    
    @staticmethod
    cdef inline NvVector2 cfrom_floats(float x, float y)
    
    @staticmethod
    cdef inline NvVector2 cfrom_tuple(tuple other)
    
    @staticmethod
    cdef inline NvVector2 cfrom_nvvector2(NvVector2 other)
    
    @staticmethod
    cdef inline NvVector2 cfrom_xy(double x, double y)

    cdef NvVector2 _add(self, NvVector2 other)
    cdef NvVector2 _sub(self, NvVector2 other)
    cdef NvVector2 _mul_scalar(self, double val)
    cdef NvVector2 _mul_vector(self, NvVector2 other)
    cdef void _iadd(self, NvVector2 other) nogil
    cdef void _isub(self, NvVector2 other) nogil
    cdef void _imul(self, NvVector2 other) nogil 
    cdef void _sadd(self, NvVector2 new_vec, NvVector2 old_vec) nogil
    cpdef NvVector2 copy(self)
    cpdef void sadd(self, NvVector2 new_vec, NvVector2 old_vec)
