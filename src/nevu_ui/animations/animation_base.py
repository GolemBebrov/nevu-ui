from enum import Enum, auto
from abc import ABC, abstractmethod
from typing import Any
from nevu_ui.utils import time

class AnimationType(Enum):
    COLOR = auto()
    SIZE = auto()
    POSITION = auto()
    ROTATION = auto()
    OPACITY = auto()
    _not_used = auto()

class Animation(ABC):
    def __init__(self, time: int = 0, start: Any = None, end: Any = None, type: AnimationType = AnimationType._not_used):
        """
        Initializes an Animation object with specified parameters.

        Parameters:
        time (float): The total time duration of the animation.
        start: The starting value of the animation parameter.
        end: The ending value of the animation parameter.
        type (AnimationType): The type of animation to be performed.
        """

        self.time_maximum = time
        self.time = 0
        self.start = start
        self.end = end
        self.type = type
        self.ended = False
        self.current_value = None

    @abstractmethod
    def _animation_update(self, value):
        pass
    
    def _apply_easing(self, eased_value):
        pass
    
    def update(self):
        if self.ended:
            return
        self._animation_update(self.time / self.time_maximum)
        self.time += 1 * time.delta_time
        if self.time >= self.time_maximum:
            self.time = self.time_maximum
            self.ended = True
            self.current_value = self.end
    
    def reset(self):
        self.time = 0
        self.ended = False