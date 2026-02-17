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
    
    cpdef bint check(self, value):
        return isinstance(value, self.type)
    
    cpdef void set(self, value):
        if self.setter != None: print(self.name,self.setter(value))
        self.value = value
        
    cpdef object get(self):
        if self.getter: return self.getter(self.value)
        return self.value

    def __repr__(self) -> str:
        return f"NvParam(name={self.name}, layer={self.layer}, value={self.value}, default={self.default}, type={self.type}, getter={self.getter}, setter={self.setter})"
    
    cpdef void reset(self):
        self.value = self.default 