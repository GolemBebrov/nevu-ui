from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from typing import TYPE_CHECKING, Any, TypedDict, Unpack

from nevu_ui.core import Annotations
from nevu_ui.core.callbacks import Callbacks
from nevu_ui.core.classes import DictAccessMixin, GlobalsBase
from nevu_ui.core.enums import Align, FlexDirection, FlexJustify, SwitchAxis
from nevu_ui.fast.nvvector2 import NvVector2
from nevu_ui.overlay.tooltip import Tooltip
from nevu_ui.presentation.animations import AnimationManager
from nevu_ui.presentation.color import SubThemeRole
from nevu_ui.presentation.style import Style
from nevu_ui.rendering.canvas import Canvas

if TYPE_CHECKING:
    from nevu_ui.components.layouts import LayoutType
    from nevu_ui.components.layouts.misc.checkbox_group import CheckBoxGroup
    from nevu_ui.components.nevuobj import NevuObject
    from nevu_ui.components.widgets import Input, Label, ProgressBar, Switch, Widget
    from nevu_ui.presentation.color import PairColorRole, SubThemeRole, TupleColorRole
    from nevu_ui.presentation.style import Style

class _NevuObjectKwargsBase(TypedDict, total=False):
    id: Any
    single_instance: bool
    tooltip: Tooltip
    subtheme_role: SubThemeRole
    callbacks: Callbacks | dict
    canvas: Canvas
    bg_variant: bool
    start_pos: list | tuple | NvVector2

class _NevuObjectKwargsShort(TypedDict, total=False):
    z: int
    anim_manager: AnimationManager

class _NevuObjectKwargsLong(TypedDict, total=False):
    depth: int
    animation_manager: AnimationManager

class _NevuObjectKwargsShortFull(_NevuObjectKwargsBase, _NevuObjectKwargsShort): ...
class _NevuObjectKwargsLongFull(_NevuObjectKwargsBase, _NevuObjectKwargsLong): ...
class _NevuObjectKwargs(_NevuObjectKwargsShortFull, _NevuObjectKwargsLongFull): ...


@dataclass
class _NevuObjectTemplate(DictAccessMixin):
    size: Annotations.nevuobj_size


class _NevuObjectGlobalsKwargs(TypedDict, total=False):
    size: Annotations.nevuobj_size
    style: Style | str


class _NevuObjectGlobalsKwargsFull(_NevuObjectGlobalsKwargs, _NevuObjectKwargs): ...
class _NevuObjectGlobals(GlobalsBase):
    def modify(self, **kwargs: Unpack[_NevuObjectGlobalsKwargsFull]):
        return super().modify(**kwargs)

    def modify_temp(self, **kwargs: Unpack[_NevuObjectGlobalsKwargsFull]):
        return super().modify_temp(**kwargs)

class _WidgetKwargsBase(TypedDict, total=False):
    clickable: bool
    hoverable: bool
    invert_on_click: bool
    inline: bool
    font_role: PairColorRole
    draw_borders: bool
    draw_content: bool
    ripple_effect: bool
    animate_color_change: bool
    override_color: tuple[int, ...] | None
    subtheme_role: SubThemeRole
    glassy: bool

class _WidgetKwargsShort(_NevuObjectKwargsShortFull, total=False):
    alt: bool

class _WidgetKwargsLong(_NevuObjectKwargsLongFull, total=False):
    inverted: bool

class _WidgetKwargsShortFull(_WidgetKwargsBase, _WidgetKwargsShort, total=False): ...
class _WidgetKwargsLongFull(_WidgetKwargsBase, _WidgetKwargsLong, total=False): ...
class _WidgetKwargs(_WidgetKwargsShortFull, _WidgetKwargsLongFull, total=False): ...


class _SwitchKwargs(_WidgetKwargs, total=False):
    axis: SwitchAxis
    on_switch_change: Callable[[Switch, bool], None]


class _LabelKwargs(_WidgetKwargs, total=False):
    words_indent: bool
    on_text_change: Callable[[Label, str], None]


class _ButtonKwargs(_LabelKwargs, total=False):
    is_active: bool
    throw_errors: bool


