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

    cpdef void add(self, ZRequest z_request):
        self._registered_requests.append(weakref.ref(z_request))
        self.mark_dirty()
        
    cdef void _rebuild_arrays(self):
        cdef list live_requests_refs = []
        cdef list rect_list = []
        cdef list z_list = []
        cdef list temp_live_requests = []
        
        cdef object req_ref
        cdef ZRequest req
        cdef NvRect current_rect
        cdef NevuCobject current_link
        
        for req_ref in self._registered_requests:
            req = req_ref()
            
            if req is not None:
                current_link = req.get_link()
                if current_link is not None:
                    if current_link._dead: continue
                    live_requests_refs.append(req_ref)
                    current_rect = current_link.get_nvrect()
                    rect_list.append((current_rect.x, current_rect.y, current_rect.w, current_rect.h))
                    z_list.append(current_link.get_param_strict("z").value)
                    temp_live_requests.append(req)
                    
        self._registered_requests = live_requests_refs
        self.live_requests = temp_live_requests
        
        if not temp_live_requests:
            self._reset_arrays()
            return

        self.rects_data = np.array(rect_list, dtype=np.int32)
        self.z_indices = np.array(z_list, dtype=np.int32)
    
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

        cdef object current_winner_request = self.request_cycle(mouse_pos, any_wheel, wheel_down, self.live_requests)
        cdef ZRequest clicked_request, winner_request_z, hovered_request_z

        if self.clicked_request is None:
            if self.last_hovered_request is not current_winner_request:
                
                if self.last_hovered_request is not None:
                    hovered_request_z = self.last_hovered_request
                    if hovered_request_z.on_unhover_func is not None:
                        hovered_request_z.on_unhover_func()
                
                if current_winner_request is not None:
                    winner_request_z = current_winner_request
                    if winner_request_z.on_hover_func is not None:
                        winner_request_z.on_hover_func()

            self.last_hovered_request = current_winner_request
        
        if mouse_down and current_winner_request is not None:
            winner_request_z = current_winner_request
            clicked_request = winner_request_z
            self.clicked_request = clicked_request
            if clicked_request.on_click_func is not None:
                clicked_request.on_click_func()
        
        if mouse_up:
            if self.clicked_request is not None:
                clicked_request = self.clicked_request
                if clicked_request.get_link() is not None:
                    if clicked_request is current_winner_request:
                        if clicked_request.on_keyup_func is not None:
                            clicked_request.on_keyup_func()
                    else:
                        if clicked_request.on_keyup_abandon_func is not None:
                            clicked_request.on_keyup_abandon_func()
                self.clicked_request = None

    cdef object request_cycle(self, NvVector2 mouse_pos, bint any_wheel, bint wheel_down, list live_requests):
        if not live_requests:
            return None
        
        cdef np.ndarray collided_mask
        cdef np.ndarray[np.intp_t, ndim=1] candidate_indices
        cdef np.ndarray[np.intp_t, ndim=1] sorted_indices
        cdef ZRequest candidate_req
        cdef NevuCobject candidate_link
        
        cdef int mx = int(mouse_pos.x)
        cdef int my = int(mouse_pos.y)
        
        cdef np.ndarray[np.int32_t, ndim=2] rects = self.rects_data

        if len(live_requests) != rects.shape[0]:
            return None
        
        collided_mask = ((rects[:, 0] <= mx) & 
                         (mx < rects[:, 0] + rects[:, 2]) &
                         (rects[:, 1] <= my) & 
                         (my < rects[:, 1] + rects[:, 3]))

        candidate_indices = np.where(collided_mask)[0]
        
        if candidate_indices.size > 0:
            sorted_indices = candidate_indices[np.argsort(self.z_indices[candidate_indices])[::-1]]
            
            for idx in sorted_indices:
                candidate_req = live_requests[idx]
                candidate_link = candidate_req.get_link()
                
                if candidate_link is None:
                    self.mark_dirty()
                    continue
            
                if any_wheel and candidate_req.on_scroll_func is not None:
                    candidate_req.on_scroll_func(wheel_down)
        
                return candidate_req
            
        return None