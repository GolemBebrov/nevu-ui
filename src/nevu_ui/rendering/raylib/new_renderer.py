from __future__ import annotations
import math
from typing import Any, override

from nevu_ui.fast.nevucache import Cache
from nevu_ui.presentation.style import Style, default_style
import nevu_ui.core.modules as md
from nevu_ui.core.annotations import Annotations
from nevu_ui.core.classes import SurfaceLike
from nevu_ui.core.enums import Align, CacheType
from nevu_ui.core.state import nevu_state
from nevu_ui.fast.nvrendertex import NvRenderTexture
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


class _RaylibCoreNamespace(_BaseCoreNamespace):
    @override
    def get_gradient(self, style: Style):
        if not style.gradient:
            raise ValueError("Gradient is not set in specified style.")
        return style.gradient

    @override
    def draw_line(
        self,
        surface_like: SurfaceLike,
        pos_from: Annotations.dest_like_v,
        pos_to: Annotations.dest_like_v,
        *,
        width: float | None = None,
        radius: Annotations.rad_like | None = None,
        relative: bool = False,
        relm: float | None  = None,
        color: Annotations.rgb_like_color = Color.White,
        style: Style = default_style,
    ) -> None:
        assert Annotations.raylib_surface_like_check(surface_like)
        relm = relm or self.get_relm()

        border_width = width or style.border_width
        if relative:
            border_width *= relm
        radius = radius or style.border_radius
        normalized_radius = self.normalize_radius(radius, relative=relative, relm=relm)
        color = self.normalize_color(color)

        display = nevu_state.window.renderer
        assert nevu_state.window.is_raylib(display)

        with surface_like:
            display.draw_sdf_line(
                pos_from,
                pos_to,
                border_width,
                normalized_radius,
                color,
                (surface_like.width, surface_like.height),
            )

    @override
    def create_clear(self, size: Annotations.dest_like | NvVector2) -> SurfaceLike:
        texture = NvRenderTexture(NvVector2(size))
        texture.clear(Color.Blank)
        assert SurfaceLike.as_type(texture)
        return texture

    @override
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

        font_name = path or style.font_name
        font_size = size if size is not None else round(self.get_font_size(style, relative=relative, relm=relm))

        def _load_font():
            codepoints = list(range(32, 127)) + list(range(1024, 1104)) + [1025, 1105]
            glyph_count = len(codepoints)
            rl = md.rl
            ffi = rl.ffi
            c_array = ffi.new("int[]", codepoints)
            c_ptr = ffi.cast("int *", c_array)
            font = rl.load_font_ex(font_name, font_size, c_ptr, glyph_count)
            if font.glyphCount == 0:
                raise ValueError(f"Font {font_name} not found")
            return font, font_size

        if cache:
            return cache.get_or_exec(CacheType.RlFont, _load_font)
        return _load_font()

    @override
    def draw_rect(
        self,
        surface_like: SurfaceLike,
        pos: Annotations.dest_like_v,
        size: Annotations.dest_like_v,
        *,
        color: Annotations.rgb_like_color = Color.White,
        style: Style = default_style,
        glassy: bool = False,
    ):
        assert Annotations.raylib_surface_like_check(surface_like)
        Annotations.window_check()

        radius = self.normalize_radius(style.border_radius, relative = True)
        color = self.normalize_color(color)

        if all(item == 0 for item in radius):
            with surface_like:
                md.rl.draw_rectangle(int(pos[0]), int(pos[1]), int(size[0]), int(size[1]), color)
            return

        display = nevu_state.window.renderer

        rect_texture = NvRenderTexture(NvVector2(size))
        rect_texture.clear(color)
        pos = (pos[0], pos[1])

        assert nevu_state.window.is_raylib(display)
        with surface_like:
            if glassy:
                display.fast_blit_glassy_sdf_vec(rect_texture.texture, pos, radius)
            else:
                display.fast_blit_sdf_vec(rect_texture.texture, pos, radius)

    @override
    def get_image(
        self,
        style: Style,
        *,
        size: Annotations.dest_like_v | None = None
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

    @override
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
    ) -> NvVector2:
        if font is None:
            font, font_size = self.get_font(style = style, cache=cache, relative=relative, relm=relm, size=font_size)
        if font_size is None:
            font_size = round(self.get_font_size(style))
        result = md.rl.measure_text_ex(font, text, font_size, 0)
        return NvVector2.from_xy(result.x, result.y)


_gradient_base_color = Color.White
_gradient_hover_color = None
_gradient_click_color = None

def _adjust_color_brightness(color: Annotations.rgba_color, offset: int) -> Annotations.rgba_color:
    r, g, b, a = color
    return max(0, min(255, r + offset)), max(0, min(255, g + offset)), max(0, min(255, b + offset)), a

