# TypedDicts
from .button import Button
from .deprecated import Gif, Image, MusicPlayer  # Deprecated
from .element_switcher import Element, ElementSwitcher
from .empty_widget import EmptyWidget
from .input import Input
from .label import Label
from .progress_bar import ProgressBar
from .rect_checkbox import RectCheckBox
from .slider_bar import Slider
from .switch import Switch

# Templates
from .typehints import (
    ButtonKwargs,
    ElementSwitcherKwargs,
    ElementSwitcherTemplate,
    InputKwargs,
    LabelKwargs,
    LabelTemplate,
    ProgressBarKwargs,
    RectCheckBoxKwargs,
    SliderKwargs,
    SwitchKwargs,
    SwitchTemplate,
    WidgetKwargs,
    WidgetTemplate,
)

# Widgets
from .widget import Widget

__all__ = [
    "Widget",
    "Label",
    "Button",
    "EmptyWidget",
    "RectCheckBox",
    "Image",
    "Gif",
    "Input",
    "MusicPlayer",
    "ElementSwitcher",
    "Element",
    "ProgressBar",
    "Slider",
]