class _ElementSwitcherKwargs(_WidgetKwargs, total=False):
    on_content_change: Callable
    current_index: int
    button_padding: int
    words_indent: bool
    arrow_width: int
    left_text: str
    left_key: Any
    right_text: str
    right_key: Any


class _InputKwargs(_WidgetKwargs, total=False):
    is_active: bool
    multi_line: bool
    allow_paste: bool
    words_indent: bool
    max_characters: int
    blacklist: list | tuple | str
    whitelist: list | tuple | str
    padding: list | tuple
    cursor_width: int
    default: str
    placeholder: str
    on_change_function: Callable[[Input, str], None] | None


class _ProgressBarKwargsLong(TypedDict, total=False):
    start_value: float
    end_value: float
    current_value: float
    filled_rect_role: PairColorRole
    on_current_value_change: Callable[[ProgressBar, float], None]


class _ProgressBarKwargsShort(TypedDict, total=False):
    start: float
    end: float
    current: float
    role: PairColorRole
    on_value_change: Callable[[ProgressBar, float], None]


class _ProgressBarKwargsLongFull(_ProgressBarKwargsLong, _WidgetKwargs): ...
class _ProgressBarKwargsShortFull(_ProgressBarKwargsShort, _WidgetKwargs): ...
class _ProgressBarKwargs(_ProgressBarKwargsLongFull, _ProgressBarKwargsShortFull, _WidgetKwargs): ...


class _SliderKwargsBase(TypedDict, total=False):
    bar_style: Style
    step: float
    bar_font_role: TupleColorRole

class _SliderKwargsShort(_ProgressBarKwargsShort, _SliderKwargsBase, total=False):
    pad_x: int
    pad_y: int

class _SliderKwargsLong(_ProgressBarKwargsLong, _SliderKwargsBase, total=False):
    padding_x: int
    padding_y: int

class _SliderKwargsShortFull(_SliderKwargsShort, _WidgetKwargs): ...
class _SliderKwargsLongFull(_SliderKwargsLong, _WidgetKwargs): ...
class _SliderKwargs(_SliderKwargsShortFull, _SliderKwargsLongFull, _WidgetKwargs): ...


class _RectCheckBoxKwargsBase(TypedDict, total=False):
    toggled: bool
    toggled_rect_opacity: int

class _RectCheckBoxKwargsShort(_RectCheckBoxKwargsBase, total=False):
    on_toggle: Callable | None
    group: CheckBoxGroup
    toggled_scale: float

class _RectCheckBoxKwargsLong(_RectCheckBoxKwargsBase, total=False):
    on_toggle_function: Callable | None
    checkbox_group: CheckBoxGroup
    toggled_rect_scale: float

class _RectCheckBoxKwargsShortFull(_RectCheckBoxKwargsShort, _WidgetKwargs): ...
class _RectCheckBoxKwargsLongFull(_RectCheckBoxKwargsLong, _WidgetKwargs): ...
class _RectCheckBoxKwargs(_RectCheckBoxKwargsShortFull, _RectCheckBoxKwargsLongFull, _WidgetKwargs): ...


@dataclass
class _WidgetTemplate(_NevuObjectTemplate): ...

@dataclass
class _LabelTemplate(_WidgetTemplate):
    text: str

@dataclass
class _ElementSwitcherTemplate(_WidgetTemplate):
    elements: Any | list | None = None

@dataclass
class _InputTemplate(_WidgetTemplate):
    text: str

@dataclass
class _SwitchTemplate(_WidgetTemplate):
    state: bool


class _WidgetGlobalsKwargs(_NevuObjectGlobalsKwargsFull, _WidgetKwargs): ...
class _WidgetGlobals(GlobalsBase):
    def modify(self, **kwargs: Unpack[_WidgetGlobalsKwargs]):
        return super().modify(**kwargs)

    def modify_temp(self, **kwargs: Unpack[_WidgetGlobalsKwargs]):
        return super().modify_temp(**kwargs)


class _LayoutTypeKwargs(_NevuObjectKwargs, total=False):
    bg_widget: Widget


