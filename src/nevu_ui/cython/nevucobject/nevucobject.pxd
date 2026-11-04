# distutils: language = c++
# cython: language_level=3
# cython: boundscheck=False
# cython: wraparound=False
# cython: cdivision=True
# cython: nonecheck=False
# cython: initializedcheck=False

from nevu_ui.cython.vector2.vector2 cimport Vector2
from nevu_ui.cython.surface.surface cimport _NvSurfBase
from libcpp.vector cimport vector
from nevu_ui.cython.nvparam.nvparam cimport NvParam
from nevu_ui.cython.rect.rect cimport Rect
from nevu_ui.cython.cache.cache cimport Cache
from nevu_ui.cython.z_system.z_system cimport ZRequest
from libc.stdint cimport uint8_t

cdef class NevuCobject:
    cdef public bint _sended_z_link, _dragging, _is_kup, _kup_abandoned, _force_state_set_continue, _visible, _active, _changed, _first_update, _wait_mode, _dead, booted, _inner_active
    cdef public Vector2 coordinates, absolute_coordinates, size, _resize_ratio,
    cdef public object _style, hover_state
    cdef public object _system_callbacks # type: Callbacks
    cdef public list params, _blacklisted_params, _next_frame_functions
    cdef public unsigned short node_type #1 - layout, 0 - widget
    cdef public dict _params_map, _param_links
    cdef public Cache cache
    cdef public long long _update_stamp
    cdef public bint _has_position_anim
    cdef public _NvSurfBase surface
    cdef uint8_t _custom_flags
    cdef public ZRequest _z_request
    cdef list specific_cache_whitelist
    cpdef void _set_node_type(self, short node_type)
    cpdef list _get_param_names(self)
    cpdef NvParam _find_param(self, str name)
    cpdef void _add_param(self, str name, supported_classes, default, getter, setter, int layer)
    cpdef NvParam get_param_strict(self, str name)
    cpdef NvParam get_param(self, str name)
    cpdef object get_param_value(self, str name)
    cpdef void set_param_value(self, str name, object new_value)
    cpdef double relx_custom(self, double num, double min, double max)
    cpdef double rely_custom(self, double num, double min, double max)
    cpdef double relm_custom(self, double num, double min, double max)
    cpdef void _draw_start(self)
    cpdef void _draw_main(self)
    cpdef void _draw_end(self)
    cpdef void _update_start(self)
    cpdef void _update_main(self)
    cpdef void _update_end(self)
    cpdef double relx(self, double num)
    cpdef double rely(self, double num)
    cpdef void set_hover_state(self, value)
    cpdef double relm(self, double num)
    cpdef Vector2 rel(self, Vector2 vec)
    cpdef Rect get_rect(self)
    cpdef void set_coordinates(self, Vector2 coordinates)
    cpdef void clear_all(self)
    cdef inline void c_set_coords_xy(self, double x, double y) noexcept
    cpdef void clear_surfaces(self)
    cdef inline Vector2 c_get_actual_size(self)
    cpdef void update(self)
    cpdef void _click(self)
    cpdef void draw(self)
    cpdef void _unhover(self)
    cpdef void _hover(self)
    cpdef void _kup(self)
    cpdef void _kup_abandon(self)
    cdef inline void _c_run_callbacks(self, bind_type, args = None)
    cdef inline void _update_core(self)
    cdef inline void _update_core_end(self)
