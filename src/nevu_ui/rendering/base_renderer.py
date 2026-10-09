from __future__ import annotations

import math
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import TYPE_CHECKING, Any

from nevu_ui.core.classes import SurfaceLike
from nevu_ui.core.state import nevu_state
from nevu_ui.fast.nevucache.nevucache import Cache
from nevu_ui.presentation.style import default_style

if TYPE_CHECKING:
    from nevu_ui.presentation.style import Style
    from nevu_ui.rendering.raylib.gradient import ClickGradient
from nevu_ui.core.annotations import Annotations
from nevu_ui.core.enums import (
    Align,
    RenderReturnType,
)
from nevu_ui.fast.nvvector2 import NvVector2
from nevu_ui.presentation.color import Color


class _BaseCoreNamespace(ABC):
    def __init__(self): ...

    @abstractmethod
    def get_gradient(self, style: Style) -> Any:  # pyright: ignore[reportAny]
        raise NotImplementedError

    @abstractmethod
    def get_font(
        self,
        *,
        style: Style = default_style,
        cache: Cache | None = None,
        relative = False,
        relm: float | None = None,
        size: int | None = None,
        path: str | None = None,
    ) -> tuple[Any, int]:  # pyright: ignore[reportAny]
        raise NotImplementedError

    @abstractmethod
    def create_clear(self, size: Annotations.dest_like_v) -> SurfaceLike:
        raise NotImplementedError

    @abstractmethod
    def draw_rect(
        self,
        surface_like: Any,
        pos: Annotations.dest_like_v,
        size: Annotations.dest_like_v,
        *,
        color: Annotations.rgb_like_color = Color.White,
        style: Style = default_style,
    ) -> None: raise NotImplementedError

    @abstractmethod
    def draw_line(
        self,
        surface_like: Any,
        pos_from: Annotations.dest_like_v,
        pos_to: Annotations.dest_like_v,
        *,
        width: float | None = None,
        radius: Annotations.rad_like | None = None,
        relative: bool = False,
        relm: float | None  = None,
        color: Annotations.rgb_like_color = Color.White,
        style: Style = default_style,
    ) -> None: raise NotImplementedError

    @abstractmethod
    def get_image(
        self,
        style: Style,
        *,
        size: Annotations.dest_like_v | None = None
    ): raise NotImplementedError

    @abstractmethod
    def measure_text(
        self,
        text: str,
        *,
        style: Style = default_style,
        cache: Cache | None = None,
        relative = False,
        relm: float | None = None,
        font: Any = None,
        font_size: int | None = None,
    ) -> NvVector2: raise NotImplementedError

    def get_font_size(
        self,
        style: Style,
        *,
        relative = False,
        relm: float | None = None
    ) -> float:
        font_size = style.font_size
        if relative:
            relm = relm or self.get_relm()
            return font_size * relm
        return font_size

    def get_relm(self) -> float:
        """Can be used only after Window initialized"""
        Annotations.window_check()
        rel = nevu_state.window.rel
        return (rel.x + rel.y) / 2

    def align_text_line(
        self,
        block_width: float,
        line_width: float,
        line_number: int,
        *,
        line_height_px: int,
        half_leading: float,
        style = default_style,
    ):
        match style.text_align_x:
            case Align.CENTER: dx = (block_width - line_width) / 2
            case Align.RIGHT:  dx = block_width - line_width
            case _:            dx = 0
        match style.text_align_y:
            case Align.CENTER: dy = line_number * line_height_px + half_leading
            case Align.BOTTOM: dy = line_number * line_height_px + half_leading * 2
            case _:            dy = line_number * line_height_px
        return dx, dy

    def wrap_text(
        self,
        text_parts: list[str],
        *,
        max_width: float = float("inf"),
        separator: str = " ",
        style: Style = default_style,
        literal_newline_support: bool = True,
        cache: Cache | None = None,
        relative: bool = False,
        relm: float | None = None,
        font: Any | None = None,
        font_size: int | None = None,
    ) -> list[str]:
        if max_width <= 0:
            raise ValueError("Max_width must be greater than zero.")
        if math.isnan(max_width):
            raise ValueError("Max_width cannot be NaN!")

        if not text_parts:
            return []

        lines: list[str] = []
        unlimited_width = max_width == float("inf")

        current_part = ""
        measure = self.measure_text
        ended_with_newline = False

        for new_part in text_parts:
            if new_part == "\n" or (new_part == "\\n" and literal_newline_support):
                lines.append(current_part)
                current_part = ""
                ended_with_newline = True
                continue

            ended_with_newline = False
            has_content = current_part != ""

            if has_content:
                test_line = current_part + separator + new_part
            else:
                test_line = new_part

            if unlimited_width:
                current_part = test_line
                continue

            if measure(test_line, style=style, cache=cache, relative=relative, relm=relm, font=font, font_size=font_size).x > max_width:
                if has_content:
                    lines.append(current_part)
                    current_part = new_part
                else:
                    current_part = test_line
            else:
                current_part = test_line

        if current_part != "" or ended_with_newline:
            lines.append(current_part)

        return lines

    def normalize_radius(
        self,
        radius: Annotations.rad_like,
        *,
        relative = False,
        relm: float | None = None
    ) -> Annotations.normalized_radius:
        if isinstance(radius, int | float):
            radius = (radius, radius, radius, radius)

        if not relative:
            return radius

        if relm:
            ratio = relm
        else:
            ratio = self.get_relm()
        return (radius[0] * ratio, radius[1] * ratio, radius[2] * ratio, radius[3] * ratio)

    def normalize_color(
        self,
        color: Annotations.rgb_like_color
    ) -> Annotations.rgba_color:
        if len(color) == 3:
            return color[0], color[1], color[2], 255
        return color

    def align_inner_rect(
        self,
        container_rect: Annotations.rect_like,
        inner_size: Annotations.dest_like_v,
        *,
        style: Style = default_style,
        strict_size = True,
    ) -> NvVector2:
        result_x = container_rect[0]
        result_y = container_rect[1]

        container_width = container_rect[2]
        container_height = container_rect[3]

        inner_width =  inner_size[0]
        inner_height = inner_size[1]

        if strict_size:
            if inner_width > container_width or inner_height > container_height:
                raise ValueError("Inner size is larger than the container size.")
        else:
            inner_width = min(container_width, inner_width)
            inner_height = min(container_height, inner_height)

        match style.align_x:
            case Align.LEFT: result_x = container_rect[0]
            case Align.CENTER: result_x = container_rect[0] + (container_width - inner_width) / 2
            case Align.RIGHT: result_x = container_rect[0] + container_width - inner_width

        match style.align_y:
            case Align.TOP: result_y = container_rect[1]
            case Align.CENTER: result_y = container_rect[1] + (container_height - inner_height) / 2
            case Align.BOTTOM: result_y = container_rect[1] + container_height - inner_height

        return NvVector2(round(result_x), round(result_y))

