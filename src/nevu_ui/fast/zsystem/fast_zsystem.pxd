cimport numpy as np
from nevu_ui.fast.nvvector2.nvvector2 cimport NvVector2

cdef class ZRequest:
    cdef object _link_ref
    cdef public object on_hover_func
    cdef public object on_unhover_func
    cdef public object on_click_func
    cdef public object on_scroll_func
    cdef public object on_keyup_func
    cdef public object on_keyup_abandon_func
    cdef object __weakref__

cdef class ZSystem:
    cdef list _registered_requests
    cdef object last_hovered_request
    cdef object clicked_request  
    cdef list live_requests
    cdef bint is_dirty

    cdef np.ndarray rects_data
    cdef np.ndarray z_indices

    cdef void _reset_arrays(self)
    cpdef add(self, ZRequest z_request)
    cdef void _rebuild_arrays(self)
    cpdef mark_dirty(self)
    cpdef list get_active_requests(self)
    cpdef cycle(self, NvVector2 mouse_pos, bint mouse_down, bint mouse_up, bint any_wheel, bint wheel_down)
    cdef object request_cycle(self, NvVector2 mouse_pos, bint any_wheel, bint wheel_down, list live_requests)