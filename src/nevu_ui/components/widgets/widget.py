import copy
from collections.abc import Callable
from typing import Unpack, overload

import nevu_ui.core.modules as md
from nevu_ui.components._typehints import (
    _WidgetKwargs,
    _WidgetKwargsLongFull,
    _WidgetKwargsShortFull,
)
from nevu_ui.components.nevuobject import NevuObject
from nevu_ui.core import Annotations
from nevu_ui.core.enums import (
    AnimType,
    BindType,
    CacheType,
    CustomFunctions,
    ParamLayer,
    RenderReturnType,
)
from nevu_ui.core.state import _analize_bg, nevu_state
from nevu_ui.cython.logic import check_moved
from nevu_ui.cython.surface.surface import Surface
from nevu_ui.cython.vector2 import Vector2
from nevu_ui.cython.raylib.raylib import begin_blend_mode, end_blend_mode
from nevu_ui.presentation.animations import (
    ColorAnimation,
    FloatAnimation,
    TupleAnimation,
    ease_out_quad,
)
from nevu_ui.presentation.animations.presets import ease_out_cubic
from nevu_ui.presentation.theme import PairColorRole, SubThemeRole
from nevu_ui.presentation import color
from nevu_ui.presentation.style import StateVariable, Style
from nevu_ui.rendering import DrawBaseCall, DrawBordersCall, DrawEffectsCall
from nevu_ui.rendering.raylib.gradient import ClickGradient
from nevu_ui.utils import mouse


