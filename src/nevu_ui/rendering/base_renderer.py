from __future__ import annotations

import math
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import TYPE_CHECKING, Any

from nevu_ui.core.state import nevu_state
from nevu_ui.cython.cache.cache import Cache
from nevu_ui.cython.font.font import Font
from nevu_ui.cython.surface.surface import Surface
from nevu_ui.presentation.style import default_style
from nevu_ui.core.size.rules import (
    CFill,
    CFillH,
    CFillW,
    Fill,
    FillH,
    FillW,
    _SizeRule,
)
if TYPE_CHECKING:
    from nevu_ui.presentation.style import Style
    from nevu_ui.rendering.raylib.gradient import ClickGradient
from nevu_ui.core.annotations import Annotations
from nevu_ui.core.enums import (
    Align,
    CacheType,
    RenderReturnType,
)
from nevu_ui.cython.vector2 import Vector2
from nevu_ui.presentation.color import Color

_bg_surface_pool: dict[tuple[int, int], tuple] = {}

class _BaseCoreNamespace(ABC):
    def __init__(self): ...

    @abstractmethod
    def get_gradient(self, style: Style) -> Any:  # pyright: ignore[reportAny]
        raise NotImplementedError

    def _get_font(self, size: int, path: str):
        font = Font(size, path)
        return font, font.size

    def get_font(
        self,
        *,
        style: Style = default_style,
        cache: Cache | None = None,

        size: int | None = None,
        path: str | None = None,

        relative = False,
        relm: float | None = None,
        container_size: Vector2 | None = None,
    ) -> tuple[Font, int]:

        font_name = path or style.font_name
        font_size = size if size is not None else round(self.get_font_size(style, relative=relative, relm=relm, container_size=container_size))

        if cache:
            return cache.get_or_exec(CacheType.Font, lambda name=font_name, size=font_size: self._get_font(size, name))
        return self._get_font(font_size, font_name)

    def create_surface(
        self,
        size: Annotations.vec2_like_v,
        *,
        clear_color: Annotations.rgb_like_color | None = Color.Blank,
        normalize_color: bool = True,
    ) -> Surface:
        surface = Surface(size)
        if clear_color is not None:
            clear_color = self.normalize_color(clear_color) if normalize_color else clear_color
            surface.clear(clear_color)
        return surface

    @abstractmethod
    def draw_rect(
        self,
        surface: Surface,
        pos: Annotations.vec2_like_v,
        size: Annotations.vec2_like_v,
        *,
        color: Annotations.rgb_like_color = Color.White,
        style: Style = default_style,
    ) -> None: raise NotImplementedError

    @abstractmethod
    def draw_line(
        self,
        surface: Surface,
        pos_from: Annotations.vec2_like_v,
        pos_to: Annotations.vec2_like_v,
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
        size: Annotations.vec2_like_v | None = None
    ): raise NotImplementedError

    def measure_text(
        self,
        text: str,
        *,
        style: Style = default_style,
        cache: Cache | None = None,
        relative = False,
        relm: float | None = None,
        font: Font | None = None,
        font_size: int | None = None,
    ) -> Vector2:
        if font is None:
            font, _ = self.get_font(style = style, cache=cache, relative=relative, relm=relm, size=font_size)
        result = font.measure(text)
        return Vector2.from_xy(result.x, result.y)

    def get_font_size(
        self,
        style: Style,
        *,
        container_size: Vector2 | None = None,
        relative: bool = False,
        relm: float | None = None
    ) -> float:
        raw_size = style.font_size
        if isinstance(raw_size, _SizeRule):
            if container_size is not None:
                rule_type = type(raw_size)
                if rule_type in (FillW, CFillW):
                    base = container_size.x
                elif rule_type in (FillH, CFillH, Fill, CFill):
                    base = container_size.y
                else:
                    raise ValueError(f"Style.font_size must be int or SizeRule.\nGot {raw_size}({rule_type})")
                size_px = base * (raw_size.value / 100)
            else:
                size_px = 16
            return max(6, size_px)

        if relative:
            relm = relm or self.get_relm()
            return raw_size * relm
        return float(raw_size)

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
            raise ValueError("max_width must be greater than zero.")
        if math.isnan(max_width):
            raise ValueError("max_width cannot be NaN!")

        if not text_parts:
            return []

        size_cache: dict[str, float] = {}
        lines: list[str] = []
        unlimited_width = max_width == float("inf")

        current_parts = []
        measure = self.measure_text
        ended_with_newline = False
        line_width = 0
        separator_width = measure(separator, style=style, cache=cache, relative=relative, relm=relm, font=font, font_size=font_size).x
        size_cache[separator] = separator_width

        for new_part in text_parts:
            if new_part == "\n" or (new_part == "\\n" and literal_newline_support):
                lines.append(separator.join(current_parts))
                line_width = 0
                current_parts.clear()
                ended_with_newline = True
                continue

            ended_with_newline = False

            if unlimited_width:
                current_parts.append(new_part)
                continue

            if new_part in size_cache:
                part_width = size_cache[new_part]
            else:
                part_width = measure(new_part, style=style, cache=cache, relative=relative, relm=relm, font=font, font_size=font_size).x
                size_cache[new_part] = part_width

            has_content = len(current_parts) != 0

            if has_content:
                width = line_width + separator_width + part_width
            else:
                width = part_width

            if width > max_width and has_content:
                lines.append(separator.join(current_parts))
                current_parts = [new_part]
                line_width = part_width
            else:
                current_parts.append(new_part)
                line_width = width

        if len(current_parts) != 0 or ended_with_newline:
            lines.append(separator.join(current_parts))

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
        inner_size: Annotations.vec2_like_v,
        *,
        style: Style = default_style,
        strict_size = True,
    ) -> Vector2:
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

        return Vector2(round(result_x), round(result_y))

