from .core import size
from .core.annotations import VERSION, Annotations
from .core.classes import TooltipType, nevu_globals
from .components.nevuobject import NevuObject  # noqa: I001
from .components._typehints import nevu_object_globals
from .components.widgets import (
    Button,
    Element,
    ElementSwitcher,
    EmptyWidget,
    Input,
    Label,
    ProgressBar,
    CheckBox,
    Slider,
    Switch,
    Widget,
)
from .components.layouts import (
    Column,
    Grid,
    BaseLayout,
    Row,
    Scroll,
    VScroll,
    HScroll,
    Stack,
    VStack,
    HStack,
    Flex,
    VFlex,
    HFlex,
)
from .components import CheckBoxGroup
from . import components, core, presentation, utils
from .components._typehints import widget_globals

from .cython.callbacks.callbacks import Callbacks
from .core.enums import (
    Align,
    AnimationType,
    Backend,
    CacheType,
    Orientation,
    ConfigLoadType,
    EventType,
    GradientType,
    HoverState,
    LinearSide,
    RadialPosition,
    BindType,
    FlexJustify
)
from .core.size.rules import(
    Fill,
    FillH,
    FillW,
    Gc,
    Gch,
    Gcw,
    Px,
    Vh,
    Vw,
    Auto
)
from .core.size.units import (

    cfill,
    cfillh,
    cfillw,
    cgc,
    cgch,
    cgcw,
    cvh,
    cvw,
    fill,
    fill_all,
    fill_half,
    fill_perc,
    fillh,
    fillw,
    gc,
    gch,
    gcw,
    px,
    vh,
    vw,
    auto,
)
from .core.state import nevu_state
from .cython import Vector2
from .cython.cache.cache import Cache
from .cython.rect import Rect
from .manager import Manager
from .components.layouts.menu import Menu
from .overlay import overlay
from .components import Tooltip
from .parser import (
    apply_config,
    get_all_colors,
    get_all_colorthemes,
    get_all_styles,
    get_color,
    get_colortheme,
    get_style,
)

from .presentation import animations
from .presentation.theme import (
    ColorPair,
    ColorSubTheme,
    ColorTheme,
    ColorThemeLibrary,
    PairColorRole,
    SubThemeRole,
    TupleColorRole,
)
from .presentation.color import Color
from .presentation.style import StateVariable, Style, default_style
from .rendering import Gradient
from .assets.font import FontLibrary
from .utils import InputType, Keys, Time, keyboard, load_font, mouse, time
from .window import (
    ConfiguredWindow,
    InitializedWindow,
    Window,
)
from .rendering.canvas import Canvas

__all__ = [  # noqa: RUF022
    # ===Most Used===
    "Menu",
    "Callbacks",
    "Canvas",
    "Window",
    "CacheType",
    "BindType",
    "FontLibrary",
    "HoverState",
    "ConfiguredWindow",
    "InitializedWindow",
    "get_all_colorthemes",
    "get_colortheme",
    "NevuObject",
    "nevu_object_globals",
    "widget_globals",
    "Manager",
    "Vector2",
    "nevu_state",
    "apply_config",
    "get_style",
    "get_color",
    "get_all_styles",
    "get_all_colors",
    "overlay",
    "TooltipType",
    # ===Widgets===
    "Widget",
    "Label",
    "Button",
    "EmptyWidget",
    "CheckBox",
    "Input",
    "ElementSwitcher",
    "Element",
    "ProgressBar",
    "Slider",
    "Tooltip",
    "Switch",
    # ===Layouts===
    "BaseLayout",
    "Grid",
    "Flex",
    "Row",
    "Column",
    "VScroll",
    "HScroll",
    "Stack",
    "CheckBoxGroup",
    "VStack",
    "HStack",
    "VFlex",
    "HFlex",
    "Scroll",
    # ===Utils===
    "time",
    "Time",
    "mouse",
    "keyboard",
    "Cache",
    "InputType",
    "Rect",
    "load_font",
    "Keys",
    # ===Size vars===
    "Fill",
    "FillW",
    "FillH",
    "Vh",
    "Vw",
    "Gc",
    "Gcw",
    "Gch",
    "fill",
    "fillw",
    "fillh",
    "vh",
    "vw",
    "gc",
    "gcw",
    "gch",
    "px",
    "Px",
    "auto",
    "Auto",
    "cfill",
    "cfillw",
    "cfillh",
    "fill_all",
    "fill_perc",
    "fill_half",
    "cvh",
    "cvw",
    "cgc",
    "cgcw",
    "cgch",
    # ===Color===
    "Color",
    "ColorTheme",
    "ColorSubTheme",
    "ColorPair",
    "ColorThemeLibrary",
    "SubThemeRole",
    "PairColorRole",
    "TupleColorRole",
    # ===Style===
    "Style",
    "default_style",
    "StateVariable",
    "Gradient",
    "ConfigLoadType",
    # ===Enums===
    "Align",
    "LinearSide",
    "RadialPosition",
    "GradientType",
    "EventType",
    "Backend",
    "AnimationType",
    "FlexJustify",
    "Orientation",
    # ===Submodules===
    "animations",
    "utils",
    "size",
    "core",
    "presentation",
    "cython",
    "rendering",
    "components",
]

# okabe 1.048596% based, lelush buryatskiy povelevae bagi uydite
# os.environ(it wont be implemented womp womp)
print(f"nevu-ui {VERSION}")
