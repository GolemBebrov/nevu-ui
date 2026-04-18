from enum import StrEnum, Enum
import contextlib
from dataclasses import dataclass
from typing import Any
from typing import TYPE_CHECKING, Callable
from nevu_ui.core.enums import Backend
if TYPE_CHECKING:
    from nevu_ui.fast.nvvector2 import NvVector2
    
class Events:
    __slots__ = ('content', 'on_add')
    def __init__(self):
        self.content = []
        self.on_add = self._default_on_add_hook
        
    def add(self, event): self.content.append(event)
    @staticmethod
    def _default_on_add_hook(event): pass
    
    def __copy__(self): return self.copy()
    def copy(self):
        new = self.__new__(self.__class__)
        new.content = self.content.copy()
        new.on_add = self.on_add
        return new

class ConfigType():
    class Window():
        class Size():
            Small = (600, 300)
            Medium = (800, 600)
            Big = (1600, 800)
            
        Display = Backend

        class Utils:
            All = ["keyboard", "mouse", "time"]
            Keyboard = ["keyboard"]
            Mouse = ["mouse"]
            Time = ["time"]

class TooltipType:
    @dataclass
    class Small():
        title: str = ""
    @dataclass
    class Medium():
        title: str = ""
        content: str = ""
    @dataclass
    class Large():
        title: str = ""
        content: str = ""
        
    @dataclass
    class Custom():
        ratio: Any
        title: str = ""
    
    @dataclass
    class BigCustom():
        ratio: Any
        title: str = ""
        content: str = ""
    
class DictAccessMixin:
    def __getitem__(self, key):
        try: return getattr(self, key)
        except AttributeError as e:
            raise KeyError(key) from e
    def __setitem__(self, key, value):
        setattr(self, key, value)
    def get(self, key, default=None):
        return getattr(self, key, default)

@dataclass
class BorderConfig:
    width: int = 1
    color: tuple[int, int, int] | tuple[int, int, int, int] = (255, 255, 255, 255)
    name: str | None = None
    font: Any | None = None

class Counter:
    __slots__ = ('val', 'max_val', 'ended', '_initial_val')
    def __init__(self, val: int | float, max_val: int | float | None = None):
        self.val = val
        self._initial_val = val
        self.max_val = max_val or float("inf")
        self.ended = False
        
    def inc(self, add: int | float = 1):
        self.val += add
        if self.max_val is not None and self.val > self.max_val: 
            self.val = self.max_val
            self.ended = True
            
    def reset(self, reset_value: int | float | None = None): 
        self.val = reset_value or self._initial_val
        self.ended = False

class EnumValidator:
    __slots__ = ('_enum_class', '_handlers')
    def __init__(self, enum_class: type[Enum]):
        object.__setattr__(self, '_enum_class', enum_class)
        object.__setattr__(self, '_handlers', {})

    def __enter__(self) -> 'EnumValidator':
        return self

    def __setattr__(self, name: str, value: Callable[..., Any] | bool) -> None:
        if not __debug__: return
        if name in self._enum_class.__members__:
            self._handlers[name] = value
        else:
            raise AttributeError(f"'{self._enum_class.__name__}' has no member '{name}'")

    def __exit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        if not __debug__: return
        if exc_type is not None: return

        if missing := [name for name in self._enum_class.__members__ if name not in self._handlers]:
            raise NotImplementedError(f"Missing definitions for {self._enum_class.__name__} members: {', '.join(missing)}")


class GlobalsBase:
    def __init__(self):
        pass
    
    @property
    def library(self): 
        return nevu_globals
    
    def modify(self, **kwargs): 
        nevu_globals.update(kwargs)

    @contextlib.contextmanager
    def modify_temp(self, **kwargs):
        saved_state = {}
        added_keys =[]
        
        for key in kwargs:
            if key in nevu_globals:
                saved_state[key] = nevu_globals[key]
            else:
                added_keys.append(key)
        self.modify(**kwargs)
        
        try:
            yield
        finally:
            for key in added_keys:
                if key in nevu_globals:
                    del nevu_globals[key]
            
            for key, old_value in saved_state.items():
                nevu_globals[key] = old_value

nevu_globals = {}