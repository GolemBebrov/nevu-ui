import time as tt

class Time():
    def __init__(self):
        """Initializes the Time object with default delta time, frames per second (fps),
            and timestamps for time calculations.
            Attributes:
                delta_time/dt (float): The time difference between the current and last frame.
                fps (int): Frames per second, calculated based on delta time."""
        self._delta_time = 1.0
        self._float_fps = 0.0
        self._fps = 0
        self._now = tt.time()
        self._after = tt.time()
        
    @property
    def delta_time(self): return self._delta_time
    @property
    def dt(self): return self._delta_time
    @property
    def fps(self): return self._fps
    @property
    def float_fps(self): return self._float_fps
    
    def _calculate_delta_time(self):
        self._now = tt.time()
        self._delta_time = self._now - self._after
        self._after = self._now
        
    def _calculate_fps(self):
        if self._delta_time == 0: return
        self._float_fps = 1 / self.delta_time
        self._fps = round(self._float_fps)
            
    def update(self):
        self._calculate_delta_time()
        self._calculate_fps()

time = Time()