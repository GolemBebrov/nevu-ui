cdef class Cache:
    cdef public dict cache_default
    cdef public dict cache  
    cdef inline void c_clear(self)
    cdef inline void c_clear_selected(self, list blacklist, list whitelist)
    cdef inline object c_get(self, object type)
    cdef inline void c_set(self, object type, object value)
    cdef inline object c_get_or_set_val(self, object type, object value)
    cdef inline object c_get_or_exec(self, object type, func)
    @staticmethod
    cdef inline Cache new()