from enum import Enum, auto, StrEnum, IntEnum
from dataclasses import dataclass
from typing import Callable

#Svalka
#faputa approved

class PressType(IntEnum):
    Still = 0
    Fdown = 1
    Down = 2
    Up = 3
    
    WheelDown = -10
    WheelUp = 10
    WheelStill = 5

class Backend(StrEnum):
    Pygame = "pygame"
    Sdl = "sdl" 
    Opengl = "opengl"
    RayLib = "raylib"

class Align(StrEnum):
    CENTER = "center"
    LEFT = "left"
    RIGHT = "right"
    TOP = "top"
    BOTTOM = "bottom"

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
    
    #NEW FUKING RL cache
    RlFont = auto()
    RlText = auto()
    RlTexture = auto()
    RlradTexture = auto()
    RlfinalTexture = auto()
    RlBaseTexture = auto()

class CacheName(StrEnum):
    MAIN = "main"
    PRESERVED = "preversed"
    CUSTOM = "custom"

class AnimationType(Enum):
    Color = auto()
    Size = auto()
    Position = auto()
    Rotation = auto()
    Opacity = auto()
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

class OvItemType(Enum):
    Texture = auto()
    DrawCall = auto()
    
class ConfigLoadType(StrEnum):
    Yaml = "yaml"
    Json = "json"

class RenderConfig(StrEnum):
    Root = "root"
    Style = "style"
    DrawL1 = "draw_l1"
    DrawL2 = "draw_l2"
    DrawL3 = "draw_l3"
    DrawL4 = "draw_l4"

class _RenderArg:
    pass

class RenderArgs:
    class DrawBase(_RenderArg): pass
    class DrawText(_RenderArg): pass
    class DrawEffects(_RenderArg): pass
    @dataclass
    class DrawCustom(_RenderArg):
        custom_func: Callable 
