from typing import Any, Callable

from nevu_ui.cython.vector2 import Vector2
from nevu_ui.utils.time import time


class Animation:
    """
    Base Nevu-UI animation class.
    ### do not use.
    """
    __slots__ = [
        "_check_errors",
        "current_time",
        "current_value",
        "easing_func",
        "end",
        "ended",
        "max_time",
        "start",
    ]

    def __init__(
        self,
        start: Any,
        end: Any,
        time: float = 1,
        easing_func: Callable | None = None,
        check_errors: bool = False,
    ):
        self.max_time = time
        self.current_time = 0
        self.start = start
        self.end = end
        self.ended = False
        self.current_value = None
        self.easing_func = easing_func
        self._check_errors = check_errors

    def _update_current_value(self, value):
        easing_func = self.easing_func
        if not easing_func:
            return value
        if not self._check_errors:
            return easing_func(value)
        try:
            return easing_func(value)
        except Exception as e:
            print(f"Error occured during execution of Animation easing function: {e}")
            return value

    def _apply_easing(self, eased_value: float):
        pass

    def update(self):
        if self.ended:
            return
        current_time = self.current_time
        max_time = self.max_time
        eased_value = self._update_current_value(current_time / max_time)
        self._apply_easing(eased_value)
        current_time += time.dt
        if current_time >= max_time:
            current_time = max_time
            self.ended = True
            self.current_value = self.end
        self.current_time = current_time

    def reset(self):
        self.current_time = 0
        self.ended = False

    def revert_time(self):
        self.current_time = self.max_time

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}<from {self.start} to {self.end}; {self.current_time:.2f}:{self.max_time}s>"

class Vector2Animation(Animation):
    __slots__ = ()

    def __init__(
        self,
        start: Vector2 | tuple | list,
        end: Vector2 | tuple | list,
        time: float = 1,
        easing_func: Callable | None = None,
        check_errors: bool = False,
    ):
        super().__init__(
            Vector2(start), Vector2(end), time, easing_func, check_errors
        )

    def _apply_easing(self, eased_value):
        if isinstance(eased_value, tuple):
            progress, offset = eased_value
            start, end = self.start, self.end
            start_x, start_y = start[0], start[1]
            self.current_value = Vector2.from_xy(
                start_x + (end[0] - start_x) * progress + offset[0],
                start_y + (end[1] - start_y) * progress + offset[1],
            )
        else:
            self.current_value = Vector2(
                *(
                    self.start[i] + (self.end[i] - self.start[i]) * eased_value
                    for i in range(2)
                )
            )


class ColorAnimation(Animation):
    __slots__ = ()

    def __init__(
        self,
        start,
        end,
        time: float = 1,
        easing_func: Callable | None = None,
        check_errors: bool = False,
    ):
        super().__init__(start, end, time, easing_func, check_errors)

    def _apply_easing(self, eased_value):
        length = min(len(self.start), len(self.end))
        if isinstance(eased_value, tuple):
            progress, offset = eased_value
            is_seq = isinstance(offset, (tuple, list)) or hasattr(offset, "__getitem__")
            self.current_value = tuple(
                self.start[i]
                + (self.end[i] - self.start[i]) * progress
                + (offset[i] if is_seq else offset)
                for i in range(length)
            )
        else:
            self.current_value = tuple(
                self.start[i] + (self.end[i] - self.start[i]) * eased_value
                for i in range(length)
            )


class FloatAnimation(Animation):
    __slots__ = ()

    def __init__(
        self,
        start: float,
        end: float,
        time: float = 1,
        easing_func: Callable | None = None,
        check_errors: bool = False,
    ):
        super().__init__(start, end, time, easing_func, check_errors)

    def _apply_easing(self, eased_value):
        if isinstance(eased_value, tuple):
            progress, offset = eased_value
            self.current_value = (
                self.start + (self.end - self.start) * progress + offset
            )
        else:
            self.current_value = self.start + (self.end - self.start) * eased_value


class AnimationQueue(Animation):
    __slots__ = ["animations", "current_index"]

    def __init__(self, *animations: Animation):
        if not animations:
            raise ValueError("AnimationQueue requires at least one animation")
        self.animations = list(animations)
        self.current_index = 0
        max_time = sum(anim.max_time for anim in self.animations)
        start = self.animations[0].start
        end = self.animations[-1].end
        super().__init__(start, end, max_time)
        self.current_value = start

    def update(self):
        if self.ended:
            return
        active = self.animations[self.current_index]
        active.update()
        self.current_value = active.current_value
        if active.ended:
            if self.current_index < len(self.animations) - 1:
                self.current_index += 1
            else:
                self.ended = True
                self.current_value = self.end
        self.current_time = min(self.max_time, self.current_time + time.dt)

    def reset(self):
        super().reset()
        self.current_index = 0
        self.current_value = self.start
        for anim in self.animations:
            anim.reset()

    def revert_time(self):
        super().revert_time()
        self.current_index = len(self.animations) - 1
        for anim in self.animations:
            anim.revert_time()
        self.current_value = self.end


from .presets import (  # noqa: E402
    linear,
    ease_out_bounce,
    ease_in_out_bounce,
    ease_in_sine,
    ease_out_sine,
    ease_in_out_sine,
    ease_in_quad,
    ease_out_quad,
    ease_in_out_quad,
    ease_in_cubic,
    ease_out_cubic,
    ease_in_out_cubic,
    ease_in_quart,
    ease_out_quart,
    ease_in_out_quart,
    ease_in_quint,
    ease_out_quint,
    ease_in_out_quint,
    ease_in_expo,
    ease_out_expo,
    ease_in_out_expo,
    ease_in_circ,
    ease_out_circ,
    ease_in_out_circ,
    ease_in_back,
    ease_out_back,
    ease_in_out_back,
    ease_in_elastic,
    ease_out_elastic,
    ease_in_power,
    ease_out_power,
    ease_in_bounce,
    steps,
    shake_easing,
    smoothstep,
    smootherstep,
    cubic_bezier,
    spring,
    pulse,
    breathe,
    smooth_shake_easing
)
from .manager import AnimationManager  # noqa: E402

__all__ = [
    "Vector2Animation", "FloatAnimation", "ColorAnimation",
    "linear", "ease_in_sine", "ease_out_sine", "ease_in_out_sine",
    "ease_in_quad", "ease_out_quad", "ease_in_out_quad", "ease_in_cubic", "ease_out_cubic", "ease_in_out_cubic",
    "ease_in_quart", "ease_out_quart", "ease_in_out_quart", "ease_in_quint", "ease_out_quint", "ease_in_out_quint",
    "ease_in_expo", "ease_out_expo", "ease_in_out_expo", "ease_in_circ", "ease_out_circ", "ease_in_out_circ",
    "ease_in_back", "ease_out_back", "ease_in_out_back", "ease_in_elastic", "ease_out_elastic",
    "ease_in_power", "ease_out_power", "steps",
    "AnimationManager", "ease_out_bounce", "shake_easing", "smoothstep", "smootherstep",
    "cubic_bezier", "spring", "pulse", "breathe", "smooth_shake_easing", "AnimationQueue", "ease_in_out_bounce", "ease_in_bounce"
]
