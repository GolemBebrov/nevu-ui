# distutils: language = c++
from libc.stdint cimport uint8_t

cdef enum NvParamFlag:
    NvParamFlagGetter = 1 << 0
    NvParamFlagSetter = 1 << 1

cdef class NvParam:
    cdef public str name
    cdef public int layer
    cdef public object value, default, getter, setter, type
    cdef public uint8_t flags

    @staticmethod
    cdef NvParam new(str name, int layer, object value, object default, object type, object getter, object setter)
    cpdef bool check(self, value)
    cpdef void reset(self)
    cpdef void set(self, value)
    cpdef object get(self)
    cdef inline str _get_cool_error_message(self)
