from .menu import Menu
from .nevuobj import NevuObject
from .ui_manager import Manager

from . import animations
from . import utils
from .fast import NvVector2
from .color import (
    Color, ColorTheme, ColorSubTheme, ColorPair, ColorThemeLibrary, SubThemeRole, PairColorRole, TupleColorRole
)
from .core.state import nevu_state
from .style import (
    Style, default_style, StateVariable
)
from .struct import apply_config
from .core.enums import (
    Align, 
    Quality, HoverState,
    LinearSide, RadialPosition, GradientType,CacheName, CacheType, EventType
)
from . import size
from .size.units import SizeRule, PercentSizeRule, SizeUnit, Fill, FillW, FillH, Vh, Vw, Gc, Gcw, Gch, fill, fillw, fillh, vh, vw, gc, gcw, gch, px, Px, cfill, cfillw, cfillh, cvh, cvw, cgc, cgcw, cgch
from .widgets import (
    Widget, Label, Button, EmptyWidget, RectCheckBox, Image, Gif, Input, MusicPlayer, ElementSwitcher, Element, ProgressBar, Slider
)
from .layouts import (
    LayoutType, Grid, Row, Column, ScrollableColumn, ScrollableRow, IntPickerGrid, Pages, Gallery_Pages, StackRow, StackColumn, CheckBoxGroup
)
from .rendering import (
    Gradient
)
from .utils import (
    time, Time, mouse, Mouse, keyboard, Keyboard,
    Cache, NevuEvent, InputType
)
from .window.window import (
    Window, ResizeType, ZRequest, ConfiguredWindow #Only request
)

__all__ = [
    #### color.py ####
    'Color', 'Color_Type', 'ColorTheme', 'ColorSubTheme', 'ColorPair', 'ColorThemeLibrary', 'SubThemeRole', 'PairColorRole', 'TupleColorRole', 
    #### style.py ####
    'Style', 'default_style', 'Gradient',
    #### core_types.py ####
    'Align', 'SizeRule', 'PercentSizeRule', 'SizeUnit', 'Vh', 'vh', 'Vw', 'vw', 'Fill', 'fill', 'Px', 'px', 'Element',
    'Quality', 'HoverState', 'Events', 'LinearSide', 'RadialPosition', 'GradientType', 
    #### widgets.py ####
    'Widget', 'Label', 'Button', 'EmptyWidget', 'RectCheckBox', 'ElementSwitcher', 'ProgressBar', 'Image', 'Gif', 'Input', 'MusicPlayer', 'Slider',
    #### layouts.py ####
    'LayoutType', 'Grid', 'Row', 'Column', 'ScrollableColumn', 'ScrollableRow', 'IntPickerGrid', 'Pages', 'Gallery_Pages', 'StackRow', 'StackColumn', 'CheckBoxGroup', 
    #### menu.py ####
    'Menu',
    #### utils.py ####
    'time', 'mouse', 'Time', 'Mouse', 'Keyboard', 'keyboard', 'Cache', 'CacheName', 'CacheType', 'NevuEvent', 'EventType','InputType', 'NvVector2', 
    'utils', 
    #### ui_manager.py ####
    'Manager',
    #### window.py ####
    'Window', 'ZRequest', 'ResizeType',
    #### rendering.py ####
    'rendering', 
    #### nevuobj.py ####
    'NevuObject', 
    #### animations.py ####
    'animations', 
]

version = "0.6.6"

print(f"nevu-ui {version}")