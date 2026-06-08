# distutils: language = c++
# cython: language_level=3
# cython: boundscheck=False
# cython: wraparound=False
# cython: cdivision=True
# cython: nonecheck=False
# cython: initializedcheck=False

import numpy as np
cimport numpy as np
cimport cython
import weakref
from nevu_ui.fast.nvvector2.nvvector2 cimport NvVector2
from nevu_ui.fast.nvrect.nvrect cimport NvRect
from nevu_ui.fast.nevucobj.nevucobj cimport NevuCobject

np.import_array()

cdef class ZRequest:
    @staticmethod
    cdef ZRequest new(link, 
                  on_hover_func, on_unhover_func, on_click_func, 
                  on_keyup_func, on_keyup_abandon_func, on_scroll_func):
        cdef ZRequest req = ZRequest.__new__(ZRequest)
        req._link_ref = weakref.ref(link)
        req.on_hover_func = on_hover_func
        req.on_unhover_func = on_unhover_func
        req.on_click_func = on_click_func
        req.on_scroll_func = on_scroll_func
        req.on_keyup_func = on_keyup_func
        req.on_keyup_abandon_func = on_keyup_abandon_func
        return req
        
    def __init__(self, link,
                 on_hover_func=None, on_unhover_func=None, on_click_func=None, 
                 on_keyup_func=None, on_keyup_abandon_func=None, on_scroll_func=None):
        self._link_ref = weakref.ref(link)
        self.on_hover_func = on_hover_func
        self.on_unhover_func = on_unhover_func
        self.on_click_func = on_click_func
        self.on_scroll_func = on_scroll_func
        self.on_keyup_func = on_keyup_func
        self.on_keyup_abandon_func = on_keyup_abandon_func

    cdef object get_link(self):
        return self._link_ref()

cdef class ZSystem:
    def __cinit__(self):
        self._registered_requests = []
        self.last_hovered_request = None
        self.clicked_request = None
        self.live_requests = []
        self.is_dirty = True  
        self._reset_arrays()

    cdef void _reset_arrays(self):
        self.rects_data = np.empty((0, 4), dtype=np.int32)
        self.z_indices = np.empty(0, dtype=np.int32)
        self.rects_view = self.rects_data
        self.z_view = self.z_indices

    cpdef void add(self, ZRequest z_request):
        self._registered_requests.append(weakref.ref(z_request))
        self.is_dirty = True
        
    cdef void _rebuild_arrays(self):
        cdef list live_requests_refs = []
        cdef list temp_live_requests = []
        
        cdef object req_ref
        cdef ZRequest req
        cdef NvRect current_rect
        cdef NevuCobject current_link
        
        cdef Py_ssize_t max_len = len(self._registered_requests)
        cdef np.ndarray[np.int32_t, ndim=2] new_rects = np.empty((max_len, 4), dtype=np.int32)
        cdef np.ndarray[np.int32_t, ndim=1] new_zs = np.empty(max_len, dtype=np.int32)
        
        cdef int[:, ::1] r_view = new_rects
        cdef int[::1] z_view = new_zs
        
        cdef Py_ssize_t valid_count = 0
        
        for req_ref in self._registered_requests:
            req = req_ref()
            
            if req is not None:
                current_link = req.get_link()
                if current_link is not None and not current_link._dead:
                    live_requests_refs.append(req_ref)
                    temp_live_requests.append(req)
                    
                    current_rect = current_link.get_nvrect()
                    r_view[valid_count, 0] = <int>current_rect.x
                    r_view[valid_count, 1] = <int>current_rect.y
                    r_view[valid_count, 2] = <int>current_rect.w
                    r_view[valid_count, 3] = <int>current_rect.h
                    z_view[valid_count] = current_link.get_param_strict("z").value
                    
                    valid_count += 1
                    
        self._registered_requests = live_requests_refs
        self.live_requests = temp_live_requests
        
        if valid_count == 0:
            self._reset_arrays()
            return

        self.rects_data = new_rects[:valid_count]
        self.z_indices = new_zs[:valid_count]
        self.rects_view = self.rects_data
        self.z_view = self.z_indices
    
    cpdef mark_dirty(self):
        self.is_dirty = True

    cdef void c_mark_dirty(self) nogil:
        self.is_dirty = True

    cpdef list get_active_requests(self):
        if self.is_dirty:
            self._rebuild_arrays()
            self.is_dirty = False
        return list(self.live_requests)

    cpdef cycle(self, NvVector2 mouse_pos, bint mouse_down, bint mouse_up, bint any_wheel, bint wheel_down):
        if self.is_dirty:
            self._rebuild_arrays()
            self.is_dirty = False

        cdef ZRequest current_winner_request = self.request_cycle(mouse_pos, any_wheel, wheel_down)
        cdef ZRequest clicked_req
        
        if self.clicked_request is None:
            if self.last_hovered_request is not current_winner_request:
                if self.last_hovered_request is not None:
                    if (<ZRequest>self.last_hovered_request).on_unhover_func is not None:
                        (<ZRequest>self.last_hovered_request).on_unhover_func()
                
                if current_winner_request is not None:
                    if current_winner_request.on_hover_func is not None:
                        current_winner_request.on_hover_func()

            self.last_hovered_request = current_winner_request
        
        if mouse_down and current_winner_request is not None:
            self.clicked_request = current_winner_request
            if current_winner_request.on_click_func is not None:
                current_winner_request.on_click_func()
        
        if mouse_up:
            if self.clicked_request is not None:
                clicked_req = <ZRequest>self.clicked_request
                if clicked_req.get_link() is not None:
                    if clicked_req is current_winner_request:
                        if clicked_req.on_keyup_func is not None:
                            clicked_req.on_keyup_func()
                    else:
                        if clicked_req.on_keyup_abandon_func is not None:
                            clicked_req.on_keyup_abandon_func()
                self.clicked_request = None

    cdef ZRequest request_cycle(self, NvVector2 mouse_pos, bint any_wheel, bint wheel_down):
        if not self.live_requests:
            return None
            
        cdef int mx = int(mouse_pos.x)
        cdef int my = int(mouse_pos.y)
        
        cdef Py_ssize_t i
        cdef Py_ssize_t best_idx = -1
        cdef int best_z = -2147483648
        cdef int current_z
        cdef ZRequest candidate_req
        cdef NevuCobject candidate_link
        
        cdef Py_ssize_t num_rects = self.rects_view.shape[0]

        if len(self.live_requests) != num_rects:
            return None
        
        for i in range(num_rects):
            if (mx >= self.rects_view[i, 0] and 
                mx < self.rects_view[i, 0] + self.rects_view[i, 2] and
                my >= self.rects_view[i, 1] and 
                my < self.rects_view[i, 1] + self.rects_view[i, 3]):
                
                current_z = self.z_view[i]
                
                if current_z > best_z:
                    candidate_req = <ZRequest>self.live_requests[i]
                    candidate_link = candidate_req.get_link()
                    
                    if candidate_link is None:
                        self.is_dirty = True
                        continue
                    
                    best_z = current_z
                    best_idx = i
                    
        if best_idx != -1:
            candidate_req = <ZRequest>self.live_requests[best_idx]
            
            if any_wheel and candidate_req.on_scroll_func is not None:
                candidate_req.on_scroll_func(wheel_down)
                
            return candidate_req
            
        return None