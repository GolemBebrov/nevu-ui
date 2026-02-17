# distutils: language = c++


cdef class NvParam:
    cdef public str name
    cdef public int layer
    cdef public object value, default, getter, setter, type
    
    @staticmethod
    cdef NvParam new(str name, int layer, object value, object default, object type, object getter, object setter)
    cpdef bint check(self, value)
    cpdef void reset(self)
    cpdef void set(self, value)
    cpdef object get(self)