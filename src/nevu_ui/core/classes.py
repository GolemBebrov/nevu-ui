from enum import StrEnum
from dataclasses import dataclass
from typing import TYPE_CHECKING
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
        class Display(StrEnum):
            Classic = "classic"
            Sdl = "sdl"
            Opengl = "opengl"

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
        ratio: NvVector2
        title: str = ""
    
    @dataclass
    class BigCustom():
        ratio: NvVector2
        title: str = ""
        content: str = ""