@dataclass(kw_only=True, slots=True)
class _BaseCall:
    size: Vector2
    relative: bool = True
    relm: float | None = None
    return_type: RenderReturnType = RenderReturnType.CreateNew
    modify_object: Surface | None = None
    pos: Annotations.vec2_like_v | None = None


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
    max_size: Vector2 | None = None
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
    original_surface: Surface
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
                f"unexpected error - '{error}'", func_name
            )
        )

    def __init__(self):
        self.core: _BaseCoreNamespace = self._get_core_namespace()

    def run_base(self, call: DrawBaseCall):
        return_type = call.return_type

        try:
            match return_type:
                case RenderReturnType.Modify:
                    surface = call.modify_object
                    if surface is None:
                        raise ValueError("Modify return type selected but no modify_object provided.")
                    self._base_draw(surface, call)
                case RenderReturnType.CreateNew:
                    surface = self.core.create_surface(call.size)
                    self._base_draw(surface, call)
                    return surface
                case _:
                    raise ValueError(f"Invalid return type: {return_type}")
        except Exception as e:
            raise self._get_unexpected_error(e, "run_base")

    def run_borders(self, call: DrawBordersCall):
        return_type = call.return_type
        try:
            match return_type:
                case RenderReturnType.Modify:
                    surface = call.modify_object
                    assert surface, "Modify return type selected but no object provided"
                    self._borders_draw(surface, call)
                case RenderReturnType.CreateNew:
                    surface = self.core.create_surface(call.size)
                    self._borders_draw(surface, call)
                    return surface

                case _:
                    raise ValueError(f"Invalid return type: {return_type}")
        except Exception as e:
            raise self._get_unexpected_error(e, "run_text")

    def run_text(self, call: DrawTextCall):
        return_type = call.return_type
        try:
            match return_type:
                case RenderReturnType.Modify:
                    surface = call.modify_object
                    if surface is None:
                        raise ValueError("Modify return type requires a non-None modify_object.")
                    text_lines, text_pos, _ = self._arrange_text(call)
                    self._text_draw(text_lines, surface, call, text_pos)
                    return text_pos, surface
                case RenderReturnType.CreateNew:
                    text_lines, text_pos, text_size = self._arrange_text(call, pos = Vector2(0, 0))
                    surface = self.core.create_surface(text_size)
                    self._text_draw(text_lines, surface, call, Vector2())
                    return text_pos, surface

                case _:
                    raise ValueError(f"Unknown return type: {return_type}")
        except Exception as e:
            raise self._get_unexpected_error(e, "run_text")

    def run_effects(self, call: DrawEffectsCall):
        core = self.core
        click_gradient = call.click_gradient
        effect_texture = call.effect_texture
        effect_texture = effect_texture or self.core.create_surface(call.size)
        return_type = call.return_type

        try:
            match return_type:
                case RenderReturnType.Modify:
                    surface = call.modify_object
                    assert surface, "Modify return type selected but no object provided"
                    self._add_effects(call, effect_texture, click_gradient, surface)
                case RenderReturnType.CreateNew:
                    surface = core.create_surface(call.size)
                    self._add_effects(call, effect_texture, click_gradient, surface)
                    return surface

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
                    surface = call.modify_object
                    if surface is None:
                        raise ValueError("Modify return type selected but no modify_object provided.")
                    self._base_draw(surface, base_call)
                    result_surface = surface.copy()
                    borders_call.original_surface = surface
                    self._borders_draw(surface, borders_call)

                case RenderReturnType.CreateNew:
                    key = (int(call.size[0]), int(call.size[1]))
                    pair = _bg_surface_pool.get(key)
                    if pair is None:
                        pair = (self.core.create_surface(call.size), self.core.create_surface(call.size))
                        _bg_surface_pool[key] = pair
                    surface, result_surface = pair
                    self._base_draw(surface, base_call)
                    borders_call.original_surface = surface
                    self._borders_draw(result_surface, borders_call)
                    return result_surface

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
        surface: Surface,
        call: DrawBaseCall,
    ): raise NotImplementedError

    @abstractmethod
    def _text_draw(
        self,
        text_lines: list[str],
        surface: Surface,
        call: DrawTextCall,
        pos: Vector2 | None = None,
    ): raise NotImplementedError

    @abstractmethod
    def _arrange_text(
        self,
        call: DrawTextCall,
        pos: Annotations.vec2_like_v | None = None,
    ) -> tuple[list[str], Vector2, Vector2]:
        raise NotImplementedError

    @abstractmethod
    def _borders_draw(
        self,
        surface: Surface,
        call: DrawBordersCall,
    ): raise NotImplementedError

    @abstractmethod
    def _add_effects(
        self,
        call: DrawEffectsCall,
        effect_texture: Any,
        gradient: ClickGradient,
        surface: Surface,
    ): raise NotImplementedError
