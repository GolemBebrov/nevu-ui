import inspect
from collections.abc import Callable
from typing import Any, Concatenate, ParamSpec
from weakref import WeakMethod, ref
from cpython.list cimport PyList_GET_SIZE
from nevu_ui.core.enums import BindType
from cpython.object cimport PyObject
cdef extern from "Python.h":
    ctypedef struct PyListObject:
        PyObject **ob_item

# FA
# PU
# TA
# 0_0
# SO
# LO

P = ParamSpec("P")

WeakType = ref | WeakMethod
CallbackType = Callable[Concatenate[Any, P], Any] | WeakType
CallbackList = list[CallbackType]

cdef inline bint is_weak(callback) noexcept:
    return type(callback) is ref or type(callback) is WeakMethod

cdef class Callbacks:
    def __init__(self, dict content: dict[BindType, CallbackList | CallbackType] | None = None):
        content = content or {}
        self._storage: dict[BindType, CallbackList] = {
            bind_type: [callback] if inspect.isfunction(callback) else callback
            for bind_type, callback in content.items()
        }

    def bind(self, bind_type: BindType, function: Callable[Concatenate[Any, P], Any], *, bint add_to_end = True, bint weak = False):
        cdef list callbacks_list = self._storage.setdefault(bind_type, [])

        callback: CallbackType = function
        if weak:
            if hasattr(function, "__self__") and function.__self__ is not None:
                callback = WeakMethod(function)
            else:
                callback = ref(function)

        if add_to_end:
            callbacks_list.append(callback)
        else:
            callbacks_list.insert(0, callback)

    cpdef unbind(self, bind_type: BindType, function: Callable[[Any], Any]):
        cdef list callbacks_list
        callbacks_list = self._storage.get(bind_type)
        if not callbacks_list: return


        for callback in list(callbacks_list):
            target = callback() if is_weak(callback) else callback

            if target == function or callback == function:
                callbacks_list.remove(callback)

    cpdef run_noargs(self, bind_type: BindType, arg: Any):
        cdef list callbacks_list
        callbacks_list = self._storage.get(bind_type)
        if not callbacks_list: return
        self.c_run(callbacks_list, (arg,), {})

    cdef inline void c_run(self, list callbacks_list, tuple args, dict kwargs):
        cdef list active_callbacks = callbacks_list.copy()
        cdef list live_callbacks = []

        for cb in active_callbacks:
            func = cb() if is_weak(cb) else cb
            if func is None:
                continue
            func(*args, **kwargs)
            live_callbacks.append(cb)

        callbacks_list[:] = live_callbacks

    def run(self, bind_type: BindType, *args, **kwargs):
        cdef list callbacks_list
        callbacks_list = self._storage.get(bind_type)
        if not callbacks_list: return
        self.c_run(callbacks_list, args, kwargs)
