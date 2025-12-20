from nevu_ui.core.enums import (
    CacheName, CacheType
)

class Cache:
    __slots__ = ("name", "namespaces", "cache_default")
    def __init__(self):
        self.name = CacheName.MAIN
        self.cache_default = {member: None for member in CacheType}
        self.namespaces = {
            CacheName.MAIN: self.cache_default.copy(),
            CacheName.PRESERVED: self.cache_default.copy(),
            CacheName.CUSTOM: self.cache_default.copy()}
        
    def set_name(self, name: CacheName): self.name = name
    
    def clear(self, name = None):
        name = name or self.name
        self.namespaces[name] = self.cache_default.copy()
        
    def clear_selected(self, blacklist = None, whitelist = None, name = None):
        name = name or self.name
        cachename = self.namespaces[name]
        blacklist = blacklist or []
        whitelist = whitelist or CacheType
        for item, value in cachename.items():
            if item not in blacklist and item in whitelist:
                cachename[item] = None
                
    def get(self, type: CacheType, name = None):
        name = name or self.name
        return self.namespaces[name][type]
    
    def set(self, type: CacheType, value, name = None):
        name = name or self.name
        self.namespaces[name][type] = value
    
    @property
    def current_namespace(self): return self.namespaces[self.name]
    
    def get_or_set_val(self, type: CacheType, value, name = None):
        name = name or self.name
        if self.namespaces[name][type] is None:
            self.namespaces[name][type] = value
        return self.namespaces[name][type]
    
    def get_or_exec(self, type: CacheType, func, name = None):
        name = name or self.name
        if self.namespaces[name][type] is None:
            self.namespaces[name][type] = func()
        return self.namespaces[name][type]
    
    def __getattr__(self, type): return self.namespaces[self.name][type]
    def __getitem__(self, key: CacheType):
        if not isinstance(key, CacheType): raise TypeError("The key for cache access must be of type CacheType")
        return self.namespaces[self.name][key]

    def copy(self):
        copy = Cache()
        copy.name = self.name
        copy.namespaces = self.namespaces.copy()
        return copy
    
    def __deepcopy__(self, memo): 
        return self.copy()