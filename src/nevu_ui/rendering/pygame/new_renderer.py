from __future__ import annotations

import math
from typing import TYPE_CHECKING, Any, override

from nevu_ui.cython.nvsurface.nvsurface import NvSurface

if TYPE_CHECKING:
    from nevu_ui.presentation.style import Style
    from nevu_ui.rendering.pygame.gradient import GradientPygame
    from nevu_ui.rendering.raylib.gradient import ClickGradient

import nevu_ui.core.modules as md
from nevu_ui.core.annotations import Annotations
from nevu_ui.core.enums import CacheType
from nevu_ui.cython.nvvector2 import NvVector2
from nevu_ui.cython.shapes import (
    transform_into_outlined_rounded_rect,
    transform_into_rounded_rect,
)
from nevu_ui.cython.shapes.shapes import draw_sdf_line
from nevu_ui.presentation.color import Color
from nevu_ui.presentation.style import default_style
from nevu_ui.rendering.base_renderer import (
    BaseRenderer,
    DrawBaseCall,
    DrawBordersCall,
    DrawEffectsCall,
    DrawTextCall,
    _BaseCoreNamespace,
)

_pygame_font_cache: dict[tuple[str, int], tuple[Any, int]] = {}

class _PygameCoreNamespace(_BaseCoreNamespace):
    @override
    def get_gradient(self, style: Style) -> Any:
        if not style.gradient:
            raise ValueError("Gradient is not set in specified style.")
        gr: GradientPygame = style.gradient
        return gr

    @override
    def draw_rect(
        self,
        surface: NvSurface,
        pos: Annotations.vec2_like_v,
        size: Annotations.vec2_like_v,
        *,
        color: Annotations.rgb_like_color = Color.White,
        style: Style = default_style,
    ) -> None:
        radius = self.normalize_radius(style.border_radius, relative=True)
        color = self.normalize_color(color)
        x, y = int(pos[0]), int(pos[1])
        w, h = int(size[0]), int(size[1])

        if all(r == 0 for r in radius):
            md.pygame.draw.rect(surface.native, color, (x, y, w, h))
            return

        if x == 0 and y == 0 and (surface.get_width(), surface.get_height()) == (w, h):
            transform_into_rounded_rect(surface, radius, color)
        else:
            temp = self.create_surface((w, h))
            transform_into_rounded_rect(temp, radius, color)
            surface.blit(temp, (x, y))

    @override
    def draw_line(
        self,
        surface: NvSurface,
        pos_from: Annotations.vec2_like_v,
        pos_to: Annotations.vec2_like_v,
        *,
        width: float | None = None,
        radius: Annotations.rad_like | None = None,
        relative: bool = False,
        relm: float | None = None,
        color: Annotations.rgb_like_color = Color.White,
        style: Style = default_style,
    ) -> None:
        relm = relm or self.get_relm()

        line_width = width if width is not None else style.border_width
        if relative:
            line_width *= relm

        line_radius = radius if radius is not None else style.border_radius
        if isinstance(line_radius, tuple):
            line_radius = line_radius[0]
        if relative:
            line_radius *= relm

        color = self.normalize_color(color)
        w = max(1, round(line_width)) if line_width > 0 else 0
        r = round(line_radius)
        draw_sdf_line(surface.native, pos_from, pos_to, w, r, color)

    @override
    def get_image(
        self,
        style: Style,
        *,
        size: Annotations.vec2_like_v | None = None,
    ):
        image_path = getattr(style, "background_image", None) or getattr(style, "bg_image", None)
        if image_path is None:
            raise ValueError("Image path not provided in specified style.")

        img = md.pygame.image.load(image_path)
        try:
            img = img.convert_alpha()
        except Exception:
            pass

        if size:
            img = md.pygame.transform.smoothscale(img, (int(size[0]), int(size[1])))
        return img

