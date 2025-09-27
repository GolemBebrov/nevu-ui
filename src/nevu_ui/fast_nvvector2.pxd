# cython: language_level=3

from libc.math cimport sqrt
import pygame

cdef class NvVector2:
    cdef public float x
    cdef public float y
    cdef NvVector2 _add(self, NvVector2 other)
    cdef NvVector2 _sub(self, NvVector2 other)
    cdef NvVector2 _mul_scalar(self, float val)
    cdef NvVector2 _mul_vector(self, NvVector2 other)
    cdef NvVector2 _iadd(self, NvVector2 other)
    cdef NvVector2 _isub(self, NvVector2 other)
    cdef NvVector2 _imul(self, NvVector2 other)