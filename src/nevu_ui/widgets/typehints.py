from typing import NotRequired, Any, Callable
from dataclasses import dataclass

from nevu_ui.style import Style
from nevu_ui.color import PairColorRole, TupleColorRole
from nevu_ui.nevuobj.typehints import NevuObjectKwargs, NevuObjectTemplate


#=== TypedDicts ===
class WidgetKwargs(NevuObjectKwargs):
    alt: NotRequired[bool]
    clickable: NotRequired[bool]
    hoverable: NotRequired[bool]
    fancy_click_style: NotRequired[bool]
    resize_bg_image: NotRequired[bool]
    z: NotRequired[int]
    inline: NotRequired[bool]
    font_role: NotRequired[PairColorRole]
    _draw_borders: NotRequired[bool]
    _draw_content: NotRequired[bool]

class LabelKwargs(WidgetKwargs):
    words_indent: NotRequired[bool]

class ButtonKwargs(LabelKwargs):
    is_active: NotRequired[bool]
    throw_errors: NotRequired[bool]

class ElementSwitcherKwargs(WidgetKwargs):
    on_content_change: NotRequired[Callable]
    current_index: NotRequired[int]
    button_padding: NotRequired[int]
    arrow_width: NotRequired[int]
    left_text: NotRequired[str]
    left_key: NotRequired[Any]
    right_text: NotRequired[str]
    right_key: NotRequired[Any]

class InputKwargs(WidgetKwargs):
    is_active: NotRequired[bool]
    multiple: NotRequired[bool]
    allow_paste: NotRequired[bool]
    words_indent: NotRequired[bool]
    max_characters: NotRequired[int]
    blacklist: NotRequired[list]
    whitelist: NotRequired[list]
    padding: NotRequired[list | tuple]

class ProgressBarKwargs(WidgetKwargs):
    min_value: NotRequired[int | float]
    min: NotRequired[int | float]
    max_value: NotRequired[int | float]
    max: NotRequired[int | float]
    value: NotRequired[int | float]
    color_pair_role: NotRequired[PairColorRole]
    role: NotRequired[PairColorRole]

class SliderKwargs(WidgetKwargs):
    start: NotRequired[int | float]
    end: NotRequired[int | float]
    step: NotRequired[int | float]
    current_value: NotRequired[Any]
    progress_style: NotRequired[Style]
    padding_x: NotRequired[int]
    padding_y: NotRequired[int]
    tuple_role: NotRequired[TupleColorRole]
    bar_pair_role: NotRequired[PairColorRole]
    
class RectCheckBoxKwargs(WidgetKwargs):
    function: NotRequired[Callable | None]
    on_toggle: NotRequired[Callable | None]
    toggled: NotRequired[bool]
    active: NotRequired[bool]
    active_rect_factor: NotRequired[int | float]
    active_factor: NotRequired[int | float]

#=== Templates ===
@dataclass
class WidgetTemplate(NevuObjectTemplate):
    pass

@dataclass
class LabelTemplate(WidgetTemplate):
    text: str 

@dataclass
class ButtonTemplate(LabelTemplate):
    is_active: bool | None = None
    throw_errors: bool | None = None

@dataclass
class ElementSwitcherTemplate(WidgetTemplate):
    elements: Any | list | None = None