class PygameRenderer(BaseRenderer):
    @override
    def _get_core_namespace(self) -> _BaseCoreNamespace:
        return _PygameCoreNamespace()

    @override
    def _base_draw(
        self,
        surface: NvSurface,
        call: DrawBaseCall,
    ):
        cache = call.cache
        style = call.style
        size = call.size
        w, h = int(size[0]), int(size[1])
        color = self.core.normalize_color(call.color)
        cache_available = cache is not None

        pos = call.pos or (0, 0)
        pos_xy = (int(pos[0]), int(pos[1]))
        direct_draw = (
            pos_xy == (0, 0)
            and surface.get_width() == w
            and surface.get_height() == h
        )

        target = surface if direct_draw else self.core.create_surface(size)

        if call.gradient_support and style.gradient:
            def _create_grad():
                gr = self.core.get_gradient(style)
                if hasattr(gr, "apply_gradient"):
                    return gr.apply_gradient(w, h)
                if hasattr(gr, "generate_texture"):
                    return gr.generate_texture(w, h)
                raise ValueError("Gradient object does not support apply_gradient or generate_texture")

            if cache_available:
                grad_surf = cache.get_or_exec(CacheType.Gradient, _create_grad)
            else:
                grad_surf = _create_grad()

            target.blit(grad_surf, (0, 0))
            if call.radius_support:
                radius = self.core.normalize_radius(style.border_radius, relative=True)
                if any(r > 0 for r in radius):
                    transform_into_rounded_rect(target.native, radius, None)

        elif call.image_support and (getattr(style, "background_image", None) or getattr(style, "bg_image", None)):
            if cache_available:
                image = cache.get_or_exec(
                    CacheType.Image,
                    lambda: self.core.get_image(style, size=size),
                )
            else:
                image = self.core.get_image(style, size=size)

            target.blit(image, (0, 0))
            if call.radius_support:
                radius = self.core.normalize_radius(style.border_radius, relative=True)
                if any(r > 0 for r in radius):
                    transform_into_rounded_rect(target.native, radius, None)

        elif call.radius_support:
            radius = self.core.normalize_radius(style.border_radius, relative=True)
            if all(r == 0 for r in radius):
                target.fill(color)
            else:
                transform_into_rounded_rect(target.native, radius, color)

        else:
            target.fill(color)

        if not direct_draw:
            surface.blit(target, pos_xy)

    @override
    def _arrange_text(
        self,
        call: DrawTextCall,
        pos: Annotations.vec2_like_v | None = None,
    ) -> tuple[list[str], NvVector2, NvVector2]:
        cache = call.cache
        style = call.style
        text = call.text
        size = call.size
        max_size = call.max_size
        max_size = max_size or size
        max_size = max_size.xy
        max_size.x = min(max_size.x, size.x)
        max_size.y = min(max_size.y, size.y)

        font, font_size = self.core.get_font(
            style=style, cache=cache, relative=True, size=call.font_size, container_size=call.size
        )

        if call.unlimited_x:
            text_size = self.core.measure_text(text, font=font, font_size=font_size)
            text_lines = [text]
        else:
            line_height_px = round(font_size * call.line_height)
            if call.words_indent:
                text_to_wrap = text.strip().split(" ")
                separator = " "
            else:
                text_to_wrap = list(text)
                separator = ""

            text_lines = self.core.wrap_text(
                text_to_wrap,
                separator=separator,
                font_size=font_size,
                font=font,
                max_width=max_size.x,
            )

            if not call.unlimited_y:
                y_cropped = False
                while len(text_lines) * line_height_px > max_size.y:
                    text_lines.pop()
                    y_cropped = True

                if y_cropped and len(text_lines) > 0:
                    text_lines[-1] = text_lines[-1][:-3] + "..."

            text_sizes = [
                self.core.measure_text(line, font=font, font_size=font_size)
                for line in text_lines
            ]
            text_size_y = len(text_lines) * line_height_px
            if text_sizes:
                text_size = NvVector2.from_xy(
                    max(text_sizes, key=lambda s: s.x).x, text_size_y
                )
            else:
                text_size = NvVector2()

        container_pos = pos or call.pos or (0, 0)
        result_pos = self.core.align_inner_rect(
            (container_pos[0], container_pos[1], size.x, size.y),
            text_size,
            style=style,
            strict_size=False,
        )
        return text_lines, result_pos, text_size

    @override
    def _text_draw(
        self,
        text_lines: list[str],
        surface: NvSurface,
        call: DrawTextCall,
        pos: NvVector2 | None = None,
    ):
        cache = call.cache
        style = call.style
        pos = NvVector2(pos or call.pos or NvVector2(0, 0))

        font, font_size = self.core.get_font(
            style=style, cache=cache, relative=True, size=call.font_size, container_size=call.size
        )
        line_height_px = round(font_size * call.line_height)
        half_leading = (line_height_px - font_size) / 2
        color = self.core.normalize_color(call.color or Color.White)

        widths = [
            self.core.measure_text(line, font=font, font_size=font_size).x
            for line in text_lines
        ]
        block_w = math.ceil(max(widths, default=0))

        for i, (line, w) in enumerate(zip(text_lines, widths)):
            if not line:
                continue
            dx, dy = self.core.align_text_line(
                block_w,
                w,
                i,
                line_height_px=line_height_px,
                half_leading=half_leading,
                style=style,
            )
            dy -= half_leading
            coordinates = NvVector2.from_xy(round(pos.x + dx), round(pos.y + dy))
            font.render(line, surface_like=surface, pos=coordinates, color=color)

    @override
    def _borders_draw(
        self,
        surface: NvSurface,
        call: DrawBordersCall,
    ):
        color = self.core.normalize_color(call.color or Color.White)
        style = call.style
        pos = call.pos or (0, 0)
        pos_xy = (int(pos[0]), int(pos[1]))
        relm = self.core.get_relm()
        border_width = style.border_width * relm
        width = max(1, round(border_width)) if border_width > 0 else 0
        radius = self.core.normalize_radius(style.border_radius, relative=True, relm=relm)

        subject = call.original_surface if call.original_surface is not None else surface

        if subject is surface:
            if width <= 0:
                if any(r > 0 for r in radius):
                    transform_into_rounded_rect(surface.native, radius, None)
            else:
                transform_into_outlined_rounded_rect(
                    surface.native,
                    radius,
                    width,
                    color,
                    background_color=None,
                )
        else:
            subj = subject.copy()
            if width <= 0:
                if any(r > 0 for r in radius):
                    transform_into_rounded_rect(subj.native, radius, None)
            else:
                transform_into_outlined_rounded_rect(
                    subj.native,
                    radius,
                    width,
                    color,
                    background_color=None,
                )
            surface.blit(subj, pos_xy)

    @override
    def _add_effects(
        self,
        call: DrawEffectsCall,
        effect_texture: Any,
        gradient: ClickGradient,
        surface: Any,
    ):
        raise NotImplementedError("pygame renderer does not support effects")
