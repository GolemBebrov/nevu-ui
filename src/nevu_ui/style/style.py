import copy
from typing import TypedDict, NotRequired, Unpack

from nevu_ui.core_types import Align
from nevu_ui.rendering import Gradient

from nevu_ui.color import (
    Color, ColorThemeLibrary, ColorTheme, SubThemeRole
)


class StyleKwargs(TypedDict):
    borderradius: NotRequired[int]
    br: NotRequired[int]
    borderwidth: NotRequired[int]
    bw: NotRequired[int]
    fontsize: NotRequired[int]
    fontname: NotRequired[str]
    fontpath: NotRequired[str]
    text_align_x: NotRequired[Align]
    text_align_y: NotRequired[Align]
    transparency: NotRequired[int]
    bgimage: NotRequired[str]
    colortheme: NotRequired[ColorTheme]
    gradient: NotRequired[Gradient]
    
class Style:
    def __init__(self,**kwargs: Unpack[StyleKwargs]):
        self._kwargs_for_copy = copy.copy(kwargs)
        self.kwargs_dict = {}
        
        self._init_basic()
        
        self._add_paramethers()
        
        self._handle_kwargs(**kwargs)
    
    def _add_paramethers(self):
        self.add_style_parameter("borderradius", "borderradius", lambda value:self.parse_int(value, min_restriction=0))
        self.add_style_parameter("br", "borderradius", lambda value:self.parse_int(value, min_restriction=0))
        self.add_style_parameter("borderwidth", "borderwidth", lambda value:self.parse_int(value, min_restriction=0))
        self.add_style_parameter("bw", "borderwidth", lambda value:self.parse_int(value, min_restriction=0))
        self.add_style_parameter("fontsize", "fontsize", lambda value:self.parse_int(value, min_restriction=1))
        self.add_style_parameter("fontname", "fontname", lambda value:self.parse_str(value))
        self.add_style_parameter("fontpath", "fontname", lambda value:self.parse_str(value))
        self.add_style_parameter("text_align_x", "text_align_x", lambda value:self.parse_type(value, Align))
        self.add_style_parameter("text_align_y", "text_align_y", lambda value:self.parse_type(value, Align))
        self.add_style_parameter("transparency", "transparency", lambda value:self.parse_int(value, max_restriction=255, min_restriction=0))
        self.add_style_parameter("bgimage", "bgimage", lambda value:self.parse_str(value))
        self.add_style_parameter("colortheme", "colortheme", lambda value:self.parse_type(value, ColorTheme))
        self.add_style_parameter("gradient", "gradient", lambda value:self.parse_type(value, Gradient))
        
    def _init_basic(self):
        self.colortheme = copy.copy(ColorThemeLibrary.material3_dark)
        self.borderwidth = 1
        self.borderradius = 0
        self.fontname = "Arial"
        self.fontsize = 20
        self.text_align_x = Align.CENTER
        self.text_align_y = Align.CENTER
        self.transparency = None
        self.bgimage = None
        self.gradient = None
        
    def add_style_parameter(self, name: str, attribute_name: str, checker_lambda):
        self.kwargs_dict[name] = (attribute_name, checker_lambda)
        
    def parse_color(self, value, can_be_gradient: bool = False, can_be_trasparent: bool = False, can_be_string: bool = False) -> tuple[bool, tuple|None]:
        if isinstance(value, Gradient) and can_be_gradient:
            return True, None

        elif isinstance(value, (tuple, list)) and (len(value) == 3 or len(value) == 4) and all(isinstance(c, int) for c in value):
            for item in value:
                if item < 0 or item > 255:
                    return False, None
            return True, None

        elif isinstance(value, str) and can_be_string:
            try:
                color_value = Color[value] # type: ignore
            except KeyError:
                return False, None
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
    
    def parse_str(self, value: str) -> tuple[bool, None]:
        return self.parse_type(value, str)
    
    def parse_type(self, value: str, type: type|tuple) -> tuple[bool, None]:
        return (True, None) if isinstance(value, type) else (False, None)
    
    def _handle_kwargs(self, raise_errors: bool = False, **kwargs):
        for item_name, item_value in kwargs.items():
            dict_value = self.kwargs_dict.get(item_name.lower(), None)
            if dict_value is None:
                continue
            attribute_name, checker = dict_value
            checker_result, checker_value = checker(item_value)
            if checker_result:
                end_value = checker_value if checker_value is not None else item_value
                setattr(self, attribute_name, end_value)
            elif raise_errors:
                raise ValueError(f"Некорректное значение {item_name}")

    def __call__(self ,**kwargs):
        style = copy.copy(self)
        style._handle_kwargs(**kwargs)
        return style
    
    def clone(self):
        return Style(**self._kwargs_for_copy)
    
default_style = Style()

