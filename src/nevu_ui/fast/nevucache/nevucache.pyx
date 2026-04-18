from nevu_ui.core.enums import CacheName, CacheType
from cpython.dict cimport PyDict_Size, PyDict_Next, PyDict_Keys

cdef class Cache:
    @staticmethod
    cdef inline Cache new():
        cdef Cache cache = Cache.__new__(Cache)
        cache.cache_default = {member: None for member in CacheType}
        cache.cache = cache.cache_default.copy()
        return cache

    def __init__(self):
        self.cache_default = {member: None for member in CacheType}
        self.cache = self.cache_default.copy()

    cdef inline void c_clear(self):
        self.cache = self.cache_default.copy()

    def clear(self):
        self.c_clear()

    cdef inline void c_clear_selected(self, list blacklist, list whitelist):
        cdef Py_ssize_t max_i, i
        cdef dict cache = self.cache
        keys = PyDict_Keys(cache)
        max_i = PyDict_Size(cache)
        i = 0
        while i < max_i:
            item = keys[i]
            if item not in blacklist and item in whitelist:
                cache[item] = None
            i += 1   

    def clear_selected(self, blacklist = None, whitelist = None):
        blacklist = blacklist or []
        whitelist = whitelist or list(CacheType.__members__.values())
        self.c_clear_selected(blacklist, whitelist)

    cdef inline object c_get(self, type):
        return self.cache[type]

    def get(self, type not None):
        return self.c_get(type)

    cdef inline void c_set(self, type, object value):
        self.cache[type] = value

    def set(self, type, object value):
        self.c_set(type, value)

    cdef inline object c_get_or_set_val(self, type, object value):
        if self.cache[type] is None:
            self.cache[type] = value
        return self.cache[type]

    def get_or_set_val(self, type, object value):
        return self.c_get_or_set_val(type, value)

    cdef inline object c_get_or_exec(self, type, func):
        if self.cache[type] is None:
            self.cache[type] = func()
        return self.cache[type]

    def get_or_exec(self, type not None, func not None):
        return self.c_get_or_exec(type, func)

    def __getattr__(self, str type):
        if type in CacheType.__members__:
            return self.cache[CacheType[type]]
        raise AttributeError(type)

    def __getitem__(self, key: CacheType):
        if not isinstance(key, CacheType):
            raise TypeError("The key for cache access must be of type CacheType")
        return self.cache[key]

    def copy(self):
        copy = Cache()
        copy.cache = self.cache.copy()
        return copy

    def __deepcopy__(self, memo):
        return self.copy()