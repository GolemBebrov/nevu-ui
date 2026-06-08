from typing import Callable, Any

from nevu_ui.core import Annotations
from nevu_ui.core.enums import GradientType
from nevu_ui.fast.nvraygrad.nvraygrad import GradientRaylib, ClickGradient
from nevu_ui.presentation.animations.animation_base import ColorAnimation, FloatAnimation, Vector2Animation
from nevu_ui.presentation.animations.animation_manager import AnimationManager
from nevu_ui.fast.nvvector2 import NvVector2
from nevu_ui.presentation.animations.animations_library import ease_in_out_quad

#Siuuuu void file, basically a real nothing

#Reg approved

__WOW_THIS_IS_REAL_NOTHING = float("NaN")

def animated_slot(start: Any = None, end: Any = None, time: int = 1, easing_func: Callable = ease_in_out_quad):
    return (start, end, time, easing_func)

anim_slot = tuple[Any, Any, int, Callable]
anim_color_slot = tuple[Annotations.rgba_color, Annotations.rgba_color, int, Callable]

_base_text = "__reserved_"

class AnimatedGradient(GradientRaylib):
    ColorBase = f"{_base_text}color"
    AngleBase = f"{_base_text}angle"
    CenterBase = f"{_base_text}center"
    TransparencyBase = f"{_base_text}transparency"
    def __init__(self, colors: anim_color_slot, type = GradientType.Linear, 
                 angle: anim_slot | None = None, center: anim_slot | None = None, transparency: anim_slot | None = None):
        start = 0
        end = 1
        time = 2
        func = 3
        
        self.transparency_initalized = False
        self.center_initalized = False
        self.angle_initalized = False
        
        nvvec = NvVector2.from_tuple
        self.animation_manager = AnimationManager()
        
        # === Colors ===
        if len(colors[start]) != len(colors[end]):
            raise ValueError("Start and end colors must have the same length.")
        
        colors_time = colors[time] or 1
        colors_func = colors[func]
        self.colors_len = len(colors[start])
        for i in range(len(colors[start])):
            anim = ColorAnimation(colors[start][i], colors[end][i], colors_time, colors_func)
            self.animation_manager.add_continuous_animation(self.ColorBase + str(i), anim)
        base_colors = colors[start]
        
        # === Angle ===
        if angle is not None:
            base_angle = angle[start]
            angle_anim = FloatAnimation(base_angle, angle[end], angle[time], angle[func])
            self.animation_manager.add_continuous_animation(self.AngleBase, angle_anim)
            self.angle_initalized = True
        else:
            angle_anim = None
            base_angle = 255
        
        # === Center ===
        if center is not None:
            base_center = center[start]
            center_anim = Vector2Animation(nvvec(base_center), nvvec(center[end]), center[time], center[func])
            self.animation_manager.add_continuous_animation(self.CenterBase, center_anim)
            self.center_initalized = True
        else:
            center_anim = None
            base_center = (0.5, 0.5)
        
        # === Transparency ===
        if transparency is not None:
            base_transparency = transparency[start]
            transparency_anim = FloatAnimation(base_transparency, transparency[end], transparency[time], transparency[func])
            self.animation_manager.add_continuous_animation(self.TransparencyBase, transparency_anim)
            self.transparency_initalized = True
        else:
            transparency_anim = None
            base_transparency = 0
        
        super().__init__(base_colors, type, None, base_angle, base_center, base_transparency)
        
    def update(self):
        old_angle = self.angle
        old_center = self.center
        old_transparency = self.transparency
        old_colors = self.colors
        changed = False
        self.animation_manager.update()
        if self.angle_initalized:
            new_angle = self.animation_manager.get_animation_value(self.AngleBase)
            if new_angle != old_angle and new_angle is not None:
                self.angle = new_angle
                changed = True
        if self.center_initalized:
            new_center = self.animation_manager.get_animation_value(self.CenterBase)
            if new_center != old_center and new_center is not None:
                self.center = new_center
                changed = True
        if self.transparency_initalized:
            new_transparency = self.animation_manager.get_animation_value(self.TransparencyBase)
            if new_transparency != old_transparency and new_transparency is not None:
                self.transparency = new_transparency
                changed = True
        new_colors = []
        skip_colors = False
        for i in range(self.colors_len):
            color = self.animation_manager.get_animation_value(self.ColorBase + str(i))
            if color is None:
                skip_colors = True
                break
            new_colors.append(color)
        if skip_colors: return changed
        if new_colors != old_colors:
            self.colors = new_colors
            changed = True
        return changed