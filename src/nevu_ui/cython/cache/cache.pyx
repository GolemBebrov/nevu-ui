# distutils: language = c++
# cython: language_level=3
# cython: boundscheck=False
# cython: wraparound=False
# cython: cdivision=True
# cython: nonecheck=False
# cython: initializedcheck=False

from nevu_ui.core.enums import CacheType

cdef class Cache:
    @staticmethod
    cdef inline Cache new():
        cdef Cache cache = Cache.__new__(Cache)
        cache.cache_arr = [None] * 32
        return cache

    def __init__(self):
        self.cache_arr = [None] * 32

    cdef inline void c_clear(self):
        cdef int i
        for i in range(32):
            self.cache_arr[i] = None

    def clear(self):
        self.c_clear()

    cdef inline void c_clear_selected(self, list blacklist, list whitelist):
        cdef bint[32] bl
        cdef bint[32] wl
        cdef int i, idx
        cdef object item

        for i in range(32):
            bl[i] = False
            wl[i] = False

        for item in blacklist:
            idx = <int>item.value
            if 0 <= idx < 32:
                bl[idx] = True

        for item in whitelist:
            idx = <int>item.value
            if 0 <= idx < 32:
                wl[idx] = True

        for i in range(32):
            if not bl[i] and wl[i]:
                self.cache_arr[i] = None

    def clear_selected(self, blacklist = None, whitelist = None):
        blacklist = blacklist or []
        whitelist = whitelist or list(CacheType.__members__.values())
        self.c_clear_selected(blacklist, whitelist)

    cdef inline object c_get(self, int type_idx):
        return self.cache_arr[type_idx]

    def get(self, type not None):
        return self.c_get(<int>type.value)

    cdef inline void c_set(self, int type_idx, object value):
        self.cache_arr[type_idx] = value

    def set(self, type, object value):
        self.c_set(<int>type.value, value)

    cdef inline object c_get_or_set_val(self, int type_idx, object value):
        if self.cache_arr[type_idx] is None:
            self.cache_arr[type_idx] = value
        return self.cache_arr[type_idx]

    def get_or_set_val(self, type, object value):
        return self.c_get_or_set_val(<int>type.value, value)

    cdef inline object c_get_or_exec(self, int type_idx, func):
        if self.cache_arr[type_idx] is None:
            self.cache_arr[type_idx] = func()
        return self.cache_arr[type_idx]

    def get_or_exec(self, type not None, func not None):
        return self.c_get_or_exec(<int>type.value, func)

    def __getattr__(self, str type):
        if type in CacheType.__members__:
            return self.cache_arr[<int>CacheType[type].value]
        raise AttributeError(type)

    def __getitem__(self, key):
        if not isinstance(key, CacheType):
            raise TypeError("The key for cache access must be of type CacheType")
        return self.cache_arr[<int>key.value]

    def copy(self):
        copy = Cache()
        copy.cache_arr = self.cache_arr[:]
        return copy

    def __deepcopy__(self, memo):
        return self.copy()