class _StackKwargsBase(TypedDict, total=False):
    spacing: float
    basic_alignment: Align

class _StackKwargs(_StackKwargsBase, _LayoutTypeKwargs): ...


class _ScrollableKwargsBase(_LayoutTypeKwargs, total=False):
    arrow_scroll_power: int
    wheel_scroll_power: int
    inverted_scrolling: bool
    scrollbar_perc: NvVector2 | None
    basic_alignment: Align
    append_key: Any
    descend_key: Any
    spacing: float

class _ScrollableKwargs(_ScrollableKwargsBase, _LayoutTypeKwargs): ...


class _Grid_Specifics_rc(TypedDict, total=False):
    row: float
    column: float

class _Grid_Specifics_xy(TypedDict, total=False):
    x: float
    y: float

class _GridKwargs_rc(_Grid_Specifics_rc, _LayoutTypeKwargs): ...
class _GridKwargs_xy(_Grid_Specifics_xy, _LayoutTypeKwargs): ...
class _GridKwargs_uni(_GridKwargs_rc, _GridKwargs_xy, _LayoutTypeKwargs): ...

class _MenuKwargs(_LayoutTypeKwargs, total=False):
    main_layout: LayoutType

class _ColorPickerKwargs(_GridKwargs_uni, total=False):
    on_change_function: Any
    raise_errors: bool
    item_size: NvVector2
    margin: int
    input_style: Style
    label_style: Style


class _FlexLayoutKwargs(_LayoutTypeKwargs, total=False):
    direction: FlexDirection
    wrap: bool
    justify_content: FlexJustify
    align_items: Align
    gap: int | float | NvVector2
    max_wrap_size: int | float


@dataclass
class _LayoutTemplate(_NevuObjectTemplate):
    content: list | None = None


@dataclass
class _GridTemplate(_NevuObjectTemplate):
    content: dict[tuple[int | float, int | float], NevuObject] | None = None


@dataclass
class _GridTemplateShort(_NevuObjectTemplate):
    content: dict[int | float, NevuObject] | None = None


@dataclass
class _AlignTemplate(_NevuObjectTemplate):
    content: list[tuple[Align, NevuObject]] | None = None

class KwargsLibrary:

    # NevuObject
    type NevuObjectAll = _NevuObjectKwargs
    type NevuObjectShort = _NevuObjectKwargsShort
    type NevuObjectLong = _NevuObjectKwargsLong

    # Widget
    type WidgetAll = _WidgetKwargs
    type WidgetShort = _WidgetKwargsShortFull
    type WidgetLong = _WidgetKwargsLongFull

    # Progressbar
    type ProgressbarAll = _ProgressBarKwargs
    type ProgressbarShort = _ProgressBarKwargsShortFull
    type ProgressbarLong = _ProgressBarKwargsLongFull

    # Slider
    type SliderAll = _SliderKwargs
    type SliderShort = _SliderKwargsShortFull
    type SliderLong = _SliderKwargsLongFull

    # Checkbox
    type CheckboxAll = _RectCheckBoxKwargs
    type CheckboxShort = _RectCheckBoxKwargsShortFull
    type CheckboxLong = _RectCheckBoxKwargsLongFull

    # Switch
    type SwitchAll = _SwitchKwargs

    # Label
    type LabelAll = _LabelKwargs

    # Button
    type ButtonAll = _ButtonKwargs

    # ElementSwitcher
    type ElementSwitcherAll = _ElementSwitcherKwargs

    # Input
    type InputAll = _InputKwargs

    # Layout
    type LayoutAll = _LayoutTypeKwargs

    # Stack
    type StackAll = _StackKwargs

    # Scrollable
    type ScrollableAll = _ScrollableKwargs

    # Grid
    type GridAll = _GridKwargs_uni
    type GridShort = _GridKwargs_xy
    type GridLong = _GridKwargs_rc

    # ColorPicker
    type ColorPickerAll = _ColorPickerKwargs

    # Flex
    type FlexLayoutAll = _FlexLayoutKwargs

nevu_object_globals = _NevuObjectGlobals()
widget_globals = _WidgetGlobals()
