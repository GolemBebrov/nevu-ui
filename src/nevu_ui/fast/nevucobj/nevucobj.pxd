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
from nevu_ui.fast.zsystem.fast_zsystem cimport ZRequest
cdef class NevuCobject:
    cdef public bint _sended_z_link, _dragging, _is_kup, _kup_abandoned, _force_state_set_continue, _visible, _active, _changed, _first_update, _wait_mode, _dead, booted
    cdef public bint _custom_secondary_update, _custom_animation_update, _custom_logic_update, _custom_event_update
    cdef public bint _custom_secondary_draw, _custom_secondary_draw_content, _custom_secondary_draw_end, _custom_primary_draw
    cdef public NvVector2 coordinates, absolute_coordinates, size, _resize_ratio
    cdef public object _style, hover_state
    cdef public list params, _blacklisted_params, _next_frame_functions
    cdef public unsigned short node_type #1 - layout, 0 - widget
    cdef public dict _params_map, _param_links
    cdef public Cache cache
    cdef public bint _has_position_anim
    cdef ZRequest _z_request
    cdef list specific_cache_whitelist
    cpdef _set_node_type(self, short node_type)
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
    cdef inline void c_set_coords_xy(self, double x, double y) noexcept
    cpdef void clear_surfaces(self)
    cdef inline NvVector2 c_get_actual_size(self)
    cpdef update(self)
    cdef inline void _primary_update(self, events)
    cdef inline void _base_animation_update(self)
    cdef inline void _base_logic_update(self)


    cpdef _on_click_system(self)
    cpdef _on_hover_system(self)
    cpdef _on_keyup_system(self)
    cpdef _on_keyup_abandon_system(self)
    cpdef _on_unhover_system(self)
    cpdef _on_scroll_system(self, bint side)
    cpdef _on_change_system(self)

    cpdef _group_on_click(self)
    cpdef _group_on_hover(self)
    cpdef _group_on_keyup(self)
    cpdef _group_on_keyup_abandon(self)
    cpdef _group_on_unhover(self)
    cpdef _group_on_scroll(self, bint side)

    cpdef _click(self)
    cpdef draw(self)
    cpdef _unhover(self)
    cpdef _hover(self)
    cpdef _kup(self)
    #cpdef _scroll(self, bint scrolled)
    cpdef _kup_abandon(self)
    cdef inline void _core_event_cycle(self, object type, list content, tuple args, dict kwargs)
    cdef inline void _core_event_cycle_clear(self, object type)
   # cpdef draw(self)
    cdef inline void _base_secondary_draw_end(self)
    cdef inline void _base_secondary_draw(self)
    cdef set_hover_state(self, value)