@dataclass(kw_only=True, slots=True)
class _BaseCall:
    size: NvVector2
    relative: bool = True
    relm: float | None = None
    return_type: RenderReturnType = RenderReturnType.CreateNew
    modify_object: Any = None
    pos: Annotations.dest_like_v | None = None

@dataclass(kw_only=True, slots=True)
class DrawBgCall(_BaseCall):
    bg_color: Annotations.rgba_color
    border_color: Annotations.rgba_color | None = None
    style: Style = default_style
    cache: Cache | None = None

    gradient_support: bool = False
    image_support: bool = False
    radius_support: bool = True
    inline: bool = False
    glassy: bool = False


@dataclass(kw_only=True, slots=True, unsafe_hash=True)
class DrawBaseCall(_BaseCall):
    color: Annotations.rgba_color
    style: Style = default_style
    cache: Cache | None = None

    gradient_support: bool = False
    image_support: bool = False
    radius_support: bool = True
    inline: bool = False
    glassy: bool = False


@dataclass(kw_only=True, slots=True)
class DrawTextCall(_BaseCall):
    text: str

    cache: Cache | None = None
    style: Style = default_style
    font_size: int | None = None
    color: Annotations.rgba_color | None = None
    max_size: NvVector2 | None = None
    line_height: float = 1.25

    unlimited_x: bool = False
    unlimited_y: bool = False
    words_indent: bool = False


@dataclass(kw_only=True, slots=True)
class DrawEffectsCall(_BaseCall):
    """Currently supported only for Raylib backend"""
    click_gradient: ClickGradient
    effect_texture: Any = None
    radius: Annotations.rad_like | None = None


@dataclass(kw_only=True, slots=True)
class DrawBordersCall(_BaseCall):
    original_surface: Any
    style: Style = default_style
    color: Annotations.rgba_color | None = None
    glassy: bool = False


