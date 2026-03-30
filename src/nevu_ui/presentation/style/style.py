from __future__ import annotations
import copy
from typing import TypedDict, TypeVar, NotRequired, Unpack, Generic, TYPE_CHECKING

from nevu_ui.core.enums import Align, HoverState
if TYPE_CHECKING: 
    from nevu_ui.rendering.pygame.gradient import GradientPygame

from nevu_ui.presentation.color import (
    Color, ColorThemeLibrary, ColorTheme, SubThemeRole, PairColorRole
)

TV = TypeVar("TV")

class StateVariable(Generic[TV]):
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
    
    def __setitem__(self, name: int, value: TV):
        if name == 0:
            self.static = value
        elif name == 1:
            self.hover = value
        elif name == 2:
            self.active = value
        elif name in {"static", "hover", "active"}:
            setattr(self, name, value)
        raise KeyError

T = TypeVar("T")
type SVar[T] = T | StateVariable[T]

class StyleKwargs(TypedDict):
    border_radius: NotRequired[SVar[int | float | tuple]]
    br: NotRequired[SVar[int]]
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
    gradient: NotRequired[SVar[GradientPygame]]
    font_role: NotRequired[SVar[PairColorRole]]
    color_role: NotRequired[SVar[SubThemeRole]]
    subtheme_role: NotRequired[SVar[SubThemeRole]]
    
class Style:
    def __init__(self, **kwargs: Unpack[StyleKwargs]):
        self._kwargs_for_copy = copy.deepcopy(kwargs)
        self.kwargs_dict = {}
        self.parameters_dict = {
            "border_radius": ["border_radius", self._parse_br],
            "br": ["border_radius", self._parse_int_min0],
            "border_width": ["border_width", self._parse_int_min0],
            "bw": ["border_width", self._parse_int_min0],
            "font_size": ["font_size", lambda value: self.parse_int(value, min_restriction = 1)],
            "font_name": ["font_name", self.parse_str],
            "font_path": ["font_name", self.parse_str],
            "align_x": ["align_x", self._parse_align],
            "align_y": ["align_y", self._parse_align],
            "transparency": ["transparency", lambda value: self.parse_int(value, max_restriction = 255, min_restriction = 0)],
            "bg_image": ["bg_image", self.parse_str],
            "colortheme": ["colortheme", lambda value: self.parse_type(value, ColorTheme)],
            "gradient": ["gradient", lambda value: (True, None)],
            "color_role": ["color_role", lambda value: self.parse_type(value, SubThemeRole)],
            "subtheme_role": ["subtheme_role", lambda value: self.parse_type(value, SubThemeRole)],
            "font_role": ["font_role", lambda value: self.parse_type(value, PairColorRole)],
        }
        self._curr_state = HoverState.UN_HOVERED
        self._init_basic()
        self._add_paramethers()
        self._handle_kwargs(**kwargs)
    
    def _parse_int_min0(self, value):
        return self.parse_int(value, min_restriction = 0)
    
    def _parse_br(self, value):
        if isinstance(value, int | float):
            return self._parse_int_min0(value)
        elif self.parse_type(value, tuple) and len(value) == 4 and all(isinstance(i, int | float) for i in value):
            return True, None
        return False, None
    
    def _parse_align(self, value):
        return self.parse_type(value, Align)
    
    def _add_paramethers(self):
        for name, value in self.parameters_dict.items():
            paramether, checker_lambda = value
            self.add_style_parameter(name, paramether, checker_lambda)
        
    def _init_basic(self):
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
    
    def add_style_parameter(self, name: str, attribute_name: str, checker_lambda):
        self.kwargs_dict[name] = (attribute_name, checker_lambda)
        
    def parse_color(self, value, can_be_gradient: bool = False, can_be_trasparent: bool = False, can_be_string: bool = False) -> tuple[bool, tuple|None]:
        if isinstance(value, GradientPygame) and can_be_gradient:
            return True, None

        elif isinstance(value, (tuple, list)) and len(value) in {3, 4} and all(isinstance(c, int) for c in value):
            return next(((False, None) for item in value if item < 0 or item > 255), (True, None))
        
        elif isinstance(value, str) and can_be_string:
            try:
                color_value = Color[value] # type: ignore
            except KeyError: return False, None
            else:
                assert isinstance(color_value, tuple)
                return True, color_value

        return False, None
    
    def parse_int(self, value: int, max_restriction: int|None = None, min_restriction: int|None = None) -> tuple[bool, None]:
        if isinstance(value, int):
            if max_restriction is not None and value > max_restriction:
                return False, None
            if min_restriction is not None and value < min_restriction:
                return False, None
            return True, None
        return False, None
    
    def mark_state(self, state: HoverState):
        self._curr_state = state
    
    def parse_str(self, value: str) -> tuple[bool, None]:
        return self.parse_type(value, str)
    
    def parse_type(self, value: str, type: type | tuple) -> tuple[bool, None]:
        return (True, None) if isinstance(value, type) else (False, None)
    
    def _handle_kwargs(self, raise_errors: bool = False, **kwargs):
        for item_name, item_value in kwargs.items():
            dict_value = self.kwargs_dict.get(item_name.lower(), None)
            if dict_value is None:
                kwargs_dict = {key.replace("_", ""): value for key, value in self.kwargs_dict.items()}
                if item_name not in kwargs_dict:
                    if raise_errors:
                        raise ValueError(f"Unknown attribute '{item_name}'")
                    continue
                else:
                    dict_value = kwargs_dict[item_name]
            self._handle_single_item(item_name, item_value, dict_value, raise_errors)

    def _handle_single_item(self, item_name, item_value, dict_value, raise_errors: bool = False):
        attribute_name, checker = dict_value
        if isinstance(item_value, StateVariable):
            validated_values = {}
            for state_name in ["static", "hover", "active"]:
                value_to_check = item_value[state_name]
                is_valid, new_value = checker(value_to_check)
                if not is_valid and raise_errors:
                    raise ValueError(f"Invalid value for state '{state_name}' in attribute '{item_name}'")
                validated_values[state_name] = new_value if new_value is not None else value_to_check
            end_value = StateVariable(**validated_values)
            setattr(self, attribute_name, end_value)
        else:
            checker_result, checker_value = checker(item_value)
            if checker_result:
                end_value = checker_value if checker_value is not None else item_value
                setattr(self, attribute_name, end_value)
            elif raise_errors:
                raise ValueError(f"Incorrect value {item_value} for {item_name} of type {type(item_value).__name__}")

    def __getattribute__(self, name: str):
        try:
            item = super().__getattribute__(name)
        except AttributeError as e:
            raise AttributeError(f"'{type(self).__name__}' object has no attribute '{name}'") from e

        if not isinstance(item, StateVariable):
            return item
        
        current_state_name = hstate_to_state[super().__getattribute__('_curr_state')]
        return item[current_state_name]

    def __call__(self, **kwargs: Unpack[StyleKwargs]):
        style = copy.copy(self)
        style._kwargs_for_copy = copy.deepcopy(self._kwargs_for_copy)
        style._kwargs_for_copy.update(kwargs)
        
        style._handle_kwargs(raise_errors=True, **kwargs)
        style._curr_state = HoverState.UN_HOVERED
        return style
    
    def clone(self): return Style(**self._kwargs_for_copy)
    def __deepcopy__(self, memo): return copy.copy(self)
    
hstate_to_state = {
    HoverState.CLICKED: "active",
    HoverState.HOVERED: "hover",
    HoverState.UN_HOVERED: "static"
}

default_style = Style()