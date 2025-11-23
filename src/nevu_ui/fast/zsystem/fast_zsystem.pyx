# distutils: language = c++
# cython: language_level=3
# cython: boundscheck=False
# cython: wraparound=False
# cython: cdivision=True
# cython: nonecheck=False

import numpy as np
cimport numpy as np
cimport cython
import weakref
from nevu_ui.fast.nvvector2.nvvector2 cimport NvVector2
from nevu_ui.fast.logic import get_rect_helper

np.import_array()

cdef class ZRequest:
    cdef object _link_ref
    cdef public object on_hover_func, on_unhover_func, on_click_func, on_scroll_func, on_keyup_func, on_keyup_abandon_func
    cdef object __weakref__

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

    @property
    def link(self):
        return self._link_ref()

@cython.boundscheck(False)
@cython.wraparound(False)
cdef class ZSystem:
    cdef list _registered_requests
    cdef object last_hovered_request
    cdef object clicked_request  
    cdef list live_requests
    cdef bint is_dirty

    cdef np.ndarray rects_data
    cdef np.ndarray z_indices

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

    cpdef add(self, ZRequest z_request):
        self._registered_requests.append(weakref.ref(z_request))
        self.mark_dirty()
        
    cdef void _rebuild_arrays(self):
        cdef list live_requests_refs = []
        cdef list rect_list = []
        cdef list z_list = []
        cdef list temp_live_requests = []
        
        cdef object req_ref, req, current_link, current_rect
        
        for req_ref in self._registered_requests:
            req = req_ref()
            
            if req is not None:
                current_link = req.link
                if current_link is not None:
                    if hasattr(current_link, 'is_active') and not current_link.is_active:
                        continue
                    if hasattr(current_link, 'visible') and not current_link.visible:
                        continue

                    live_requests_refs.append(req_ref)
                    current_rect = current_link.get_rect()
                    rect_list.append((current_rect.x, current_rect.y, current_rect.width, current_rect.height))
                    z_list.append(current_link.z)
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

        if self.last_hovered_request is not current_winner_request:
            if self.last_hovered_request is not None:
                if self.last_hovered_request.on_unhover_func is not None:
                    self.last_hovered_request.on_unhover_func()
            
            if current_winner_request is not None:
                if current_winner_request.on_hover_func is not None:
                    current_winner_request.on_hover_func()

        self.last_hovered_request = current_winner_request
        
        if mouse_down and current_winner_request is not None:
            self.clicked_request = current_winner_request
            if self.clicked_request.on_click_func is not None:
                self.clicked_request.on_click_func()
        
        if mouse_up:
            if self.clicked_request is not None:
                if self.clicked_request.link is not None:
                    if self.clicked_request is current_winner_request:
                        if self.clicked_request.on_keyup_func is not None:
                            self.clicked_request.on_keyup_func()
                    else:
                        if self.clicked_request.on_keyup_abandon_func is not None:
                            self.clicked_request.on_keyup_abandon_func()
                self.clicked_request = None

    cdef object request_cycle(self, NvVector2 mouse_pos, bint any_wheel, bint wheel_down, list live_requests):
        if not live_requests:
            return None
        
        cdef np.ndarray collided_mask
        cdef np.ndarray[np.intp_t, ndim=1] candidate_indices
        cdef np.ndarray[np.intp_t, ndim=1] sorted_indices
        cdef object candidate_req, candidate_link
        
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
                candidate_link = candidate_req.link
                
                if candidate_link is None:
                    self.mark_dirty()
                    continue
                
                if hasattr(candidate_link, 'is_active') and not candidate_link.is_active:
                    self.mark_dirty()
                    continue
                
                if hasattr(candidate_link, 'visible') and not candidate_link.visible:
                    self.mark_dirty()
                    continue

                if any_wheel and candidate_req.on_scroll_func is not None:
                    candidate_req.on_scroll_func(wheel_down)
        
                return candidate_req
            
        return None