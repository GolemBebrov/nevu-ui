import math
import random

from .animation_base import Animation, AnimationType

class Linear(Animation):
    def _animation_update(self, value):
        if self.type == AnimationType.COLOR:
            self.current_value = tuple(round(self.start[i] + (self.end[i] - self.start[i]) * value) for i in range(4))
        elif self.type == AnimationType.SIZE:
            self.current_value = tuple(round(self.start[i] + (self.end[i] - self.start[i]) * value) for i in range(2))
        elif self.type == AnimationType.POSITION:
            self.current_value = tuple(round(self.start[i] + (self.end[i] - self.start[i]) * value) for i in range(2))
        elif self.type == AnimationType.ROTATION:
            self.current_value = self.start + (self.end - self.start) * value
        elif self.type == AnimationType.OPACITY:
            self.current_value = self.start + (self.end - self.start) * value
        else:
            raise ValueError(f"Unsupported animation type: {self.type}")

class EaseIn(Animation):
    def _animation_update(self, value):
        eased_value = value * value
        self._apply_easing(eased_value)

class EaseOut(Animation):
    def _animation_update(self, value):
        eased_value = 1 - (1 - value) * (1 - value)
        self._apply_easing(eased_value)

class EaseInOut(Animation):
    def _animation_update(self, value):
        if value < 0.5:
            eased_value = 2 * value * value
        else:
            eased_value = -1 + (4 - 2 * value) * value
        self._apply_easing(eased_value)

class Bounce(Animation):
    def _animation_update(self, value):
        def bounce_easing(t):
            if t < (1 / 2.75):
                return 7.5625 * t * t
            elif t < (2 / 2.75):
                t -= (1.5 / 2.75)
                return 7.5625 * t * t + 0.75
            elif t < (2.5 / 2.75):
                t -= (2.25 / 2.75)
                return 7.5625 * t * t + 0.9375
            else:
                t -= (2.625 / 2.75)
                return 7.5625 * t * t + 0.984375

        eased_value = bounce_easing(value)
        self._apply_easing(eased_value)

    def _apply_easing(self, eased_value):
        if self.type == AnimationType.COLOR:
            self.current_value = tuple(round(self.start[i] + (self.end[i] - self.start[i]) * eased_value) for i in range(4))
        elif self.type == AnimationType.SIZE:
            self.current_value = tuple(round(self.start[i] + (self.end[i] - self.start[i]) * eased_value) for i in range(2))
        elif self.type == AnimationType.POSITION:
            self.current_value = tuple(round(self.start[i] + (self.end[i] - self.start[i]) * eased_value) for i in range(2))
        elif self.type == AnimationType.ROTATION:
            self.current_value = self.start + (self.end - self.start) * eased_value
        elif self.type == AnimationType.OPACITY:
            self.current_value = self.start + (self.end - self.start) * eased_value
        else:
            raise ValueError(f"Unsupported animation type: {self.type}")

class EaseInSine(Animation):
    def _animation_update(self, value):
        eased_value = 1 - math.cos((value * math.pi) / 2)
        self._apply_easing(eased_value)

class EaseOutSine(Animation):
    def _animation_update(self, value):
        eased_value = math.sin((value * math.pi) / 2)
        self._apply_easing(eased_value)

class EaseInOutSine(Animation):
    def _animation_update(self, value):
        eased_value = -(math.cos(math.pi * value) - 1) / 2
        self._apply_easing(eased_value)

class Glitch(Animation):
    def _animation_update(self, value):
        if value < 0.9:
            if random.random() < 0.1:
                if self.type == AnimationType.COLOR:
                    self.current_value = tuple(random.randint(0, 255) for _ in range(4))
                elif self.type == AnimationType.SIZE:
                    self.current_value = tuple(random.randint(int(self.start[i] * 0.5), int(self.end[i] * 1.5)) for i in range(2))
                elif self.type == AnimationType.POSITION:
                    self.current_value = tuple(random.randint(int(self.start[i] - 50), int(self.end[i] + 50)) for i in range(2))
                elif self.type == AnimationType.ROTATION:
                    self.current_value = random.uniform(self.start - 45, self.end + 45)
                elif self.type == AnimationType.OPACITY:
                    self.current_value = random.uniform(0, 1)
            else:
                self._apply_easing(value)
        else:
            self._apply_easing(1)

