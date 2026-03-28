from typing import Callable

from nevu_ui.utils.time import time
from nevu_ui.fast.nvvector2 import NvVector2
from nevu_ui.core.annotations import Annotations

class Animation():
    def __init__(self, start, end, time: int | float = 1, easing_func: Callable | None = None, check_errors: bool = False):
        self.max_time = time
        self.curr_time = 0
        self.start = start
        self.end = end
        self.ended = False
        self.current_value = None
        self.easing_func = easing_func
        self.check_errors = check_errors

    def _update_current_value(self, value):
        if not self.easing_func: return value
        if not self.check_errors: return self.easing_func(value)
        try:
            return self.easing_func(value)
        except Exception as e:
            print(f"Error occured during execution of Animation easing function: {e}")
            return value
    
    def _apply_easing(self, eased_value):
        pass
    
    def update(self):
        if self.ended: return
        eased_value = self._update_current_value(self.curr_time / self.max_time)
        self._apply_easing(eased_value)
        self.curr_time += 1 * time.dt
        if self.curr_time >= self.max_time:
            self.curr_time = self.max_time
            self.ended = True
            self.current_value = self.end
    
    def reset(self):
        self.curr_time = 0
        self.ended = False
    
    def revert_time(self):
        self.curr_time = self.max_time

class Vector2Animation(Animation):
    def __init__(self, start: NvVector2, end: NvVector2, time: int | float = 1, easing_func: Callable | None = None, check_errors: bool = False): 
        super().__init__(start, end, time, easing_func, check_errors)
    def _apply_easing(self, eased_value):
        self.current_value = NvVector2(*(round(self.start[i] + (self.end[i] - self.start[i]) * eased_value) for i in range(2)))

class ColorAnimation(Animation):
    def __init__(self, start: Annotations.rgba_color, end: Annotations.rgba_color, time: int | float = 1, easing_func: Callable | None = None, check_errors: bool = False):
        super().__init__(start, end, time, easing_func, check_errors)
    def _apply_easing(self, eased_value):
        lenght = min(len(self.start), len(self.end))
        self.current_value = tuple(round(self.start[i] + (self.end[i] - self.start[i]) * eased_value) for i in range(lenght))

class FloatAnimation(Animation):
    def __init__(self, start: float, end: float, time: int | float = 1, easing_func: Callable | None = None, check_errors: bool = False):
        super().__init__(start, end, time, easing_func, check_errors)
    def _apply_easing(self, eased_value):
        self.current_value = self.start + (self.end - self.start) * eased_value