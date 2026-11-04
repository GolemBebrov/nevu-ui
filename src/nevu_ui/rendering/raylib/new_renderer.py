from __future__ import annotations
import math
from typing import Any, override

from nevu_ui.fast.nvsurface.nvsurface import NvSurface
from nevu_ui.presentation.style import Style, default_style
import nevu_ui.core.modules as md
from nevu_ui.core.annotations import Annotations
from nevu_ui.core.enums import CacheType
from nevu_ui.core.state import nevu_state
from nevu_ui.fast.nvvector2 import NvVector2
from nevu_ui.fast.raylib.nevu_raylib import begin_blend_mode, end_blend_mode
from nevu_ui.presentation.color.color import Color
from nevu_ui.rendering.base_renderer import (
    BaseRenderer,
    DrawBaseCall,
    DrawBordersCall,
    DrawEffectsCall,
    DrawTextCall,
    _BaseCoreNamespace,
)
from nevu_ui.rendering.raylib.gradient import ClickGradient

_text_blend_factors_set = False

def _ensure_text_blend_factors():
    global _text_blend_factors_set
    if not _text_blend_factors_set:
        md.rl.rl_set_blend_factors_separate(0x0302, 0x0303, 1, 0x0303, 0x8006, 0x8006)
        _text_blend_factors_set = True

class _RaylibCoreNamespace(_BaseCoreNamespace):
    @override
    def get_gradient(self, style: Style):
        if not style.gradient:
            raise ValueError("Gradient is not set in specified style.")
        return style.gradient

    @override
    def draw_line(
        self,
        surface: NvSurface,
        pos_from: Annotations.vec2_like_v,
        pos_to: Annotations.vec2_like_v,
        *,
        style: Style = default_style,
        color: Annotations.rgb_like_color = Color.White,
        radius: Annotations.rad_like | None = None,
        width: float | None = None,

        relative: bool = False,
        relm: float | None = None,

        normalize_color: bool = True
    ) -> None:
        border_width = width or style.border_width
        radius = radius or style.border_radius

        if relative:
            relm = relm or self.get_relm()
            border_width *= relm
            normalized_radius = self.normalize_radius(radius, relative=relative, relm=relm)
        else:
            normalized_radius = self.normalize_radius(radius)
        color = self.normalize_color(color) if normalize_color else color

        renderer = nevu_state.window.renderer
        assert nevu_state.window.is_raylib(renderer)

        with surface:
            renderer.draw_sdf_line(
                pos_from,
                pos_to,
                border_width,
                normalized_radius,
                color,
                (surface.width, surface.height),
            )

    #@override
    #def create_surface(
    #    self,
    #    size: Annotations.vec2_like_v,
    #    *,
    #    clear_color: Annotations.rgb_like_color | None = Color.Blank,
    #    normalize_color: bool = True,
    #) -> SurfaceLike:
    #    texture = NvRenderTexture(NvVector2(size))
    #    if clear_color is not None:
    #        clear_color = self.normalize_color(clear_color) if normalize_color else clear_color
    #        texture.clear(clear_color)
    #    assert SurfaceLike.as_type(texture)
    #    return texture

    @override
    def draw_rect(
        self,
        surface: NvSurface,
        pos: Annotations.vec2_like_v,
        size: Annotations.vec2_like_v,
        *,
        color: Annotations.rgb_like_color = Color.White,
        style: Style = default_style,
        glassy: bool = False,
    ):
        Annotations.window_check()

        w, h = float(size[0]), float(size[1])
        if w <= 0.0 or h <= 0.0:
            return

        x, y = float(pos[0]), float(pos[1])
        radius = self.normalize_radius(style.border_radius, relative=True)
        color = self.normalize_color(color)

        with surface:
            if all(r == 0 for r in radius):
                md.rl.draw_rectangle(int(x), int(y), int(w), int(h), color)
                return

            renderer = nevu_state.window.renderer
            assert nevu_state.window.is_raylib(renderer)

            renderer.draw_sdf_rect(
                (x, y), (w, h), radius, color, glassy=glassy
            )
    @override
    def get_image(
        self,
        style: Style,
        *,
        size: Annotations.vec2_like_v | None = None
    ):
        image_path = style.background_image

        if image_path is None:
            raise ValueError("Image path not provided in specified style.")

        image = md.rl.load_image(image_path)
        if size:
            md.rl.image_resize(image, int(size[0]), int(size[1]))
        texture = md.rl.load_texture_from_image(image)
        md.rl.unload_image(image)
        return texture

