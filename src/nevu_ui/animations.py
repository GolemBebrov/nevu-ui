import copy
import math
from abc import ABC, abstractmethod
from .utils import * 
import random
from enum import Enum, auto

class AnimationType(Enum):
    COLOR = auto()
    SIZE = auto()
    POSITION = auto()
    ROTATION = auto()
    OPACITY = auto()
    _not_used = auto()

class Animation(ABC):
    def __init__(self, time: int = 0, start: any = None, end: any = None, type: AnimationType = AnimationType._not_used):
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

class AnimationLinear(Animation):
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

class AnimationEaseIn(Animation):
    def _animation_update(self, value):
        eased_value = value * value
        self._apply_easing(eased_value)

class AnimationEaseOut(Animation):
    def _animation_update(self, value):
        eased_value = 1 - (1 - value) * (1 - value)
        self._apply_easing(eased_value)

class AnimationEaseInOut(Animation):
    def _animation_update(self, value):
        if value < 0.5:
            eased_value = 2 * value * value
        else:
            eased_value = -1 + (4 - 2 * value) * value
        self._apply_easing(eased_value)

class AnimationBounce(Animation):
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

class AnimationEaseInSine(Animation):
    def _animation_update(self, value):
        eased_value = 1 - math.cos((value * math.pi) / 2)
        self._apply_easing(eased_value)

class AnimationEaseOutSine(Animation):
    def _animation_update(self, value):
        eased_value = math.sin((value * math.pi) / 2)
        self._apply_easing(eased_value)

class AnimationEaseInOutSine(Animation):
    def _animation_update(self, value):
        eased_value = -(math.cos(math.pi * value) - 1) / 2
        self._apply_easing(eased_value)
class AnimationGlitch(Animation):
    def _animation_update(self, value):
        if value < 0.9:
            if random.random() < 0.1:  # 10% chance of glitching
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
            else: # Apply linear interpolation most of the time
                self._apply_easing(value)
        else: # Ensure it ends at the correct value
            self._apply_easing(1)

class AnimationShake(Animation):
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

class AnimationFlicker(Animation):
    def _animation_update(self, value):
        if self.type == AnimationType.OPACITY:
            if random.random() < 0.2:  # 20% chance of flickering
                self.current_value = random.uniform(0, 0.5)  # Flicker to a lower opacity
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

class AnimationPulse(Animation):
    def _animation_update(self, value):
        pulse_value = math.sin(value * math.pi * 4) * 0.2 + 0.8  # Pulse between 0.8 and 1.2

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
        
class AnimationEaseInQuad(Animation):
    def _animation_update(self, value):
        eased_value = value * value
        self._apply_easing(eased_value)
    
class AnimationEaseOutQuad(Animation):
     def _animation_update(self, value):
        eased_value = 1 - (1-value)*(1-value)
        self._apply_easing(eased_value)

class AnimationEaseInOutQuad(Animation):
    def _animation_update(self, value):
        if value < 0.5:
            eased_value = 2 * value * value
        else:
            eased_value =  -1 + (4 - 2 * value) * value
        self._apply_easing(eased_value)

class AnimationEaseInCubic(Animation):
    def _animation_update(self, value):
        eased_value = value * value * value
        self._apply_easing(eased_value)

class AnimationEaseOutCubic(Animation):
    def _animation_update(self, value):
        eased_value = 1 - pow(1 - value, 3)
        self._apply_easing(eased_value)

class AnimationEaseInOutCubic(Animation):
    def _animation_update(self, value):
        if value < 0.5:
            eased_value = 4 * value * value * value
        else:
            eased_value = 1 - pow(-2 * value + 2, 3) / 2
        self._apply_easing(eased_value)
    
class AnimationEaseInQuart(Animation):
    def _animation_update(self, value):
        eased_value = value * value * value * value
        self._apply_easing(eased_value)

class AnimationEaseOutQuart(Animation):
    def _animation_update(self, value):
        eased_value = 1 - pow(1 - value, 4)
        self._apply_easing(eased_value)

