from __future__ import annotations

import copy
import weakref
from typing import TYPE_CHECKING

import nevu_ui.core.modules as md
from nevu_ui.core.classes import SurfaceLike, TooltipType
from nevu_ui.core.state import nevu_state
from nevu_ui.fast import Cache, NvRect, NvRenderTexture, NvVector2
from nevu_ui.fast.raylib import begin_blend_mode, end_blend_mode
from nevu_ui.presentation.style import Style, default_style

if TYPE_CHECKING:
    from nevu_ui.components.nevuobj import NevuObject
from nevu_ui.core.enums import (
    CacheType,
    EventType,
    HoverState,
    Malign,
    RenderConfig,
    RenderReturnType,
)
from nevu_ui.overlay import overlay
from nevu_ui.presentation.color import SubThemeRole, TupleColorRole
from nevu_ui.rendering.base_renderer import BaseRenderer, DrawBaseCall, DrawTextCall
from nevu_ui.utils import NevuEvent, mouse, time

# include <brain.h>
# include <not bugs.h>
# include <stability.h>
# define GurrenLagann


class _TooltipBase:
    __slots__ = (
        "ratio",
        "pos",
        "size",
        "style",
        "title",
        "_cached_surf",
        "initial_ratio",
        "cache",
    )

    def __init__(self, title: str, style: Style = default_style):
        self.initial_ratio = NvVector2(1, 1)
        self.ratio = NvVector2(1, 1)
        self.pos = NvVector2()
        self.size = NvVector2()
        self.style = copy.deepcopy(style)
        self.title = title
        self.cache = Cache()
        self._cached_surf = None

    def _clear_rl_specific(self):
        assert nevu_state.window

        if self.cache.get(CacheType.RlFont):
            md.rl.unload_font(self.cache.get(CacheType.RlFont))  # type: ignore
        if self.cache.get(CacheType.Scaled_Image):
            md.rl.unload_texture(self.cache.get(CacheType.Scaled_Image))  # type: ignore

    def clear_all(self):
        if nevu_state.window.renderer_type.raylib:
            self._clear_rl_specific()
        self.cache.clear()

    def clear_surfaces(self):
        if nevu_state.window.renderer_type.raylib:
            self._clear_rl_specific()
        self.cache.clear_selected(
            whitelist=[
                CacheType.Scaled_Image,
                CacheType.Image,
                CacheType.Scaled_Gradient,
                CacheType.Surface,
                CacheType.Borders,
                CacheType.Scaled_Borders,
                CacheType.Scaled_Background,
                CacheType.Background,
                CacheType.Texture,
                CacheType.RlFont,
                CacheType.TextArgs,
                CacheType.ClickTexture,
            ],
            blacklist=[],
        )

    def adapted_coords(self):
        return mouse.pos

    def get_surf(self, renderer: BaseRenderer):
        if not self._cached_surf:
            self._cached_surf = self._get_surf_content(renderer)
        return self._cached_surf

    def resize(self, ratio: NvVector2):
        self.ratio = ratio
        self._cached_surf = None
        self.clear_all()

    def _get_surf_content(self, renderer: BaseRenderer) -> SurfaceLike:
        br = self.style.border_radius
        if isinstance(br, list | tuple):
            br = max(br)
            self.style.border_radius = br
        title_rect = NvRect(0, 0, *self._csize)

        surf = renderer.run_base(
            DrawBaseCall(
                size=self._csize,
                radius=br,
                color=self.style.colortheme.get_subtheme(
                    SubThemeRole.TERTIARY
                ).oncontainer,
                return_type=RenderReturnType.CreateNew,
            )
        )

        title_kwargs = renderer.run_text(
            DrawTextCall(
                text=self.title,
                font_size=self.style.font_size * self.ratio.y,
                color=self.style.colortheme.get_tuple(TupleColorRole.INVERSE_PRIMARY),
                return_type=RenderReturnType.CreateNew,
                max_size=self._csize,
            )
        )

        _, title_surf = title_kwargs  # type: ignore

        assert SurfaceLike.as_type(surf)
        assert SurfaceLike.as_type(title_surf)

        title_width = title_surf.width
        title_rect[0] += self._csize.x / 2 - title_width / 2

        surf.blit(title_surf, title_rect.get_int_tuple())

        return surf

    @property
    def _csize(self):
        return self.size * self.ratio


class _ExtendedTooltipBase(_TooltipBase):
    __slots__ = tuple(list(_TooltipBase.__slots__) + ["content"])

    def __init__(self, title: str, content, style: Style = default_style):
        super().__init__(title, style)
        self.content = content

    def _get_surf_content(self, renderer: BaseRenderer) -> SurfaceLike:
        br = self.style.border_radius
        if isinstance(br, list | tuple):
            br = max(br)
            self.style.border_radius = br

        surf = renderer.run_base(
            DrawBaseCall(
                size=self._csize,
                radius=br,
                color=self.style.colortheme.get_subtheme(
                    SubThemeRole.TERTIARY
                ).oncontainer,
                return_type=RenderReturnType.CreateNew,
            )
        )

        title_size = self._csize - NvVector2.from_xy(0, self._csize.y / 1.3)
        content_size = self._csize - NvVector2.from_xy(0, title_size.y)
        title_rect = NvRect(0, 0, *title_size)
        content_rect = NvRect(0, title_rect.h, *content_size)

        title_kwargs = renderer.run_text(
            DrawTextCall(
                font_size=self.style.font_size * self.ratio.y,
                text=self.title,
                color=self.style.colortheme.get_tuple(TupleColorRole.INVERSE_PRIMARY),
                return_type=RenderReturnType.CreateNew,
                max_size=title_size,
            )
        )

        content_kwargs = renderer.run_text(
            DrawTextCall(
                font_size=self.style.font_size * self.ratio.y,
                text=self.content,
                color=self.style.colortheme.get_tuple(TupleColorRole.INVERSE_PRIMARY),
                return_type=RenderReturnType.CreateNew,
                max_size=content_size,
            )
        )

        _, title_surf = title_kwargs  # type: ignore
        _, content_surf = content_kwargs  # type: ignore

        assert SurfaceLike.as_type(surf)
        assert SurfaceLike.as_type(title_surf)
        assert SurfaceLike.as_type(content_surf)

        title_width = title_surf.width
        content_width = content_surf.width
        title_rect[0] += title_size.x / 2 - title_width / 2 + 0.001
        content_rect[0] += content_size.x / 2 - content_width / 2 + 0.001

        surf.blit(title_surf, (title_rect.x, title_rect.y))
        surf.blit(content_surf, (content_rect.x, content_rect.y))
        return surf


