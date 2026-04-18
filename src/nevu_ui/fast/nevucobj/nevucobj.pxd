# distutils: language = c++
# cython: language_level=3
# cython: boundscheck=False
# cython: wraparound=False
# cython: cdivision=True
# cython: nonecheck=False
# cython: initializedcheck=False

from nevu_ui.fast.nvvector2.nvvector2 cimport NvVector2
from libcpp.vector cimport vector
from nevu_ui.fast.nvparam.nvparam cimport NvParam
from nevu_ui.fast.nvrect.nvrect cimport NvRect
from nevu_ui.fast.nevucache.nevucache cimport Cache

cdef class NevuCobject:
    cdef public bint _sended_z_link, _dragging, _is_kup, _kup_abandoned, _force_state_set_continue, _visible, _active, _changed, _first_update, _wait_mode, _dead, booted
    cdef public NvVector2 coordinates, absolute_coordinates, size, _resize_ratio
    cdef public object _style, animation_manager
    cdef public list[NvParam] params
    cdef public dict _params_map 
    cdef public Cache cache
    cdef list specific_cache_whitelist
    cpdef list _get_param_names(self)
    cpdef object _find_param(self, str name)
    cpdef void _add_param(self, str name, supported_classes, default, getter, setter, int layer)
    cpdef NvParam get_param_strict(self, str name)
    cpdef NvParam get_param(self, str name)
    cpdef object get_param_value(self, str name)
    cpdef void set_param_value(self, str name, object new_value)
    cpdef double relx_custom(self, double num, double min, double max)
    cpdef double rely_custom(self, double num, double min, double max)
    cpdef double relm_custom(self, double num, double min, double max)
    cpdef double relx(self, double num)
    cpdef double rely(self, double num)
    cpdef double relm(self, double num)
    cpdef NvVector2 rel(self, NvVector2 vec)
    cpdef NvRect get_nvrect(self)
    cpdef set_coordinates(self, NvVector2 coordinates)
    cpdef void clear_all(self)
    cpdef void clear_surfaces(self)