class Widget(NevuObject):
    inverted: bool
    clickable: bool
    hoverable: bool
    invert_on_click: bool
    ripple_effect: bool
    animate_color_change: bool
    transition_time: int | float
    transition_easing: Callable | None
    font_role: PairColorRole
    z: int
    draw_borders: bool
    draw_content: bool
    glassy: bool

    @overload
    def __init__(
        self,
        size: Annotations.nevuobj_size = None,
        style: Annotations.nevuobj_style = None,
        **params: Unpack[_WidgetKwargsShortFull],
    ): ...
    @overload
    def __init__(
        self,
        size: Annotations.nevuobj_size = None,
        style: Annotations.nevuobj_style = None,
        **params: Unpack[_WidgetKwargsLongFull],
    ): ...
    def __init__(
        self,
        size: Annotations.nevuobj_size = None,
        style: Annotations.nevuobj_style = None,
        **params: Unpack[_WidgetKwargs],
    ):
        super().__init__(size, style, **params)

    def _add_params(self):
        super()._add_params()
        self._add_param(
            "inverted",
            bool,
            False,
            setter=self._inverted_setter,
            layer=ParamLayer.Complicated,
        )
        self._add_param_link("alt", "inverted")
        self._add_param("clickable", bool, False)
        self._add_param("hoverable", bool, False)
        self._add_param("invert_on_click", bool, False)
        self._change_param_default("z", 1)
        self._add_param("font_role", PairColorRole, PairColorRole.InverseSurface)
        self._add_param("draw_borders", bool, True)
        self._add_param("draw_content", bool, True)
        self._add_param("ripple_effect", bool, True)
        self._add_param("animate_color_change", bool, True)
        self._add_param("transition_time", int | float, 0.15)
        self._add_param("transition_easing", (type(None), Callable), None)
        self._add_param("glassy", bool, False)
        self._change_param_default("subtheme_role", SubThemeRole.Secondary)

    def _init_objects(self):
        super()._init_objects()
        self.__inner_bg_transparent = False
        self._style_targets = {}
        self._cached_gradient_ref = None
        self._cached_image_ref = None
        self._cached_font_key = None

    def _system_callback_binds(self):
        super()._system_callback_binds()
        self._system_callbacks.bind(BindType.Hover, _widget_on_hover_change)
        self._system_callbacks.bind(BindType.Unhover, _widget_on_hover_change)

        self._system_callbacks.bind(BindType.KeyUp, _widget_on_keyup)
        self._system_callbacks.bind(BindType.KeyUpAbandon, _widget_on_keyup)

        self._system_callbacks.bind(BindType.Click, _widget_on_click)
        self._system_callbacks.bind(
            BindType.BeforeStyleChange, _widget_before_style_change, add_to_end=False
        )
        self._system_callbacks.bind(
            BindType.StyleChange, _widget_on_style_change, add_to_end=False
        )

    def _init_lists(self):
        super()._init_lists()
        self._dr_coordinates_old = self.coordinates.copy()

    def _init_booleans(self):
        super()._init_booleans()
        self._add_custom_flags(
            CustomFunctions.draw_main
            | CustomFunctions.draw_end
            | CustomFunctions.update_start
            | CustomFunctions.draw_start
        )
        self._click_started = False
        self._supports_tuple_borderradius = True
        self._changed_size = True
        self._handling_style_change = False

    def _init_style(self, style: Style | str):
        super()._init_style(style)
        self.add_first_update_action(self._normalize_borderradius)

    def _on_style_param_mutated(self):
        if not self._handling_style_change:
            self._run_callbacks(BindType.StyleChange)

    @staticmethod
    def _normalize_color_tuple(c) -> tuple[int, int, int, int]:
        if len(c) == 3:
            return (int(round(c[0])), int(round(c[1])), int(round(c[2])), 255)
        return (
            int(round(c[0])),
            int(round(c[1])),
            int(round(c[2])),
            int(round(c[3])),
        )

    def _clamp_radius(self, radius) -> tuple[float, float, float, float]:
        if isinstance(radius, (int, float)):
            radius = (radius, radius, radius, radius)
        if getattr(self, "_auto_sized", False) and (self.size.x <= 1 or self.size.y <= 1):
            return (float(radius[0]), float(radius[1]), float(radius[2]), float(radius[3]))
        if self.size.x <= 0 or self.size.y <= 0:
            return (float(radius[0]), float(radius[1]), float(radius[2]), float(radius[3]))
        max_x = self.size.x / 2.0
        max_y = self.size.y / 2.0
        return (
            max(0.0, min(float(radius[0]), max_x, max_y)),
            max(0.0, min(float(radius[1]), max_x, max_y)),
            max(0.0, min(float(radius[2]), max_x, max_y)),
            max(0.0, min(float(radius[3]), max_x, max_y)),
        )

    def _normalize_borderradius(self):
        if getattr(self, "_auto_sized", False) and (self.size.x <= 1 or self.size.y <= 1):
            return
        if self.size.x == 0 and self.size.y == 0:
            return
        param = self.style._params["border_radius"]
        changed = False
        prev_guard = self._handling_style_change
        self._handling_style_change = True
        try:
            if isinstance(param.value, StateVariable):
                clamped_sv = StateVariable(
                    self._clamp_radius(param.value.static),
                    self._clamp_radius(param.value.hover),
                    self._clamp_radius(param.value.active),
                )
                if clamped_sv != param.value:
                    self.style.border_radius = clamped_sv
                    changed = True
            else:
                new_radius = self._clamp_radius(self.style.border_radius)
                if new_radius != self.style.border_radius:
                    self.style.border_radius = new_radius
                    changed = True
        finally:
            self._handling_style_change = prev_guard
        if changed:
            self._changed = True
            self.clear_surfaces()
            if self._style_targets:
                self._sync_style_transitions(animate=False)

    @property
    def subtheme_border(self):
        return self.style.get_border_color(
            self.subtheme_role, inverted=self.inverted, swap=self.bg_variant
        )

    @property
    def subtheme_content(self):
        return self.style.get_content_color(
            self.subtheme_role, inverted=self.inverted, swap=self.bg_variant
        )

    @property
    def subtheme_font(self):
        return self.style.font_color or self.style.get_pair_color(
            self.font_role, inverted=self.inverted
        )

    @property
    def _correct_blend(self):
        return md.rl.BlendMode.BLEND_ALPHA_PREMULTIPLY

    def _regen_surface(self):
        assert nevu_state.window
        self.surface = Surface(self.current_size)

    def _lazy_init(self, size: Vector2 | list):
        super()._lazy_init(size)
        self.__inner_bg_transparent = _analize_bg(self)
        self._original_inverted = self.inverted
        self._normalize_borderradius()
        self._regen_surface()
        if self.ripple_effect and nevu_state.window.renderer_type.raylib:
            self._click_gradient = ClickGradient(
                [((255, 255, 255, 255), 0), (255, 255, 255, 0)], center=(0.5, 0.5)
            )
            self._click_texture = None
        self._style._bind_on_change(self._on_style_param_mutated)
        self._cached_gradient_ref = self.style.gradient
        self._cached_image_ref = self.style.background_image
        self._cached_font_key = (
            self.subtheme_font,
            self.style.font_size,
            self.style.font_name,
            self.style.text_align_x,
            self.style.text_align_y,
        )
        self._sync_style_transitions(animate=False)

    def _subtheme_role_setter(self, value: SubThemeRole):
        self.get_param_strict("subtheme_role").value = value
        return super()._subtheme_role_setter(value)

    def _on_subtheme_role_change(self):
        super()._on_subtheme_role_change()
        self._run_callbacks(BindType.StyleChange)

    def _inverted_setter(self, value):
        self.get_param_strict("inverted").value = value
        self._run_callbacks(BindType.StyleChange)
        return value

    def _toggle_click_style(self):
        if not self.clickable:
            return
        if self.invert_on_click:
            self.inverted = not self.inverted
        else:
            self._run_callbacks(BindType.StyleChange)

    def _sync_style_transitions(self, animate: bool = True):
        if not hasattr(self, "renderer"):
            return

        bg_target = self._normalize_color_tuple(
            self._get_correct_color(self.subtheme_content, self.hover_state)
        )
        bd_target = self._normalize_color_tuple(self.subtheme_border)
        bw_target = max(0.0, float(self.style.border_width))
        br_target = self._clamp_radius(self.style.border_radius)

        targets = (
            (AnimType.BgColor, bg_target, ColorAnimation),
            (AnimType.BdColor, bd_target, ColorAnimation),
            ("border_width", bw_target, FloatAnimation),
            ("border_radius", br_target, TupleAnimation),
        )

        style_tt = self.style.transition_time
        style_te = self.style.transition_easing
        duration = self.transition_time if style_tt is None else style_tt
        easing = self.transition_easing if style_te is None else style_te
        if not animate or not self.animate_color_change:
            duration = 0.0

        for key, new_target, anim_cls in targets:
            old_target = self._style_targets.get(key)
            self._style_targets[key] = new_target

            if old_target is None or duration <= 0:
                self.animation_manager.stop(key)
                continue

            if old_target == new_target:
                continue

            self.animation_manager.transition(
                key,
                new_target,
                anim_cls,
                duration,
                easing,
                current_fallback=old_target,
            )

    def _clear_rl_specific(self):
        assert nevu_state.window
        if self.cache.get(CacheType.Image):
            md.rl.unload_texture(self.cache.get(CacheType.Image))

    def _build_background(self):
        bg = self.cache.get_or_exec(
            CacheType.Background,
            lambda: self.renderer.core.create_surface(self.current_size),
        )
        bg.fill(color.Blank)

        draw_borders = self.draw_borders

        bg_val = self.animation_manager.get(AnimType.BgColor)
        if bg_val is None:
            bg_val = self._style_targets.get(AnimType.BgColor, self.subtheme_content)
        bg_color = self._normalize_color_tuple(bg_val)

        bd_val = self.animation_manager.get(AnimType.BdColor)
        if bd_val is None:
            bd_val = self._style_targets.get(AnimType.BdColor, self.subtheme_border)
        bd_color = self._normalize_color_tuple(bd_val)

        bw = self.animation_manager.get("border_width")
        if bw is None:
            bw = self._style_targets.get("border_width", self.style.border_width)
        bw = max(0.0, float(bw))

        br = self.animation_manager.get("border_radius")
        if br is None:
            br = self._style_targets.get("border_radius", self.style.border_radius)
        br = self._clamp_radius(br)

        draw_style = self.style
        if bw != draw_style.border_width or br != draw_style.border_radius:
            draw_style = copy.copy(self.style)
            draw_style.border_width = bw
            draw_style.border_radius = br

        if self.draw_content:
            self.renderer.run_base(
                DrawBaseCall(
                    size=self.current_size,
                    color=bg_color,
                    glassy=self.glassy,
                    style=draw_style,
                    radius_support=draw_borders and draw_style.border_radius != 0,
                    gradient_support=True,
                    image_support=True,
                    return_type=RenderReturnType.Modify,
                    modify_object=bg,
                    cache=self.cache,
                ),
            )

        if not draw_borders:
            return bg

        borders_surf = self.cache.get_or_exec(
            CacheType.Borders,
            lambda: self.renderer.core.create_surface(self.current_size),
        )
        borders_surf.fill(color.Blank)

        self.renderer.run_borders(
            DrawBordersCall(
                size=self.current_size,
                original_surface=bg,
                modify_object=borders_surf,
                glassy=self.glassy,
                style=draw_style,
                return_type=RenderReturnType.Modify,
                color=bd_color,
            )
        )

        return borders_surf

    def _draw_start(self):
        cached_bg = self.cache.get_or_exec(
            CacheType.Surface, self._build_background
        )

        surface = self.surface
        coords = (0, 0)
        is_raylib = nevu_state.window.renderer_type.raylib

        with surface:
            surface.fill(color.Blank)
            if is_raylib:
                begin_blend_mode(md.rl.BlendMode.BLEND_ALPHA_PREMULTIPLY)
            surface.blit(cached_bg, coords)
            if is_raylib:
                end_blend_mode()

    def _on_visible_set(self):
        super()._on_visible_set()
        if not self._visible:
            self.clear_surfaces()

    def _draw_end(self):
        super()._draw_end()
        if self._changed_size:
            self._changed_size = False
        assert nevu_state.window
        if self._click_started and nevu_state.window.renderer_type.raylib:
            self._click_texture = self.cache.get_or_exec(
                CacheType.ClickTexture,
                lambda: self.renderer.core.create_surface(self.current_size),
            )
            self.renderer.run_effects(
                DrawEffectsCall(
                    size=self.current_size,
                    modify_object=self.surface,
                    radius=self.style.border_radius,
                    return_type=RenderReturnType.Modify,
                    click_gradient=self._click_gradient,
                    effect_texture=self._click_texture,
                )
            )

    def _update_start(self):
        if self.animation_manager.was_updated(
            AnimType.BgColor, AnimType.BdColor, "border_width", "border_radius"
        ):
            self._changed = True
            self.cache.clear_selected(whitelist=[CacheType.Surface])

        if self._click_started:
            thickness = self.animation_manager.get("thickness")
            opacity = self.animation_manager.get("opacity")

            if thickness is not None and opacity is not None:
                self._click_gradient.set_weight(0, thickness)
                self._click_gradient.transparency = opacity
                self._changed = True
            else:
                self._click_started = False

        check_moved(
            self
        )

        if self._first_update:
            self._first_update = False
            for function in self._first_update_functions:
                if type(function).__name__ in ("ref", "WeakMethod"):
                    resolved = function()
                    if resolved is not None:
                        resolved()
                else:
                    function()

    def _resize_content(self, resize_ratio: Vector2):
        super()._resize_content(resize_ratio)
        self._resize_ratio = resize_ratio
        self.cache.clear_selected(whitelist=[CacheType.RelSize])
        self.clear_surfaces()
        self._changed_size = True
        assert nevu_state.window
        self._regen_surface()
        self._changed = True
        self._click_texture = None

    def _kill_base(self):
        super()._kill_base()
        if getattr(self, "_style", None) is not None:
            self._style._bind_on_change(None)
        self._style_targets.clear()
        self.clear_surfaces()
        self.clear_all()


