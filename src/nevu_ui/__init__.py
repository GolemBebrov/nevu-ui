from .components.nevuobj import NevuObject  # noqa: I001
from .components._typehints import nevu_object_globals
from .components.widgets import (
    Button,
    Element,
    ElementSwitcher,
    EmptyWidget,
    Input,
    Label,
    ProgressBar,
    RectCheckBox,
    Slider,
    Switch,
    Widget,
)
from .components.layouts import (
    CheckBoxGroup,
    ColorPicker,
    Column,
    Grid,
    LayoutType,
    Panel,
    Row,
    ScrollableColumn,
    ScrollableRow,
    StackColumn,
    StackRow,
    FlexLayout
)
from . import components, core, presentation, utils
from .components._typehints import widget_globals
from .core import size
from .core.annotations import VERSION, Annotations
from .core.classes import BorderConfig, TooltipType, nevu_globals
from .core.callbacks import Callbacks
from .core.enums import (
    Align,
    AnimationType,
    Backend,
    CacheType,
    ConfigLoadType,
    EventType,
    GradientType,
    HoverState,
    LinearSide,
    RadialPosition,
    BindType,
    FlexDirection, FlexJustify
)
from .core.size.units import (
    Fill,
    FillH,
    FillW,
    Gc,
    Gch,
    Gcw,
    Px,
    Vh,
    Vw,
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
)
from .core.state import nevu_state
from .fast import NvVector2
from .fast.nevucache.nevucache import Cache
from .fast.nvrect import NvRect
from .fast.nvrendertex import NvRenderTexture
from .manager import Manager
from .menu import Menu
from .overlay import Tooltip, overlay
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
from .presentation.color import (
    Color,
    ColorPair,
    ColorSubTheme,
    ColorTheme,
    ColorThemeLibrary,
    PairColorRole,
    SubThemeRole,
    TupleColorRole,
)
from .presentation.style import StateVariable, Style, default_style
from .rendering import Gradient
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
    "BorderConfig",
    "Canvas",
    "Window",
    "CacheType",
    "BindType",
    "HoverState",
    "ConfiguredWindow",
    "InitializedWindow",
    "get_all_colorthemes",
    "get_colortheme",
    "NevuObject",
    "Manager",
    "NvVector2",
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
    "RectCheckBox",
    "Input",
    "ElementSwitcher",
    "Element",
    "ProgressBar",
    "Slider",
    "Tooltip",
    "Switch",
    # ===Layouts===
    "LayoutType",
    "Grid",
    "FlexLayout",
    "Row",
    "Column",
    "ScrollableColumn",
    "ScrollableRow",
    "ColorPicker",
    "StackRow",
    "StackColumn",
    "CheckBoxGroup",
    "Panel",
    # ===Utils===
    "time",
    "Time",
    "mouse",
    "keyboard",
    "Cache",
    "InputType",
    "NvRect",
    "load_font",
    "load_image",
    "load_image_texture",
    "gradient_queue",
    "Keys",
    "NvRenderTexture",
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
    "ResizeType",
    "Backend",
    "AnimationType",
    "FlexDirection",
    "FlexJustify",
    # ===Submodules===
    "animations",
    "utils",
    "size",
    "core",
    "presentation",
    "fast",
    "rendering",
    "components",
]

# okabe 1.048596% based, lelush buryatskiy povelevae bagi uydite
print(f"nevu-ui {VERSION}")
