from __future__ import annotations

import math
from typing import TYPE_CHECKING, Any, override

if TYPE_CHECKING:
    from nevu_ui.presentation.style import Style
    from nevu_ui.rendering.pygame.gradient import GradientPygame
    from nevu_ui.rendering.raylib.gradient import ClickGradient

import nevu_ui.core.modules as md
from nevu_ui.core.annotations import Annotations
from nevu_ui.core.classes import SurfaceLike
from nevu_ui.core.enums import CacheType
from nevu_ui.fast.nevucache import Cache
from nevu_ui.fast.nvvector2 import NvVector2
from nevu_ui.fast.shapes import (
    transform_into_outlined_rounded_rect,
    transform_into_rounded_rect,
)
from nevu_ui.fast.shapes.fast_shapes import draw_sdf_line
from nevu_ui.presentation.color.color import Color
from nevu_ui.presentation.style import default_style
from nevu_ui.rendering.base_renderer import (
    BaseRenderer,
    DrawBaseCall,
    DrawBordersCall,
    DrawEffectsCall,
    DrawTextCall,
    _BaseCoreNamespace,
)


class _PygameCoreNamespace(_BaseCoreNamespace):
    @override
    def get_gradient(self, style: Style) -> Any:
        if not style.gradient:
            raise ValueError("Gradient is not set in specified style.")
        gr: GradientPygame = style.gradient
        return gr

    @override
    def get_font(
        self,
        *,
        style: Style = default_style,
        cache: Cache | None = None,
        relative: bool = False,
        relm: float | None = None,
        size: int | None = None,
        path: str | None = None,
    ) -> tuple[Any, int]:
        font_name = path or style.font_name
        font_size = (
            size
            if size is not None
            else round(self.get_font_size(style, relative=relative, relm=relm))
        )
        font_size = max(1, font_size)

        def _load_font():
            font = md.pygame.font.Font(font_name, font_size)
            return font, font_size

        if cache:
            cache_type = getattr(
                CacheType,
                "PygameFont",
                getattr(CacheType, "PgFont", getattr(CacheType, "Font", CacheType.RlFont)),
            )
            return cache.get_or_exec(cache_type, _load_font)
        return _load_font()

    @override
    def create_clear(self, size: Annotations.dest_like_v) -> SurfaceLike:
        w, h = int(size[0]), int(size[1])
        surf = md.pygame.Surface((w, h), flags=md.pygame.SRCALPHA, depth=32)
        try:
            surf = surf.convert_alpha()
        except Exception:
            pass
        surf.fill((0, 0, 0, 0))
        assert SurfaceLike.as_type(surf)
        return surf

    @override
    def draw_rect(
        self,
        surface_like: Any,
        pos: Annotations.dest_like_v,
        size: Annotations.dest_like_v,
        *,
        color: Annotations.rgb_like_color = Color.White,
        style: Style = default_style,
    ) -> None:
        assert isinstance(surface_like, md.pygame.Surface), (
            "surface_like must be a pygame Surface"
        )
        radius = self.normalize_radius(style.border_radius, relative=True)
        color = self.normalize_color(color)
        x, y = int(pos[0]), int(pos[1])
        w, h = int(size[0]), int(size[1])

        if all(r == 0 for r in radius):
            md.pygame.draw.rect(surface_like, color, (x, y, w, h))
            return

        # Если прямоугольник занимает всю поверхность с позиции (0, 0)
        if x == 0 and y == 0 and (surface_like.get_width(), surface_like.get_height()) == (w, h):
            transform_into_rounded_rect(surface_like, radius, color)
        else:
            temp = self.create_clear((w, h))
            transform_into_rounded_rect(temp, radius, color)
            surface_like.blit(temp, (x, y))

    @override
    def draw_line(
        self,
        surface_like: Any,
        pos_from: Annotations.dest_like_v,
        pos_to: Annotations.dest_like_v,
        *,
        width: float | None = None,
        radius: Annotations.rad_like | None = None,
        relative: bool = False,
        relm: float | None = None,
        color: Annotations.rgb_like_color = Color.White,
        style: Style = default_style,
    ) -> None:
        assert isinstance(surface_like, md.pygame.Surface), (
            "surface_like must be a pygame Surface"
        )
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
        draw_sdf_line(surface_like, pos_from, pos_to, w, r, color)

    @override
    def get_image(
        self,
        style: Style,
        *,
        size: Annotations.dest_like_v | None = None,
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

    @override
    def measure_text(
        self,
        text: str,
        *,
        style: Style = default_style,
        cache: Cache | None = None,
        relative: bool = False,
        relm: float | None = None,
        font: Any = None,
        font_size: int | None = None,
    ) -> NvVector2:
        if font is None:
            font, font_size = self.get_font(
                style=style, cache=cache, relative=relative, relm=relm, size=font_size
            )
        assert isinstance(font, md.pygame.font.Font), "font must be a pygame font"

        lines = text.split("\n")
        if len(lines) > 1:
            max_w = max((font.size(line)[0] for line in lines), default=0)
            total_h = len(lines) * font.get_linesize()
            return NvVector2.from_xy(max_w, total_h)

        result = font.size(text)
        return NvVector2.from_xy(result[0], result[1])


class PygameRenderer(BaseRenderer):
    @override
    def _get_core_namespace(self) -> _BaseCoreNamespace:
        return _PygameCoreNamespace()

    @override
    def _base_draw(
        self,
        texture: SurfaceLike,
        call: DrawBaseCall,
    ):
        assert isinstance(texture, md.pygame.Surface), "texture must be a pygame Surface"

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
            and texture.get_width() == w
            and texture.get_height() == h
        )

        target = texture if direct_draw else self.core.create_clear(size)

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
                    transform_into_rounded_rect(target, radius, None)

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
                    transform_into_rounded_rect(target, radius, None)

        elif call.radius_support:
            radius = self.core.normalize_radius(style.border_radius, relative=True)
            if all(r == 0 for r in radius):
                target.fill(color)
            else:
                transform_into_rounded_rect(target, radius, color)

        else:
            target.fill(color)

        if not direct_draw:
            texture.blit(target, pos_xy)

    @override
    def _arrange_text(
        self,
        call: DrawTextCall,
        pos: Annotations.dest_like_v | None = None,
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
            style=style, cache=cache, relative=True, size=call.font_size
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
        texture: SurfaceLike,
        call: DrawTextCall,
        pos: NvVector2 | None = None,
    ):
        assert isinstance(texture, md.pygame.Surface), "texture must be a pygame Surface"
        cache = call.cache
        style = call.style
        pos = NvVector2(pos or call.pos or NvVector2(0, 0))

        font, font_size = self.core.get_font(
            style=style, cache=cache, relative=True, size=call.font_size
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
            coordinates = (round(pos.x + dx), round(pos.y + dy))
            rendered_texture = font.render(line, True, color)
            texture.blit(rendered_texture, coordinates)

    @override
    def _borders_draw(
        self,
        texture: SurfaceLike,
        call: DrawBordersCall,
    ):
        assert isinstance(texture, md.pygame.Surface), "texture must be a pygame Surface"

        color = self.core.normalize_color(call.color or Color.White)
        style = call.style
        pos = call.pos or (0, 0)
        pos_xy = (int(pos[0]), int(pos[1]))
        relm = self.core.get_relm()
        border_width = style.border_width * relm
        width = max(1, round(border_width)) if border_width > 0 else 0
        radius = self.core.normalize_radius(style.border_radius, relative=True, relm=relm)

        subject = call.original_surface if call.original_surface is not None else texture
        assert isinstance(subject, md.pygame.Surface), "subject must be a pygame Surface"

        if subject is texture:
            if width <= 0:
                if any(r > 0 for r in radius):
                    transform_into_rounded_rect(texture, radius, None)
            else:
                transform_into_outlined_rounded_rect(
                    texture,
                    radius,
                    width,
                    color,
                    background_color=None,
                )
        else:
            subj = subject.copy()
            if width <= 0:
                if any(r > 0 for r in radius):
                    transform_into_rounded_rect(subj, radius, None)
            else:
                transform_into_outlined_rounded_rect(
                    subj,
                    radius,
                    width,
                    color,
                    background_color=None,
                )
            texture.blit(subj, pos_xy)

    @override
    def _add_effects(
        self,
        call: DrawEffectsCall,
        effect_texture: Any,
        gradient: ClickGradient,
        texture: Any,
    ):
        raise NotImplementedError("pygame renderer does not support effects")
