from nevu_ui.core_types import (
    CacheName, CacheType
)

class Cache:
    def __init__(self):
        self.name = CacheName.MAIN
        self.cache_default = {
            CacheType.Coords: None,
            CacheType.RelSize: None,
            CacheType.Surface: None,
            CacheType.Gradient: None,
            CacheType.Image: None,
            CacheType.Borders: None,
            CacheType.Scaled_Borders: None,
            CacheType.Scaled_Background: None,
            CacheType.Background: None,
            CacheType.Scaled_Gradient: None,
            CacheType.Scaled_Image: None
            
        }
        self.cache = {
            CacheName.MAIN: self.cache_default.copy(),
            CacheName.PREVERSED: self.cache_default.copy(),
            CacheName.CUSTOM: self.cache_default.copy()
        }
        
    def set_name(self, name: CacheName):
        self.name = name
        
    def clear(self, name = None):
        name = name or self.name
        self.cache[name] = self.cache_default.copy()
        
    def clear_selected(self, blacklist = None, whitelist = None, name = None):
        name = name or self.name
        cachename = self.cache[name]
        blacklist = [] if blacklist is None else blacklist
        whitelist = [CacheType.RelSize,
                     CacheType.Coords,
                     CacheType.Surface,
                     CacheType.Gradient,
                     CacheType.Image,
                     CacheType.Scaled_Image,
                     CacheType.Borders,
                     CacheType.Scaled_Borders,
                     CacheType.Scaled_Background,
                     CacheType.Scaled_Gradient,
                     CacheType.Background
                    ] if whitelist is None else whitelist
        for item, value in cachename.items():
            if item not in blacklist and item in whitelist:
                cachename[item] = None
                
    def get(self, type: CacheType, name = None):
        name = name or self.name
        return self.cache[name][type]
    
    def set(self, type: CacheType, value, name = None):
        name = name or self.name
        self.cache[name][type] = value
        
    def get_or_set_val(self, type: CacheType, value, name = None):
        name = name or self.name
        if self.cache[name][type] is None:
            self.cache[name][type] = value
        return self.cache[name][type]
    
    def get_or_exec(self, type: CacheType, func, name = None):
        name = name or self.name
        if self.cache[name][type] is None:
            self.cache[name][type] = func()
        return self.cache[name][type]
    
    def __getattr__(self, type):
        return self.cache[self.name][type]
    def __getitem__(self, key: CacheType):
        if not isinstance(key, CacheType):
            raise TypeError("Ключ для доступа к кешу должен быть типа CacheType")
        return self.cache[self.name][key]