import copy
from typing import Callable, Unpack

import nevu_ui.core.modules as md
from nevu_ui.components.widgets import SwitchKwargs, SwitchTemplate, Widget
from nevu_ui.core import Annotations, nevu_state
from nevu_ui.core.enums import (
    AnimationManagerState,
    CacheType,
    ParamLayer,
    RenderArgs,
    RenderConfig,
    RenderReturnType,
    SwitchAxis,
)
from nevu_ui.fast.nvrendertex import NvRenderTexture
from nevu_ui.fast.nvvector2 import NvVector2
from nevu_ui.fast.raylib.nevu_raylib import begin_blend_mode, end_blend_mode
from nevu_ui.presentation.animations import (
    AnimationManager,
    Vector2Animation,
    animations_library,
)
from nevu_ui.presentation.color import Color, SubThemeRole
from nevu_ui.rendering import DrawBaseCall
from nevu_ui.utils import mouse, time


class Switch(Widget):
    # === Params ===
    axis: SwitchAxis
    on_switch_change: None | Callable
    easing_func: Callable
    animation_time: float

    # ==============
    def __init__(
        self,
        base_state: bool = False,
        size: Annotations.nevuobj_size = None,
        style: Annotations.nevuobj_style = None,
        **constant_kwargs: Unpack[SwitchKwargs],
    ):
        super().__init__(size, style, **constant_kwargs)
        self._template = SwitchTemplate(self._template.size, base_state)

    def _init_lists(self):
        super()._init_lists()
        self._bg_circle_coords = NvVector2.from_xy(0, 0)
        self._bg_circle_coords_before = NvVector2.from_xy(0, 0)
        self._goal_circle_coords = NvVector2.from_xy(0, 0)
        self._click_pos = None
        self._click_treshold = 5

    def _init_flags(self):
        super()._init_flags()
        self._changed_bg_circle = True
        self._custom_secondary_draw = True

    def _init_objects(self):
        super()._init_objects()
        self._bg_circle = None
        self._bg_circle_anim_manager = None
        self._bg_surf = None

    def _init_numerical(self):
        super()._init_numerical()
        self._after_key_down_time = None

    def _on_click_system(self):
        super()._on_click_system()
        self._after_key_down_time = 0
        self._click_pos = mouse.pos

    def _on_keyup_system(self):
        super()._on_keyup_system()
        down_time = self._after_key_down_time
        if self._dragging:
            self._after_kup()
        elif down_time is not None and down_time < 0.5:
            self.state = not self.state
        self._after_key_down_time = None

    def _on_keyup_abandon_system(self):
        super()._on_keyup_abandon_system()
        if self._dragging:
            self._after_kup()
        self._after_key_down_time = None

    def _after_kup(self):
        self._dragging = False
        self._click_pos = None
        axis = self._get_correct_axis()
        main_coords = 0 if axis == SwitchAxis.Horizontal else 1
        self.state = (
            self._bg_circle_coords[main_coords]
            > self._no_borders_size[main_coords] / 2 - self.minimal_side / 2
        )

    def _add_params(self):
        super()._add_params()
        self._add_param("axis", SwitchAxis, SwitchAxis.Auto, layer=ParamLayer.Basic)
        self._add_param("on_switch_change", type(None) | Callable, None)
        self._add_param("easing_func", Callable, animations_library.smootherstep)
        self._add_param("animation_time", float, 0.15)
        self._add_param_link("anim_time", "animation_time")

    def _lazy_init(self, size: NvVector2 | list, state: bool = False):
        super()._lazy_init(size)
        self.state = state

    @property
    def bg_circle_coords(self):
        return self._bg_circle_coords

    @bg_circle_coords.setter
    def bg_circle_coords(self, value):
        self._set_bg_circle_coords(value)

    def _set_bg_circle_coords(self, value, anim_time=None):
        anim_time = anim_time or self.get_param_value("animation_time")
        self._bg_circle_anim_manager = AnimationManager(warn=False)
        self._goal_circle_coords = NvVector2(value)
        self._bg_circle_anim_manager.add_start_animation(
            "main",
            Vector2Animation(
                self._bg_circle_coords,
                self._goal_circle_coords,
                anim_time,
                self.get_param_value("easing_func"),
            ),
        )

    @property
    def state(self):
        return self._state

    @state.setter
    def state(self, value):
        if not hasattr(self, "_state"):
            self._state = False
        if self._state != value:
            on_switch_change = self.get_param_value("on_switch_change")
            if on_switch_change is not None:
                on_switch_change(self, value)
        self._state = value
        axis = self._get_correct_axis()
        main_coord = 0 if axis == SwitchAxis.Horizontal else 1
        bg_coords = self._bg_circle_coords.xy
        if self._state is True:
            bg_coords[main_coord] = (
                self._no_borders_size[main_coord] - self.minimal_side
            )
        else:
            bg_coords[main_coord] = 0
        self.bg_circle_coords = bg_coords

    @property
    def minimal_side(self):
        return min(self._no_borders_size.x, self._no_borders_size.y)

    def _create_bg_circle(self):
        minimal_size = self.minimal_side
        size = NvVector2.from_xy(minimal_size, minimal_size)
        dtype = nevu_state.window.renderer_type
        if dtype.pygame_like:
            bg_texture = md.pygame.Surface(size, md.pygame.SRCALPHA)
        elif dtype.raylib:
            bg_texture = NvRenderTexture(size)
        else:
            raise ValueError("Unsupported backend")
        bg_texture.fill((0, 0, 0, 0))
        self.renderer.run_base(
            DrawBaseCall(
                return_type=RenderReturnType.Modify,
                size=size,
                gradient_support=False,
                image_support=False,
                cache=None,
                radius=999,
                color=self.subtheme_font,
                standstill=True,
                modify_object=bg_texture,
            )
        )
        return bg_texture

    def _rebuild_bg(self):
        if not self._bg_circle or not self._bg_surf:
            return
        dtype = nevu_state.window.renderer_type
        surface = self.surface
        if dtype.pygame_like:
            assert isinstance(surface, md.pygame.Surface)
            surface.fill((0, 0, 0, 0))
            surface.blit(self._bg_surf, (0, 0))
            surface.blit(
                self._bg_circle,
                (self._bg_circle_coords + self._borders_marg_size)
                .get_round()
                .get_int_tuple(),
            )
        elif dtype.raylib:
            assert isinstance(surface, NvRenderTexture)
            surface_fblit = surface.fast_blit
            with surface:
                surface.fast_clear(Color.Blank)
                begin_blend_mode(md.rl.BlendMode.BLEND_ALPHA_PREMULTIPLY)
                surface_fblit(self._bg_surf, (0, 0))
                surface_fblit(
                    self._bg_circle,
                    (self._bg_circle_coords + self._borders_marg_size)
                    .get_round()
                    .get_int_tuple(),
                )
                end_blend_mode()

    def _logic_update(self):
        super()._logic_update()
        if self._after_key_down_time is not None:
            self._after_key_down_time += time.dt

        bg_anim_manager = self._bg_circle_anim_manager

        if bg_anim_manager is not None:
            if bg_anim_manager.state != AnimationManagerState.Start:
                self._bg_circle_coords = self._goal_circle_coords.xy
                self._bg_circle_anim_manager = None
                self._changed_bg_circle = True
                return
            bg_anim_manager.update()
            value = bg_anim_manager.get_animation_value("main")
            if value is not None:
                self._bg_circle_coords = value
                self._changed_bg_circle = True

        if not self._bg_circle:
            self._bg_circle = self._create_bg_circle()
            self._changed_bg_circle = True

        curr_pos = mouse.pos

        if self._dragging:
            pos = NvVector2.from_xy(0, 0)
            click_pos = self._click_pos
            assert click_pos
            coords_before = self._bg_circle_coords_before
            rsize = self._no_borders_size
            minimal_side = self.minimal_side

            if self._get_correct_axis() == SwitchAxis.Horizontal:
                pos.x = max(
                    0,
                    min(
                        curr_pos.x - click_pos.x + coords_before.x,
                        rsize.x - minimal_side,
                    ),
                )
            else:
                pos.y = max(
                    0,
                    min(
                        curr_pos.y - click_pos.y + coords_before.y,
                        rsize.y - minimal_side,
                    ),
                )

            self._changed_bg_circle = True
            self._bg_circle_coords = pos

        elif self._click_pos is not None and self._after_key_down_time is not None:
            if (
                abs(curr_pos.x - self._click_pos.x) > self._click_treshold
                or abs(curr_pos.y - self._click_pos.y) > self._click_treshold
                or self._after_key_down_time > 0.5
            ):
                self._dragging = True
                self._bg_circle_coords_before = self._bg_circle_coords.xy
        if self._changed:
            self._changed_bg_circle = False

        if self._changed_bg_circle is True:
            self._rebuild_bg()
            self._changed_bg_circle = False

    def secondary_draw_content(self):
        super().secondary_draw_content()
        self._bg_surf = self.cache.get(CacheType.Borders)

    def _secondary_draw_end(self):
        super()._secondary_draw_end()
        self._bg_circle = self._create_bg_circle()
        self._rebuild_bg()

    def _get_correct_axis(self):
        axis = self.get_param_value("axis")
        if axis == SwitchAxis.Auto:
            if self.size.x > self.size.y:
                axis = SwitchAxis.Horizontal
            else:
                axis = SwitchAxis.Vertical
        return axis

    def _resize_content(self, resize_ratio: NvVector2):
        super()._resize_content(resize_ratio)
        self._bg_circle = None

        axis = self._get_correct_axis()
        main_coord = 0 if axis == SwitchAxis.Horizontal else 1

        bg_coords = self._bg_circle_coords.xy
        if self.state is True:
            bg_coords[main_coord] = (
                self._no_borders_size[main_coord] - self.minimal_side
            )
        else:
            bg_coords[main_coord] = 0

        self._bg_circle_coords = bg_coords
        self._goal_circle_coords = bg_coords.copy()

        self._bg_circle_anim_manager = None
        self._changed_bg_circle = True

    def _create_clone(self):
        return self.__class__(
            self._template.state,
            self._template.size,
            copy.deepcopy(self.style),
            **self.constant_kwargs,
        )
