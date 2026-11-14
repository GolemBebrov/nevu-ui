from __future__ import annotations

import copy
import pathlib as pl
import weakref
from collections.abc import Callable
from dataclasses import dataclass
from typing import (
    TYPE_CHECKING,
    Any,
    Iterator,
    TypedDict,
    TypeVar,
    Unpack,
    final,
)

from nevu_ui.assets.font import FontLibrary
from nevu_ui.core.annotations import Annotations
from nevu_ui.core.enums import Align, HoverState, Malign
from nevu_ui.core.size import _SizeRule
from nevu_ui.presentation.theme import (
    ColorSubTheme,
    ColorTheme,
    ColorThemeLibrary,
    PairColorRole,
    SubThemeRole,
)
from nevu_ui.presentation import color

if TYPE_CHECKING:
    from nevu_ui.rendering.gradient import Gradient
    from nevu_ui.rendering.pygame.gradient import GradientPygame
    from nevu_ui.rendering.raylib.gradient import GradientRaylib

StateType = TypeVar("StateType")


class StateVariable[StateType]:
    def __init__(self, static: StateType, hover: StateType, active: StateType):
        self.static: StateType = static
        self.hover: StateType = hover
        self.active: StateType = active

    def __getitem__(self, name: str | int) -> StateType:
        if name in [0, "static"]:
            return self.static
        elif name in [1, "hover"]:
            return self.hover
        elif name in [2, "active"]:
            return self.active
        raise KeyError

    def __setitem__(self, name: int | str, value: StateType):
        if name == 0:
            self.static = value
        elif name == 1:
            self.hover = value
        elif name == 2:
            self.active = value
        elif name in {"static", "hover", "active"}:
            setattr(self, name, value)
        else:
            raise KeyError

    def __iter__(self) -> Iterator[StateType]:
        yield self.static
        yield self.hover
        yield self.active

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, StateVariable):
            return False
        return (self.static, self.hover, self.active) == (
            other.static,
            other.hover,
            other.active,
        )

    def __hash__(self) -> int:
        return hash((self.static, self.hover, self.active))


T = TypeVar("T")
type SVar[T] = T | StateVariable[T]


class _StyleKwargs(TypedDict, total=False):
    border_radius: SVar[float | tuple[float, float, float, float]]
    br: SVar[float | tuple[float, float, float, float]]
    border_width: SVar[float]
    bw: SVar[float]
    font_size: SVar[float]
    fs: SVar[float]
    font_name: SVar[str]
    font_path: SVar[str]
    fn: SVar[str]
    align_x: SVar[Align | Malign]
    align_y: SVar[Align | Malign]
    text_align_x: SVar[Align | Malign]
    text_align_y: SVar[Align | Malign]
    bg_image: SVar[str]
    background_image: SVar[str]
    colortheme: SVar[ColorTheme]
    gradient: SVar[GradientPygame | GradientRaylib | Gradient]
    font_role: SVar[PairColorRole]
    color_role: SVar[SubThemeRole]
    subtheme_role: SVar[SubThemeRole]
    background_color: SVar[Annotations.rgb_like_color]
    bg_color: SVar[Annotations.rgb_like_color]
    border_color: SVar[Annotations.rgb_like_color]
    bd_color: SVar[Annotations.rgb_like_color]
    font_color: SVar[Annotations.rgb_like_color]
    fn_color: SVar[Annotations.rgb_like_color]
    transition_time: SVar[float | None]
    tt: SVar[float | None]
    transition_easing: SVar[Callable | None]
    te: SVar[Callable | None]


@dataclass(slots=True)
class _StyleParam:
    value: Any
    value_type: Any
    validator: Callable | None = None
    modified: bool = False
    name: str = "unknown"
    convertor: Callable | None = None

    def set(self, value: Any) -> None:
        if not isinstance(value, self.value_type | StateVariable):
            raise TypeError(
                f"In style.{self.name} '{value}' must be of type '{self.value_type}'"
            )
        if self.validator:
            if isinstance(value, StateVariable):
                if any(not self.validator(val)[0] for val in value):
                    raise ValueError(f"In style.{self.name} '{value}' is invalid.'")
            else:
                result = self.validator(value)
                if not result[0]:
                    raise ValueError(
                        f"In style.{self.name} '{value}' is invalid.'\n'{result[1]}'"
                    )

        if isinstance(value, StateVariable) and self.convertor:
            self.value = StateVariable(
                self.convertor(value.static),
                self.convertor(value.hover),
                self.convertor(value.active),
            )
        else:
            self.value = self.convertor(value) if self.convertor else value
        self.modified = True


def _validate_br(value: float | tuple):
    if not isinstance(value, tuple):
        return value >= 0, "Value is lesser than 0."
    return (
        len(value) == 4 and all(isinstance(it, int | float) and it >= 0 for it in value),
        "Value is not tuple or one of its value is lesser than 0,",
    )


