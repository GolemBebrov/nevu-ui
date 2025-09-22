    
import numpy as np
cimport numpy as np
cimport cython
import weakref

np.import_array()

cdef class ZRequest:
    cdef public object link
    cdef public object on_hover_func, on_unhover_func, on_click_func, on_scroll_func, on_keyup_func
    cdef __weakref__

    def __init__(self, link,
                 on_hover_func=None, on_unhover_func=None, on_click_func=None, on_keyup_func=None, on_scroll_func=None):
        self.link = link
        self.on_hover_func = on_hover_func
        self.on_unhover_func = on_unhover_func
        self.on_click_func = on_click_func
        self.on_scroll_func = on_scroll_func
        self.on_keyup_func = on_keyup_func

@cython.boundscheck(False)
@cython.wraparound(False)
cdef class ZSystem:
    cdef list _registered_requests
    cdef object last_hovered_winner_data
    
    cdef np.ndarray rects_data
    cdef np.ndarray z_indices
    cdef list callbacks

    def __cinit__(self):
        self._registered_requests = []
        self.last_hovered_winner_data = None
        self._reset_arrays()

    cdef void _reset_arrays(self):
        self.rects_data = np.empty((0, 4), dtype=np.int32)
        self.z_indices = np.empty(0, dtype=np.int32)
        self.callbacks = []

    cpdef add(self, ZRequest z_request):
        self._registered_requests.append(weakref.ref(z_request))
        
    cdef void _rebuild_arrays(self):
        cdef list live_requests = []
        cdef object req_ref, req
        for req_ref in self._registered_requests:
            req = req_ref()
            if req is not None and req.link is not None:
                live_requests.append(req)

        self._registered_requests = [weakref.ref(obj) for obj in live_requests]
        
        cdef int count = len(live_requests)
        if count == 0:
            self._reset_arrays()
            return
            
        self.rects_data = np.empty((count, 4), dtype=np.int32)
        self.z_indices = np.empty(count, dtype=np.int32)
        self.callbacks = [None] * count
        
        cdef int i
        cdef object current_rect
        for i, req in enumerate(live_requests):
            current_rect = req.link.get_rect()
            self.rects_data[i, 0] = current_rect.x
            self.rects_data[i, 1] = current_rect.y
            self.rects_data[i, 2] = current_rect.width 
            self.rects_data[i, 3] = current_rect.height 
            self.z_indices[i] = req.link.z
            self.callbacks[i] = (req.on_hover_func, req.on_unhover_func, req.on_click_func, 
                                 req.on_scroll_func, req.on_keyup_func)
        
    cpdef cycle(self, object mouse_pos, bint mouse_clicked, bint any_wheel, bint wheel_down):
        self._rebuild_arrays()

        cdef object current_winner_data = self.request_cycle(mouse_pos, mouse_clicked, any_wheel, wheel_down)
        
        if self.last_hovered_winner_data is not current_winner_data:
            if self.last_hovered_winner_data:
                on_unhover_func = self.last_hovered_winner_data[1]
                if callable(on_unhover_func):
                    on_unhover_func()
            
            if current_winner_data:
                on_hover_func = current_winner_data[0]
                if callable(on_hover_func):
                    on_hover_func()

        self.last_hovered_winner_data = current_winner_data

    cdef object request_cycle(self, tuple mouse_pos, bint mouse_clicked, bint any_wheel, bint wheel_down):
        if self.rects_data.shape[0] == 0:
            return None
        
        cdef int winner_idx = -1
        cdef np.ndarray[np.uint8_t, ndim=1] collided_mask
        cdef np.ndarray[np.intp_t, ndim=1] candidate_indices
        cdef object on_scroll_func, on_click_func
        
        collided_mask = ((self.rects_data[:, 0] <= mouse_pos[0]) & 
                         (mouse_pos[0] < self.rects_data[:, 0] + self.rects_data[:, 2]) &
                         (self.rects_data[:, 1] <= mouse_pos[1]) & 
                         (mouse_pos[1] < self.rects_data[:, 1] + self.rects_data[:, 3]))

        candidate_indices = np.where(collided_mask)[0]
        if candidate_indices.size > 0:
            winner_idx = candidate_indices[np.argmax(self.z_indices[candidate_indices])]

        if winner_idx != -1:
            on_hover_func, on_unhover_func, on_click_func, on_scroll_func, on_keyup_func = self.callbacks[winner_idx]

            if any_wheel and callable(on_scroll_func):
                on_scroll_func(wheel_down)

            if mouse_clicked and callable(on_click_func):
                on_click_func()
        
        if winner_idx != -1:
            return self.callbacks[winner_idx]
        return None

  