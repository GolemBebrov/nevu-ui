from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING, Any, Callable, NotRequired, TypedDict, Unpack

from nevu_ui.components.nevuobj.typehints import (
    GlobalsBase,
    NevuObjectGlobalsKwargs,
    NevuObjectKwargs,
    NevuObjectKwargsLong,
    NevuObjectKwargsShort,
    NevuObjectTemplate,
)
from nevu_ui.core.enums import SwitchAxis

if TYPE_CHECKING:
    from nevu_ui.components.layouts.misc.checkbox_group import CheckBoxGroup
    from nevu_ui.components.widgets import Label, ProgressBar, Switch
    from nevu_ui.presentation.color import PairColorRole, SubThemeRole, TupleColorRole
    from nevu_ui.presentation.style import Style

#   ------------------
#   === TypedDicts ===
#   ------------------


class _WidgetKwargsBase(TypedDict, total=False):
    bg_variant: bool
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
    on_switch_change: Callable[["Switch", bool], None]


class LabelKwargs(WidgetKwargs, total=False):
    words_indent: bool
    on_text_change: Callable[["Label", str], None]


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
    multiple: bool
    allow_paste: bool
    words_indent: bool
    max_characters: int
    blacklist: list | tuple | str
    whitelist: list | tuple | str
    padding: list | tuple
    cursor_width: int


class _SpecProgressBarKwargsLong(TypedDict, total=False):
    start_value: int | float
    end_value: int | float
    current_value: int | float
    filled_rect_role: PairColorRole
    on_current_value_change: Callable[["ProgressBar", int | float], None]


class _SpecProgressBarKwargsShort(TypedDict, total=False):
    start: int | float
    end: int | float
    current: int | float
    role: PairColorRole
    on_value_change: Callable[["ProgressBar", int | float], None]


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


#   -----------------
#   === Templates ===
#   -----------------


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


widget_globals = WidgetGlobals()
