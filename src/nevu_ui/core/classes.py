from enum import StrEnum
from dataclasses import dataclass
from typing import Any
from typing import TYPE_CHECKING
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