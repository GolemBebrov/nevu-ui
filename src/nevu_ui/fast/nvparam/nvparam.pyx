# distutils: language = c++
import weakref
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
        cdef object actual_setter
        if self.setter != None: 
            actual_setter = self.setter

            if isinstance(actual_setter, (weakref.ReferenceType, weakref.WeakMethod)) or type(actual_setter).__name__ in ('ref', 'WeakMethod'):
                actual_setter = actual_setter()
                
            if actual_setter != None:
                
                new_value = actual_setter(value)
                if new_value != None:
                    self.value = new_value
                    return
                    
        if not self.check(value):
            raise TypeError(f"Parameter '{self.name}' must be of type '{self._get_cool_error_message()}', but got '{value} ({type(value).__name__})'.")
        self.value = value
        
    cpdef object get(self):
        cdef object actual_getter
        
        if self.getter != None: 
            actual_getter = self.getter
            if isinstance(actual_getter, (weakref.ReferenceType, weakref.WeakMethod)) or type(actual_getter).__name__ in ('ref', 'WeakMethod'):
                actual_getter = actual_getter()
                
            if actual_getter != None:
                return actual_getter(self.value)
                
        return self.value

    def __repr__(self) -> str:
        return f"NvParam(name={self.name}, layer={self.layer}, value={self.value}, default={self.default}, type={self.type}, getter={self.getter}, setter={self.setter})"
    
    def __str__(self) -> str:
        return f"{self.name}: {self.value}"
    
    def _get_cool_error_message(self):
        return f"{self.type.__name__ if not isinstance(self.type, tuple) else ', '.join([t.__name__ for t in self.type])}"

    cpdef void reset(self):
        self.value = self.default 