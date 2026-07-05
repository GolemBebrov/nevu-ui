import math
from typing import Any, Callable, Unpack, overload

import nevu_ui.core.modules as md
from nevu_ui.components.widgets.typehints import (
    ProgressBarKwargs,
    ProgressBarKwargsLong,
    ProgressBarKwargsShort,
)
from nevu_ui.components.widgets.widget import Widget
from nevu_ui.core import Annotations
from nevu_ui.core.enums import ParamLayer, RenderConfig, RenderReturnType
from nevu_ui.core.state import nevu_state
from nevu_ui.fast import NvRenderTexture, NvVector2
from nevu_ui.fast.raylib.nevu_raylib import begin_blend_mode, end_blend_mode
from nevu_ui.presentation.color import Color, PairColorRole
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
        **constant_kwargs: Unpack[ProgressBarKwargsLong],
    ): ...

    @overload
    def __init__(
        self,
        size: Annotations.nevuobj_size = None,
        style: Annotations.nevuobj_style = None,
        **constant_kwargs: Unpack[ProgressBarKwargsShort],
    ): ...

    def __init__(
        self,
        size: Annotations.nevuobj_size = None,
        style: Annotations.nevuobj_style = None,
        **constant_kwargs: Any,
    ):
        super().__init__(size, style, **constant_kwargs)
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
        self._add_param("filled_rect_role", PairColorRole, PairColorRole.BACKGROUND)
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
        self.clear_surfaces()
        self.clear_texture()

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
        if self._changed_other_val:
            self._changed_other_val = False
            return value
        self._changed_curr_val = True
        return value

    def set_progress_by_value(self, value: int | float):
        self.progress = (value - self.start_value) / (self.end_value - self.start_value)

    def _init_inverted(self):
        super()._init_inverted()
        self._subtheme_progress = (
            self._alt_subtheme_progress()
            if self.inverted
            else self._main_subtheme_progress()
        )
        if len(self._subtheme_progress) == 3:
            self._subtheme_progress = (
                self._subtheme_progress[0],
                self._subtheme_progress[1],
                self._subtheme_progress[2],
                255,
            )

    def _main_subtheme_progress(self):
        return self.style.colortheme.get_pair(self.filled_rect_role).color

    def _alt_subtheme_progress(self):
        return self.style.colortheme.get_pair(self.filled_rect_role).oncolor

    def _primary_draw(self):
        super()._primary_draw()
        surface = self.surface

        dtype = nevu_state.window.renderer_type

        if dtype.raylib:
            assert isinstance(surface, NvRenderTexture)
            texture = surface.texture
            bg_surf = NvRenderTexture(NvVector2.from_xy(texture.width, texture.height))
            with bg_surf:
                bg_surf.fast_clear(Color.Blank)
                begin_blend_mode(md.rl.BlendMode.BLEND_ALPHA_PREMULTIPLY)
                bg_surf.fast_blit(surface, (0, 0))
                end_blend_mode()
            self.bgsurface = bg_surf

        elif dtype.pygame_like:
            pygame = md.pygame
            assert isinstance(surface, pygame.Surface)
            bgsurface = pygame.Surface(surface.get_size(), pygame.SRCALPHA)
            bgsurface.blit(surface, (0, 0))
            self.bgsurface = bgsurface
            surface.fill(Color.Blank)

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

        self.clear_texture()

    def _create_surface(self, bar_surf=None, coords=None):
        assert self.surface
        assert coords
        self.clear_texture()
        surface = self.surface
        bg_surf = self.bgsurface
        rtype = nevu_state.window.renderer_type

        if rtype.raylib:
            assert isinstance(surface, NvRenderTexture)
            assert isinstance(bg_surf, NvRenderTexture)
            surf_fast_blit = surface.fast_blit
            with surface:
                surface.fast_clear(Color.Blank)
                begin_blend_mode(md.rl.BlendMode.BLEND_ALPHA_PREMULTIPLY)
                surf_fast_blit(bg_surf, (0, 0))
                if bar_surf:
                    surf_fast_blit(bar_surf, coords)
                end_blend_mode()

        elif rtype.pygame_like:
            assert isinstance(surface, md.pygame.Surface)
            assert isinstance(bg_surf, md.pygame.Surface)
            surface.fill(Color.Blank)
            surf_blit = surface.blit
            surf_blit(bg_surf, (0, 0))
            if bar_surf:
                surf_blit(bar_surf, coords)

    def secondary_draw_content(self):
        super().secondary_draw_content()
        if self.progress < 0:
            return

        self._changed_value = False
        self._changed_curr_val = False

        rsize = self._no_borders_size
        ceil = math.ceil
        relm = self.relm
        style = self.style

        progress = max(0.0, min(1.0, self.progress))

        width = int(rsize.x * progress)
        if progress > 0 and width == 0:
            width = 1

        height = int(rsize.y)

        size = NvVector2.from_xy(width, height)
        half_size = size / 2

        bw = ceil(relm(style.border_width))
        radius = relm(style.border_radius) - bw
        min_side = min(rsize.x // 2, rsize.y // 2)
        radius = min(min_side, max(radius, 0))

        y_decrease = 0
        if half_size.x < radius:
            y_decrease = ceil(radius - half_size.x)
            if size.y - y_decrease * 2 > 0:
                size.y -= y_decrease * 2

        if size.x <= 0 or size.y <= 0:
            self._create_surface(None, (0, 0))
            return

        if isinstance(radius, int | float):
            radius = min(half_size.x, half_size.y, radius)
            radius = tuple((radius, radius, radius, radius))

        color = self._subtheme_progress

        renderer = self.renderer
        surf = renderer.core.create_clear(size)
        if nevu_state.window.renderer_type.raylib:
            assert isinstance(surf, NvRenderTexture)
            md.rl.set_texture_filter(
                surf.texture, md.rl.TextureFilter.TEXTURE_FILTER_TRILINEAR
            )

        renderer.run_base(
            DrawBaseCall(
                radius=style.border_radius,
                easy_background=False,
                size=size,
                color=color,
                gradient_support=False,
                return_type=RenderReturnType.Modify,
                modify_object=surf,
                standstill=True,
            )
        )

        coords = NvVector2.from_xy(
            self._borders_marg_size.x, self._borders_marg_size.y + y_decrease
        )
        assert self.surface

        self._create_surface(surf, coords.to_tuple())
