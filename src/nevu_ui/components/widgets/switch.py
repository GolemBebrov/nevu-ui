import copy
from collections.abc import Callable
from typing import Unpack

import nevu_ui.core.modules as md
from nevu_ui.components._typehints import _SwitchKwargs, _SwitchTemplate
from nevu_ui.components.widgets.widget import Widget
from nevu_ui.core import Annotations, nevu_state
from nevu_ui.core.enums import (
    AnimationManagerState,
    BindType,
    CacheType,
    CustomFunctions,
    ParamLayer,
    RenderReturnType,
    SwitchAxis,
)
from nevu_ui.cython.surface.surface import Surface
from nevu_ui.cython.vector2 import Vector2
from nevu_ui.cython.raylib.raylib import begin_blend_mode, end_blend_mode
from nevu_ui.presentation.animations import (
    AnimationManager,
    Vector2Animation,
    presets,
)
from nevu_ui.presentation.color import Color
from nevu_ui.rendering import DrawBaseCall
from nevu_ui.utils import mouse, time


class Switch(Widget):
    # === Params ===
    axis: SwitchAxis
    on_switch_change: None | Callable
    easing_func: Callable
    animation_time: float
    circle_size: float
    # ==============
    def __init__(
        self,
        base_state: bool = False,
        size: Annotations.nevuobj_size = None,
        style: Annotations.nevuobj_style = None,
        **params: Unpack[_SwitchKwargs],
    ):
        super().__init__(size, style, **params)
        self._template = _SwitchTemplate(self._template.size, base_state)

    def _init_lists(self):
        super()._init_lists()
        self._circle_coordinates = Vector2.from_xy(0, 0)
        self._bg_circle_coords_before = Vector2.from_xy(0, 0)
        self._goal_circle_coords = Vector2.from_xy(0, 0)
        self._click_pos: Vector2 | None = None
        self._click_treshold = 5

    def _init_flags(self):
        super()._init_flags()
        self._circle_changed = True
        self._add_custom_flags(
            CustomFunctions.draw_main
        )

    def _init_objects(self):
        super()._init_objects()
        self._circle_surface = None
        self._circle_anim_manager = None
        self._background = None

    def _init_numerical(self):
        super()._init_numerical()
        self._after_key_down_time: float | None = None

    def _after_kup(self):
        self._dragging = False
        self._click_pos = None
        axis = self._get_correct_axis()
        main_coords = 0 if axis == SwitchAxis.Horizontal else 1
        self.state = (
            self._circle_coordinates[main_coords]
            > self._no_borders_current_size[main_coords] / 2 - self.minimal_side / 2
        )

    def _add_params(self):
        super()._add_params()
        self._add_param("axis", SwitchAxis, SwitchAxis.Auto, layer=ParamLayer.Basic)
        self._add_param("on_switch_change", type(None) | Callable, None)
        self._add_param("easing_func", Callable, presets.smootherstep)
        self._add_param("animation_time", float, 0.15)
        self._add_param_link("anim_time", "animation_time")
        self._add_param("circle_size", float | int, 0.85)

    def _lazy_init(self, size: Vector2 | list, state: bool = False):
        super()._lazy_init(size)
        self.state = state

    def _system_callback_binds(self):
        super()._system_callback_binds()
        self._system_callbacks.bind(BindType.Click, switch_on_click)
        self._system_callbacks.bind(BindType.KeyUp, switch_on_keyup)
        self._system_callbacks.bind(BindType.KeyUpAbandon, switch_on_keyup_abandon)

    @property
    def bg_circle_coords(self):
        return self._circle_coordinates

    @bg_circle_coords.setter
    def bg_circle_coords(self, value):
        self._set_bg_circle_coords(value)

    def _set_bg_circle_coords(self, value, anim_time=None):
        anim_time = anim_time or self.animation_time
        self._circle_anim_manager = AnimationManager(warn=False)
        self._goal_circle_coords = Vector2(value)
        self._circle_anim_manager.add_start_animation(
            "main",
            Vector2Animation(
                self._circle_coordinates,
                self._goal_circle_coords,
                anim_time,
                self.easing_func,
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
            on_switch_change = self.on_switch_change
            if on_switch_change is not None:
                on_switch_change(self, value)
        self._state = value
        axis = self._get_correct_axis()
        main_coord = 0 if axis == SwitchAxis.Horizontal else 1
        bg_coords = self._circle_coordinates.xy
        if self._state is True:
            bg_coords[main_coord] = (
                self._no_borders_current_size[main_coord] - self.minimal_side
            )
        else:
            bg_coords[main_coord] = 0
        self.bg_circle_coords = bg_coords

    @property
    def minimal_side(self):
        return min(self._no_borders_current_size.x, self._no_borders_current_size.y)

    def _create_bg_circle(self):
        circle_size = max(0.0, min(1.0, float(self.circle_size)))
        minimal_size = self.minimal_side * circle_size
        if minimal_size <= 0:
            size = Vector2.from_xy(1, 1)
        else:
            size = Vector2.from_xy(minimal_size, minimal_size)
        bg_texture = Surface(size)
        bg_texture.fill(Color.Blank)
        if minimal_size <= 0:
            return bg_texture
        self.renderer.run_base(
            DrawBaseCall(
                return_type=RenderReturnType.Modify,
                size=size,
                gradient_support=False,
                image_support=False,
                cache=None,
                style = self.style(br = 999),
                color=self.subtheme_font,
                modify_object=bg_texture,
                glassy=self.glassy,
            )
        )
        return bg_texture

    def _rebuild_bg(self):
        if not self._circle_surface or not self._background:
            return
        surface = self.surface
        circle_size = max(0.0, min(1.0, float(self.circle_size)))
        circle_offset = (self.minimal_side * (1 - circle_size)) / 2
        circle_pos = (
            self._circle_coordinates
            + self._borders_of_current_size
            + Vector2.from_xy(circle_offset, circle_offset)
        ).get_round()

        is_raylib = nevu_state.window.renderer_type.raylib
        with surface:
            surface.clear(Color.Blank)
            if is_raylib:
                begin_blend_mode(md.rl.BlendMode.BLEND_ALPHA_PREMULTIPLY)
            surface.blit(self._background, (0, 0))
            if circle_size > 0:
                surface.blit(self._circle_surface, circle_pos)
            if is_raylib:
                end_blend_mode()

    def _update_start(self):
        super()._update_start()
        if self._after_key_down_time is not None:
            self._after_key_down_time += time.dt

        bg_anim_manager = self._circle_anim_manager

        if bg_anim_manager:
            if bg_anim_manager.state != AnimationManagerState.Start:
                self._circle_coordinates = self._goal_circle_coords.xy
                self._circle_anim_manager = None
                self._circle_changed = True
                return
            bg_anim_manager.update()
            value = bg_anim_manager.get_animation_value("main")
            if value is not None:
                self._circle_coordinates = value
                self._circle_changed = True

        if not self._circle_surface:
            self._circle_surface = self._create_bg_circle()
            self._circle_changed = True

        curr_pos = mouse.pos

        if self._dragging:
            pos = Vector2.from_xy(0, 0)
            click_pos = self._click_pos
            assert click_pos
            coords_before = self._bg_circle_coords_before
            rsize = self._no_borders_current_size
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

            self._circle_changed = True
            self._circle_coordinates = pos

        elif self._click_pos is not None and self._after_key_down_time is not None:
            if (
                abs(curr_pos.x - self._click_pos.x) > self._click_treshold
                or abs(curr_pos.y - self._click_pos.y) > self._click_treshold
                or self._after_key_down_time > 0.5
            ):
                self._dragging = True
                self._bg_circle_coords_before = self._circle_coordinates.xy

        if self._circle_changed is True:
            self._rebuild_bg()
            self._circle_changed = False

    def _draw_main(self):
        super()._draw_main()
        self._background = (
            self.cache.get(CacheType.Surface)
            or self.cache.get(CacheType.Borders)
            or self.cache.get(CacheType.Background)
        )

    def _draw_end(self):
        super()._draw_end()
        self._circle_surface = self._create_bg_circle()
        self._rebuild_bg()

    def _get_correct_axis(self):
        axis = self.axis
        if axis == SwitchAxis.Auto:
            if self.size.x > self.size.y:
                axis = SwitchAxis.Horizontal
            else:
                axis = SwitchAxis.Vertical
        return axis

    def _resize_content(self, resize_ratio: Vector2):
        super()._resize_content(resize_ratio)
        self._circle_surface = None

        axis = self._get_correct_axis()
        main_coord = 0 if axis == SwitchAxis.Horizontal else 1

        bg_coords = self._circle_coordinates.xy
        if self.state is True:
            bg_coords[main_coord] = (
                self._no_borders_current_size[main_coord] - self.minimal_side
            )
        else:
            bg_coords[main_coord] = 0

        self._circle_coordinates = bg_coords
        self._goal_circle_coords = bg_coords.copy()

        self._circle_anim_manager = None
        self._circle_changed = True

    def _create_clone(self):
        return self.__class__(
            self._template.state,
            self._template.size,
            copy.deepcopy(self.style),
            **self.kwargs,
        )


# === NOT CLASS FUNCTIONS ===

def switch_on_click(self: Switch):
    self._after_key_down_time = 0
    self._click_pos = mouse.pos.xy


def switch_on_keyup(self: Switch):
    down_time = self._after_key_down_time
    if self._dragging:
        self._after_kup()
    elif down_time is not None and down_time < 0.5:
        self.state = not self.state
    self._after_key_down_time = None


def switch_on_keyup_abandon(self: Switch):
    if self._dragging:
        self._after_kup()
    self._after_key_down_time = None
