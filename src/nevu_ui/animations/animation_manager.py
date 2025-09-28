import copy

from enum import Enum, auto

from .animations_library import Linear

from .animation_base import Animation, AnimationType

class AnimationManagerState(Enum):
    START = auto()
    CONTINUOUS = auto()
    TRANSITION = auto()
    IDLE = auto()
    ENDED = auto()

class AnimationManager:
    def __init__(self):
        self.basic_set_of_animations: dict[AnimationType, Animation|None] = {
            AnimationType.COLOR: None,
            AnimationType.SIZE: None,
            AnimationType.POSITION: None,
            AnimationType.ROTATION: None,
            AnimationType.OPACITY: None,
        }
        self.start_animations = self.basic_set_of_animations.copy()
        self.continuous_animations = self.basic_set_of_animations.copy()
        self.transition_animations = self.basic_set_of_animations.copy()

        self.transition_animation = Linear
        self.transition_time = None

        self.state = AnimationManagerState.START
        self.runnung = True

        self.restart_anim_values()
    def restart_anim_values(self):
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
    def current_animations(self) -> dict[AnimationType, Animation|None]:
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
        if self.start_animations[animation.type] is not None:
            print(f"Warning: A start animation of type {animation.type} already exists. It will be overwritten.")
        self.start_animations[animation.type] = copy.copy(animation)
        if animation is not None:
            self.start_animations[animation.type].reset() # type: ignore

    def add_continuous_animation(self, animation: Animation):
        if self.continuous_animations[animation.type] is not None:
            print(f"Warning: A continuous animation of type {animation.type} already exists. It will be overwritten.")
        self.continuous_animations[animation.type] = copy.copy(animation)
        if animation is not None:
            self.continuous_animations[animation.type].reset() # type: ignore
    
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
                        end_value = tuple(cont_anim.start)
                    elif anim_type in (AnimationType.ROTATION, AnimationType.OPACITY):
                        end_value = -1
                    else:
                        end_value = cont_anim.start
                    transition_time = cont_anim.time_maximum/2 if self.transition_time is None else self.transition_time
                    transition_anim = self.transition_animation(transition_time, start_value, end_value, anim_type) # type: ignore
                    self.transition_animations[anim_type] = transition_anim
                    transition_anim.reset()
    def _restart_anim(self,animation: Animation):
        if animation:
            animation.reset()
            animation.start,animation.end = animation.end,animation.start
