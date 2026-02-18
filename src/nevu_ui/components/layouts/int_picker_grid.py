from typing import Any, NotRequired

from nevu_ui.fast.nvvector2 import NvVector2
from nevu_ui.core.enums import Align
from nevu_ui.utils import InputType
from nevu_ui.components.layouts import Grid
from nevu_ui.components.layouts import GridKwargs_uni
from nevu_ui.components.widgets import Input, Label
from nevu_ui.presentation.style import Style, default_style

class ColorPickerKwargs(GridKwargs_uni):
    on_change_function: NotRequired[Any]
    raise_errors: NotRequired[bool]
    item_size: NotRequired[NvVector2]
    margin: NotRequired[int]
    input_style: NotRequired[Style]
    label_style: NotRequired[Style]

class ColorPicker(Grid):
    def __init__(self, amount_of_colors = 3, title: str | None = None, **constant_kwargs):
        self._amount_of_colors = amount_of_colors
        self._title = title
        self._check_line()
        super().__init__(size = NvVector2(0,0), style = default_style, x = self.amount_of_colors, y = self._widget_line, **constant_kwargs)
    
    def _check_line(self):
        self._widget_line = 2 if self.title and self.title.strip() != "" else 1
    
    def _lazy_init(self, *args, **kwargs):
        self._regenerate_items()
        super()._lazy_init(size=self.size)
    
    def _regenerate_items(self):
        if self.amount_of_colors <= 0: raise ValueError("Amount of colors must be greater than 0")
        if self.item_size.x <= 0 or self.item_size.y <= 0: raise ValueError("Item size must be greater than 0")
        if self.margin < 0: raise ValueError("Margin must be greater or equal to 0")
        self._check_line()
        size = self.item_size * NvVector2(self.amount_of_colors, self._widget_line)
        self.size = size + NvVector2(self.margin * (self.amount_of_colors - 1), self.margin * (self._widget_line - 1))
        for item in self.items:
            item.kill()
        self.items.clear()
        self.cached_coordinates = None
        for i in range(self.amount_of_colors): 
            self.add_item(Input(self.item_size, self.input_style(text_align_x=Align.CENTER), "", "0", 
                                whitelist = list(InputType.NUMBERS), on_change_function=self._return_colors, max_characters=3),i+1,self._widget_line)
        if self._widget_line == 2:
            offset = 0.5 if self.amount_of_colors % 2 == 0 else 1
            self.label = Label(self.title or "", NvVector2(self.size.x, self.item_size.y),self.label_style(text_align_x=Align.CENTER))
            self.add_item(self.label, self.amount_of_colors // 2 + offset,1)

    def _add_params(self):
        super()._add_params()
        self._add_param("on_change_function", Any, None)
        self._add_param("raise_errors", bool, True)
        self._add_param("item_size", NvVector2, NvVector2(50,50))
        self._add_param("margin", int, 0)
        self._add_param("input_style", Style, default_style)
        self._add_param("label_style", Style, default_style)
    
    @property
    def on_change_function(self): return self.get_param_strict("on_change_function").value
    @property
    def item_size(self): return self.get_param_strict("item_size").value
    @property
    def margin(self): return self.get_param_strict("margin").value
    @property
    def input_style(self): return self.get_param_strict("input_style").value
    @property
    def label_style(self): return self.get_param_strict("label_style").value
    
    @property
    def amount_of_colors(self): return self._amount_of_colors
    @amount_of_colors.setter
    def amount_of_colors(self, value): 
        self._amount_of_colors = value
    @property
    def title(self): return self._title
    @title.setter
    def title(self, value):
        self._title = value
        
    def _return_colors(self, *args):
        if self.on_change_function: self.on_change_function(self.get_color())
        
    def get_color(self) -> tuple:
        color = []
        color.extend(int(item.text) if item.text != "" else 0 for item in self.items if isinstance(item, Input))
        return tuple(color)
    
    def set_color(self, color: tuple | list):
        for i in range(len(color)):
            if i == len(self.items): break
            item = self.items[i]
            assert isinstance(item, Input), "Item is not an input"
            item.text = str(color[i])
            
    def _create_clone(self):
        kwargs = self.constant_kwargs.copy()
        if "x" in kwargs: del kwargs["x"]
        if "y" in kwargs: del kwargs["y"]
        return ColorPicker(amount_of_colors=self.amount_of_colors, title=self.title, **kwargs)