_gradient_base_color = Color.White

class RaylibRenderer(BaseRenderer):
    @override
    def _get_core_namespace(self):
        return _RaylibCoreNamespace()

    @override
    def _base_draw( #type: ignore
        self,
        surface: NvSurface,
        call: DrawBaseCall,
    ):
        blend_mode = md.rl.BlendMode

        cache = call.cache
        style = call.style
        size = call.size
        color = call.color
        color = self.core.normalize_color(color)

        cache_available = cache is not None
        renderer = nevu_state.window.renderer
        assert nevu_state.window.is_raylib(renderer)

        if call.gradient_support and style.gradient:
            if cache_available:
                gradient = cache.get_or_exec(
                    CacheType.Gradient,
                    lambda: self.core.get_gradient(style = style).generate_texture(
                        int(size[0]), int(size[1])
                    ),
                )
            else:
                gradient = self.core.get_gradient(style = style).generate_texture(
                    int(size[0]), int(size[1])
                )

            radius = self.core.normalize_radius(style.border_radius, relative=True)

            begin_blend_mode(blend_mode.BLEND_ALPHA_PREMULTIPLY)
            with surface:
                if call.radius_support:
                    renderer.fast_blit_sdf_vec(
                        gradient.native.texture, (0, 0), radii = radius, flip=True, color = _gradient_base_color
                    )
                else:
                    renderer.fast_blit(gradient.native.texture, (0, 0), color = _gradient_base_color)

        elif call.image_support and style.background_image:
            if cache_available:
                image = cache.get_or_exec(
                    CacheType.Image,
                    lambda: self.core.get_image(style, size = size),
                )
            else:
                image = self.core.get_image(style, size = size)

            radius = self.core.normalize_radius(style.border_radius, relative=True)

            begin_blend_mode(blend_mode.BLEND_ALPHA)
            with surface:
                if call.radius_support:
                    renderer.fast_blit_sdf_vec(
                        image, (0, 0), radii = radius, color = _gradient_base_color
                    )
                else:
                    surface.blit(image, (0, 0))

        elif call.radius_support:
            radius = self.core.normalize_radius(style.border_radius, relative=True)

            begin_blend_mode(blend_mode.BLEND_ALPHA_PREMULTIPLY)
            self.core.draw_rect(surface, NvVector2(), size, color = color, style = style, glassy=call.glassy) # type: ignore

        else:
            begin_blend_mode(blend_mode.BLEND_ALPHA_PREMULTIPLY)
            with surface:
                surface.clear(color)

        end_blend_mode()

    def _arrange_text(
        self,
        call: DrawTextCall,
        pos: Annotations.vec2_like_v | None = None,
    ) -> tuple[list[str], NvVector2, NvVector2]:
        cache = call.cache
        style = call.style
        relative = call.relative
        relm = call.relm
        text = call.text
        size = call.size
        max_size = call.max_size
        max_size = max_size or size
        max_size = max_size.xy
        max_size.x = min(max_size.x, size.x)
        max_size.y = min(max_size.y, size.y)

        font, font_size = self.core.get_font(style=style, cache=cache, relative=relative, relm=relm, size=call.font_size, container_size=call.size)

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
                text_to_wrap, separator=separator, font_size=font_size, font=font, max_width=max_size.x
            )

            if not call.unlimited_y:
                y_cropped = False
                while len(text_lines) * line_height_px > max_size.y:
                    text_lines.pop()
                    y_cropped = True

                if y_cropped and len(text_lines) > 0:
                    text_lines[-1] = text_lines[-1][:-3] + "..."

            text_sizes = [self.core.measure_text(line, font=font, font_size=font_size) for line in text_lines]
            text_size_y = len(text_lines) * line_height_px
            if text_sizes:
                text_size = NvVector2.from_xy(max(text_sizes, key=lambda s: s.x).x, text_size_y)
            else:
                text_size = NvVector2()

        container_pos = pos or call.pos or (0, 0)
        result_pos = self.core.align_inner_rect(
            (container_pos[0], container_pos[1], size.x, size.y),
            text_size,
            style = style,
            strict_size=False
        )
        return text_lines, result_pos, text_size

    @override
    def _text_draw(  # type: ignore
        self,
        text_lines: list[str],
        surface: NvSurface,
        call: DrawTextCall,
        pos: NvVector2 | None = None,
    ):
        cache = call.cache
        style = call.style
        relm = call.relm
        relative = call.relative
        pos = NvVector2(pos or call.pos or NvVector2(0, 0))

        font, font_size = self.core.get_font(style=style, cache=cache, relative=relative, relm=relm, size=call.font_size, container_size=call.size)
        line_height_px = round(font_size * call.line_height)
        half_leading = (line_height_px - font_size) / 2
        color = self.core.normalize_color(call.color or Color.White)

        widths = [
            self.core.measure_text(line, font=font, font_size=font_size).x
            for line in text_lines
        ]
        block_w = math.ceil(max(widths, default=0))

        rl = md.rl
        _ensure_text_blend_factors()

        with surface:
            begin_blend_mode(rl.BlendMode.BLEND_CUSTOM_SEPARATE)
            for i, (line, w) in enumerate(zip(text_lines, widths)):
                dx, dy = self.core.align_text_line(block_w, w, i, line_height_px=line_height_px, half_leading=half_leading)
                coordinates = (round(pos.x + dx), round(pos.y + dy))
                rl.draw_text_ex(font.native, line, coordinates, font_size, 0, color)
            end_blend_mode()

    def _borders_draw(  # type: ignore
        self,
        surface: NvSurface,
        call: DrawBordersCall,
    ):
        color = call.color or Color.White
        style = call.style
        pos = call.pos or (0, 0)
        pos = (pos[0], pos[1])
        relm = self.core.get_relm()
        width = style.border_width * relm
        radius = self.core.normalize_radius(style.border_radius, relative=True, relm=relm)
        window = nevu_state.window
        assert window is not None
        window_renderer = window.renderer
        assert window.is_raylib(window_renderer)

        begin_blend_mode(md.rl.BlendMode.BLEND_ALPHA_PREMULTIPLY)
        with surface:
            if width <= 0:
                window_renderer.fast_blit_sdf_vec(call.original_surface.native.texture, pos, radius, flip=True)
            else:
                if call.glassy:
                    fast_blit_vec = window_renderer.fast_blit_glassy_borders_vec
                else:
                    fast_blit_vec = window_renderer.fast_blit_borders_vec
                fast_blit_vec(
                    call.original_surface.native.texture,
                    pos,
                    radius,
                    color,
                    thickness=width,
                    flip=True,
                )
        end_blend_mode()

    @override
    def _add_effects(
        self,
        call: DrawEffectsCall,
        effect_texture: NvSurface,
        gradient: ClickGradient,
        surface: NvSurface,
    ):
        display = nevu_state.window.renderer
        assert nevu_state.window.is_raylib(display)
        begin_blend_mode(md.rl.BlendMode.BLEND_ADDITIVE)
        pos = call.pos or (0, 0)
        radius = call.radius if call.radius is not None else 0
        radius = self.core.normalize_radius(radius, relative=True)
        with effect_texture:
            effect_texture.clear(Color.Blank)
            gradient.draw(0, 0, effect_texture.width, effect_texture.height)
        with surface:
            display.fast_blit_sdf_vec(effect_texture.native.texture, (pos[0], pos[1]), radius)
        end_blend_mode()
