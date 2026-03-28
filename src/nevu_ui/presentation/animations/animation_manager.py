import copy

from nevu_ui.presentation.animations.animations_library import linear
from nevu_ui.presentation.animations.animation_base import Animation, ColorAnimation, FloatAnimation, Vector2Animation
from nevu_ui.core.enums import AnimationType, AnimationManagerState

class AnimationManager:
    def __init__(self):
        self._basic_set_of_animations: dict[AnimationType | str, Animation|None] = {} #For annotationaaas !!
        
        self._basic_animation_type_requirements = {
            AnimationType.Color: ColorAnimation,
            AnimationType.Size: Vector2Animation,
            AnimationType.Position: Vector2Animation,
            AnimationType.Rotation: FloatAnimation,
            AnimationType.Opacity: FloatAnimation,
        }
        
        self._start_animations = self._basic_set_of_animations.copy()
        self._continuous_animations = self._basic_set_of_animations.copy()
        self._transition_animations = self._basic_set_of_animations.copy()

        self.transition_animation_easing = linear
        self.transition_time = 2

        self.state = AnimationManagerState.START
        self._running = True

        self.clear_current_animations()
        
    def clear_current_animations(self): self.current_animations.clear()

    def update(self):
        State = AnimationManagerState
        match self.state:
            case State.START:
                current_animations = self.current_animations
                for animation in current_animations.values():
                    if not animation: continue
                    animation.update()
                if all(animation is None or animation.ended for animation in current_animations.values()):
                    self.state = AnimationManagerState.TRANSITION
                    self._start_transition_animations()
            case State.TRANSITION:
                current_animations = self.current_animations
                all_transitions_finished = True  
                for anim_type, animation in current_animations.items():
                    if not animation: continue
                    animation.update()
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
                    if animation.ended:
                        self._restart_anim(animation)

            case State.ENDED:
                self._running = False
                self.clear_current_animations()
                self.state = AnimationManagerState.IDLE

            case State.IDLE: pass
    @property
    def current_animations(self) -> dict[AnimationType | str, Animation | None]:
        match self.state:
            case AnimationManagerState.START:
                return self._start_animations
            case AnimationManagerState.CONTINUOUS:
                return self._continuous_animations
            case AnimationManagerState.TRANSITION:
                return self._transition_animations
            case _: return {}

    @current_animations.setter
    def current_animations(self, new_animations: dict):
        match self.state:
            case AnimationManagerState.START:
                self._start_animations = new_animations
            case AnimationManagerState.CONTINUOUS:
                self._continuous_animations = new_animations
            case AnimationManagerState.TRANSITION:
                self._transition_animations = new_animations
            case _: pass
    
    def _add_animation_template(self, animations_dict, animation_key: AnimationType | str, animation: Animation):
        if animation_key in animations_dict:
            print(f"Warning: An animation of type {animation_key} already exists. It will be overwritten.")
        if animation_key in self._basic_animation_type_requirements and not isinstance(animation, self._basic_animation_type_requirements[animation_key]):
            raise ValueError(f"Animation of type {animation_key} must be of type {self._basic_animation_type_requirements[animation_key].__name__}")
        animations_dict[animation_key] = copy.copy(animation)
        animations_dict[animation_key].reset()
    
    def add_start_animation(self, animation_key: AnimationType | str, animation: Animation):
        self._add_animation_template(self._start_animations, animation_key, animation)
    
    def add_continuous_animation(self, animation_key: AnimationType | str, animation: Animation):
        self._add_animation_template(self._continuous_animations, animation_key, animation)
    
    def get_animation_value(self, animation_type: AnimationType | str):
        if anim := self.current_animations.get(animation_type): return anim.current_value
    
    def get_animation(self, animation_type: AnimationType):
        return self.current_animations.get(animation_type)
    
    def _start_transition_animations(self):
        for anim_type, cont_anim in self._continuous_animations.items():
            if not cont_anim: continue
            start_value = self.get_animation_value(anim_type) # type: ignore
            if start_value is None: continue
            end_value = cont_anim.start
            transition_time = cont_anim.max_time/2 if self.transition_time is None else self.transition_time
            transition_anim = cont_anim.__class__(start_value, end_value, transition_time, self.transition_animation_easing)# type: ignore
            self._transition_animations[anim_type] = transition_anim
            transition_anim.reset()
                
    def _restart_anim(self, animation: Animation):
        if animation:
            animation.start, animation.end = animation.end, animation.start
            animation.reset()