from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from typing import TYPE_CHECKING, Any, NotRequired, TypedDict, Unpack

from nevu_ui.core import Annotations
from nevu_ui.core.callbacks import Callbacks
from nevu_ui.core.classes import BorderConfig, DictAccessMixin, GlobalsBase
from nevu_ui.core.enums import Align, FlexDirection, FlexJustify, SwitchAxis
from nevu_ui.fast.nvvector2 import NvVector2
from nevu_ui.overlay.tooltip import Tooltip
from nevu_ui.presentation.animations import AnimationManager
from nevu_ui.presentation.color import SubThemeRole
from nevu_ui.presentation.style import Style
from nevu_ui.rendering.canvas import Canvas

if TYPE_CHECKING:
    from nevu_ui.components.layouts.misc.checkbox_group import CheckBoxGroup
    from nevu_ui.components.nevuobj import NevuObject
    from nevu_ui.components.widgets import Input, Label, ProgressBar, Switch
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


class _NevuObjectKwargsShort(TypedDict, total=False):
    z: int
    anim_manager: AnimationManager


class _NevuObjectKwargsLong(TypedDict, total=False):
    depth: int
    animation_manager: AnimationManager


class NevuObjectKwargsShort(_NevuObjectKwargsBase, _NevuObjectKwargsShort):
    pass


class NevuObjectKwargsLong(_NevuObjectKwargsBase, _NevuObjectKwargsLong):
    pass


class NevuObjectKwargs(NevuObjectKwargsShort, NevuObjectKwargsLong):
    pass


@dataclass
class NevuObjectTemplate(DictAccessMixin):
    size: Annotations.nevuobj_size


class _NevuObjecGlobalsKwargs(TypedDict):
    size: NotRequired[Annotations.nevuobj_size]
    style: NotRequired[Style | str]


class NevuObjectGlobalsKwargs(_NevuObjecGlobalsKwargs, NevuObjectKwargs):
    pass


class NevuObjectGlobals(GlobalsBase):
    def modify(self, **kwargs: Unpack[NevuObjectGlobalsKwargs]):
        return super().modify(**kwargs)

    def modify_temp(self, **kwargs: Unpack[NevuObjectGlobalsKwargs]):
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


class _WidgetKwargsShort(NevuObjectKwargsShort, total=False):
    alt: bool


class _WidgetKwargsLong(NevuObjectKwargsLong, total=False):
    inverted: bool


class WidgetKwargsShort(_WidgetKwargsBase, _WidgetKwargsShort, total=False):
    pass


class WidgetKwargsLong(_WidgetKwargsBase, _WidgetKwargsLong, total=False):
    pass


class WidgetKwargs(WidgetKwargsShort, WidgetKwargsLong, total=False):
    pass


class SwitchKwargs(WidgetKwargs, total=False):
    axis: SwitchAxis
    on_switch_change: Callable[[Switch, bool], None]


class LabelKwargs(WidgetKwargs, total=False):
    words_indent: bool
    on_text_change: Callable[[Label, str], None]


class ButtonKwargs(LabelKwargs, total=False):
    is_active: bool
    throw_errors: bool


class ElementSwitcherKwargs(WidgetKwargs, total=False):
    on_content_change: Callable
    current_index: int
    button_padding: int
    words_indent: bool
    arrow_width: int
    left_text: str
    left_key: Any
    right_text: str
    right_key: Any


class InputKwargs(WidgetKwargs, total=False):
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


class _SpecProgressBarKwargsLong(TypedDict, total=False):
    start_value: int | float
    end_value: int | float
    current_value: int | float
    filled_rect_role: PairColorRole
    on_current_value_change: Callable[[ProgressBar, int | float], None]


class _SpecProgressBarKwargsShort(TypedDict, total=False):
    start: int | float
    end: int | float
    current: int | float
    role: PairColorRole
    on_value_change: Callable[[ProgressBar, int | float], None]


class ProgressBarKwargsLong(_SpecProgressBarKwargsLong, WidgetKwargs):
    pass


class ProgressBarKwargsShort(_SpecProgressBarKwargsShort, WidgetKwargs):
    pass


class ProgressBarKwargs(ProgressBarKwargsLong, ProgressBarKwargsShort, WidgetKwargs):
    pass


class _SliderKwargsDefault(TypedDict, total=False):
    bar_style: Style
    step: int | float
    bar_font_role: TupleColorRole


class _SliderKwargsShort(
    _SpecProgressBarKwargsShort, _SliderKwargsDefault, total=False
):
    pad_x: int
    pad_y: int


