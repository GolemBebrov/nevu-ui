import math

def linear(value):
    return value

def ease_in(value):
    return value * value

def ease_out(value):
    return 1 - (1 - value) * (1 - value)

def ease_in_out(value):
    if value < 0.5:
        return 2 * value * value
    else:
        return -1 + (4 - 2 * value) * value

def bounce(value):
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

def ease_in_sine(value):
    return 1 - math.cos((value * math.pi) / 2)

def ease_out_sine(value):
    return math.sin((value * math.pi) / 2)

def ease_in_out_sine(value):
    return -(math.cos(math.pi * value) - 1) / 2

def ease_in_quad(value):
    return value * value

def ease_out_quad(value):
    return 1 - (1 - value) * (1 - value)

def ease_in_out_quad(value):
    if value < 0.5:
        return 2 * value * value
    else:
        return -1 + (4 - 2 * value) * value

def ease_in_cubic(value):
    return value * value * value

def ease_out_cubic(value):
    return 1 - pow(1 - value, 3)

def ease_in_out_cubic(value):
    if value < 0.5:
        return 4 * value * value * value
    else:
        return 1 - pow(-2 * value + 2, 3) / 2

def ease_in_quart(value):
    return value * value * value * value

def ease_out_quart(value):
    return 1 - pow(1 - value, 4)

def ease_in_out_quart(value):
    if value < 0.5:
        return 8 * value * value * value * value
    else:
        return 1 - pow(-2 * value + 2, 4) / 2

def ease_in_quint(value):
    return value * value * value * value * value

def ease_out_quint(value):
    return 1 - pow(1 - value, 5)

def ease_in_out_quint(value):
    if value < 0.5:
        return 16 * value * value * value * value * value
    else:
        return 1 - pow(-2 * value + 2, 5) / 2

def ease_in_expo(value):
    return 0 if value == 0 else pow(2, 10 * value - 10)

def ease_out_expo(value):
    return 1 if value == 1 else 1 - pow(2, -10 * value)

def ease_in_out_expo(value):
    if value == 0:
        return 0
    elif value == 1:
        return 1
    elif value < 0.5:
        return pow(2, 20 * value - 10) / 2
    else:
        return (2 - pow(2, -20 * value + 10)) / 2

def ease_in_circ(value):
    return 1 - math.sqrt(1 - pow(value, 2))

def ease_out_circ(value):
    return math.sqrt(1 - pow(value - 1, 2))

def ease_in_out_circ(value):
    if value < 0.5:
        return (1 - math.sqrt(1 - pow(2 * value, 2))) / 2
    else:
        return (math.sqrt(1 - pow(-2 * value + 2, 2)) + 1) / 2

def ease_in_back(value):
    c1 = 1.70158
    c3 = c1 + 1
    return c3 * value * value * value - c1 * value * value

def ease_out_back(value):
    c1 = 1.70158
    c3 = c1 + 1
    return 1 + c3 * pow(value - 1, 3) + c1 * pow(value - 1, 2)

def ease_in_out_back(value):
    c1 = 1.70158
    c2 = c1 * 1.525
    if value < 0.5:
        return (pow(2 * value, 2) * ((c2 + 1) * 2 * value - c2)) / 2
    else:
        return (pow(2 * value - 2, 2) * ((c2 + 1) * (value * 2 - 2) + c2) + 2) / 2

def ease_in_power(power):
    return lambda value: pow(value, power)

def ease_out_power(power):
    return lambda value: 1 - pow(1 - value, power)

def ease_in_elastic(value):
    c4 = (2 * math.pi) / 3
    if value == 0: return 0
    if value == 1: return 1
    return -pow(2, 10 * value - 10) * math.sin((value * 10 - 10.75) * c4)

def ease_out_elastic(value):
    c4 = (2 * math.pi) / 3
    if value == 0: return 0
    if value == 1: return 1
    return pow(2, -10 * value) * math.sin((value * 10 - 0.75) * c4) + 1

def ease_in_bounce(value):
    return 1 - bounce(1 - value)

def ease_in_out_bounce(value):
    if value < 0.5:
        return (1 - bounce(1 - 2 * value)) / 2
    else:
        return (1 + bounce(2 * value - 1)) / 2

def steps(n):
    return lambda value: math.floor(value * n) / n