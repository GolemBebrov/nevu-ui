from enum import Enum, auto, StrEnum

class Align(Enum):
    CENTER = auto()
    LEFT = auto()
    RIGHT = auto()
    TOP = auto()
    BOTTOM = auto()

class SizeRule:
    __slots__ = ('value')
    def __init__(self, value: int):
        self.value = value
class PercentSizeRule(SizeRule):
    def __init__(self, value: int) -> None:
        if value < 0 or value > 100:
            raise ValueError("percentage must be between 0 and 100")
        self.value = value

class SizeUnit:
    __slots__ = ('_supported_types', '_size_rule')
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

class Events:
    __slots__ = ('content', 'on_add')
    def __init__(self):
        self.content = []
        self.on_add = self._default_on_add_hook

    def add(self, event):
        self.content.append(event)
    
    def _default_on_add_hook(self):
        pass

class GradientConfig(StrEnum):
    pass

class LinearSide(GradientConfig):
    Right = 'to right'
    Left = 'to left'
    Top = 'to top'
    Bottom = 'to bottom'
    TopRight = 'to top right'
    TopLeft = 'to top left'
    BottomRight = 'to bottom right'
    BottomLeft = 'to bottom left'

class RadialPosition(GradientConfig):
    Center = 'center'
    TopCenter = 'top center'
    TopLeft = 'top left'
    TopRight = 'top right'
    BottomCenter = 'bottom center'
    BottomLeft = 'bottom left'
    BottomRight = 'bottom right'

class GradientType(StrEnum):
    Linear = 'linear'
    Radial = 'radial'

class ResizeType(Enum):
    CropToRatio = auto()
    FillAllScreen = auto()
    ResizeFromOriginal = auto()

class RenderMode(Enum): 
    AA = auto()
    SDF = auto()

class CacheType(Enum):
    Coords = auto()
    RelSize = auto()
    Surface = auto()
    Gradient = auto()
    Image = auto()
    Scaled_Image = auto()
    Borders = auto()
    Scaled_Borders = auto()
    Scaled_Background = auto()
    Scaled_Gradient = auto()
    Background = auto()

class CacheName(StrEnum):
    MAIN = "main"
    PREVERSED = "preversed"
    CUSTOM = "custom"

class EventType(Enum):
    Resize = auto()
    Render = auto()
    Draw = auto()
    Update = auto()
    OnKeyUp = auto()
    OnKeyDown = auto()
    OnKeyUpAbandon = auto()
    OnHover = auto()
    OnUnhover = auto()
    OnMouseScroll = auto()
    OnCopy = auto()

class ZRequestType(Enum):
    HoverCandidate = auto()
    Action = auto()
    Unclick = auto()

class ScrollBarType(StrEnum):
    Vertical = "vertical"
    Horizontal = "horizontal"

class TooltipType(StrEnum):
    Small = "small"
    Medium = "medium"
    Large = "large"