class BaseRenderer(ABC):
    __slots__ = [
        "_key_to_func",
        "_pipeline",
        "_root",
        "core",
        "release",
        "unsafe",
    ]

    def _get_unexpected_error(self, error: Exception, func_name: str):
        raise ValueError(
            Annotations.format_nvtype_renderer_error(
                f"unexpected error - '{error}'", self, func_name
            )
        )

    def __init__(self):
        self.core: _BaseCoreNamespace = self._get_core_namespace()

    def run_base(self, call: DrawBaseCall):
        return_type = call.return_type

        try:
            match return_type:
                case RenderReturnType.Modify:
                    texture = call.modify_object
                    if texture is None:
                        raise ValueError("Modify return type selected but no modify_object provided.")
                    self._base_draw(texture, call)
                case RenderReturnType.CreateNew:
                    texture = self.core.create_clear(call.size)
                    self._base_draw(texture, call)
                    return texture
                case _:
                    raise ValueError(f"Invalid return type: {return_type}")
        except Exception as e:
            raise self._get_unexpected_error(e, "run_base")

    def run_borders(self, call: DrawBordersCall):
        return_type = call.return_type
        try:
            match return_type:
                case RenderReturnType.Modify:
                    texture = call.modify_object
                    assert texture, "Modify return type selected but no object provided"
                    self._borders_draw(texture, call)
                case RenderReturnType.CreateNew:
                    texture = self.core.create_clear(call.size)
                    self._borders_draw(texture, call)
                    return texture

                case _:
                    raise ValueError(f"Invalid return type: {return_type}")
        except Exception as e:
            raise self._get_unexpected_error(e, "run_text")

    def run_text(self, call: DrawTextCall):
        return_type = call.return_type
        try:
            match return_type:
                case RenderReturnType.Modify:
                    texture = call.modify_object
                    if texture is None:
                        raise ValueError("Modify return type requires a non-None modify_object.")
                    text_lines, text_pos, _ = self._arrange_text(call)
                    self._text_draw(text_lines, texture, call, text_pos)
                    return text_pos, texture
                case RenderReturnType.CreateNew:
                    text_lines, text_pos, text_size = self._arrange_text(call, pos = NvVector2(0, 0))
                    texture = self.core.create_clear(text_size)
                    self._text_draw(text_lines, texture, call, NvVector2())
                    return text_pos, texture

                case _:
                    raise ValueError(f"Unknown return type: {return_type}")
        except Exception as e:
            raise self._get_unexpected_error(e, "run_text")

    def run_effects(self, call: DrawEffectsCall):
        core = self.core
        click_gradient = call.click_gradient
        effect_texture = call.effect_texture
        effect_texture = effect_texture or self.core.create_clear(call.size)
        return_type = call.return_type

        try:
            match return_type:
                case RenderReturnType.Modify:
                    texture = call.modify_object
                    assert texture, "Modify return type selected but no object provided"
                    self._add_effects(call, effect_texture, click_gradient, texture)
                case RenderReturnType.CreateNew:
                    texture = core.create_clear(call.size)
                    self._add_effects(call, effect_texture, click_gradient, texture)
                    return texture

                case _:
                    raise ValueError(f"Invalid return type: {return_type}")
        except Exception as e:
            raise self._get_unexpected_error(e, "run_effects")

    def run_bg(self, call: DrawBgCall):
        return_type = call.return_type
        base_call = DrawBaseCall(
            pos=call.pos,
            size=call.size,
            color=call.bg_color,
            style=call.style,
            cache=call.cache,
            gradient_support=call.gradient_support,
            image_support=call.image_support,
            radius_support=call.radius_support,
            inline=call.inline,
            glassy=call.glassy,
        )
        borders_call = DrawBordersCall(
            original_surface=None,
            pos=call.pos,
            size=call.size,
            color=call.border_color,
            style=call.style,
        )
        try:
            match return_type:
                case RenderReturnType.Modify:
                    texture = call.modify_object
                    if texture is None:
                        raise ValueError("Modify return type selected but no modify_object provided.")
                    self._base_draw(texture, base_call)
                    result_texture = texture.copy()
                    borders_call.original_surface = texture
                    self._borders_draw(texture, borders_call)

                case RenderReturnType.CreateNew:
                    texture = self.core.create_clear(call.size)
                    self._base_draw(texture, base_call)
                    result_texture = self.core.create_clear(call.size)
                    borders_call.original_surface = texture
                    self._borders_draw(result_texture, borders_call)
                    return result_texture

                case _:
                    raise ValueError(f"Invalid return type: {return_type}")
        except Exception as e:
            raise self._get_unexpected_error(e, "run_base")

    @abstractmethod
    def _get_core_namespace(self) -> _BaseCoreNamespace:
        raise NotImplementedError

    @abstractmethod
    def _base_draw(
        self,
        texture: SurfaceLike,
        call: DrawBaseCall,
    ): raise NotImplementedError

    @abstractmethod
    def _text_draw(
        self,
        text_lines: list[str],
        texture: SurfaceLike,
        call: DrawTextCall,
        pos: NvVector2 | None = None,
    ): raise NotImplementedError

    @abstractmethod
    def _arrange_text(
        self,
        call: DrawTextCall,
        pos: Annotations.dest_like_v | None = None,
    ) -> tuple[list[str], NvVector2, NvVector2]:
        raise NotImplementedError

    @abstractmethod
    def _borders_draw(
        self,
        texture: SurfaceLike,
        call: DrawBordersCall,
    ): raise NotImplementedError

    @abstractmethod
    def _add_effects(
        self,
        call: DrawEffectsCall,
        effect_texture: Any,
        gradient: ClickGradient,
        texture: Any,
    ): raise NotImplementedError
