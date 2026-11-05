# distutils: language = c++
from libc.stdint cimport uint8_t


cdef enum ParamFlag:
    ParamFlagGetter = 1 << 0
    ParamFlagSetter = 1 << 1


cdef class Param:
    cdef public str name
    cdef public int layer
    cdef public object value, default, getter, setter, type
    cdef public uint8_t flags

    @staticmethod
    cdef Param new(str name, int layer, object value, object default, object type, object getter, object setter)
    cpdef bool check(self, value)
    cpdef void reset(self)
    cpdef void set(self, value)
    cpdef object get(self)
    cdef inline str _get_cool_error_message(self)
