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

cdef class NevuCobject:
    cdef public bint _sended_z_link, _dragging, _is_kup, _kup_abandoned, _force_state_set_continue, _visible, _active, _changed, _first_update, _wait_mode, _dead, booted,
    cdef public NvVector2 coordinates, absolute_coordinates, size, _resize_ratio
    cdef public object _style, animation_manager
    cdef public list[NvParam] params
    cdef public dict _params_map 
    cpdef list _get_param_names(self)
    cpdef object _find_param(self, str name)
    cpdef void _add_param(self, str name, supported_classes, default, getter, setter, int layer)
    cpdef NvParam get_param_strict(self, str name)
    cpdef NvParam get_param(self, str name)
    cpdef object get_param_value(self, str name)
    cpdef void set_param_value(self, str name, object new_value)
    cpdef float relx_custom(self, float num, float min, float max)
    cpdef float rely_custom(self, float num, float min, float max)
    cpdef float relm_custom(self, float num, float min, float max)
    cpdef float relx(self, float num)
    cpdef float rely(self, float num)
    cpdef float relm(self, float num)
    cpdef NvVector2 rel(self, NvVector2 vec)
    cpdef NvRect get_nvrect(self)
    cpdef set_coordinates(self, NvVector2 coordinates)