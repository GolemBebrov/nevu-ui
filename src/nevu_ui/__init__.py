
from . import core

from . import utils
from . import presentation
from . import components

from .presentation import animations
from .core import size

from .components.nevuobj import NevuObject
from .menu import Menu

from .manager import Manager
from .fast import NvVector2
from .fast.nvrect import NvRect
from .fast.nvrendertex import NvRenderTexture

from .rendering import Gradient, gradient_queue
from .core.state import nevu_state
from .json_parser import apply_config, get_style, get_color, get_all_styles, get_all_colors, get_colortheme, get_all_colorthemes
from .overlay import overlay, Tooltip

from .core.size.units import (
    SizeRule, PercentSizeRule, SizeUnit, Fill, FillW, FillH, Vh, Vw, Gc, Gcw, Gch, fill, fillw, fillh, vh, vw, gc, gcw, gch, px, Px, cfill, cfillw, cfillh, cvh, cvw, cgc, cgcw, cgch
)
from .presentation.color import (
    Color, ColorTheme, ColorSubTheme, ColorPair, ColorThemeLibrary, SubThemeRole, PairColorRole, TupleColorRole
)
from .presentation.style import (
    Style, default_style, StateVariable
)
from .core.enums import (
    Align, Quality, HoverState, LinearSide, RadialPosition, GradientType, CacheName, CacheType, EventType, Backend, ConfigLoadType
)
from .core.classes import TooltipType, BorderConfig
from .components.widgets import (
    Widget, Label, Button, EmptyWidget, RectCheckBox, Image, Gif, Input, MusicPlayer, ElementSwitcher, Element, ProgressBar, Slider
)
from .components.layouts import (
    LayoutType, Grid, Row, Column, ScrollableColumn, ScrollableRow, ColorPicker, Pages, Gallery_Pages, StackRow, StackColumn, CheckBoxGroup
)
from .utils import (
    time, Time, keyboard, Cache, NevuEvent, InputType, mouse, load_font, load_image, load_image_texture, Keys
)
from .window.window import (
    Window, ResizeType, ZRequest, ConfiguredWindow
)

__all__ = [
    #===Most Used===
    "Menu", "Window", "ConfiguredWindow", "NevuObject", "Manager", "NvVector2", "nevu_state", "apply_config", "get_style", "get_color", "get_all_styles", "get_all_colors", "overlay", "TooltipType",
    #===Widgets===
    "Widget", "Label", "Button", "EmptyWidget", "RectCheckBox", "Image", "Gif", "Input", "MusicPlayer", "ElementSwitcher", "Element", "ProgressBar", "Slider", "Tooltip",
    #===Layouts===
    "LayoutType", "Grid", "Row", "Column", "ScrollableColumn", "ScrollableRow", "ColorPicker", "Pages", "Gallery_Pages", "StackRow", "StackColumn", "CheckBoxGroup",
    #===Utils===
    "time", "Time", "mouse", "keyboard", "Cache", "NevuEvent", "InputType", "NvRect", "load_font", "load_image", "load_image_texture", "gradient_queue", "Keys", "NvRenderTexture",
    #===Size vars===
    "Fill", "FillW", "FillH", "Vh", "Vw", "Gc", "Gcw", "Gch", "fill", "fillw", "fillh", "vh", "vw", "gc", "gcw", "gch", "px", "Px", "cfill", "cfillw", "cfillh", "cvh", "cvw", "cgc", "cgcw", "cgch",
    #===Color===
    "Color", "ColorTheme", "ColorSubTheme", "ColorPair", "ColorThemeLibrary", "SubThemeRole", "PairColorRole", "TupleColorRole",
    #===Style===
    "Style", "default_style", "StateVariable", "Gradient", "ConfigLoadType",
    #===Enums===
    "Align", "LinearSide", "RadialPosition", "GradientType", "EventType", "ResizeType", "Backend",
    #===Submodules===
    "animations", "utils", "size"
]

version = "0.7.3" #okabe 1.048596% based, lelush buryatskiy povelevae bagi uydite
print(f"nevu-ui {version}")