from __future__ import annotations

import copy
from collections.abc import Callable
from typing import (
    TYPE_CHECKING,
    Any,
    NotRequired,
    TypedDict,
    TypeVar,
    Unpack,
    final,
    override,
)

from nevu_ui.core.enums import Align, HoverState
from nevu_ui.presentation.color.color_theme import ColorSubTheme

if TYPE_CHECKING:
    from nevu_ui.rendering.pygame.gradient import GradientPygame
    from nevu_ui.rendering.raylib.gradient import GradientRaylib

from nevu_ui.presentation.color import (
    Color,
    ColorTheme,
    ColorThemeLibrary,
    PairColorRole,
    SubThemeRole,
)

TV = TypeVar("TV")


class StateVariable[TV]:
    def __init__(self, static: TV, hover: TV, active: TV):
        self.static: TV = static
        self.hover: TV = hover
        self.active: TV = active

    def __getitem__(self, name: str | int) -> TV:
        if name in [0, "static"]:
            return self.static
        elif name in [1, "hover"]:
            return self.hover
        elif name in [2, "active"]:
            return self.active
        raise KeyError

    def __setitem__(self, name: int | str, value: TV):
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


T = TypeVar("T")
type SVar[T] = T | StateVariable[T]


class StyleKwargs(TypedDict):
    border_radius: NotRequired[SVar[float | tuple[float, float, float, float]]]
    br: NotRequired[SVar[float | tuple[float, float, float, float]]]
    border_width: NotRequired[SVar[int]]
    bw: NotRequired[SVar[int]]
    font_size: NotRequired[SVar[int]]
    font_name: NotRequired[SVar[str]]
    font_path: NotRequired[SVar[str]]
    align_x: NotRequired[SVar[Align]]
    align_y: NotRequired[SVar[Align]]
    transparency: NotRequired[SVar[int]]
    bg_image: NotRequired[SVar[str]]
    colortheme: NotRequired[SVar[ColorTheme]]
    gradient: NotRequired[SVar[GradientPygame | GradientRaylib]]
    font_role: NotRequired[SVar[PairColorRole]]
    color_role: NotRequired[SVar[SubThemeRole]]
    subtheme_role: NotRequired[SVar[SubThemeRole]]

