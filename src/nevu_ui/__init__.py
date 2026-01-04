from . import animations
from . import utils
from . import size

from .menu import Menu
from .nevuobj import NevuObject
from .ui_manager import Manager
from .fast import NvVector2
from .rendering import Gradient
from .core.state import nevu_state
from .struct import apply_config
from .overlay import overlay

from .size.units import (
    SizeRule, PercentSizeRule, SizeUnit, Fill, FillW, FillH, Vh, Vw, Gc, Gcw, Gch, fill, fillw, fillh, vh, vw, gc, gcw, gch, px, Px, cfill, cfillw, cfillh, cvh, cvw, cgc, cgcw, cgch
)
from .color import (
    Color, ColorTheme, ColorSubTheme, ColorPair, ColorThemeLibrary, SubThemeRole, PairColorRole, TupleColorRole
)
from .style import (
    Style, default_style, StateVariable
)
from .core.enums import (
    Align, Quality, HoverState, LinearSide, RadialPosition, GradientType, CacheName, CacheType, EventType
)
from .widgets import (
    Widget, Label, Button, EmptyWidget, RectCheckBox, Image, Gif, Input, MusicPlayer, ElementSwitcher, Element, ProgressBar, Slider
)
from .layouts import (
    LayoutType, Grid, Row, Column, ScrollableColumn, ScrollableRow, IntPickerGrid, Pages, Gallery_Pages, StackRow, StackColumn, CheckBoxGroup
)
from .utils import (
    time, Time, mouse, Mouse, keyboard, Keyboard, Cache, NevuEvent, InputType
)
from .window.window import (
    Window, ResizeType, ZRequest, ConfiguredWindow 
)

__all__ = [
    #===Most Used===
    "Menu", "Window", "ConfiguredWindow", "NevuObject", "Manager", "NvVector2", "nevu_state", "apply_config",
    #===Widgets===
    "Widget", "Label", "Button", "EmptyWidget", "RectCheckBox", "Image", "Gif", "Input", "MusicPlayer", "ElementSwitcher", "Element", "ProgressBar", "Slider",
    #===Layouts===
    "LayoutType", "Grid", "Row", "Column", "ScrollableColumn", "ScrollableRow", "IntPickerGrid", "Pages", "Gallery_Pages", "StackRow", "StackColumn", "CheckBoxGroup",
    #===Utils===
    "time", "Time", "mouse", "Mouse", "keyboard", "Keyboard", "Cache", "NevuEvent", "InputType",
    #===Size vars===
    "Fill", "FillW", "FillH", "Vh", "Vw", "Gc", "Gcw", "Gch", "fill", "fillw", "fillh", "vh", "vw", "gc", "gcw", "gch", "px", "Px", "cfill", "cfillw", "cfillh", "cvh", "cvw", "cgc", "cgcw", "cgch",
    #===Color===
    "Color", "ColorTheme", "ColorSubTheme", "ColorPair", "ColorThemeLibrary", "SubThemeRole", "PairColorRole", "TupleColorRole",
    #===Style===
    "Style", "default_style", "StateVariable", "Gradient",
    #===Enums===
    "Align", "LinearSide", "RadialPosition", "GradientType", "EventType",
    #===Submodules===
    "animations", "utils", "size"
]

version = "0.6.7"
print(f"nevu-ui {version}")