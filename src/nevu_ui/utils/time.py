import numpy as np
import time as tt

class Time():
    def __init__(self):
        """
        Initializes the Time object with default delta time, frames per second (fps),
        and timestamps for time calculations.

        Attributes:
            delta_time/dt (float): The time difference between the current and last frame.
            fps (int): Frames per second, calculated based on delta time.
        """
        self._delta_time = 1.0
        self._fps = np.int16()
        self._now = tt.time()
        self._after = tt.time()
    @property
    def delta_time(self):
        return float(self._delta_time)
    @property
    def dt(self):
        return float(self._delta_time)
    @property
    def fps(self):
        return int(self._fps)
    def _calculate_delta_time(self):
        self._now = tt.time()
        self._delta_time = self._now - self._after
        self._after = self._now
    def _calculate_fps(self):
        try:
            self._fps = np.int16(int(1 / (self.delta_time)))
        except Exception:
            self._fps = 0
    def update(self):
        self._calculate_delta_time()
        self._calculate_fps()

time = Time()