class AnimationEaseInOutQuart(Animation):
    def _animation_update(self, value):
        if value < 0.5:
            eased_value = 8 * value * value * value * value
        else:
            eased_value = 1 - pow(-2 * value + 2, 4) / 2
        self._apply_easing(eased_value)

class AnimationEaseInQuint(Animation):
    def _animation_update(self, value):
        eased_value = value * value * value * value * value
        self._apply_easing(eased_value)
    
class AnimationEaseOutQuint(Animation):
    def _animation_update(self, value):
        eased_value = 1 - pow(1 - value, 5)
        self._apply_easing(eased_value)

class AnimationEaseInOutQuint(Animation):
    def _animation_update(self, value):
        if value < 0.5:
            eased_value = 16 * value * value * value * value * value
        else:
            eased_value = 1 - pow(-2 * value + 2, 5) / 2
        self._apply_easing(eased_value)

class AnimationEaseInExpo(Animation):
    def _animation_update(self, value):
        eased_value = 0 if value == 0 else pow(2, 10 * value - 10)
        self._apply_easing(eased_value)

class AnimationEaseOutExpo(Animation):
    def _animation_update(self, value):
        eased_value = 1 if value == 1 else 1 - pow(2, -10 * value)
        self._apply_easing(eased_value)
        
class AnimationEaseInOutExpo(Animation):
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


class AnimationEaseInCirc(Animation):
    def _animation_update(self, value):
        eased_value = 1 - math.sqrt(1 - pow(value, 2))
        self._apply_easing(eased_value)

class AnimationEaseOutCirc(Animation):
    def _animation_update(self, value):
        eased_value = math.sqrt(1 - pow(value - 1, 2))
        self._apply_easing(eased_value)
    
class AnimationEaseInOutCirc(Animation):
    def _animation_update(self, value):
        if value < 0.5:
            eased_value = (1 - math.sqrt(1 - pow(2 * value, 2))) / 2
        else:
            eased_value = (math.sqrt(1 - pow(-2 * value + 2, 2)) + 1) / 2
        self._apply_easing(eased_value)

class AnimationEaseInBack(Animation):
    def _animation_update(self, value):
        c1 = 1.70158
        c3 = c1 + 1
        eased_value = c3 * value * value * value - c1 * value * value
        self._apply_easing(eased_value)
        
class AnimationEaseOutBack(Animation):
    def _animation_update(self, value):
        c1 = 1.70158
        c3 = c1 + 1
        eased_value = 1 + c3 * pow(value - 1, 3) + c1 * pow(value - 1, 2)
        self._apply_easing(eased_value)

class AnimationEaseInOutBack(Animation):
    def _animation_update(self, value):
        c1 = 1.70158
        c2 = c1 * 1.525
        if value < 0.5:
            eased_value = (pow(2 * value, 2) * ((c2 + 1) * 2 * value - c2)) / 2
        else:
            eased_value = (pow(2 * value - 2, 2) * ((c2 + 1) * (value * 2 - 2) + c2) + 2) / 2
        self._apply_easing(eased_value)

def _apply_common_easing(self, eased_value):
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

for cls in Animation.__subclasses__():
  if cls not in (AnimationLinear, AnimationBounce):
    cls._apply_easing = _apply_common_easing

class AnimationManagerState(Enum):
    START = auto()
    CONTINUOUS = auto()
    TRANSITION = auto()
    IDLE = auto()
    ENDED = auto()

