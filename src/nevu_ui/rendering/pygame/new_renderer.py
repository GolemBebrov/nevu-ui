from __future__ import annotations

from typing_extensions import TYPE_CHECKING, Any, override

if TYPE_CHECKING:
    from nevu_ui.presentation.style import Style
    from nevu_ui.rendering.uni_gradient import GradientPygame

import nevu_ui.core.modules as md
from nevu_ui.core.annotations import Annotations
from nevu_ui.core.enums import CacheType, RenderReturnType
from nevu_ui.fast.nvvector2 import NvVector2
from nevu_ui.fast.shapes import (
    transform_into_outlined_rounded_rect,
    transform_into_rounded_rect,
)
from nevu_ui.presentation.color.color import Color, is_rgba
from nevu_ui.rendering.base_renderer import (
    BaseRenderer,
    DrawBaseCall,
    DrawBordersCall,
    DrawEffectsCall,
    DrawTextCall,
    _BaseCoreNamespace,
    _BaseSpecifiedDraw,
)


class _PygameCoreNamespace(_BaseCoreNamespace):
    @override
    def get_gradient(self, style: Style | None = None):
        style = style or self.style
        if not style.gradient:
            raise ValueError("Gradient not set in style")
        gr: GradientPygame = style.gradient
        return gr

    @override
    def create_clear(self, size: Annotations.dest_like | NvVector2, **kwargs):
        flags = kwargs.get("flags", 0)
        surf = md.pygame.Surface(
            size, flags=flags | md.pygame.SRCALPHA, depth=32
        ).convert_alpha()
        surf.fill((0, 0, 0, 0))
        return surf

    @override
    def get_font_size(self, override_size=None) -> int | float:
        return round(self.root.relm(override_size or self.style.font_size))

    @override
    def get_font(self, name: str | None = None, size=None):
        font_size = round(self.get_font_size(size))
        font_name = name or self.style.font_name
        return (
            md.pygame.font.SysFont(font_name, font_size)
            if font_name == "Arial" or font_name is None
            else md.pygame.font.Font(font_name, font_size)
        )

    @override
    def draw_rect(
        self,
        subject,
        pos: Annotations.dest_like | NvVector2,
        size: Annotations.dest_like | NvVector2,
        color: Annotations.rgba_color = Color.White,
        radii: Annotations.rect_like | int = 0,
    ):
        assert isinstance(subject, md.pygame.Surface), (
            "subject must be a pygame Surface"
        )
        if radii == 0:
            md.pygame.draw.rect(subject, color, (0, 0, int(size[0]), int(size[1])))
            return
        if isinstance(radii, int | float):
            radii = (radii, radii, radii, radii)
        transform_into_rounded_rect(subject, radii, color)

    @override
    def load_image(
        self, path: str, size: Annotations.dest_like | NvVector2 | None = None
    ):
        img = md.pygame.image.load(path)
        img = img.convert_alpha()
        if size:
            img = md.pygame.transform.smoothscale(img, (int(size[0]), int(size[1])))
        return img

    @override
    def measure_text(self, font: Any, text: str, font_size: float) -> NvVector2:
        assert isinstance(font, md.pygame.font.Font), "font must be a pygame font"
        lines = text.split("\n")
        if len(lines) > 1:
            max_w = max(font.size(line)[0] for line in lines)
            total_h = len(lines) * font.get_linesize()
            return NvVector2.from_xy(max_w, total_h)

        result = font.size(text)
        return NvVector2.from_xy(result[0], result[1])


class _PygameSpecifiedDraw(_BaseSpecifiedDraw):
    def adjust_brightness(self, color: tuple, offset: int) -> tuple:
        return tuple(max(0, min(255, c + offset)) for c in color[:3]) + (color[3],)


