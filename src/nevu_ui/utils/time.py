import time as tt
from typing import final


@final
class Time:
    __slots__ = ("_last_time", "delta_time", "float_fps", "fps")

    def __init__(self):
        """Initializes the Time object with default delta time, frames per second (fps),
        and timestamps for time calculations.
        Attributes:
            delta_time/dt (float): The time difference between the current and last frame.
            fps (int): Frames per second, calculated based on delta time.
            float_fps (float): A floating-point representation of the frames per second."""
        self.delta_time: float = 1.0
        self.float_fps: float = 0.0
        self.fps: int = 0
        self._last_time: float = tt.perf_counter()

    @property
    def dt(self) -> float:
        return self.delta_time

    def update(self) -> None:
        now = tt.perf_counter()
        dt = now - self._last_time
        self._last_time = now
        self.delta_time = dt
        if dt == 0:
            return
        f_fps = 1 / dt
        fps = round(f_fps)
        self.float_fps = f_fps
        self.fps = fps


time = Time()