class _SliderKwargsLong(_SpecProgressBarKwargsLong, _SliderKwargsDefault, total=False):
    padding_x: int
    padding_y: int


class SliderKwargsShort(_SliderKwargsShort, WidgetKwargs):
    pass


class SliderKwargsLong(_SliderKwargsLong, WidgetKwargs):
    pass


class SliderKwargs(SliderKwargsShort, SliderKwargsLong, WidgetKwargs):
    pass


class _RectCheckBoxKwargsDefault(TypedDict, total=False):
    toggled: bool
    toggled_rect_opacity: int


class _RectCheckBoxKwargsShort(_RectCheckBoxKwargsDefault, total=False):
    on_toggle: Callable | None
    group: CheckBoxGroup
    toggled_scale: int | float


class _RectCheckBoxKwargsLong(_RectCheckBoxKwargsDefault, total=False):
    on_toggle_function: Callable | None
    checkbox_group: CheckBoxGroup
    toggled_rect_scale: int | float


class RectCheckBoxKwargsShort(_RectCheckBoxKwargsShort, WidgetKwargs):
    pass


class RectCheckBoxKwargsLong(_RectCheckBoxKwargsLong, WidgetKwargs):
    pass


class RectCheckBoxKwargs(RectCheckBoxKwargsShort, RectCheckBoxKwargsLong, WidgetKwargs):
    pass

@dataclass
class WidgetTemplate(NevuObjectTemplate):
    pass


@dataclass
class LabelTemplate(WidgetTemplate):
    text: str


@dataclass
class ElementSwitcherTemplate(WidgetTemplate):
    elements: Any | list | None = None


@dataclass
class InputTemplate(WidgetTemplate):
    text: str


@dataclass
class SwitchTemplate(WidgetTemplate):
    state: bool


class WidgetGlobalsKwargs(NevuObjectGlobalsKwargs, WidgetKwargs):
    pass


class WidgetGlobals(GlobalsBase):
    def modify(self, **kwargs: Unpack[WidgetGlobalsKwargs]):
        return super().modify(**kwargs)

    def modify_temp(self, **kwargs: Unpack[WidgetGlobalsKwargs]):
        return super().modify_temp(**kwargs)

class LayoutTypeKwargs(NevuObjectKwargs, total = False):
    borders: BorderConfig

class _StackKwargs(TypedDict, total = False):
    spacing: float
    basic_alignment: Align

class StackKwargs(_StackKwargs, LayoutTypeKwargs):
    pass

class _ScrollableKwargs(LayoutTypeKwargs, total = False):
    arrow_scroll_power: int
    wheel_scroll_power: int
    inverted_scrolling: bool
    scrollbar_perc: NvVector2 | None
    basic_alignment: Align
    append_key: Any
    descend_key: Any
    spacing: float


class ScrollableKwargs(_ScrollableKwargs, LayoutTypeKwargs):
    pass

class _Grid_Specifics_rc(TypedDict):
    row: NotRequired[int | float]
    column: NotRequired[int | float]


class _Grid_Specifics_xy(TypedDict):
    x: NotRequired[int | float]
    y: NotRequired[int | float]


class _GridKwargs_rc(_Grid_Specifics_rc, LayoutTypeKwargs):
    pass


class _GridKwargs_xy(_Grid_Specifics_xy, LayoutTypeKwargs):
    pass


class _GridKwargs_uni(_GridKwargs_rc, _GridKwargs_xy, LayoutTypeKwargs):
    pass

class ColorPickerKwargs(_GridKwargs_uni):
    on_change_function: NotRequired[Any]
    raise_errors: NotRequired[bool]
    item_size: NotRequired[NvVector2]
    margin: NotRequired[int]
    input_style: NotRequired[Style]
    label_style: NotRequired[Style]

class _FlexLayoutKwargs(LayoutTypeKwargs, total=False):
    direction: FlexDirection
    wrap: bool
    justify_content: FlexJustify
    align_items: Align
    gap: int | float | NvVector2
    max_wrap_size: int | float

@dataclass
class LayoutTemplate(NevuObjectTemplate):
    content: list | None = None


@dataclass
class GridTemplate(NevuObjectTemplate):
    content: dict[tuple[int | float, int | float], NevuObject] | None = None


@dataclass
class Grid1xTemplate(NevuObjectTemplate):
    content: dict[int | float, NevuObject] | None = None


@dataclass
class AlignTemplate(NevuObjectTemplate):
    content: list[tuple[Align, NevuObject]] | None = None

nevu_object_globals = NevuObjectGlobals()
widget_globals = WidgetGlobals()
