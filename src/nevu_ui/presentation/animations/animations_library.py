import math
from typing import Callable
from nevu_ui.fast.nvvector2 import NvVector2
import random

def linear(value: float) -> float: return value

# === Bounce ===
def ease_out_bounce(value: float) -> float:
    if value < (1 / 2.75):
        return 7.5625 * value * value
    elif value < (2 / 2.75):
        value -= (1.5 / 2.75)
        return 7.5625 * value * value + 0.75
    elif value < (2.5 / 2.75):
        value -= (2.25 / 2.75)
        return 7.5625 * value * value + 0.9375
    else:
        value -= (2.625 / 2.75)
        return 7.5625 * value * value + 0.984375
def ease_in_bounce(value: float) -> float: return 1 - ease_out_bounce(1 - value)
def ease_in_out_bounce(value: float) -> float:
    if value < 0.5:
        return (1 - ease_out_bounce(1 - 2 * value)) / 2
    else:
        return (1 + ease_out_bounce(2 * value - 1)) / 2

# === Sine ===
def ease_in_sine(value: float) -> float: return 1 - math.cos((value * math.pi) / 2)
def ease_out_sine(value: float) -> float: return math.sin((value * math.pi) / 2)
def ease_in_out_sine(value: float) -> float: return -(math.cos(math.pi * value) - 1) / 2

# === Quad ===
def ease_in_quad(value: float) -> float: return value ** 2
def ease_out_quad(value: float) -> float: return 1 - (1 - value) * (1 - value)
def ease_in_out_quad(value: float) -> float:
    if value < 0.5:
        return 2 * value * value
    else:
        return -1 + (4 - 2 * value) * value

# === Cubic ===
def ease_in_cubic(value: float) -> float: return value ** 3
def ease_out_cubic(value: float) -> float: return 1 - pow(1 - value, 3)
def ease_in_out_cubic(value: float) -> float:
    if value < 0.5:
        return 4 * value * value * value
    else:
        return 1 - pow(-2 * value + 2, 3) / 2

# === Quart ===
def ease_in_quart(value: float) -> float: return value ** 4
def ease_out_quart(value: float) -> float: return 1 - pow(1 - value, 4)
def ease_in_out_quart(value: float) -> float:
    if value < 0.5:
        return 8 * value * value * value * value
    else:
        return 1 - pow(-2 * value + 2, 4) / 2

# === Quint ===
def ease_in_quint(value: float) -> float: return value ** 5
def ease_out_quint(value: float) -> float: return 1 - pow(1 - value, 5)
def ease_in_out_quint(value: float) -> float:
    if value < 0.5:
        return 16 * value * value * value * value * value
    else:
        return 1 - pow(-2 * value + 2, 5) / 2

# === Expo ===
def ease_in_expo(value: float) -> float: return 0.0 if value == 0 else pow(2, 10 * value - 10)
def ease_out_expo(value: float) -> float: return 1.0 if value == 1 else 1 - pow(2, -10 * value)
def ease_in_out_expo(value: float) -> float:
    if value == 0:
        return 0.0
    elif value == 1:
        return 1.0
    elif value < 0.5:
        return pow(2, 20 * value - 10) / 2
    else:
        return (2 - pow(2, -20 * value + 10)) / 2

# === Circ ===
def ease_in_circ(value: float) -> float: return 1 - math.sqrt(1 - pow(value, 2))
def ease_out_circ(value: float) -> float: return math.sqrt(1 - pow(value - 1, 2))
def ease_in_out_circ(value: float) -> float:
    if value < 0.5:
        return (1 - math.sqrt(1 - pow(2 * value, 2))) / 2
    else:
        return (math.sqrt(1 - pow(-2 * value + 2, 2)) + 1) / 2

# === Back ===
def ease_in_back(value: float) -> float:
    c1: float = 1.70158
    c3: float = c1 + 1
    return c3 * value * value * value - c1 * value * value
def ease_out_back(value: float) -> float:
    c1: float = 1.70158
    c3: float = c1 + 1
    return 1 + c3 * pow(value - 1, 3) + c1 * pow(value - 1, 2)
def ease_in_out_back(value: float) -> float:
    c1: float = 1.70158
    c2: float = c1 * 1.525
    if value < 0.5:
        return (pow(2 * value, 2) * ((c2 + 1) * 2 * value - c2)) / 2
    else:
        return (pow(2 * value - 2, 2) * ((c2 + 1) * (value * 2 - 2) + c2) + 2) / 2

# === Power ===
def ease_in_power(power: float) -> Callable[[float], float]: return lambda value: pow(value, power)
def ease_out_power(power: float) -> Callable[[float], float]: return lambda value: 1 - pow(1 - value, power)

# === Elastic ===
def ease_in_elastic(value: float) -> float:
    c4: float = (2 * math.pi) / 3
    if value == 0: return 0.0
    if value == 1: return 1.0
    return -pow(2, 10 * value - 10) * math.sin((value * 10 - 10.75) * c4)
def ease_out_elastic(value: float) -> float:
    c4: float = (2 * math.pi) / 3
    if value == 0: return 0.0
    if value == 1: return 1.0
    return pow(2, -10 * value) * math.sin((value * 10 - 0.75) * c4) + 1

# === Steps ===
def steps(n: int) -> Callable[[float], float]:
    return lambda value: math.floor(value * n) / n

# === Custom ===
def shake_easing(amplitude: float = 8.0, continuous: bool = False):
    def easing(progress: float):
        current_amp = amplitude if continuous else amplitude * (1 - progress)
        
        offset = NvVector2.from_xy(
            random.uniform(-current_amp, current_amp),
            random.uniform(-current_amp, current_amp)
        )
        return progress, offset
    return easing

def smoothstep(value: float) -> float:
    return (value ** 2) * (3 - 2 * value)

def smootherstep(value: float) -> float:
    return (value ** 3) * (value * (value * 6 - 15) + 10)

def cubic_bezier(x1: float, y1: float, x2: float, y2: float) -> Callable[[float], float]:
    def get_coordinate(t: float, p1: float, p2: float) -> float:
        return 3 * p1 * (1 - t)**2 * t + 3 * p2 * (1 - t) * t**2 + t**3

    def solver(value: float) -> float:
        if value <= 0.0: return 0.0
        if value >= 1.0: return 1.0
        
        low, high = 0.0, 1.0
        for _ in range(8): 
            t = (low + high) / 2
            x = get_coordinate(t, x1, x2)
            if x < value:
                low = t
            else:
                high = t
        return get_coordinate((low + high) / 2, y1, y2)
    return solver

def spring(damping: float = 10.0, frequency: float = 10.0) -> Callable[[float], float]:
    return lambda value: 1.0 - math.exp(-damping * value) * math.cos(frequency * value)

def pulse(frequency: float = 1.0) -> Callable[[float], float]:
    return lambda value: (1 - math.cos(value * math.pi * 2 * frequency)) / 2

def breathe(value: float) -> float:
    return math.exp(math.sin(value * math.pi * 2 - math.pi / 2)) / math.e

def smooth_shake_easing(amplitude: float = 8.0, frequency: float = 20.0, decay: float = 5.0):
    def easing(progress: float):
        current_amp = amplitude * math.exp(-decay * progress)
        angle = progress * frequency * math.pi * 2

        offset = NvVector2.from_xy(
            current_amp * math.cos(angle),
            current_amp * math.sin(angle * 1.3)
        )
        return progress, offset
    return easing