class _SmallTooltip(_TooltipBase):
    def __init__(self, title: str, style: Style = default_style):
        super().__init__(title, style)
        self.initial_ratio = NvVector2(0.2, 0.2)


class _MediumTooltip(_ExtendedTooltipBase):
    def __init__(self, title: str, content, style: Style = default_style):
        super().__init__(title, content, style)
        self.initial_ratio = NvVector2(0.4, 0.3)


class _LargeTooltip(_ExtendedTooltipBase):
    def __init__(self, title: str, content, style: Style = default_style):
        super().__init__(title, content, style)
        self.initial_ratio = NvVector2(0.6, 0.4)


class _CustomTooltip(_TooltipBase):
    def __init__(self, ratio: NvVector2, title: str, style: Style = default_style):
        super().__init__(title, style)
        self.initial_ratio = ratio


class _BigCustomTooltip(_ExtendedTooltipBase):
    def __init__(
        self, ratio: NvVector2, title: str, content: str, style: Style = default_style
    ):
        super().__init__(title, content, style)
        self.initial_ratio = ratio


# faputa solo sosu
class Tooltip:
    tooltip_type = (
        TooltipType.Large
        | TooltipType.Medium
        | TooltipType.Small
        | TooltipType.Custom
        | TooltipType.BigCustom
    )

    def __init__(self, type: tooltip_type, style: Style = default_style):
        self.style = style
        self.type = type
        self.master: NevuObject | None = None
        self._data = self.unpack_type()
        self.get_surf = self._data.get_surf
        self._counter = 0
        self._counter_max = 1.5
        self._counter_max_opened = self._counter_max * 0.4
        self.old_coord = NvVector2()

    def adapted_coords(self):
        assert self.master, "Tooltip is not connected to NevuObject!"
        return self._data.adapted_coords()

    @property
    def size(self):
        return self._data.size

    @size.setter
    def size(self, size: NvVector2):
        self._data.size = size

    def resize(self, resize_ratio: NvVector2):
        self._data.resize(resize_ratio)

    def unpack_type(self):
        if isinstance(self.type, TooltipType.Small):
            return _SmallTooltip(self.type.title, self.style)
        elif isinstance(self.type, TooltipType.Medium):
            return _MediumTooltip(self.type.title, self.type.content, self.style)
        elif isinstance(self.type, TooltipType.Large):
            return _LargeTooltip(self.type.title, self.type.content, self.style)
        elif isinstance(self.type, TooltipType.Custom):
            return _CustomTooltip(self.type.ratio, self.type.title, self.style)
        elif isinstance(self.type, TooltipType.BigCustom):
            return _BigCustomTooltip(
                self.type.ratio, self.type.title, self.type.content, self.style
            )
        raise ValueError("Invalid tooltip type!")

    def _off(self, *args):
        if overlay.has_element(self):
            overlay.remove_element(self)

    def _on(self, *args):
        assert self.master and self.master.renderer, (
            "Tooltip is not connected to NevuObject!"
        )
        overlay.change_element(
            self,
            self.get_surf(self.master.renderer),
            self.adapted_coords(),
            2,
            strict=False,
        )

    def _adjust_size(self):
        assert self.master, "Tooltip is not connected to NevuObject!"
        self.size = self.master.size * self._data.initial_ratio

    def _update(self, *args):
        assert self.master, "Tooltip is not connected to NevuObject!"
        if self.master.hover_state == HoverState.NotHovered and overlay.has_element(
            self
        ):
            self._off()
            self._counter = 0
        elif self.master.hover_state in [HoverState.Hovered, HoverState.Clicked]:
            new_pos = mouse.pos
            if new_pos != self.old_coord:
                self._counter += 1 * time.dt
                if (
                    overlay.has_element(self)
                    and self._counter >= self._counter_max_opened
                ):
                    self._move_to_mouse(new_pos)
                elif self._counter >= self._counter_max:
                    self._move_to_mouse(new_pos)

    def _move_to_mouse(self, new_pos):
        self._on()
        self._counter = 0
        self.old_coord = new_pos

    def connect_to_master(self, master: NevuObject):
        self.master = weakref.proxy(master)
        assert self.master, "Tooltip is not connected to NevuObject!"
        self.master.add_first_update_action(self._adjust_size)
        self.master.subscribe(NevuEvent(self, self._off, EventType.OnUnhover))
        self.master.subscribe(NevuEvent(self, self._update, EventType.Update))