def _widget_on_keyup(self: Widget):
    if self.inverted != self._original_inverted:
        self.inverted = self._original_inverted
    if self.clickable:
        self._run_callbacks(BindType.StyleChange)


def _widget_on_hover_change(self: Widget):
    if self.hoverable:
        self._run_callbacks(BindType.StyleChange)


def _widget_on_click(self: Widget):
    if not self.clickable:
        return
    if self.ripple_effect and nevu_state.window.renderer_type.raylib:
        if not hasattr(self, "_click_gradient"):
            self._click_gradient = ClickGradient(
                [((255, 255, 255, 255), 0), (255, 255, 255, 0)], center=(0.5, 0.5)
            )
        self._click_started = True
        anim_time = 1
        self._click_gradient.set_weight(0, 0)
        self._click_gradient.transparency = 255

        self.animation_manager.bind(
            BindType.Click, "opacity", FloatAnimation(255, 0, anim_time * 2, ease_out_quad)
        )
        self.animation_manager.bind(
            BindType.Click, "thickness", FloatAnimation(0, 25, anim_time, ease_out_cubic)
        )
        self.animation_manager.call(BindType.Click)

        pos = mouse.pos.copy() - self.absolute_coordinates
        self._click_gradient.set_center_nvvec(pos / self.current_size)

    self._toggle_click_style()


