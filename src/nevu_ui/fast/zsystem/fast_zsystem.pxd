cimport numpy as np
from nevu_ui.fast.nvvector2.nvvector2 cimport NvVector2
from nevu_ui.fast.nevucobj.nevucobj cimport NevuCobject

cdef class ZRequest:
    @staticmethod
    cdef ZRequest new(link, 
                  on_hover_func, on_unhover_func, on_click_func, 
                  on_keyup_func, on_keyup_abandon_func, on_scroll_func)
    cdef object _link_ref
    cdef public object on_hover_func
    cdef public object on_unhover_func
    cdef public object on_click_func
    cdef public object on_scroll_func
    cdef public object on_keyup_func
    cdef public object on_keyup_abandon_func
    cdef object __weakref__
    cdef object get_link(self)

cdef class ZSystem:
    cdef list _registered_requests
    cdef public object last_hovered_request
    cdef public object clicked_request  
    cdef public list live_requests
    cdef public bint is_dirty

    cdef np.ndarray rects_data
    cdef np.ndarray z_indices
    cdef int[:, ::1] rects_view
    cdef int[::1] z_view

    cdef void c_mark_dirty(self) nogil
    cdef void _reset_arrays(self)
    cpdef void add(self, ZRequest z_request)
    cdef void _rebuild_arrays(self)
    cpdef mark_dirty(self)
    cpdef list get_active_requests(self)
    cpdef cycle(self, NvVector2 mouse_pos, bint mouse_down, bint mouse_up, bint any_wheel, bint wheel_down)
    cdef ZRequest request_cycle(self, NvVector2 mouse_pos, bint any_wheel, bint wheel_down)