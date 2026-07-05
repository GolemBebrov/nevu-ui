from typing_extensions import Any, Unpack, overload

import nevu_ui.core.modules as md
from nevu_ui.components.nevuobj import NevuObject
from nevu_ui.components.widgets.typehints import (
    WidgetKwargs,
    WidgetKwargsLong,
    WidgetKwargsShort,
)
from nevu_ui.core import Annotations
from nevu_ui.core.classes import SurfaceLike
from nevu_ui.core.enums import (
    AnimationManagerState,
    Backend,
    CacheType,
    ParamLayer,
    RenderConfig,
    RenderReturnType,
)
from nevu_ui.core.state import _analize_bg, nevu_state
from nevu_ui.fast.logic import logic_update_helper
from nevu_ui.fast.nvrendertex import NvRenderTexture
from nevu_ui.fast.nvvector2 import NvVector2
from nevu_ui.fast.raylib.nevu_raylib import begin_blend_mode, end_blend_mode
from nevu_ui.presentation.animations import (
    AnimationManager,
    ColorAnimation,
    FloatAnimation,
    ease_out_quad,
)
from nevu_ui.presentation.color import Color, PairColorRole, SubThemeRole
from nevu_ui.presentation.style import Style, default_style
from nevu_ui.rendering import DrawBaseCall, DrawBordersCall, DrawEffectsCall
from nevu_ui.rendering.raylib.gradient import ClickGradient
from nevu_ui.utils import mouse