def _widget_before_style_change(self: Widget):
    if getattr(self, "_style", None) is not None:
        self._style._bind_on_change(None)


def _widget_on_style_change(self: Widget):
    if self._handling_style_change:
        return
    self._handling_style_change = True
    try:
        self.cache.clear_selected(whitelist=[CacheType.Surface])
        if self.style.gradient is not self._cached_gradient_ref:
            self._cached_gradient_ref = self.style.gradient
            self.cache.clear_selected(whitelist=[CacheType.Gradient])
        if self.style.background_image is not self._cached_image_ref:
            self._cached_image_ref = self.style.background_image
            self.cache.clear_selected(whitelist=[CacheType.Image])
        font_key = (
            self.subtheme_font,
            self.style.font_size,
            self.style.font_name,
            self.style.text_align_x,
            self.style.text_align_y,
        )
        if self._cached_font_key is not None and font_key != self._cached_font_key:
            self.cache.clear_selected(whitelist=[CacheType.Font, CacheType.TextArgs])
        self._cached_font_key = font_key
        self._style.mark_state(self.hover_state)
        self._style._bind_on_change(self._on_style_param_mutated)
        self._normalize_borderradius()
        self._sync_style_transitions(animate=not self._first_update)
        self._changed = True
        self.__inner_bg_transparent = _analize_bg(self)
    finally:
        self._handling_style_change = False
