import copy
import math

from nevu_ui.fast.nvvector2 import NvVector2
from nevu_ui.widgets import Widget, WidgetKwargs
from nevu_ui.color import PairColorRole
from nevu_ui.rendering.blit import ReverseAlphaBlit, AlphaBlit

from typing import Any, TypedDict, NotRequired, Unpack, Union

from nevu_ui.style import (
    Style, default_style
)

class ProgressBarKwargs(WidgetKwargs):
    min_value: NotRequired[Union[int, float]]
    min: NotRequired[Union[int, float]]
    max_value: NotRequired[Union[int, float]]
    max: NotRequired[Union[int, float]]
    value: NotRequired[Union[int, float]]
    color_pair_role: NotRequired[PairColorRole]
    role: NotRequired[PairColorRole]

class ProgressBar(Widget):
    min_value: int | float
    max_value: int | float
    _current_value: int | float
    color_pair_role: PairColorRole
    def __init__(self, size: NvVector2 | list, style: Style = default_style, **constant_kwargs: Unpack[ProgressBarKwargs]):
        """Initializes a new ProgressBar widget.

        A visual widget that indicates the progress of an operation or a value
        within a defined range. The filled portion of the bar represents the
        current value relative to its minimum and maximum bounds.

        Parameters
        ----------
        size : NvVector2 | list
            The size of the widget.
        style : Style, optional
            The style object for the widget. Defaults to default_style.
        min_value : int or float, optional
            The minimum value of the progress bar. Alias: 'min'.
            Passed via keyword arguments. Defaults to 0.
        max_value : int or float, optional
            The maximum value of the progress bar. Alias: 'max'.
            Passed via keyword arguments. Defaults to 100.
        value : int or float, optional
            The initial value of the progress bar. This will determine the
            initial filled percentage. Passed via keyword arguments.
            Defaults to 0.
        color_pair_role : PairColorRole, optional
            The color role used to determine the color of the filled progress
            portion. Alias: 'role'. Passed via keyword arguments.
            Defaults to PairColorRole.BACKGROUND.
        """
        super().__init__(size, style, **constant_kwargs)
        self.set_progress_by_value(self.value)
    
    def _init_booleans(self):
        super()._init_booleans()
        self.hoverable = False
    
    def _add_constants(self):
        super()._add_constants()
        self._add_constant("min_value", (int, float), 0)
        self._add_constant_link("min", "min_value")
        self._add_constant("max_value", (int, float), 100)
        self._add_constant_link("max", "max_value")
        self._add_constant("value", (int, float), 0, getter=self.value_getter, setter=self.value_setter)
        self._add_constant("color_pair_role", PairColorRole, PairColorRole.BACKGROUND)
        self._add_constant_link("role", "color_pair_role")
        
    @property
    def progress(self): return self._progress
    
    @progress.setter
    def progress(self, value):
        self._progress = value
        self.value = self.min_value + (self.max_value - self.min_value) * self._progress
        
    def set_progress_by_value(self, value: int | float):
        self.progress = (value - self.min_value) / (self.max_value - self.min_value)
        
    def value_getter(self): return self._current_value
    def value_setter(self, value): 
        self._current_value = value
        self._changed = True
        if not hasattr(self, "_progress"):
            self.set_progress_by_value(value)
    
    def _init_alt(self):
        super()._init_alt()
        self._subtheme_progress = self._alt_subtheme_progress if self.alt else self._main_subtheme_progress
    
    @property
    def _main_subtheme_progress(self):
        return self.style.colortheme.get_pair(self.color_pair_role).color

    @property
    def _alt_subtheme_progress(self):
        return self.style.colortheme.get_pair(self.color_pair_role).oncolor
    
    def secondary_draw_content(self):
        super().secondary_draw_content()
        if not self._changed or self.progress <= 0:
            return

        bw = math.ceil(self.relm(self.style.borderwidth))
        
        inner_width = self._csize.x - self._rsize_marg.x 
        inner_height = self._csize.y - self._rsize_marg.y 
        
        size_x = math.ceil(inner_width * self.progress) + 2
        size_y = inner_height + 2
        
        radius = self.relm(self.style.borderradius) - bw
        radius = max(radius, 0)
        
        y_decrease = 0
        if size_x / 2 < radius:
            y_decrease = math.ceil(radius - (size_x / 2))
            if size_y - y_decrease * 2 > 0:
                size_y -= y_decrease * 2
        
        if size_x <= 0 or size_y <= 0:
            return
            
        surf = self.renderer._create_surf_base(
            NvVector2(size_x, size_y), 
            override_color=self._subtheme_progress, 
            radius=radius
        )
        
        coords = NvVector2(self._rsize_marg.x / 2 - 1, self._rsize_marg.y / 2 + y_decrease - 1)
        
        self.surface.blit(surf, coords.to_tuple())
    
    def clone(self):
        return ProgressBar(self._lazy_kwargs['size'], copy.deepcopy(self.style), **self.constant_kwargs)