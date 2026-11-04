from typing import Unpack, overload

import nevu_ui.core.modules as md
from nevu_ui.components._typehints import (
    _WidgetKwargs,
    _WidgetKwargsLongFull,
    _WidgetKwargsShortFull,
)
from nevu_ui.components.nevuobj import NevuObject
from nevu_ui.core import Annotations
from nevu_ui.core.classes import SurfaceLike
from nevu_ui.core.enums import (
    AnimationManagerState,
    BindType,
    CacheType,
    CustomFunctions,
    ParamLayer,
    RenderReturnType,
)
from nevu_ui.core.state import _analize_bg, nevu_state
from nevu_ui.cython.logic import logic_update_helper
from nevu_ui.cython.surface.surface import Surface
from nevu_ui.cython.vector2 import Vector2
from nevu_ui.cython.raylib.raylib import begin_blend_mode, end_blend_mode
from nevu_ui.presentation.animations import (
    AnimationManager,
    ColorAnimation,
    FloatAnimation,
    ease_out_quad,
)
from nevu_ui.presentation.theme import PairColorRole, SubThemeRole
from nevu_ui.presentation.color import Color
from nevu_ui.presentation.style import Style
from nevu_ui.rendering import DrawBaseCall, DrawBordersCall, DrawEffectsCall
from nevu_ui.rendering.raylib.gradient import ClickGradient
from nevu_ui.utils import mouse


