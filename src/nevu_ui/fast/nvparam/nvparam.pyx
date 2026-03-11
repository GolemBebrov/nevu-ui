# distutils: language = c++

cdef class NvParam:
    @staticmethod
    cdef NvParam new(str name, int layer, object value, object default, object type, object getter, object setter):
        cdef NvParam constant = NvParam.__new__(NvParam)
        constant.name = name
        constant.value = value
        constant.layer = layer
        constant.default = default
        constant.type = type
        constant.getter = getter
        constant.setter = setter
        return constant

    def __init__(self, str name, int layer, value, default, type, object getter = None, object setter = None):
        self.name = name
        self.value = value
        self.layer = layer
        self.default = default
        self.type = type
        self.getter = getter
        self.setter = setter
    
    cpdef bool check(self, value):
        return isinstance(value, self.type)
    
    cpdef void set(self, value):
        cdef object new_value
        if self.setter != None: 
            new_value = self.setter(value)
            if new_value != None:
                self.value = new_value
                return
        if not self.check(value):
            raise TypeError(f"Parameter '{self.name}' must be of type '{self._get_cool_error_message()}', but got '{value} ({type(value).__name__})'.")
        self.value = value
        
    cpdef object get(self):
        if self.getter: return self.getter(self.value)
        return self.value

    def __repr__(self) -> str:
        return f"NvParam(name={self.name}, layer={self.layer}, value={self.value}, default={self.default}, type={self.type}, getter={self.getter}, setter={self.setter})"
    
    def __str__(self) -> str:
        return f"{self.name}: {self.value}"
    
    def _get_cool_error_message(self):
        return f"{self.type.__name__ if not isinstance(self.type, tuple) else ', '.join([t.__name__ for t in self.type])}"

    cpdef void reset(self):
        self.value = self.default 