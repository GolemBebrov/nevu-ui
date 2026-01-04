from enum import StrEnum

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