class Shake(Animation):
    def __init__(self, time, start, end, type:AnimationType,shake_amplitude=1,continuous=False):
        super().__init__(time, start, end, type)
        self.shake_amplitude = shake_amplitude
        self.continuous = continuous
    def _animation_update(self, value):
        magnitude = (1 - value) * 10
        if self.type == AnimationType.POSITION:
            if self.continuous == False:
                offset_x = random.uniform(-magnitude, magnitude)*self.shake_amplitude
                offset_y = random.uniform(-magnitude, magnitude)*self.shake_amplitude
            else:
                offset_x = random.uniform(-self.shake_amplitude,self.shake_amplitude)
                offset_y = random.uniform(-self.shake_amplitude,self.shake_amplitude)
            self.current_value = (
                round(self.start[0] + (self.end[0] - self.start[0]) * value + offset_x),
                round(self.start[1] + (self.end[1] - self.start[1]) * value + offset_y)
            )
        elif self.type == AnimationType.ROTATION:
            offset_angle = random.uniform(-magnitude * 5, magnitude * 5)
            self.current_value = self.start + (self.end - self.start) * value + offset_angle
        elif self.type == AnimationType.COLOR:
             self.current_value = tuple(round(self.start[i] + (self.end[i] - self.start[i]) * value) for i in range(4))
        elif self.type == AnimationType.SIZE:
            self.current_value = tuple(round(self.start[i] + (self.end[i] - self.start[i]) * value) for i in range(2))
        elif self.type == AnimationType.OPACITY:
             self.current_value = self.start + (self.end - self.start) * value
        else:
             raise ValueError

class Flicker(Animation):
    def _animation_update(self, value):
        if self.type == AnimationType.OPACITY:
            if random.random() < 0.2:
                self.current_value = random.uniform(0, 0.5)
            else:
                self.current_value = self.start + (self.end - self.start) * value
        elif self.type == AnimationType.COLOR:
            if random.random() < 0.2:
                self.current_value = (random.randint(0,255),random.randint(0,255),random.randint(0,255),random.randint(0,255))
            else:
                self.current_value = tuple(round(self.start[i] + (self.end[i] - self.start[i]) * value) for i in range(4))
        elif self.type == AnimationType.SIZE:
            self.current_value = tuple(round(self.start[i] + (self.end[i] - self.start[i]) * value) for i in range(2))
        elif self.type == AnimationType.POSITION:
             self.current_value = tuple(round(self.start[i] + (self.end[i] - self.start[i]) * value) for i in range(2))
        elif self.type == AnimationType.ROTATION:
            self.current_value = self.start + (self.end - self.start) * value
        else:
             raise ValueError

class Pulse(Animation):
    def _animation_update(self, value):
        pulse_value = math.sin(value * math.pi * 4) * 0.2 + 0.8
        if self.type == AnimationType.SIZE:
            self.current_value = tuple(round(self.start[i] + (self.end[i] - self.start[i]) * value * pulse_value) for i in range(2))
        elif self.type == AnimationType.OPACITY:
            self.current_value = self.start + (self.end - self.start) * value * pulse_value
        elif self.type == AnimationType.COLOR:
            self.current_value = tuple(round(self.start[i] + (self.end[i] - self.start[i]) * value) for i in range(4))
        elif self.type == AnimationType.POSITION:
             self.current_value = tuple(round(self.start[i] + (self.end[i] - self.start[i]) * value) for i in range(2))
        elif self.type == AnimationType.ROTATION:
            self.current_value = self.start + (self.end - self.start) * value
        else:
            raise ValueError

class EaseInQuad(Animation):
    def _animation_update(self, value):
        eased_value = value * value
        self._apply_easing(eased_value)

class EaseOutQuad(Animation):
     def _animation_update(self, value):
        eased_value = 1 - (1-value)*(1-value)
        self._apply_easing(eased_value)

class EaseInOutQuad(Animation):
    def _animation_update(self, value):
        if value < 0.5:
            eased_value = 2 * value * value
        else:
            eased_value =  -1 + (4 - 2 * value) * value
        self._apply_easing(eased_value)

