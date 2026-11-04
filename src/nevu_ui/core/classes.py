import contextlib
from dataclasses import dataclass
from typing import TYPE_CHECKING, Any, TypeGuard

if TYPE_CHECKING:
    from nevu_ui import Vector2
from nevu_ui.core.enums import Backend


class ConfigType:
    class Window:
        class Size:
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
    class Small:
        title: str = ""

    @dataclass
    class Medium:
        title: str = ""
        content: str = ""

    @dataclass
    class Large:
        title: str = ""
        content: str = ""

    @dataclass
    class Custom:
        ratio: "Vector2"
        title: str = ""

    @dataclass
    class BigCustom:
        ratio: "Vector2"
        title: str = ""
        content: str = ""


class DictAccessMixin:
    def __getitem__(self, key):
        try:
            return getattr(self, key)
        except AttributeError as e:
            raise KeyError(key) from e

    def __setitem__(self, key, value):
        setattr(self, key, value)

    def get(self, key, default=None):
        return getattr(self, key, default)

class Counter:
    __slots__ = ("val", "max_val", "ended", "_initial_val")

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
        self.val = reset_value if reset_value is not None else self._initial_val
        self.ended = False

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
        added_keys = []

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

# Namespace



class SurfaceLike:
    def blit(self, surface, dest): ...
    def fill(self, color): ...
    @property
    def width(self) -> int | float: ...
    @property
    def height(self) -> int | float: ...
    @staticmethod
    def as_type(type: Any) -> TypeGuard["SurfaceLike"]:
        return True

class Element:
    __slots__ = ["id", "text"]

    def __init__(self, text, id: str | None = None):
        self.text = text
        self.id = id


class Elements:
    @staticmethod
    def create(*items):
        final_list = []
        element_list = []
        element_pair = []
        try:
            for item in items:
                if isinstance(item, Element):
                    element_list.append(item)
                    continue
                elif not isinstance(item, str):
                    if isinstance(item, (list, tuple)) and len(item) == 2:
                        element_pair = [str(item[0]), item[1] if item[1] else None]
                    else:
                        element_pair = [str(item), None]
                else:
                    element_pair = [item, None]
                final_list.append(element_pair)
        except Exception as e:
            raise ValueError("Some objects cannot be converted into str", e) from e

        element_list.extend(Element(pair[0], pair[1]) for pair in final_list)
        return element_list