class Widget(NevuObject):
    # === Params ===
    inverted: bool
    clickable: bool
    hoverable: bool
    invert_on_click: bool
    ripple_effect: bool
    animate_color_change: bool
    override_color: tuple | None
    font_role: PairColorRole
    z: int
    draw_borders: bool
    draw_content: bool
    glassy: bool
    # ==============

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
        self._add_param("override_color", tuple | None, None)
        self._add_param("glassy", bool, False)
        self._change_param_default("subtheme_role", SubThemeRole.Secondary)

    def _set_next_bg_color_anim(self, color):
        if self._bg_color_anim_manager:
            curr_color = self._bg_color_anim_manager.get_animation_value("main")
        else:
            curr_color = None
        self._bg_color_anim_manager = AnimationManager(warn=False)
        self._bg_color_anim_manager.add_start_animation(
            "main",
            ColorAnimation(
                curr_color or self._bg_color_before, color, 0.25, ease_out_quad
            ),
        )  # type: ignore
        self._bg_color_anim_manager.update()
        self._anim_bg_color_old = self._bg_color_anim_manager.get_animation_value(
            "main"
        )
        self._bg_color_before = color

    def _init_numerical(self):
        super()._init_numerical()
        self._last_correct_blend = None

    def _init_objects(self):
        super()._init_objects()
        self._bg_color_before = None
        self._bg_color_after = None
        self._bg_color_anim_manager = None
        self.__inner_bg_transparent = False
        self._anim_bg_color_old = None

    def _system_callback_binds(self):
        super()._system_callback_binds()
        self._system_callbacks.bind(BindType.Hover, _widget_on_hover_change)
        self._system_callbacks.bind(BindType.Unhover, _widget_on_hover_change)

        self._system_callbacks.bind(BindType.KeyUp, _widget_on_keyup)
        self._system_callbacks.bind(BindType.KeyUpAbandon, _widget_on_keyup)

        self._system_callbacks.bind(BindType.Click, _widget_on_click)
        self._system_callbacks.bind(
            BindType.StyleChange, _widget_on_style_change, add_to_end=False
        )

    def _init_lists(self):
        super()._init_lists()
        self._dr_coordinates_old = self.coordinates.copy()

    def _init_booleans(self):
        super()._init_booleans()
        self._add_custom_flags(
            CustomFunctions.draw_main |
            CustomFunctions.draw_end |
            CustomFunctions.update_start |
            CustomFunctions.draw_start
        )
        self._click_started = False
        self._supports_tuple_borderradius = True
        self._changed_size = True

    def _init_style(self, style: Style | str):
        super()._init_style(style)
        if (
            isinstance(self.style.border_radius, tuple)
            and not self._supports_tuple_borderradius
        ):
            print(
                f"Warning: tuple border radius is not support in {self.__class__.__name__}"
            )
            self.style.border_radius = self.style.border_radius[0]
        self.add_first_update_action(self._normalize_borderradius)

    def _normalize_borderradius(self):
        if self.size.x == 0 and self.size.y == 0:
            return
        if isinstance(self.style.border_radius, int | float):
            self._normalize_br_num()
        elif isinstance(self.style.border_radius, tuple):
            self._normalize_br_tuple()

    def _normalize_br_num(self):
        br = self.style.border_radius
        br = max(br, 0)
        br = min(br, self.size.x / 2)
        br = min(br, self.size.y / 2)
        if br != self.style.border_radius:
            self._changed = True
        self.style.border_radius = br  # type: ignore
        self.clear_surfaces()

    def _normalize_br_tuple(self):
        assert isinstance(self.style.border_radius, tuple)
        br = list(self.style.border_radius)
        for i in range(len(br)):
            br[i] = max(br[i], 0)
            br[i] = min(br[i], self.size.x / 2)
            br[i] = min(br[i], self.size.y / 2)
        new_br = tuple(br)
        if new_br != self.style.border_radius:
            self.style.border_radius = new_br  # type: ignore
            self._changed = True
            self.clear_surfaces()

    @property
    def subtheme_border(self):
        return self.style.get_border_color(self.subtheme_role, inverted = self.inverted, swap = self.bg_variant)

    @property
    def subtheme_content(self):
        return self.style.get_content_color(self.subtheme_role, inverted = self.inverted, swap = self.bg_variant)

    @property
    def subtheme_font(self):
        return self.style.get_pair_color(self.font_role, inverted = self.inverted)

    @property
    def _correct_blend(self):
        blend = (
            md.rl.BlendMode.BLEND_ALPHA
            if self.__inner_bg_transparent
            else md.rl.BlendMode.BLEND_ALPHA_PREMULTIPLY
        )
        if blend != self._last_correct_blend:
            self._changed = True
            self._last_correct_blend = blend
        return blend

    def _regen_surface(self):
        assert nevu_state.window
        self.surface = Surface(self.current_size)

    def _lazy_init(self, size: Vector2 | list):
        super()._lazy_init(size)
        self.__inner_bg_transparent = _analize_bg(self)
        self._original_inverted = self.inverted
        self._normalize_borderradius()
        self._regen_surface()
        if (
            self.ripple_effect
            and nevu_state.window.renderer_type.raylib
        ):
            self._click_anim_manager = AnimationManager(warn=False)
            self._click_gradient = ClickGradient(
                [((255, 255, 255, 255), 0), (255, 255, 255, 0)], center=(0.5, 0.5)
            )
            self._click_texture = None
        else:
            self._click_anim_manager = None

    def _on_subtheme_role_change(self):
        super()._on_subtheme_role_change()
        self._run_callbacks(BindType.StyleChange)

    def _inverted_setter(self, value):
        self._run_callbacks(BindType.StyleChange)
        return value

    def _toggle_click_style(self):
        if not self.clickable:
            return
        if self.invert_on_click:
            self.inverted = not self.inverted
        else:
            self._run_callbacks(BindType.StyleChange)

    def _get_correct_bg_color(self):
        new_color_pretendent = self._get_correct_color(self.subtheme_content, self.hover_state)
        new_color_tuple = tuple(new_color_pretendent)
        old_color_tuple = (
            tuple(self._bg_color_before)
            if self._bg_color_before is not None
            else None
        )
        if old_color_tuple is None:
            self._bg_color_before = new_color_pretendent
        elif old_color_tuple != new_color_tuple:
            self._set_next_bg_color_anim(new_color_pretendent)

        if color_manager := self._bg_color_anim_manager:
            value = color_manager.get_animation_value("main")
            if not value: return None
            r, g, b = value
            anim_color = (int(r), int(g), int(b), 255)
        else:
            anim_color = None

        return anim_color

    def _clear_rl_specific(self):
        assert nevu_state.window
        if self.cache.get(CacheType.Image):
            md.rl.unload_texture(self.cache.get(CacheType.Image))  # type: ignore

    def _build_background(self):
        bg = self.cache.get_or_exec(
            CacheType.Background,
            lambda: self.renderer.core.create_surface(self.current_size),
        )
        bg.fill(Color.Blank)

        draw_borders = self.draw_borders

        if self.draw_content:
            color = self.override_color or self.subtheme_content
            bg_color = self._get_correct_bg_color() or color
            self.renderer.run_base(
                DrawBaseCall(
                    size=self.current_size,
                    color=bg_color,
                    glassy=self.glassy,
                    style=self.style,
                    radius_support=draw_borders and self.style.border_radius != 0,
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
        borders_surf.fill(Color.Blank)

        self.renderer.run_borders(
            DrawBordersCall(
                size=self.current_size,
                original_surface=bg,
                modify_object=borders_surf,
                glassy=self.glassy,
                style=self.style,
                return_type=RenderReturnType.Modify,
                color=self.subtheme_border,
            )
        )

        return borders_surf

    def _draw_start(self):
        cached_bg: SurfaceLike = self.cache.get_or_exec(
            CacheType.Surface, self._build_background
        )

        surface = self.surface
        coords = (0, 0)
        is_raylib = nevu_state.window.renderer_type.raylib

        with surface:
            surface.fill(Color.Blank)
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
        if self._click_started:
            click_anim_manager = self._click_anim_manager
            assert click_anim_manager
            click_gradient = self._click_gradient
            anim_value_thickness = click_anim_manager.get_animation_value(
                "ripple_thickness"
            )
            anim_value_opacity = click_anim_manager.get_animation_value(
                "ripple_opacity"
            )
            click_anim_manager.update()
            need_to_change = False
            if anim_value_thickness:
                click_gradient.set_weight(0, anim_value_thickness)
                need_to_change = True
            if anim_value_opacity:
                click_gradient.transparency = anim_value_opacity  # type: ignore
                need_to_change = True
            self._changed = self._changed or need_to_change
            if click_anim_manager.state == AnimationManagerState.Ended:
                self._click_started = False

        color_anim_manager = self._bg_color_anim_manager
        if color_anim_manager:
            color_anim_manager.update()
            anim = color_anim_manager.get_animation("main")
            if anim:
                anim_val = anim.current_value
                if anim_val and anim_val != self._anim_bg_color_old:
                    self._anim_bg_color_old = anim_val
                    self._changed = True
                    self.cache.clear_selected(whitelist=[CacheType.Surface])
                if anim.ended:
                    self._bg_color_anim_manager = None

        logic_update_helper(
            self #type: ignore
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
        self.clear_surfaces()
        self.clear_all()


# === NOT CLASS FUNCTIONS ===


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
    if (
        self.ripple_effect
        and nevu_state.window.renderer_type.raylib
    ):
        self._click_started = True
        assert self._click_anim_manager
        self._click_anim_manager.state = AnimationManagerState.Start
        anim_time = 0.4
        self._click_gradient.set_weight(0, 0)
        self._click_gradient.transparency = 255  # type: ignore
        self._click_anim_manager.add_start_animation(
            "ripple_opacity", FloatAnimation(255, 0, anim_time)
        )
        self._click_anim_manager.add_start_animation(
            "ripple_thickness", FloatAnimation(0, 10, anim_time)
        )
        pos = mouse.pos.copy()
        pos -= self.absolute_coordinates
        normalized = pos / self.current_size
        self._click_gradient.set_center_nvvec(normalized)
    self._toggle_click_style()


def _widget_on_style_change(self: Widget):
    self.cache.clear_selected(whitelist = [CacheType.Surface, CacheType.Background, CacheType.Borders])
    self._normalize_borderradius()
    self._changed = True
    self.__inner_bg_transparent = _analize_bg(self)