class EaseInCubic(Animation):
    def _animation_update(self, value):
        eased_value = value * value * value
        self._apply_easing(eased_value)

class EaseOutCubic(Animation):
    def _animation_update(self, value):
        eased_value = 1 - pow(1 - value, 3)
        self._apply_easing(eased_value)

class EaseInOutCubic(Animation):
    def _animation_update(self, value):
        if value < 0.5:
            eased_value = 4 * value * value * value
        else:
            eased_value = 1 - pow(-2 * value + 2, 3) / 2
        self._apply_easing(eased_value)

class EaseInQuart(Animation):
    def _animation_update(self, value):
        eased_value = value * value * value * value
        self._apply_easing(eased_value)

class EaseOutQuart(Animation):
    def _animation_update(self, value):
        eased_value = 1 - pow(1 - value, 4)
        self._apply_easing(eased_value)

class EaseInOutQuart(Animation):
    def _animation_update(self, value):
        if value < 0.5:
            eased_value = 8 * value * value * value * value
        else:
            eased_value = 1 - pow(-2 * value + 2, 4) / 2
        self._apply_easing(eased_value)

class EaseInQuint(Animation):
    def _animation_update(self, value):
        eased_value = value * value * value * value * value
        self._apply_easing(eased_value)

class EaseOutQuint(Animation):
    def _animation_update(self, value):
        eased_value = 1 - pow(1 - value, 5)
        self._apply_easing(eased_value)

class EaseInOutQuint(Animation):
    def _animation_update(self, value):
        if value < 0.5:
            eased_value = 16 * value * value * value * value * value
        else:
            eased_value = 1 - pow(-2 * value + 2, 5) / 2
        self._apply_easing(eased_value)

class EaseInExpo(Animation):
    def _animation_update(self, value):
        eased_value = 0 if value == 0 else pow(2, 10 * value - 10)
        self._apply_easing(eased_value)

class EaseOutExpo(Animation):
    def _animation_update(self, value):
        eased_value = 1 if value == 1 else 1 - pow(2, -10 * value)
        self._apply_easing(eased_value)

class EaseInOutExpo(Animation):
    def _animation_update(self, value):
        if value == 0:
            eased_value = 0
        elif value == 1:
            eased_value = 1
        elif value < 0.5:
            eased_value = pow(2, 20 * value - 10) / 2
        else:
            eased_value = (2 - pow(2, -20 * value + 10)) / 2
        self._apply_easing(eased_value)

class EaseInCirc(Animation):
    def _animation_update(self, value):
        eased_value = 1 - math.sqrt(1 - pow(value, 2))
        self._apply_easing(eased_value)

class EaseOutCirc(Animation):
    def _animation_update(self, value):
        eased_value = math.sqrt(1 - pow(value - 1, 2))
        self._apply_easing(eased_value)

class EaseInOutCirc(Animation):
    def _animation_update(self, value):
        if value < 0.5:
            eased_value = (1 - math.sqrt(1 - pow(2 * value, 2))) / 2
        else:
            eased_value = (math.sqrt(1 - pow(-2 * value + 2, 2)) + 1) / 2
        self._apply_easing(eased_value)

class EaseInBack(Animation):
    def _animation_update(self, value):
        c1 = 1.70158
        c3 = c1 + 1
        eased_value = c3 * value * value * value - c1 * value * value
        self._apply_easing(eased_value)

class EaseOutBack(Animation):
    def _animation_update(self, value):
        c1 = 1.70158
        c3 = c1 + 1
        eased_value = 1 + c3 * pow(value - 1, 3) + c1 * pow(value - 1, 2)
        self._apply_easing(eased_value)

class EaseInOutBack(Animation):
    def _animation_update(self, value):
        c1 = 1.70158
        c2 = c1 * 1.525
        if value < 0.5:
            eased_value = (pow(2 * value, 2) * ((c2 + 1) * 2 * value - c2)) / 2
        else:
            eased_value = (pow(2 * value - 2, 2) * ((c2 + 1) * (value * 2 - 2) + c2) + 2) / 2
        self._apply_easing(eased_value)