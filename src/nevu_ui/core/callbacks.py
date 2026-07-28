from typing import TYPE_CHECKING, Any, Callable, ParamSpec, Concatenate
from weakref import WeakMethod, ref
import inspect

from nevu_ui.core.enums import BindType

if TYPE_CHECKING:
    from nevu_ui.components.nevuobj import NevuObject

# FA
# PU
# TA
# 0_0
# SO
# LO

P = ParamSpec("P")

WeakType = ref | WeakMethod
CallbackType = Callable[Concatenate["NevuObject", P], Any] | WeakType
CallbackList = list[CallbackType]

class Callbacks:
    def __init__(self, content: dict[BindType, CallbackList | CallbackType] | None = None):
        content = content or {}
        self._storage: dict[BindType, CallbackList] = {
            bind_type: [callback] if inspect.isfunction(callback) else callback
            for bind_type, callback in content.items()
        }

    def bind(self, bind_type: BindType, function: Callable[Concatenate["NevuObject", P], Any], *, add_to_end: bool = True, weak: bool = False):
        callbacks_list = self._storage.setdefault(bind_type, [])

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

    def unbind(self, bind_type: BindType, function: Callable[["NevuObject"], Any]):
        callbacks_list = self._storage.get(bind_type)
        if not callbacks_list: return

        for callback in list(callbacks_list):
            target = callback() if isinstance(callback,  ref | WeakMethod) else callback

            if target == function or callback == function:
                callbacks_list.remove(callback)

    def run(self, bind_type: BindType, *args, **kwargs):
        callbacks_list = self._storage.get(bind_type)
        if not callbacks_list: return

        dead_links = []

        for callback in callbacks_list:
            func = callback
            if isinstance(callback, ref | WeakMethod):
                func = callback()
                if func is None:
                    dead_links.append(callback)
                    continue

            func(*args, **kwargs)

        if dead_links:
            for dead in dead_links:
                callbacks_list.remove(dead)