def _convert_br(value: float | tuple):
    if isinstance(value, int | float):
        return value, value, value, value
    return value


def _validate_bw(value: float):
    return value >= 0, "Value is lesser than 0."


def _validate_tt(value: float | None):
    if value is None:
        return True, ""
    return value >= 0, "Value is lesser than 0."


def _validate_fs(value: float | _SizeRule):
    if isinstance(value, int | float):
        return value >= 1, "Value is lesser than 1."
    return True, ""


def _validate_path(value: str | None):
    if value is None:
        return True, ""
    return pl.Path(value).exists(), "Path doesnt exists."


def _validate_color(value: tuple):
    if not color.is_rgb_like(value) and not color.is_hsl_like(value):
        return False, "color is not RGB or HSL like."
    return True, ""


def _convert_color(value: tuple):
    if color.is_rgb_like(value):
        return value[0], value[1], value[2], value[3] if len(value) == 4 else 255
    elif color.is_hsl_like(value):
        alpha = value[3] if len(value) == 4 else 1.0
        clr = color.hsl_like_to_rgb(value)
        clr = color.set_float_alpha(clr, alpha)
        return clr
    return None


@final
class Style:
    border_radius: tuple[float, float, float, float]
    border_width: float
    font_size: float
    font_name: str
    align_x: Align
    align_y: Align
    text_align_x: Align
    text_align_y: Align
    background_image: str
    colortheme: ColorTheme
    gradient: GradientPygame | GradientRaylib | Gradient
    font_role: PairColorRole
    color_role: SubThemeRole
    subtheme_role: SubThemeRole
    background_color: Annotations.rgba_color
    border_color: Annotations.rgba_color
    font_color: Annotations.rgba_color
    transition_time: float | None
    transition_easing: Callable | None

    def __init__(self, **kwargs: Unpack[_StyleKwargs]):
        self._params = {}
        self._on_change = None
        self._add_params()
        self._kwargs = copy.deepcopy(kwargs)
        self._state = HoverState.NotHovered
        self._handle_kwargs(**kwargs)

    def _add_params(self) -> None:
        from nevu_ui.rendering.pygame.gradient import GradientPygame
        from nevu_ui.rendering.raylib.gradient import GradientRaylib

        Param = _StyleParam
        NoneType = type(None)
        add_param = self._add_param

        add_param(
            "br",
            "border_radius",
            param=Param((0, 0, 0, 0), int | float | tuple, _validate_br, convertor=_convert_br),
        )
        add_param("bw", "border_width", param=Param(1, int | float, _validate_bw))
        add_param("fs", "font_size", param=Param(20, int | float | _SizeRule, _validate_fs))
        add_param("fn", "font_path", "font_name", param=Param(FontLibrary.InterRegular, str, _validate_path))
        add_param("align_x", param=Param(Align.CENTER, Align))
        add_param("align_y", param=Param(Align.CENTER, Align))
        add_param("text_align_x", param=Param(Align.CENTER, Align))
        add_param("text_align_y", param=Param(Align.CENTER, Align))
        add_param("bg_image", "background_image", param=Param(None, str | NoneType, _validate_path))
        add_param("colortheme", param=Param(copy.copy(ColorThemeLibrary.material3_dark), ColorTheme))
        add_param("gradient", param=Param(None, GradientPygame | GradientRaylib | NoneType))
        add_param("color_role", param=Param(None, PairColorRole | NoneType))
        add_param("subtheme_role", param=Param(None, SubThemeRole | NoneType))
        add_param("font_role", param=Param(None, PairColorRole | NoneType))
        add_param("bg_color", "background_color", param=Param(None, tuple | NoneType, _validate_color, convertor=_convert_color))
        add_param("bd_color", "border_color", param=Param(None, tuple | NoneType, _validate_color, convertor=_convert_color))
        add_param("fn_color", "font_color", param=Param(None, tuple | NoneType, _validate_color, convertor=_convert_color))
        add_param("tt", "transition_time", param=Param(None, int | float | NoneType, _validate_tt))
        add_param("te", "transition_easing", param=Param(None, Callable | NoneType))

    def _add_param(self, *names: str, param: _StyleParam):
        param.name = names[-1]
        for name in names:
            self._params[name] = param

    def _bind_on_change(self, callback: Callable | None):
        if callback is None:
            self._on_change = None
        elif hasattr(callback, "__self__") and callback.__self__ is not None:
            self._on_change = weakref.WeakMethod(callback)
        else:
            self._on_change = weakref.ref(callback)

    def _get_color(
        self,
        subtheme: SubThemeRole | ColorSubTheme,
        *,
        inverted: bool = False,
        swap: bool = False,
    ):
        if type(subtheme) is SubThemeRole:
            subtheme = self.colortheme.get_subtheme(subtheme)
        assert isinstance(subtheme, ColorSubTheme)
        if inverted:
            return subtheme.on_color if swap else subtheme.on_container
        return subtheme.color if swap else subtheme.container

    def get_content_color(
        self,
        subtheme: SubThemeRole | ColorSubTheme,
        *,
        inverted: bool = False,
        swap: bool = False,
    ):
        return self.background_color or self._get_color(
            subtheme, inverted=inverted, swap=swap
        )

    def get_border_color(
        self,
        subtheme: SubThemeRole | ColorSubTheme,
        *,
        inverted: bool = False,
        swap: bool = False,
    ):
        return self.border_color or self._get_color(
            subtheme, inverted=not inverted, swap=swap
        )

    def get_pair_color(self, font_role: PairColorRole, *, inverted: bool = False):
        pair = self.colortheme.get_pair(font_role)
        return pair.on_color if inverted else pair.color

    def mark_state(self, state: HoverState):
        self._state = state

    def _handle_kwargs(self, raise_errors: bool = False, **kwargs: Any) -> None:
        for name, value in kwargs.items():
            param = self._params.get(name)
            if param is None:
                if raise_errors:
                    raise NameError(f"Unknown style param '{name}'")
                continue
            param.set(value)

    def __getattr__(self, name: str) -> Any:
        if name.startswith("_"):
            raise AttributeError(
                f"'{type(self).__name__}' object has no attribute '{name}'"
            )
        item = self.__dict__.get("_params")
        if not item:
            return
        item = item.get(name)
        if not item:
            raise AttributeError(f"Unknown style param '{name}'")

        if not isinstance(item.value, StateVariable):
            return item.value

        current_state_name = _hstate_to_state[self._state]
        return item.value[current_state_name]

    def __setattr__(self, name: str, value: Any) -> None:
        if name.startswith("_"):
            super().__setattr__(name, value)
            return

        params = self.__dict__.get("_params")
        if params is not None and name in params:
            params[name].set(value)
            if hasattr(self, "_kwargs"):
                self._kwargs[name] = value
            on_change = self.__dict__.get("_on_change")
            if on_change is not None:
                cb = on_change()
                if cb is not None:
                    cb()
            return

        super().__setattr__(name, value)

    def __call__(self, **kwargs: Unpack[_StyleKwargs]) -> Style:
        style = copy.copy(self)
        style._kwargs = copy.deepcopy(self._kwargs)
        style._kwargs.update(kwargs)

        style._handle_kwargs(raise_errors=True, **kwargs)
        style._state = HoverState.NotHovered
        return style

    def clone(self) -> Style:
        new_style = Style.__new__(Style)
        new_style._state = self._state
        new_style._on_change = None
        new_style._kwargs = copy.deepcopy(self._kwargs)
        new_style._params = {}

        seen_params: dict[int, _StyleParam] = {}
        for name, param in self._params.items():
            param_id = id(param)
            if param_id not in seen_params:
                val = param.value
                if isinstance(val, StateVariable):
                    new_val = StateVariable(val.static, val.hover, val.active)
                else:
                    new_val = copy.copy(val)
                seen_params[param_id] = _StyleParam(
                    value=new_val,
                    value_type=param.value_type,
                    validator=param.validator,
                    modified=param.modified,
                    name=param.name,
                    convertor=param.convertor,
                )
            new_style._params[name] = seen_params[param_id]
        return new_style

    def __copy__(self) -> Style:
        return self.clone()

    def __deepcopy__(self, memo: Any) -> Style:
        new_style = Style.__new__(Style)
        new_style._state = self._state
        new_style._on_change = None
        new_style._kwargs = copy.deepcopy(self._kwargs, memo)
        new_style._params = {}
        memo[id(self)] = new_style

        seen_params: dict[int, _StyleParam] = {}
        for name, param in self._params.items():
            param_id = id(param)
            if param_id not in seen_params:
                val = param.value
                if isinstance(val, StateVariable):
                    new_val = StateVariable(
                        copy.deepcopy(val.static, memo),
                        copy.deepcopy(val.hover, memo),
                        copy.deepcopy(val.active, memo),
                    )
                else:
                    new_val = copy.deepcopy(val, memo)
                seen_params[param_id] = _StyleParam(
                    value=new_val,
                    value_type=param.value_type,
                    validator=param.validator,
                    modified=param.modified,
                    name=param.name,
                    convertor=param.convertor,
                )
            new_style._params[name] = seen_params[param_id]
        return new_style

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Style):
            return NotImplemented

        params = self._params.values()
        other_params = other._params.values()
        params_equal = all(
            param == other_param for param, other_param in zip(params, other_params)
        )
        return params_equal and self._state == other._state

    def __hash__(self) -> int:
        return id(self)


_hstate_to_state = {
    HoverState.Clicked: "active",
    HoverState.Hovered: "hover",
    HoverState.NotHovered: "static",
}

__all__ = ["StateVariable", "Style", "_StyleKwargs"]