#class _RaylibSpecifiedDraw(_BaseSpecifiedDraw):
#    def adjust_brightness(self, color: tuple, offset: int) -> tuple:
#        return tuple(max(0, min(255, c + offset)) for c in color[:3]) + (color[3],)
#
#    def check_root_color_transition(self):
#        root = self.root
#        if not root.inline:
#            new_color_pretendent = self._renderer.core.get_color_on_hover(
#                root.subtheme_border if root.inverted else root.subtheme_content
#            )
#            old_color = root._bg_color_before
#            if old_color is None:
#                root._bg_color_before = new_color_pretendent  # type: ignore
#            elif old_color != new_color_pretendent:
#                root._set_next_bg_color_anim(new_color_pretendent)


class RaylibRenderer(BaseRenderer):
    @override
    def _get_core_namespace(self):
        return _RaylibCoreNamespace()

    @override
    def _base_draw( #type: ignore
        self,
        texture: NvRenderTexture,
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
            with texture:
                if call.radius_support:
                    renderer.fast_blit_sdf_vec(
                        gradient.texture, (0, 0), radii = radius, color = _gradient_base_color
                    )
                else:
                    renderer.fast_blit(gradient.texture, (0, 0), color = _gradient_base_color)

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
            with texture:
                if call.radius_support:
                    renderer.fast_blit_sdf_vec(
                        image, (0, 0), radii = radius, color = _gradient_base_color
                    )
                else:
                    texture.fast_blit_texture(image, (0, 0), flip=False, color=_gradient_base_color)

        elif call.radius_support:
            radius = self.core.normalize_radius(style.border_radius, relative=True)

            begin_blend_mode(blend_mode.BLEND_ALPHA_PREMULTIPLY)
            with texture:
                self.core.draw_rect(texture, NvVector2(), size, color = color, style = style, glassy=call.glassy)

        else:
            begin_blend_mode(blend_mode.BLEND_ALPHA_PREMULTIPLY)
            with texture:
                texture.clear(color)

        end_blend_mode()

    def _arrange_text(
        self,
        call: DrawTextCall,
        pos: Annotations.dest_like_v | None = None,
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

        font, font_size = self.core.get_font(style=style, cache=cache, relative=relative, relm=relm, size=call.font_size)

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
        texture: NvRenderTexture,
        call: DrawTextCall,
        pos: NvVector2 | None = None,
    ):
        cache = call.cache
        style = call.style
        relm = call.relm
        relative = call.relative
        pos = NvVector2(pos or call.pos or NvVector2(0, 0))

        font, font_size = self.core.get_font(style=style, cache=cache, relative=relative, relm=relm, size=call.font_size)
        line_height_px = round(font_size * call.line_height)
        half_leading = (line_height_px - font_size) / 2
        color = self.core.normalize_color(call.color or Color.White)

        widths = [
            self.core.measure_text(line, font=font, font_size=font_size).x
            for line in text_lines
        ]
        block_w = math.ceil(max(widths, default=0))

        rl = md.rl
        rl.rl_set_blend_factors_separate(0x0302, 0x0303, 1, 0x0303, 0x8006, 0x8006)

        with texture:
            begin_blend_mode(rl.BlendMode.BLEND_CUSTOM_SEPARATE)
            for i, (line, w) in enumerate(zip(text_lines, widths)):
                dx, dy = self.core.align_text_line(block_w, w, i, line_height_px=line_height_px, half_leading=half_leading)
                coordinates = (round(pos.x + dx), round(pos.y + dy))
                rl.draw_text_ex(font, line, coordinates, font_size, 0, color)
            end_blend_mode()

    def _borders_draw(  # type: ignore
        self,
        texture: NvRenderTexture,
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
        with texture:
            if width <= 0:
                window_renderer.fast_blit_sdf_vec(call.original_surface.texture, pos, radius, flip=True)
            else:
                if call.glassy:
                    fast_blit_vec = window_renderer.fast_blit_glassy_borders_vec
                else:
                    fast_blit_vec = window_renderer.fast_blit_borders_vec
                fast_blit_vec(
                    call.original_surface.texture,
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
        effect_texture: NvRenderTexture,
        gradient: ClickGradient,
        texture: NvRenderTexture,
    ):
        display = nevu_state.window.renderer
        assert nevu_state.window.is_raylib(display)
        begin_blend_mode(md.rl.BlendMode.BLEND_ADDITIVE)
        pos = call.pos or (0, 0)
        radius = call.radius if call.radius is not None else 0
        radius = self.core.normalize_radius(radius, relative=True)
        with effect_texture:
            effect_texture.fast_clear(Color.Blank)
            gradient.draw(0, 0, effect_texture.width, effect_texture.height)
        with texture:
            display.fast_blit_sdf_vec(effect_texture.texture, (pos[0], pos[1]), radius)
        end_blend_mode()
