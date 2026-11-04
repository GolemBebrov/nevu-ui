from collections.abc import Callable
from typing import Any, Unpack, overload

import nevu_ui.core.modules as md
from nevu_ui.components._typehints import (
    _ProgressBarKwargsLongFull,
    _ProgressBarKwargsShortFull,
)
from nevu_ui.components.widgets.widget import Widget
from nevu_ui.core import Annotations
from nevu_ui.core.enums import ParamLayer, RenderReturnType
from nevu_ui.core.state import nevu_state
from nevu_ui.cython import Vector2
from nevu_ui.cython.surface.surface import Surface
from nevu_ui.cython.raylib.raylib import begin_blend_mode, end_blend_mode
from nevu_ui.presentation.theme import PairColorRole
from nevu_ui.presentation.color import Color
from nevu_ui.rendering import DrawBaseCall


class ProgressBar(Widget):
    # === Params ===
    start_value: int | float
    end_value: int | float
    current_value: int | float
    filled_rect_role: PairColorRole
    on_current_value_change: Callable | None
    # ==============

    @overload
    def __init__(
        self,
        size: Annotations.nevuobj_size = None,
        style: Annotations.nevuobj_style = None,
        **params: Unpack[_ProgressBarKwargsLongFull],
    ): ...

    @overload
    def __init__(
        self,
        size: Annotations.nevuobj_size = None,
        style: Annotations.nevuobj_style = None,
        **params: Unpack[_ProgressBarKwargsShortFull],
    ): ...

    def __init__(
        self,
        size: Annotations.nevuobj_size = None,
        style: Annotations.nevuobj_style = None,
        **params: Any,
    ):
        super().__init__(size, style, **params)
        self.set_progress_by_value(self.current_value)

    def _init_booleans(self):
        super()._init_booleans()
        self.hoverable = False
        self._changed_value = True
        self._changed_curr_val = False
        self._changed_other_val = False
        self._supports_tuple_borderradius = False

    def _add_params(self):
        super()._add_params()
        self._add_param(
            "start_value",
            int | float,
            0,
            layer=ParamLayer.Top,
            setter=self._start_value_setter,
        )
        self._add_param_link("start", "start_value")
        self._add_param(
            "end_value",
            int | float,
            100,
            layer=ParamLayer.Top,
            setter=self._end_value_setter,
        )
        self._add_param_link("end", "end_value")
        self._add_param(
            "current_value",
            int | float,
            0,
            layer=ParamLayer.Complicated,
            setter=self._current_value_setter,
        )
        self._add_param_link("current", "current_value")
        self._add_param("on_current_value_change", type(None) | Callable, None)
        self._add_param_link("on_value_change", "on_current_value_change")
        self._add_param("filled_rect_role", PairColorRole, PairColorRole.Background)
        self._add_param_link("role", "filled_rect_role")

    @property
    def progress(self):
        return self._progress

    @progress.setter
    def progress(self, value):
        self._progress = value
        self.current_value = (
            self.start_value + (self.end_value - self.start_value) * self._progress
        )

    def _base_clear(self):
        self._changed = True
        self._changed_value = True

    def _start_value_setter(self, value):
        self._base_clear()
        self._changed_other_val = True
        return value

    def _end_value_setter(self, value):
        self._base_clear()
        self._changed_other_val = True
        return value

    def _current_value_setter(self, value):
        self._base_clear()
        value = min(self.end_value, max(self.start_value, value))
        if self._changed_other_val:
            self._changed_other_val = False
            return value
        self._changed_curr_val = True
        return value

    def set_progress_by_value(self, value: float):
        if (self.end_value - self.start_value) == 0:
            self.progress = 1
            return
        self.progress = (value - self.start_value) / (self.end_value - self.start_value)

    def _draw_start(self):
        super()._draw_start()
        surface = self.surface

        is_raylib = nevu_state.window.renderer_type.raylib
        bg_size = surface.size
        bg_surf = Surface(bg_size)
        with bg_surf:
            bg_surf.clear(Color.Blank)
            if is_raylib:
                begin_blend_mode(md.rl.BlendMode.BLEND_ALPHA_PREMULTIPLY)
            bg_surf.blit(surface, (0, 0))
            if is_raylib:
                end_blend_mode()
        self.bg_surface = bg_surf

        if self._changed_value:
            curr_value = self.current_value
            if on_val_change := self.on_current_value_change:
                on_val_change(self, curr_value)
            self._changed_value = False
            if self._changed_curr_val:
                start_val = self.start_value
                self._progress = (self.current_value - start_val) / (
                    self.end_value - start_val
                )
            else:
                self.set_progress_by_value(curr_value)

    def _create_surface(self, bar_surf=None, coords=None):
        assert self.surface
        assert coords
        surface = self.surface
        bg_surf = self.bg_surface

        is_raylib = nevu_state.window.renderer_type.raylib
        with surface:
            surface.clear(Color.Blank)
            if is_raylib:
                begin_blend_mode(md.rl.BlendMode.BLEND_ALPHA_PREMULTIPLY)
            surface.blit(bg_surf, (0, 0))
            if bar_surf:
                surface.blit(bar_surf, coords)
            if is_raylib:
                end_blend_mode()

    def _draw_main(self):
        super()._draw_main()
        if self.progress < 0:
            return

        self._changed_value = False
        self._changed_curr_val = False

        rsize = self._no_borders_current_size
        relm = self.relm
        style = self.style

        progress = max(0.0, min(1.0, self.progress))

        width = int(rsize.x * progress)
        if progress > 0 and width == 0:
            width = 1

        height = round(rsize.y)

        size = Vector2.from_xy(width, height)
        half_size = size / 2

        bw = relm(style.border_width)
        radius = style.border_radius - bw
        min_side = min(rsize.x // 2, rsize.y // 2)
        radius = min(min_side, max(radius, 0))

        y_decrease = 0
        if half_size.x < relm(radius):
            y_decrease = (relm(radius) - half_size.x)
            if size.y - y_decrease * 2 > 0:
                size.y -= y_decrease * 2

        if size.x <= 0 or size.y <= 0:
            self._create_surface(None, (0, 0))
            return

        if isinstance(radius, int | float):
            radius = min(half_size.x, half_size.y, radius)
            radius = (radius, radius, radius, radius)

        color = self.style.get_pair_color(self.filled_rect_role, inverted = self.inverted)

        renderer = self.renderer
        bar_surface = renderer.core.create_surface(size)
        if nevu_state.window.renderer_type.raylib:
            md.rl.set_texture_filter(
                bar_surface.native.texture, md.rl.TextureFilter.TEXTURE_FILTER_BILINEAR
            )

        renderer.run_base(
            DrawBaseCall(
                style=self.style,
                radius_support=True,
                size=size,
                color=color,
                gradient_support=False,
                return_type=RenderReturnType.Modify,
                modify_object=bar_surface,
                glassy = self.glassy
            )
        )

        coords = Vector2.from_xy(
            self._borders_of_current_size.x, self._borders_of_current_size.y + y_decrease
        )
        assert self.surface

        self._create_surface(bar_surface, coords.to_tuple())
