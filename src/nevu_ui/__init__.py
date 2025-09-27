from .menu import Menu
from .nevuobj import NevuObject
from .ui_manager import Manager
from . import rendering
from . import animations
from . import utils
from . import fast_nvvector2
from .color import (
    Color, Color_Type, ColorTheme, ColorSubTheme, ColorPair, ColorThemeLibrary, SubThemeRole, PairColorRole, TupleColorRole
)
from .style import (
    Style, default_style, Gradient
)
from .core_types import (
    Align, SizeRule, PercentSizeRule, SizeUnit, 
    Vh, vh, Vw, vw, Fill, fill, Px, px, 
    Quality, HoverState, Events,
    LinearSide, RadialPosition, GradientType
)
from .widgets import (
    Widget, Label, Button, Empty_Widget, RectCheckBox, Image, GifWidget, Input, MusicPlayer
)
from .layouts import (
    LayoutType, Grid, Row, Column, Scrollable, IntPickerGrid, Pages, Gallery_Pages, StackRow, StackColumn, CheckBoxGroup
)

from .utils import (
    time, Time, mouse, Mouse, keyboard, Keyboard,
    Cache, CacheName, CacheType, NevuEvent, InputType, EventType, NvVector2
)
from .window import (
    Window, ResizeType, ZRequest #Only request
)

__all__ = [
    #### color.py ####
    'Color', 'Color_Type', 'ColorTheme', 'ColorSubTheme', 'ColorPair', 'ColorThemeLibrary', 'SubThemeRole', 'PairColorRole', 'TupleColorRole', 
    #### style.py ####
    'Style', 'default_style', 'Gradient',
    #### core_types.py ####
    'Align', 'SizeRule', 'PercentSizeRule', 'SizeUnit', 'Vh', 'vh', 'Vw', 'vw', 'Fill', 'fill', 'Px', 'px', 
    'Quality', 'HoverState', 'Events', 'LinearSide', 'RadialPosition', 'GradientType', 
    #### widgets.py ####
    'Widget', 'Label', 'Button', 'Empty_Widget', 'RectCheckBox', 'Image', 'GifWidget', 'Input', 'MusicPlayer',
    #### layouts.py ####
    'LayoutType', 'Grid', 'Row', 'Column', 'Scrollable', 'IntPickerGrid', 'Pages', 'Gallery_Pages', 'StackRow', 'StackColumn', 'CheckBoxGroup', 
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

version = "0.5.X"

print(f"Nevu UI version:{version}")