#TypedDicts
from .typehints import WidgetKwargs, LabelKwargs, ButtonKwargs, RectCheckBoxKwargs, InputKwargs, ElementSwitcherKwargs, ProgressBarKwargs, SliderKwargs
#Templates
from .typehints import WidgetTemplate, LabelTemplate, ElementSwitcherTemplate
#Widgets
from .widget import Widget
from .label import Label
from .button import Button
from .empty_widget import EmptyWidget
from .rect_checkbox import RectCheckBox
from .input import Input
from .deprecated import Image, Gif, MusicPlayer #Deprecated
from .element_switcher import ElementSwitcher, Element
from .progress_bar import ProgressBar
from .slider_bar import Slider

__all__ = [
    'Widget', 'Label', 'Button', 'EmptyWidget', 'RectCheckBox', 'Image', 'Gif', 'Input', 'MusicPlayer', 'ElementSwitcher', 'Element', 'ProgressBar', 'Slider'
]