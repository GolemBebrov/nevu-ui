# distutils: language = c++
# cython: language_level=3

cdef class Cache:
    cdef list cache_arr
    
    cdef inline void c_clear(self)
    cdef inline void c_clear_selected(self, list blacklist, list whitelist)
    cdef inline object c_get(self, int type_idx)
    cdef inline void c_set(self, int type_idx, object value)
    cdef inline object c_get_or_set_val(self, int type_idx, object value)
    cdef inline object c_get_or_exec(self, int type_idx, func)
    @staticmethod
    cdef inline Cache new()