@final
class Style:
    def __init__(self, **kwargs: Unpack[StyleKwargs]):
        self.parameters_dict: dict[str, tuple[str, Callable[..., tuple[bool, Any]]]] = {
            "border_radius": ("border_radius", self._parse_br),
            "br": ("border_radius", self._parse_br),
            "border_width": ("border_width", self._parse_int_min0),
            "bw": ("border_width", self._parse_int_min0),
            "font_size": ("font_size", self._parse_font_size),
            "font_name": ("font_name", self._parse_str),
            "font_path": ("font_name", self._parse_str),
            "align_x": ("align_x", self._parse_align),
            "align_y": ("align_y", self._parse_align),
            "transparency": ("transparency", self._parse_transparency),
            "bg_image": ("bg_image", self._parse_str),
            "colortheme": ("colortheme", self._parse_colortheme),
            "gradient": ("gradient", self._parse_gradient),
            "color_role": ("color_role", self._parse_color_role),
            "subtheme_role": ("subtheme_role", self._parse_subtheme_role),
            "font_role": ("font_role", self._parse_font_role),
        }
        self._kwargs_for_copy = copy.deepcopy(kwargs)
        self.kwargs_dict = {}
        self._curr_state = HoverState.NotHovered
        self._init_default()
        self._add_paramethers()
        self._handle_kwargs(**kwargs)

    def _parse_int_min0(self, value: float):
        return self._parse_int(value, min_restriction=0)

    def _parse_br(self, value: float | tuple[int, ...]):
        if isinstance(value, int | float):
            return self._parse_int_min0(value)
        elif (
            self._parse_type(value, tuple)
            and len(value) == 4
            and all(isinstance(i, int | float) for i in value)
        ):
            return True, None
        return False, None

    def _parse_align(self, value: Align) -> tuple[bool, None]:
        return self._parse_type(value, Align)

    def _parse_font_size(self, value: int) -> tuple[bool, None]:
        return self._parse_int(value, min_restriction=1)

    def _parse_transparency(self, value: int) -> tuple[bool, None]:
        return self._parse_int(value, max_restriction=255, min_restriction=0)

    def _parse_colortheme(self, value: ColorTheme) -> tuple[bool, None]:
        return self._parse_type(value, ColorTheme)

    def _parse_gradient(self, value: Any) -> tuple[bool, None]:
        return (True, None)

    def _parse_color_role(self, value: SubThemeRole) -> tuple[bool, None]:
        return self._parse_type(value, SubThemeRole)

    def _parse_subtheme_role(self, value: SubThemeRole) -> tuple[bool, None]:
        return self._parse_type(value, SubThemeRole)

    def _parse_font_role(self, value: PairColorRole) -> tuple[bool, None]:
        return self._parse_type(value, PairColorRole)

    def _parse_int(
        self,
        value: int | Any,
        max_restriction: int | None = None,
        min_restriction: int | None = None
    ) -> tuple[bool, None]:
        if isinstance(value, int):
            if max_restriction is not None and value > max_restriction:
                return False, None
            if min_restriction is not None and value < min_restriction:
                return False, None
            return True, None
        return False, None

    def _parse_type(self, value: Any, types: type | tuple[type, ...]) -> tuple[bool, None]:
        return isinstance(value, types), None

    def _add_paramethers(self) -> None:
        for name, value in self.parameters_dict.items():
            parameter, checker_func = value
            self._add_style_parameter(name, parameter, checker_func)

    def _get_color(self, subtheme: SubThemeRole | ColorSubTheme, *, inverted: bool = False, swap: bool = False):
        if type(subtheme) is SubThemeRole:
            subtheme = self.colortheme.get_subtheme(subtheme)
        assert isinstance(subtheme, ColorSubTheme)
        if inverted:
            return subtheme.oncolor if swap else subtheme.oncontainer
        return subtheme.color if swap else subtheme.container

    def get_content_color(self, subtheme: SubThemeRole | ColorSubTheme, *, inverted: bool = False, swap: bool = False):
        return self._get_color(subtheme, inverted=inverted, swap=swap)

    def get_border_color(self, subtheme: SubThemeRole | ColorSubTheme, *, inverted: bool = False, swap: bool = False):
        return self._get_color(subtheme, inverted=not inverted, swap=swap)

    def get_pair_color(self, font_role: PairColorRole, *, inverted: bool = False):
        pair = self.colortheme.get_pair(font_role)
        return pair.oncolor if inverted else pair.color

    def _init_default(self) -> None:
        self.colortheme = copy.copy(ColorThemeLibrary.material3_blue)
        self.border_width = 1
        self.border_radius = 0
        self.font_name = "Arial"
        self.font_size = 20
        self.align_x = Align.CENTER
        self.align_y = Align.CENTER
        self.transparency = None
        self.bg_image = None
        self.gradient = None
        self.color_role = None
        self.font_role = None
        self.subtheme_role = None

    def _add_style_parameter(self, name: str, attribute_name: str, checker_lambda: Any):
        self.kwargs_dict[name] = (attribute_name, checker_lambda)

    def mark_state(self, state: HoverState):
        self._curr_state = state

    def _parse_str(self, value: str | Any) -> tuple[bool, None]:
        return self._parse_type(value, str)

    def _handle_kwargs(self, raise_errors: bool = False, **kwargs: Any) -> None:
        for item_name, item_value in kwargs.items():
            dict_value = self.kwargs_dict.get(item_name.lower(), None)
            if dict_value is None:
                kwargs_dict = {
                    key.replace("_", ""): value
                    for key, value in self.kwargs_dict.items()
                }
                if item_name not in kwargs_dict:
                    if raise_errors:
                        raise ValueError(f"Unknown attribute '{item_name}'")
                    continue
                else:
                    dict_value = kwargs_dict[item_name]
            self._handle_single_item(item_name, item_value, dict_value, raise_errors)

    def _handle_single_item(
        self, item_name: str, item_value: Any, dict_value: tuple[str, Callable[..., tuple[bool, Any]]], raise_errors: bool = False
    ) -> None:
        attribute_name, checker = dict_value
        if isinstance(item_value, StateVariable):
            validated_values = {}
            for state_name in ["static", "hover", "active"]:
                value_to_check = item_value[state_name]
                is_valid, new_value = checker(value_to_check)
                if not is_valid and raise_errors:
                    raise ValueError(
                        f"Invalid value for state '{state_name}' in attribute '{item_name}'"
                    )
                validated_values[state_name] = (
                    new_value if new_value is not None else value_to_check
                )
            end_value = StateVariable(**validated_values)
            setattr(self, attribute_name, end_value)
        else:
            checker_result, checker_value = checker(item_value)
            if checker_result:
                end_value = checker_value if checker_value is not None else item_value
                setattr(self, attribute_name, end_value)
            elif raise_errors:
                raise ValueError(
                    f"Incorrect value {item_value} for {item_name} of type {type(item_value).__name__}"
                )

    @override
    def __getattribute__(self, name: str) -> Any:  # pyright: ignore[reportAny]
        try:
            item = super().__getattribute__(name)
        except AttributeError as e:
            raise AttributeError(
                f"'{type(self).__name__}' object has no attribute '{name}'"
            ) from e

        if not isinstance(item, StateVariable):
            return item

        current_state_name = hstate_to_state[super().__getattribute__("_curr_state")]
        return item[current_state_name]

    def __call__(self, **kwargs: Unpack[StyleKwargs]):
        style = copy.copy(self)
        style._kwargs_for_copy = copy.deepcopy(self._kwargs_for_copy)
        style._kwargs_for_copy.update(kwargs)

        style._handle_kwargs(raise_errors=True, **kwargs)
        style._curr_state = HoverState.NotHovered
        return style

    def clone(self):
        return Style(**self._kwargs_for_copy)

    def __deepcopy__(self, memo):
        return copy.copy(self)

hstate_to_state = {
    HoverState.Clicked: "active",
    HoverState.Hovered: "hover",
    HoverState.NotHovered: "static",
}

default_style = Style()
