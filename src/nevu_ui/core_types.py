from enum import Enum, auto
class Align(Enum):
    CENTER = auto()
    LEFT = auto()
    RIGHT = auto()
    TOP = auto()
    BOTTOM = auto()


class SizeRule:
    def __init__(self, value: int):
        self.value = value
class PercentSizeRule(SizeRule):
    def __init__(self, value: int) -> None:
        if value < 0 or value > 100:
            raise ValueError("percentage must be between 0 and 100")
        self.value = value

class SizeUnit:
    def __init__(self, size_rule, supported_types = None) -> None:
        self._supported_types = (int) if supported_types is None else supported_types
        self._size_rule = size_rule
    def _create_rule(self, other_value):
        if isinstance(other_value, self._supported_types):
            return self._size_rule(other_value)
        return NotImplemented
    def __rmul__(self, other_value):
        return self._create_rule(other_value)
    def __mul__(self, other_value):
        return self._create_rule(other_value)

#------ SizeRules ------
class Fill(PercentSizeRule): pass
class Px(SizeRule): pass
class Vh(PercentSizeRule): pass
class Vw(PercentSizeRule): pass
#------ SizeRules ------


#------ SizeUnits ------
px = SizeUnit(Px)
fill = SizeUnit(Fill)
vh = SizeUnit(Vh)
vw = SizeUnit(Vw)
#------ SizeUnits ------

class Quality(Enum):
    Poor = auto()
    Medium = auto()
    Decent = auto()
    Good = auto()
    Best = auto()

_QUALITY_TO_RESOLUTION = {
    Quality.Poor:   1,
    Quality.Medium: 2,
    Quality.Decent: 4,
    Quality.Good:   5,
    Quality.Best:   6,
}

class HoverState(Enum):
    UN_HOVERED = auto()
    HOVERED = auto()
    CLICKED = auto()