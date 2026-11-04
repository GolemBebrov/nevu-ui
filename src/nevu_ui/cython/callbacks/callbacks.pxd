cdef class Callbacks:
    cdef dict _storage
    cpdef unbind(self, bind_type: BindType, function: Callable[[Any], Any])
    cpdef run_noargs(self, bind_type: BindType, arg: Any)
    cdef inline void c_run(self, list callbacks_list, tuple args, dict kwargs)