class Widget(NevuObject):
    # === Params ===
    inverted: bool
    bg_variant: bool
    clickable: bool
    hoverable: bool
    inline: bool
    invert_on_click: bool
    ripple_effect: bool
    animate_color_change: bool
    override_color: tuple | None
    font_role: PairColorRole
    z: int
    draw_borders: bool
    draw_content: bool

    # ==============
    @overload
    def __init__(
        self,
        size: Annotations.nevuobj_size = None,
        style: Annotations.nevuobj_style = None,
        **constant_kwargs: Unpack[WidgetKwargsShort],
    ): ...
    @overload
    def __init__(
        self,
        size: Annotations.nevuobj_size = None,
        style: Annotations.nevuobj_style = None,
        **constant_kwargs: Unpack[WidgetKwargsLong],
    ): ...
    def __init__(
        self,
        size: Annotations.nevuobj_size = None,
        style: Annotations.nevuobj_style = None,
        **constant_kwargs: Unpack[WidgetKwargs],
    ):
        super().__init__(size, style, **constant_kwargs)
        # === Text Cache ===
        self._init_text_cache()
        # === Alt ===
        self._init_inverted()

    def _convert_to_sdl2_texture(self):
        if nevu_state.renderer is None:
            raise ValueError("Window not initialized!")
        assert nevu_state.window, "Window not initialized!"
        assert self.surface, "Surface not initialized!"
        assert nevu_state.window.renderer_type.sdl, (
            "convert_to_sdl2_texture is supported only in SDL backend! UWO"
        )
        assert isinstance(self.surface, md.pygame.Surface)
        texture = md.pygame._sdl2.Texture.from_surface(
            nevu_state.renderer, self.surface
        )  # type: ignore
        texture = md.pygame._sdl2.Image(texture)  # type: ignore
        return texture  # type: ignore

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
        self._add_param("bg_variant", bool, False)
        self._add_param("clickable", bool, False)
        self._add_param("hoverable", bool, False)
        self._add_param("invert_on_click", bool, False)
        self._change_param_default("z", 1)
        self._add_param("inline", bool, False)
        self._add_param("font_role", PairColorRole, PairColorRole.INVERSE_SURFACE)
        self._add_param("draw_borders", bool, True)
        self._add_param("draw_content", bool, True)
        self._add_param("ripple_effect", bool, True)
        self._add_param("animate_color_change", bool, True)
        self._add_param("override_color", tuple | None, None)
        self._change_param_default("subtheme_role", SubThemeRole.SECONDARY)

    def _init_text_cache(self):
        self._text_baked = None
        self._text_surface = None
        self._text_rect = None
        assert nevu_state.window
        if nevu_state.window._backend == Backend.RayLib:
            self._text_font_size = None
            self._text_spacing = None

    def _set_new_color(self, color):
        if self._color_anim_manager:
            curr_color = self._color_anim_manager.get_animation_value("main")
        else:
            curr_color = None
        self._color_anim_manager = AnimationManager(warn=False)
        self._color_anim_manager.add_start_animation(
            "main",
            ColorAnimation(curr_color or self._old_color, color, 0.25, ease_out_quad),
        )  # type: ignore
        self._color_anim_manager.update()
        self._color_anim_old_value = self._color_anim_manager.get_animation_value(
            "main"
        )
        self._old_color = color

    def _init_numerical(self):
        super()._init_numerical()
        self._last_correct_blend = None

    def _init_objects(self):
        super()._init_objects()
        self._old_color = None
        self._new_color = None
        self._color_anim_manager = None
        self._inner_bg_transparent = False
        self._color_anim_old_value = None
        self._sdl2_texture = None

        assert nevu_state.window, "Window not initialized!"

        if (
            self.get_param_strict("ripple_effect").value
            and nevu_state.window.renderer_type.raylib
        ):
            self._click_anim_manager = AnimationManager(warn=False)
            self._click_gradient = ClickGradient(
                [((255, 255, 255, 255), 0), (255, 255, 255, 0)], center=(0.5, 0.5)
            )
            self._click_texture = None
        else:
            self._click_anim_manager = None

    def _init_lists(self):
        super()._init_lists()
        self._dr_coordinates_old = self.coordinates.copy()

    def _init_booleans(self):
        super()._init_booleans()
        self._custom_secondary_draw_end = True
        self._custom_logic_update = True
        self._custom_primary_draw = True
        self._custom_secondary_draw_content = True
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
        self.clear_texture()

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
            self.clear_texture()

    def _init_inverted(self):
        if self.inverted:
            self._subtheme_border = self._ensure_func_safety(self._alt_subtheme_border)
            self._subtheme_content = self._ensure_func_safety(
                self._alt_subtheme_content
            )
            self._subtheme_font = self._ensure_func_safety(self._alt_subtheme_font)
        else:
            self._subtheme_border = self._ensure_func_safety(self._main_subtheme_border)
            self._subtheme_content = self._ensure_func_safety(
                self._main_subtheme_content
            )
            self._subtheme_font = self._ensure_func_safety(self._main_subtheme_font)

    @property
    def subtheme_border(self):
        return self._subtheme_border()()  # type: ignore

    @property
    def subtheme_content(self):
        return self._subtheme_content()()  # type: ignore

    @property
    def subtheme_font(self):
        return self._subtheme_font()()  # type: ignore

    @property
    def _correct_blend(self):
        blend = (
            md.rl.BlendMode.BLEND_ALPHA
            if self._inner_bg_transparent
            else md.rl.BlendMode.BLEND_ALPHA_PREMULTIPLY
        )
        if blend != self._last_correct_blend:
            self._changed = True
            self._last_correct_blend = blend
        return blend

    def _regen_surface(self):
        assert nevu_state.window
        if self.inline:
            return
        if nevu_state.window.renderer_type.raylib:
            self.surface = NvRenderTexture(self._csize)
            md.rl.set_texture_filter(
                self.surface.texture, md.rl.TextureFilter.TEXTURE_FILTER_ANISOTROPIC_16X
            )
            md.rl.set_texture_wrap(
                self.surface.texture, md.rl.TextureWrap.TEXTURE_WRAP_CLAMP
            )
        else:
            self.surface = md.pygame.Surface(
                self._csize, flags=md.pygame.SRCALPHA
            ).convert_alpha()

    def _lazy_init(self, size: NvVector2 | list):
        super()._lazy_init(size)
        self._inner_bg_transparent = _analize_bg(self)
        self._original_inverted = self.inverted
        if self.inline:
            self.get_param_strict("ripple_effect").value = False
            self.get_param_strict("animate_color_change").value = False
            return
        self._normalize_borderradius()
        self._regen_surface()

    def _on_subtheme_role_change(self):
        super()._on_subtheme_role_change()
        if self.booted:
            self._init_inverted()
        self._on_style_change()

    def _inverted_setter(self, value):
        self._init_inverted()
        self._on_style_change()
        return value

    def _toggle_click_style(self):
        if not self.clickable:
            return
        if self.invert_on_click:
            self.inverted = not self.inverted
        else:
            self._on_style_change()

    def _on_hover_system(self):
        super()._on_hover_system()
        if not self.hoverable:
            return
        self._on_style_change()

    def _on_keyup_system(self):
        super()._on_keyup_system()
        if self.inverted != self._original_inverted:
            self.inverted = self._original_inverted
        if not self.clickable:
            return
        self._on_style_change()

    def _on_click_system(self):
        super()._on_click_system()
        if not self.clickable:
            return
        if (
            self.get_param_strict("ripple_effect").value
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
            normalized = pos / self._csize
            self._click_gradient.set_center_nvvec(normalized)
        self._toggle_click_style()

    def _on_unhover_system(self):
        super()._on_unhover_system()
        if not self.hoverable:
            return
        self._on_style_change()

    def _on_keyup_abandon_system(self):
        super()._on_keyup_abandon_system()
        if self.inverted != self._original_inverted:
            self.inverted = self._original_inverted
        if not self.clickable:
            return
        self._on_style_change()

    def _clear_rl_specific(self):
        assert nevu_state.window
        if self.cache.get(CacheType.RlFont):
            md.rl.unload_font(self.cache.get(CacheType.RlFont))  # type: ignore
        if self.cache.get(CacheType.Scaled_Image):
            md.rl.unload_texture(self.cache.get(CacheType.Scaled_Image))  # type: ignore

    def _on_style_change_content(self):
        if self.inline:
            self._changed_size = True
        self.clear_surfaces()
        self.clear_texture()
        self._normalize_borderradius()
        self._changed = True
        self._inner_bg_transparent = _analize_bg(self)

    def _on_style_change_additional(self):
        assert nevu_state.window
        self._text_surface = None
        self._text_rect = None

    def _main_subtheme_content(self):
        return self._subtheme.color if self.bg_variant else self._subtheme.container

    def _main_subtheme_border(self):
        return self._subtheme.oncolor if self.bg_variant else self._subtheme.oncontainer

    def _alt_subtheme_content(self):
        return self._subtheme.oncolor if self.bg_variant else self._subtheme.oncontainer

    def _alt_subtheme_border(self):
        return self._subtheme.color if self.bg_variant else self._subtheme.container

    def _main_subtheme_font(self):
        return self.style.colortheme.get_pair(self.font_role).color

    def _alt_subtheme_font(self):
        return self.style.colortheme.get_pair(self.font_role).oncolor

    def _primary_draw(self):
        super()._primary_draw()
        if self._dead:
            return
        if not self._changed:
            return
        self._uni_primary_draw_content()

    def _primary_draw_content(self):
        pass

    def _on_visible_set(self):
        super()._on_visible_set()
        if not self._visible:
            self.clear_surfaces()
            self.clear_texture()

    def _uni_primary_draw_content(self):
        def build_background() -> SurfaceLike:
            bg: SurfaceLike = self.cache.get_or_exec(
                CacheType.Background,
                lambda: self.renderer.core.create_clear(self._csize),
            )
            bg.fill(Color.Blank)

            override_color = self.override_color or None
            draw_borders = self.draw_borders and self.style.border_width > 0
            easy_background = draw_borders
            if self.draw_content:
                self.renderer.run_base(
                    DrawBaseCall(
                        color=override_color,
                        radius=self.style.border_radius,
                        easy_background=easy_background,
                        gradient_support=True,
                        image_support=True,
                        return_type=RenderReturnType.Modify,
                        modify_object=bg,
                    ),
                    key=RenderConfig.DrawL1,
                )

            if draw_borders:
                final = self.cache.get_or_exec(
                    CacheType.Borders,
                    lambda: self.renderer.core.create_clear(self._csize),
                )
                final.fill(Color.Blank)
                self.renderer.run_borders(
                    DrawBordersCall(
                        subject=bg,
                        return_type=RenderReturnType.Modify,
                        modify_object=final,
                        pos=(0, 0),
                    ),
                    key=RenderConfig.DrawL2,
                )
            else:
                return bg

            return final

        cached_bg: SurfaceLike = self.cache.get_or_exec(
            CacheType.Surface, build_background
        )

        surface = self.surface

        if not self.inline:
            surface.fill(Color.Blank)
            coords = (0, 0)
        else:
            coords = self.coordinates.to_round().to_tuple()
        if nevu_state.window.renderer_type.raylib:
            assert isinstance(surface, NvRenderTexture)
            assert isinstance(cached_bg, NvRenderTexture)
            with surface:
                begin_blend_mode(md.rl.BlendMode.BLEND_ALPHA_PREMULTIPLY)
                surface.fast_blit(cached_bg, coords)
                end_blend_mode()
        else:
            assert isinstance(surface, md.pygame.Surface)
            assert isinstance(cached_bg, md.pygame.Surface)
            surface.blit(cached_bg, coords)

    def _secondary_draw_end(self):
        if self._changed and nevu_state.renderer:
            self._sdl2_texture = self.cache.get_or_exec(
                CacheType.Texture, self._convert_to_sdl2_texture
            )
        if self._changed_size:
            self._changed_size = False
        assert nevu_state.window
        if self._click_started and nevu_state.window.renderer_type.raylib:
            self._click_texture = self.cache.get_or_exec(
                CacheType.ClickTexture,
                lambda: self.renderer.core.create_clear(self._csize),
            )
            self.renderer.run_effects(
                DrawEffectsCall(
                    return_type=RenderReturnType.Null,
                    click_gradient=self._click_gradient,
                    click_subject=self._click_texture,
                )
            )

    def clear_texture(self):
        self.cache.clear_selected(whitelist=[CacheType.Texture])

    def _logic_update(self):
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

        if self._color_anim_manager:
            color_anim_manager = self._color_anim_manager
            color_anim_manager.update()
            if anim_value := color_anim_manager.get_animation_value("main"):
                if anim_value != self._color_anim_old_value:
                    self._color_anim_old_value = anim_value
                    self._changed = True
                    self.cache.clear_selected(whitelist=[CacheType.Surface])
            if anim := color_anim_manager.get_animation("main"):  # type: ignore
                if anim.ended:
                    self._color_anim_manager = None
        logic_update_helper(
            self.absolute_coordinates, self._dr_coordinates_old, nevu_state.z_system
        )

        if self._sdl2_texture:
            alpha = self.animation_manager.get_animation_value("ripple_opacity")
            if alpha is not None:
                self._sdl2_texture.alpha = alpha

        if self._first_update:
            self._first_update = False
            for function in self._first_update_functions:
                if type(function).__name__ in ("ref", "WeakMethod"):
                    resolved = function()
                    if resolved is not None:
                        resolved()
                else:
                    function()

    def _boot_up(self):
        pass

    def _resize_content(self, resize_ratio: NvVector2):
        super()._resize_content(resize_ratio)
        self._resize_ratio = resize_ratio
        self.cache.clear_selected(whitelist=[CacheType.RelSize])
        self.clear_surfaces()
        self._changed_size = True
        assert nevu_state.window
        self._regen_surface()
        self._changed = True
        if not hasattr(self, "_click_texture"):
            self._click_texture = None
        if self._click_texture:
            self._click_texture = None

    def _kill_base(self):
        super()._kill_base()
        self.clear_surfaces()
        self.clear_texture()
        self.clear_all()
