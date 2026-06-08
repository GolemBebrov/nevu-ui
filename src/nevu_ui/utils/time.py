import time as tt

class Time():
    __slots__ = ('delta_time', 'float_fps', 'fps', 'after')
    def __init__(self):
        """Initializes the Time object with default delta time, frames per second (fps),
            and timestamps for time calculations.
            Attributes:
                delta_time/dt (float): The time difference between the current and last frame.
                fps (int): Frames per second, calculated based on delta time.
                float_fps (float): A floating-point representation of the frames per second."""
        self.delta_time = 1.0
        self.float_fps = 0.0
        self.fps = 0
        self.after = tt.perf_counter()

    @property
    def dt(self): return self.delta_time

    def update(self):
        now = tt.perf_counter()
        dt = now - self.after
        self.after = now
        self.delta_time = dt
        if dt == 0: return
        f_fps = 1 / dt
        fps = round(f_fps)
        self.float_fps = f_fps
        self.fps = fps
        
time = Time()