class PygameRenderer(BaseRenderer):
    @override
    def _get_core_namespace(self):
        return _PygameCoreNamespace(self)

    @override
    def _get_unsafe_namespace(self):
        return _PygameSpecifiedDraw(self)

    @override
    def _draw_base(self, call: DrawBaseCall):
        root = self.root
        size: NvVector2 = call.size if call.size is not None else root._csize
        standstill = call.standstill
        override_color = call.color
        cached = call.cached
        radii = call.radius if call.radius is not None else root.style.border_radius
        radii = self.core.normalize_radius_relative(radii)
        inline = call.inline
        return_type = call.return_type
        alt = root.inverted
        color = override_color or (
            root.subtheme_border if alt else root.subtheme_content
        )
        if not standstill:
            color = self.core.get_color_on_hover(color)

        def to_rgba_tuple(c):
            if c is None:
                return (0, 0, 0, 0)
            if hasattr(c, "to_tuple"):
                val = c.to_tuple()
            elif hasattr(c, "r") and hasattr(c, "g") and hasattr(c, "b"):
                val = (c.r, c.g, c.b, getattr(c, "a", 255))
            else:
                val = c
            try:
                val = list(val)
            except TypeError:
                return (0, 0, 0, 0)
            if len(val) == 3:
                val.append(255)
            return tuple(int(x) for x in val)

        def _draw_on_texture(surface):
            assert isinstance(surface, md.pygame.Surface), (
                "surface must be a pygame Surface"
            )
            nonlocal color
            gradient_support = call.gradient_support
            image_support = call.image_support
            easy_background = call.easy_background

            if gradient_support and root.style.gradient:
                gradient = root.cache.get_or_exec(
                    CacheType.Scaled_Gradient,
                    lambda: self.core.get_gradient().apply_gradient(
                        surface.width, surface.height
                    ),
                )
                surface.blit(gradient, (0, 0))

            elif image_support and root.style.bg_image:
                image = root.cache.get_or_exec(
                    CacheType.Scaled_Image,
                    lambda: self.core.load_image(root.style.bg_image, size),
                )
                surface.blit(image, (0, 0))
            else:
                if not standstill:
                    if not root.inline:
                        new_color_pretendent = self.core.get_color_on_hover(
                            root.subtheme_border
                            if root.get_param_strict("inverted").value
                            else root.subtheme_content
                        )

                        new_color_tuple = to_rgba_tuple(new_color_pretendent)
                        old_color_tuple = (
                            to_rgba_tuple(root._old_color)
                            if root._old_color is not None
                            else None
                        )

                        if old_color_tuple is None:
                            root._old_color = new_color_pretendent
                        elif old_color_tuple != new_color_tuple:
                            root._set_new_color(new_color_pretendent)

                    if color_manager := root._color_anim_manager:
                        anim_color = color_manager.get_animation_value("main")
                    else:
                        anim_color = None

                    color = anim_color or color

                color = to_rgba_tuple(color)

                if easy_background:
                    surface.fill(color)
                else:
                    self.core.draw_rect(surface, (0, 0), size, color, radii)  # type: ignore

        match return_type:
            case RenderReturnType.Null:
                assert isinstance(root.surface, md.pygame.Surface), (
                    "root.surface must be a pygame Surface"
                )
                nv_texture = root.surface
                _draw_on_texture(nv_texture)
            case RenderReturnType.Outside:
                return size, color, radii
            case RenderReturnType.Raw:
                return size, radii, override_color, cached, standstill
            case RenderReturnType.Modify:
                texture = call.modify_object
                assert texture, "Modify return type selected but no object provided"
                _draw_on_texture(texture)
            case RenderReturnType.CreateNew:
                texture = self.core.create_clear(size)
                _draw_on_texture(texture)
                return texture
            case _:
                raise ValueError(f"Invalid return type: {return_type}")

    @override
    def _draw_text(self, call: DrawTextCall):
        root = self.root
        text: str = call.text
        style: Style = call.style if call.style is not None else root.style
        font_size: float | None = call.font_size
        font_size = font_size or root.style.font_size
        size: NvVector2 = call.size if call.size is not None else root._csize
        unlimited_y = call.unlimited_y
        words_indent = call.words_indent
        continuous = call.continuous
        max_size = call.max_size if call.max_size is not None else size
        inline = call.inline
        spacing = 0
        cropped = False
        return_type = call.return_type
        color = call.color if call.color is not None else root.subtheme_font
        if len(color) == 3:
            color = (*color, 255)
        assert text is not None, "text must be provided"
        container_rect = (0, 0, 0, 0)
        baked_text = text
        text_dims = NvVector2.from_xy(0, 0)
        render_font = None

        def _arrange_text(override_size=None):
            nonlocal \
                font_size, \
                cropped, \
                container_rect, \
                baked_text, \
                text_dims, \
                render_font
            assert font_size
            render_font = self.core.get_font(size=font_size)
            assert isinstance(render_font, md.pygame.font.Font), (
                "font must be a pygame font"
            )
            font_size = font_size
            final_size = override_size or size
            final_max_size = max_size
            final_max_size.x = min(final_max_size.x, final_size.x)
            final_max_size.y = min(final_max_size.y, final_size.y)
            if not continuous:
                line_height = render_font.get_linesize()
                text_to_split = text.strip().split(" ") if words_indent else list(text)
                marg = " " if words_indent else ""
                text_lines = self.core.split_words(
                    text_to_split, render_font, font_size, final_max_size.x, marg=marg
                )
                if not unlimited_y:
                    while len(text_lines) * line_height > final_max_size.y:
                        text_lines.pop()
                        cropped = True
                baked_text = "\n".join(text_lines)
                if cropped:
                    baked_text = f"{baked_text[:-3]}..."
                text_dims = self.core.measure_text(render_font, baked_text, font_size)
                container_rect = (0, 0, final_size.x, final_size.y)
                container_rect = self.core.align_rect(
                    style.align_x,
                    style.align_y,
                    container_rect,
                    text_dims.x,
                    text_dims.y,
                )
            else:
                text_dims = self.core.measure_text(render_font, baked_text, font_size)

        def _create_text(surface, relative_size=False):
            assert render_font and font_size
            assert isinstance(render_font, md.pygame.font.Font), (
                "font must be a pygame font"
            )
            coordinates = (
                (0, 0) if relative_size else (container_rect[0], container_rect[1])
            )
            rendered_texture = render_font.render(baked_text, True, color)
            surface.blit(rendered_texture, coordinates)

        match return_type:
            case RenderReturnType.Null:
                assert isinstance(root.surface, md.pygame.Surface), (
                    "root.surface must be a pygame Surface"
                )
                surf = root.surface
                _arrange_text()
                _create_text(surf)
            case RenderReturnType.Outside:
                _arrange_text()
                return (
                    baked_text,
                    size,
                    font_size,
                    render_font,
                    spacing,
                    style,
                    cropped,
                    container_rect,
                    text_dims,
                )
            case RenderReturnType.Raw:
                return (
                    text,
                    size,
                    (call.style if call.style is not None else root.style),
                    font_size,
                    color,
                    spacing,
                )
            case RenderReturnType.Modify:
                surf = call.modify_object
                assert surf, "Modify return type selected but no object provided"
                _arrange_text()
                _create_text(surf)
                return container_rect, text_dims
            case RenderReturnType.CreateNew:
                _arrange_text(override_size=size)
                surf = self.core.create_clear(text_dims)
                _create_text(surf, True)
                return container_rect, surf
            case _:
                raise ValueError(f"Invalid return type: {return_type}")

    @override
    def _draw_effects(self, call: DrawEffectsCall):
        raise NotImplementedError("pygame renderer does not support effects")

    @override
    def _draw_borders(self, call: DrawBordersCall):
        root = self.root
        subject = call.subject
        border_width = (
            call.border_width
            if call.border_width is not None
            else root.style.border_width
        )
        radius = call.radius if call.radius is not None else root.style.border_radius
        radius = self.core.normalize_radius_relative(radius)
        override_color = (
            call.color
            if call.color is not None
            else (root.subtheme_content if root.inverted else root.subtheme_border)
        )
        override_bg_color = call.bg_color
        bg_color = override_bg_color or (
            root.subtheme_border if root.inverted else root.subtheme_content
        )
        if not override_bg_color:
            bg_color = self.core.get_color_on_hover(bg_color)
        no_borders = call.no_borders
        pos = (
            call.pos
            if call.pos is not None
            else (
                self.root.coordinates.to_tuple()
                if self.root.get_param_strict("inline").value
                else (0, 0)
            )
        )
        return_type = call.return_type
        assert isinstance(subject, md.pygame.Surface), (
            "subject must be a pygame Surface"
        )

        def _draw_on_texture(surf):
            if border_width <= 0 or no_borders:
                transform_into_rounded_rect(subject, radius, None)
            elif border_width > 0:
                transform_into_outlined_rounded_rect(
                    subject,
                    radius,
                    root.relm(border_width),
                    override_color,
                    background_color=None,
                )
            surf.blit(subject, pos)

        match return_type:
            case RenderReturnType.Null:
                assert isinstance(root.surface, md.pygame.Surface), (
                    "root.surface must be a pygame Surface"
                )
                nv_texture = root.surface
                _draw_on_texture(nv_texture)
            case RenderReturnType.Outside:
                return subject, border_width, radius, override_color, no_borders
            case RenderReturnType.Raw:
                return (
                    subject,
                    border_width,
                    (
                        call.radius
                        if call.radius is not None
                        else root.style.border_radius
                    ),
                    override_color,
                    no_borders,
                )
            case RenderReturnType.Modify:
                texture = call.modify_object
                assert texture, "Modify return type selected but no object provided"
                _draw_on_texture(texture)
            case RenderReturnType.CreateNew:
                texture = self.core.create_clear(self.root._csize)
                _draw_on_texture(texture)
                return texture
            case _:
                raise ValueError(f"Invalid return type: {return_type}")
