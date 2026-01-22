from enum import Enum, auto, StrEnum, IntEnum

#Svalka
#faputa approved


class Align(Enum):
    CENTER = auto()
    LEFT = auto()
    RIGHT = auto()
    TOP = auto()
    BOTTOM = auto()

class Malign(Enum):
    """This is a mirror of Align with PascalCase"""
    Center = Align.CENTER
    Left = Align.LEFT
    Right = Align.RIGHT
    Top = Align.TOP
    Bottom = Align.BOTTOM

class ConstantLayer(IntEnum):
    Top = 1
    Basic = 2
    Complicated = 3
    Lazy = 4

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

class AnimationManagerState(Enum):
    START = auto()
    CONTINUOUS = auto()
    TRANSITION = auto()
    IDLE = auto()
    ENDED = auto()

class GradientConfig(StrEnum): pass

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

class RenderMode(Enum): # TODO: make use for this
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
    Texture = auto()

class CacheName(StrEnum):
    MAIN = "main"
    PRESERVED = "preversed"
    CUSTOM = "custom"

class AnimationType(Enum):
    COLOR = auto()
    SIZE = auto()
    POSITION = auto()
    ROTATION = auto()
    OPACITY = auto()
    _not_used = auto()

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
    OnChange = auto()

class ZRequestType(Enum):
    HoverCandidate = auto()
    Action = auto()
    Unclick = auto()

class ScrollBarType(StrEnum):
    Vertical = "vertical"
    Horizontal = "horizontal"

class HoverState(Enum):
    UN_HOVERED = auto()
    HOVERED = auto()
    CLICKED = auto()