class AnimationManager:
    def __init__(self):
        self.basic_set_of_animations = {
            AnimationType.COLOR: None,
            AnimationType.SIZE: None,
            AnimationType.POSITION: None,
            AnimationType.ROTATION: None,
            AnimationType.OPACITY: None,
        }
        self.start_animations = self.basic_set_of_animations.copy()
        self.continuous_animations = self.basic_set_of_animations.copy()
        self.transition_animations = self.basic_set_of_animations.copy()

        self.transition_animation = AnimationLinear
        self.transition_time = None

        self.state = AnimationManagerState.START
        self.runnung = True

        self.restart_anim_values()
    def restart_anim_values(self):
        self.current_animations: dict[AnimationType, Animation]
        self.current_values = self.basic_set_of_animations.copy()
    def process_animation(self, animation: Animation):
        
        self.current_values[animation.type] = animation.current_value

    def update(self):
        State = AnimationManagerState
        match self.state:

            case State.START:
                current_animations = self.current_animations
                for anim_type, animation in current_animations.items():
                    if not animation: continue
                    animation.update()
                    self.process_animation(animation)
                    if animation.ended: current_animations[anim_type] = None
                if all(animation is None for animation in current_animations.values()):
                    self.state = AnimationManagerState.TRANSITION
                    self._start_transition_animations()

            case State.TRANSITION:
                current_animations = self.current_animations
                all_transitions_finished = True  
                for anim_type, animation in current_animations.items():
                    if not animation: continue
                    animation.update()
                    self.process_animation(animation)

                    if not animation.ended:
                        all_transitions_finished = False 

                if all_transitions_finished:
                    self.state = AnimationManagerState.CONTINUOUS

            case State.CONTINUOUS:
                current_animations = self.current_animations
                if all(animation is None for animation in current_animations.values()):
                    self.state = AnimationManagerState.ENDED
                for anim_type, animation in current_animations.items():
                    if not animation: continue
                    animation.update()
                    self.process_animation(animation)
                    if animation.ended:
                        self._restart_anim(animation)

            case State.ENDED:
                self.runnung = False
                self.restart_anim_values()
                self.state = AnimationManagerState.IDLE

            case State.IDLE:
                pass
    @property
    def current_animations(self) -> dict:
        match self.state:
            case AnimationManagerState.START:
                return self.start_animations
            case AnimationManagerState.CONTINUOUS:
                return self.continuous_animations
            case AnimationManagerState.TRANSITION:
                return self.transition_animations
            case _:
                return {}

    @current_animations.setter
    def current_animations(self, new_animations: dict):
        match self.state:
            case AnimationManagerState.START:
                self.start_animations = new_animations
            case AnimationManagerState.CONTINUOUS:
                self.continuous_animations = new_animations
            case AnimationManagerState.TRANSITION:
                self.transition_animations = new_animations
            case _:
                pass

    def add_start_animation(self, animation: Animation):
        if not self.start_animations[animation.type] is None:
            print(f"Warning: A start animation of type {animation.type} already exists. It will be overwritten.")
        self.start_animations[animation.type] = copy.copy(animation)
        self.start_animations[animation.type].reset()

    def add_continuous_animation(self, animation: Animation):
        if not self.continuous_animations[animation.type] is None:
            print(f"Warning: A continuous animation of type {animation.type} already exists. It will be overwritten.")
        self.continuous_animations[animation.type] = copy.copy(animation)
        self.continuous_animations[animation.type].reset()
    
    def get_current_value(self, anim_type: AnimationType):
        return self.current_values.get(anim_type)
    def get_animation_value(self, animation_type: AnimationType):
        return self.current_values.get(animation_type)
    def _start_transition_animations(self):
        for anim_type, cont_anim in self.continuous_animations.items():
            if cont_anim:
                start_value = self.get_current_value(anim_type)
                if start_value is not None:
                    if anim_type in (AnimationType.SIZE, AnimationType.POSITION):
                        end_value = tuple(x for x in cont_anim.start)
                    elif anim_type in (AnimationType.ROTATION, AnimationType.OPACITY):
                        end_value = -1
                    else:
                        end_value = cont_anim.start
                    transition_time = cont_anim.time_maximum/2 if self.transition_time is None else self.transition_time
                    transition_anim = self.transition_animation(transition_time, start_value, end_value, anim_type) 
                    self.transition_animations[anim_type] = transition_anim
                    transition_anim.reset()
    def _restart_anim(self,animation: Animation):
        if animation:
            animation.reset()
            animation.start,animation.end = animation.end,animation.start
