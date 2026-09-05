# distutils: language = c++
# cython: language_level=3
# cython: boundscheck=False
# cython: wraparound=False
# cython: initializedcheck=False
# cython: nonecheck=False

import weakref
import typing

cdef object TYPING_ANY = typing.Any
cdef object ref_type = weakref.ReferenceType
cdef object weak_method = weakref.WeakMethod

cdef inline object _resolve_callable(object target) noexcept:
    if target is None: return None
    cdef type t_type = type(target)
    if t_type is ref_type or t_type is weak_method:
        return target()

    cdef str t_name
    t_name = type(target).__name__
    if t_name == 'ref' or t_name == 'WeakMethod':
        return target()

    return target

cdef class NvParam:
    @staticmethod
    cdef NvParam new(str name, int layer, object value, object default, object type, object getter, object setter):
        cdef NvParam constant = <NvParam>NvParam.__new__(NvParam)
        constant.name = name
        constant.value = value
        constant.layer = layer
        constant.default = default
        constant.type = type
        constant.getter = getter
        constant.setter = setter
        constant.flags = 0
        if setter is not None:
            constant.flags |= NvParamFlagSetter
        if getter is not None:
            constant.flags |= NvParamFlagGetter
        return constant

    def __init__(self, str name, int layer, object value, object default, object type, object getter=None, object setter=None):
        self.name = name
        self.value = value
        self.layer = layer
        self.default = default
        self.type = type
        self.getter = getter
        self.setter = setter
        self.flags = 0
        if setter is not None:
            self.flags |= NvParamFlagSetter
        if getter is not None:
            self.flags |= NvParamFlagGetter

    cpdef bool check(self, value):
        if self.type is TYPING_ANY:
            return True
        return isinstance(value, self.type)

    cpdef void set(self, value):
        cdef object new_value
        cdef object actual_setter

        if not self.check(value):
            raise TypeError(
                f"Parameter '{self.name}' must be of type '{self._get_cool_error_message()}', "
                f"but got '{value} ({type(value).__name__})'."
            )

        if self.flags & NvParamFlagSetter:
            actual_setter = _resolve_callable(self.setter)
            if actual_setter is not None:
                new_value = actual_setter(value)
                if new_value is not None:
                    self.value = new_value
                    return

        self.value = value

    cpdef object get(self):
        cdef object actual_getter
        if self.flags & NvParamFlagGetter:
            actual_getter = _resolve_callable(self.getter)
            if actual_getter is not None:
                return actual_getter(self.value)
        return self.value

    def __repr__(self) -> str:
        return f"NvParam(name={self.name}, layer={self.layer}, value={self.value}, default={self.default}, type={self.type}, getter={self.getter}, setter={self.setter})"

    def __str__(self) -> str:
        return f"{self.name}: {self.value}"

    cdef inline str _get_cool_error_message(self) noexcept:
        if isinstance(self.type, tuple):
            return ', '.join([t.__name__ for t in self.type])
        return self.type.__name__

    cpdef void reset(self):
        self.set(self.default)
