from collections.abc import Callable
from typing import Any

from nevu_ui.core.enums import AnimType, BindType
from . import (
    Animation,
    AnimationQueue,
    ColorAnimation,
    FloatAnimation,
    TupleAnimation,
    Vector2Animation,
)


ANIMATION_REQUIREMENTS = {
    AnimType.BgColor: ColorAnimation,
    AnimType.BdColor: ColorAnimation,
    AnimType.TextColor: ColorAnimation,
    AnimType.Size: Vector2Animation,
    AnimType.Position: Vector2Animation,
    AnimType.Opacity: FloatAnimation,
}


class AnimationManager:
    __slots__ = [
        "_animation_requirements",
        "_animation_results",
        "_animations_pool",
        "_running_animations",
        "_updated_keys",
        "_warn",
    ]

    def __init__(
        self,
        animations: dict[BindType | str, dict[AnimType | str, Animation]] | None = None,
        warn: bool = True,
    ):
        self._animations_pool: dict[BindType | str, dict[AnimType | str, Animation]] = animations or {}
        self._animation_results: dict[AnimType | str, Any] = {}
        self._running_animations: list[tuple[AnimType | str, Animation]] = []
        self._updated_keys: set[AnimType | str] = set()
        self._warn = warn

    def call(self, bind_type: BindType | str):
        if not (anim_dict := self._animations_pool.get(bind_type)):
            return
        for anim_type, animation in anim_dict.items():
            self._running_animations = [
                (t, a) for (t, a) in self._running_animations if t != anim_type
            ]
            animation.reset()
            self._running_animations.append((anim_type, animation))
            self._animation_results[anim_type] = animation.current_value
            self._updated_keys.add(anim_type)

    def transition(
        self,
        anim_type: AnimType | str,
        target: Any,
        anim_cls: type[Animation],
        duration: float,
        easing_func: Callable | None = None,
        current_fallback: Any = None,
    ):
        running = None
        for t, a in self._running_animations:
            if t == anim_type and not a.ended:
                running = a
                break

        if running is not None:
            start_val = running.current_value
            if target == running._reversing_start and running.max_time > 0:
                out_progress = running.output_progress()
                old_factor = running._shortening_factor
                factor = max(
                    0.0,
                    min(1.0, abs(out_progress * old_factor + (1.0 - old_factor))),
                )
                rev_start = running.end
            else:
                factor = 1.0
                rev_start = start_val
        else:
            start_val = current_fallback
            factor = 1.0
            rev_start = current_fallback

        actual_duration = duration * factor
        if actual_duration <= 0:
            self.stop(anim_type)
            return

        anim = anim_cls(start_val, target, actual_duration, easing_func)
        anim._reversing_start = rev_start
        anim._shortening_factor = factor

        anim_group = self._animations_pool.setdefault("__transition", {})
        anim_group[anim_type] = anim

        self._running_animations = [
            (t, a) for (t, a) in self._running_animations if t != anim_type
        ]
        anim.reset()
        self._running_animations.append((anim_type, anim))
        self._animation_results[anim_type] = anim.current_value
        self._updated_keys.add(anim_type)

    def stop(self, anim_type: AnimType | str):
        self._running_animations = [
            (t, a) for (t, a) in self._running_animations if t != anim_type
        ]
        self._animation_results.pop(anim_type, None)
        self._updated_keys.discard(anim_type)

    def bind(
        self,
        bind_type: BindType | str,
        anim_type: AnimType | str,
        animation: Animation,
    ):
        if ANIMATION_REQUIREMENTS.get(anim_type) is not None:
            if not isinstance(animation, ANIMATION_REQUIREMENTS[anim_type] | AnimationQueue):
                raise TypeError(
                    "Animation must be of type " + str(ANIMATION_REQUIREMENTS[anim_type])
                )
        anim_group = self._animations_pool.setdefault(bind_type, {})
        if anim_group.get(anim_type) and self._warn:
            print(
                f"Warning: Binding new animation to existing one in {bind_type}. Old one will be replaced."
            )
        self._animations_pool[bind_type][anim_type] = animation

    def clear_binds(self, bind_type: BindType | str):
        self._animations_pool.pop(bind_type, None)

    def has_animations(self, bind_type: BindType | str) -> bool:
        return bind_type in self._animations_pool

    def was_updated(self, *anim_types: AnimType | str) -> bool:
        if not self._updated_keys:
            return False
        return any(t in self._updated_keys for t in anim_types)

    def is_running(self, anim_type: AnimType | str) -> bool:
        return any(t == anim_type and not a.ended for t, a in self._running_animations)

    def get(self, anim_type: AnimType | str, default: Any = None) -> Any:
        return self._animation_results.get(anim_type, default)

    def get_animation(
        self, bind_type: BindType | str, anim_type: AnimType | str
    ) -> Animation:
        try:
            return self._animations_pool[bind_type][anim_type]
        except KeyError as e:
            raise ValueError("No bindings found with type " + str(bind_type)) from e

    def update(self):
        self._updated_keys.clear()
        if not self._running_animations:
            self._animation_results.clear()
            return
        ended_animations = []
        self._animation_results.clear()
        for anim_type, animation in self._running_animations:
            if animation.ended:
                ended_animations.append((anim_type, animation))
                continue
            animation.update()
            self._animation_results[anim_type] = animation.current_value
            self._updated_keys.add(anim_type)

        for value in ended_animations:
            self._running_animations.remove(value)
