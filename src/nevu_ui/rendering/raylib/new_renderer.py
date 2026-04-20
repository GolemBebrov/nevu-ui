from __future__ import annotations
from typing_extensions import override, Any, TYPE_CHECKING

if TYPE_CHECKING:
    from nevu_ui.rendering.gradient import GradientRaylib
    from nevu_ui.presentation.style import Style

from nevu_ui.core.enums import RenderReturnType
from nevu_ui.core.state import nevu_state
from nevu_ui.core.classes import EnumValidator
from nevu_ui.rendering.raylib.gradient import ClickGradient
import nevu_ui.core.modules as md
from nevu_ui.core.annotations import Annotations
from nevu_ui.rendering import BaseRenderer, _BaseCoreNamespace, _BaseSpecifiedDraw
from nevu_ui.fast.nvvector2 import NvVector2
from nevu_ui.presentation.color.color import Color, is_rgba
from nevu_ui.fast.nvrendertex import NvRenderTexture
from nevu_ui.core.enums import CacheType

class _RaylibCoreNamespace(_BaseCoreNamespace):
    @override
    def get_gradient(self, style: Style | None = None):
        style = style or self.style
        if not style.gradient: raise ValueError("Gradient not set in style")
        gr: GradientRaylib = style.gradient
        return gr
    
    @override
    def create_clear(self, size: Annotations.dest_like | NvVector2):
        texture = NvRenderTexture(NvVector2(size))
        texture.clear(Color.Blank)
        return texture
    
    @override
    def draw_rect(self, subject, pos: Annotations.dest_like | NvVector2, size: Annotations.dest_like | NvVector2, color: Annotations.rgba_color = Color.White, radii: Annotations.rect_like | int = 0):
        assert isinstance(subject, NvRenderTexture), "subject must be a nevu ui render texture"
        if radii == 0:
            with subject:
                md.rl.draw_rectangle(0, 0, int(size[0]), int(size[1]), color)
            return
        if len(color) == 3: color = (*color, 255)
        if isinstance(radii, int | float): radii = (radii, radii, radii, radii)
        rect_texture = NvRenderTexture(NvVector2(size))
        rect_texture.clear(color)
        display = nevu_state.window.display
        assert nevu_state.window.is_raylib(display)
        with subject:
            display.fast_blit_sdf_vec(rect_texture.texture, (0, 0), radii)

    @override
    def load_image(self, path: str, size: Annotations.dest_like | NvVector2 | None = None):
        image = md.rl.load_image(path)
        if size:
            md.rl.image_resize(image, int(size[0]), int(size[1]))
        texture = md.rl.load_texture_from_image(image)
        md.rl.unload_image(image)
        return texture
    
    @override
    def measure_text(self, font: Any, text: str, font_size: float) -> NvVector2:
        assert hasattr(font, "baseSize"), "font must be a raylib font"
        result = md.rl.measure_text_ex(font, text, font_size, 0)
        return NvVector2.from_xy(result.x, result.y)

class _RaylibSpecifiedDraw(_BaseSpecifiedDraw):
    def adjust_brightness(self, color: tuple, offset: int) -> tuple:
        return tuple(max(0, min(255, c + offset)) for c in color[:3]) + (color[3],)

    def check_root_color_transition(self):
        root = self.root
        if not root.inline:
            new_color_pretendent = self._renderer.core.get_color_on_hover(root.subtheme_border if root.get_param_strict("alt").value else root.subtheme_content)
            old_color = root._old_color
            if old_color is None:
                root._old_color = new_color_pretendent #type: ignore
            elif old_color != new_color_pretendent:
                root._set_new_color(new_color_pretendent)

class RaylibRenderer(BaseRenderer):
    @override
    def _get_core_namespace(self):
        return _RaylibCoreNamespace(self)
    
    @override
    def _get_unsafe_namespace(self):
        return _RaylibSpecifiedDraw(self)
    
    @override
    def _draw_base(self, **kwargs):
        root = self.root
        unsafe: _RaylibSpecifiedDraw = self.unsafe #type: ignore
        size: NvVector2 = kwargs.get("size", root._csize)
        standstill = kwargs.get("standstill", False)
        override_color = kwargs.get("override_color", None)
        cached = kwargs.get("cached", False)
        radii = kwargs.get("radius", root.style.border_radius)
        radii = self.core.normalize_radius_relative(radii)
        inline = kwargs.get("override_inline", self.root.inline)
        return_type = kwargs.get("return_type", RenderReturnType.Null)
        alt = root.alt
        color = override_color or (root.subtheme_border if alt else root.subtheme_content)
        if not standstill:
            color = self.core.get_color_on_hover(color)
        
        def _draw_on_texture(texture: NvRenderTexture):
            nonlocal color
            gradient_support = kwargs.get("gradient_support", True)
            image_support = kwargs.get("image_support", True)
            easy_background = kwargs.get("easy_background", False)
            md.rl.begin_blend_mode(md.rl.BlendMode.BLEND_ALPHA_PREMULTIPLY if not (image_support and root.style.bg_image) else md.rl.BlendMode.BLEND_ALPHA)
            
            if gradient_support and root.style.gradient:
                gradient = root.cache.get_or_exec(CacheType.Scaled_Gradient, lambda: self.core.get_gradient().generate_texture(int(size[0]), int(size[1])))
                end_color = (205,)*4
                HoverState = root.hover_state.__class__
                match root.hover_state:
                    case HoverState.HOVERED:
                        if root.get_param_strict("hoverable").value:
                            end_color = self.unsafe.adjust_brightness(end_color, -50) #type: ignore
                    case HoverState.CLICKED: 
                        if root.get_param_strict("clickable").value:
                            end_color = self.unsafe.adjust_brightness(end_color, 50) #type: ignore
                    case _:
                        pass
                with texture:
                    texture.fast_blit(gradient, (0, 0), color = end_color) #type: ignore
            elif image_support and root.style.bg_image:
                image = root.cache.get_or_exec(CacheType.Scaled_Image, lambda: self.core.load_image(root.style.bg_image, size))
                with texture:
                    texture.fast_blit_texture(image, (0, 0), flip=False)
                    #texture.fast_blit(image, (0, 0))
            else:
                if not standstill:
                    unsafe.check_root_color_transition()
                    if root._color_anim_manager:
                        anim_color = root._color_anim_manager.get_animation_value("main") if root._color_anim_manager else None
                    else: anim_color = None
                    color = anim_color or color
                    if len(color) == 3: color = (*color, 255)
                    assert is_rgba(color), "color must be a rgba color"
                with texture:
                    if easy_background:
                        texture.clear(color)
                    else:
                        self.core.draw_rect(texture, (0, 0), size, color, radii) #type: ignore
            md.rl.end_blend_mode()    
            
        with EnumValidator(RenderReturnType) as validator:
            validator.Null = True
            validator.Outside = True
            validator.Raw = True
            validator.Modify = True
            validator.CreateNew = True
        
        match return_type:
            case RenderReturnType.Null:
                assert isinstance(root.surface, NvRenderTexture), "root.surface must be a nevu ui render texture"
                nv_texture: NvRenderTexture = root.surface
                _draw_on_texture(nv_texture)
            case RenderReturnType.Outside:
                return size, color, radii
            case RenderReturnType.Raw:
                return size, radii, override_color, cached, standstill
            case RenderReturnType.Modify:
                texture = kwargs.get("modify_object")
                assert texture, "Modify return type selected but no object provided"
                _draw_on_texture(texture)
            case RenderReturnType.CreateNew:
                texture = self.core.create_clear(size)
                _draw_on_texture(texture)
                return texture
    
    @override
    def _draw_text(self, **kwargs):
        root = self.root
        text: str = kwargs.get("text", None) #type: ignore
        style: Style = kwargs.get("override_style", root.style)
        font_size: float | None = kwargs.get("override_font_size", None)
        font_size_overriden = font_size is not None
        font_size = font_size or root.style.font_size
        size: NvVector2 = kwargs.get("size", root._csize)
        unlimited_y = kwargs.get("unlimited_y", False)
        words_indent = kwargs.get("words_indent", False)
        continuous = kwargs.get("continuous", False)
        max_size = kwargs.get("max_size", size)
        inline = kwargs.get("override_inline", self.root.inline)
        spacing = 0
        cropped = False
        return_type = kwargs.get("return_type", RenderReturnType.Null)
        color = kwargs.get("override_color", root.subtheme_font)
        if len(color) == 3: color = (*color, 255)
        assert text is not None, "text must be provided"
        container_rect = (0, 0, 0, 0)
        baked_text = text
        text_dims = NvVector2.from_xy(0, 0)
        render_font = None
        
        def _arrange_text(override_size = None):
            nonlocal font_size, cropped, container_rect, baked_text, text_dims, render_font
            assert font_size
            if font_size_overriden:
                font_size = font_size * 1.5
                render_font = root._get_raylib_font_nocache(font_size)
            else:
                render_font = root._get_raylib_font(font_size)
            assert isinstance(render_font, md.rl.Font().__class__)
            font_size = render_font.baseSize
            final_size = override_size or size
            final_max_size = max_size
            final_max_size.x = min(final_max_size.x, final_size.x)
            final_max_size.y = min(final_max_size.y, final_size.y)
            if not continuous:
                line_height = self.core.measure_text(render_font, "A", font_size).y
                text_to_split = text.strip().split(" ") if words_indent else list(text)
                marg = " " if words_indent else ""
                text_lines = self.core.split_words(text_to_split, render_font, font_size, final_max_size.x, marg=marg)
                if not unlimited_y:
                    while len(text_lines) * line_height > final_max_size.y:
                        text_lines.pop()
                        cropped = True
                baked_text = "\n".join(text_lines)
                if cropped:
                    baked_text = f"{baked_text[:-3]}..."
                text_dims = self.core.measure_text(render_font, baked_text, font_size)
                container_rect = (0, 0, final_size.x, final_size.y)
                container_rect = self.core.align_rect(style.align_x, style.align_y, container_rect, text_dims.x, text_dims.y)
            else:
                text_dims = self.core.measure_text(render_font, baked_text, font_size)
                
        def _create_text(texture: NvRenderTexture, relative_size = False):
            assert render_font and font_size
            coordinates = (0, 0) if relative_size else (container_rect[0], container_rect[1])
            with texture:
               # print(render_font, baked_text, coordinates, font_size, spacing, color)
                md.rl.draw_text_ex(render_font, baked_text, coordinates, font_size, spacing, color)
            if font_size_overriden:
                md.rl.unload_font(render_font)
        
        with EnumValidator(RenderReturnType) as validator:
            validator.Null = True
            validator.Outside = True
            validator.Raw = True
            validator.Modify = True
            validator.CreateNew = True
        
        match return_type:
            case RenderReturnType.Null: 
                assert isinstance(root.surface, NvRenderTexture), "root.surface must be a nevu ui render texture"
                nv_texture: NvRenderTexture = root.surface
                _arrange_text()
                _create_text(nv_texture)
            case RenderReturnType.Outside: 
                _arrange_text()
                return baked_text, size, font_size, render_font, spacing, style, cropped, container_rect, text_dims
            case RenderReturnType.Raw: return text, size, kwargs.get("style", root.style), font_size, color, spacing
            case RenderReturnType.Modify:
                texture = kwargs.get("modify_object")
                assert texture, "Modify return type selected but no object provided"
                _arrange_text()
                _create_text(texture)
                return container_rect, text_dims
            case RenderReturnType.CreateNew:
                _arrange_text(override_size = size)
                texture = self.core.create_clear(text_dims)
                _create_text(texture, True)
                return container_rect, texture
    
    @override
    def _draw_effects(self, **kwargs):
        radius = kwargs.get("radius", self.style.border_radius)
        radius = self.core.normalize_radius_relative(radius)
        click_gradient = kwargs.get("click_gradient", None)
        assert isinstance(click_gradient, ClickGradient), "click_gradient must be provided"
        click_subject = kwargs.get("click_subject", None) or NvRenderTexture(self.root._csize)
        assert isinstance(click_subject, NvRenderTexture), "click_subject must be a nevu ui render texture"
        return_type = kwargs.get("return_type", RenderReturnType.Null)
        
        def _add_effects(texture: NvRenderTexture):
            display = nevu_state.window.display
            assert nevu_state.window.is_raylib(display)
            md.rl.begin_blend_mode(md.rl.BlendMode.BLEND_ADDITIVE)
            with click_subject:
                click_subject.fast_clear(Color.Blank)
                click_gradient.draw(0, 0, click_subject.width, click_subject.height)
            with texture:
                display.fast_blit_sdf_vec(click_subject.texture, (0, 0), radius)
            md.rl.end_blend_mode()
        
        with EnumValidator(RenderReturnType) as validator:
            validator.Null = True
            validator.Outside = True
            validator.Raw = True
            validator.Modify = True
            validator.CreateNew = True

        match return_type:
            case RenderReturnType.Null:
                assert isinstance(self.root.surface, NvRenderTexture), "root.surface must be a nevu ui render texture"
                nv_texture: NvRenderTexture = self.root.surface
                _add_effects(nv_texture)
            case RenderReturnType.Outside: return radius, click_gradient, click_subject
            case RenderReturnType.Raw: return radius, click_gradient, click_subject
            case RenderReturnType.Modify:
                texture = kwargs.get("modify_object")
                assert texture, "Modify return type selected but no object provided"
                _add_effects(texture)
            case RenderReturnType.CreateNew:
                texture = self.core.create_clear(self.root._csize)
                _add_effects(texture)
                return texture
    
    @override
    def _draw_borders(self, **kwargs):
        root = self.root
        subject: NvRenderTexture = kwargs.get("subject") #type: ignore
        border_width = kwargs.get("border_width", root.style.border_width)
        radius = kwargs.get("radius", root.style.border_radius)
        radius = self.core.normalize_radius_relative(radius)
        override_color = kwargs.get("override_color", root.subtheme_content if root.alt else root.subtheme_border)
        no_borders = kwargs.get("no_borders", False)
        display = nevu_state.window.display
        pos = kwargs.get("override_position", self.root.coordinates.to_tuple() if self.root.get_param_strict("inline").value else (0, 0))
        assert nevu_state.window.is_raylib(display)
        return_type = kwargs.get("return_type", RenderReturnType.Null)
        assert isinstance(subject, NvRenderTexture), "subject must be a nevu ui render texture"

        def _draw_on_texture(texture: NvRenderTexture):
            with texture:
                if border_width <= 0 or no_borders:
                    display.fast_blit_sdf_vec(subject.texture, pos, radius, flip=True)
                elif border_width > 0:
                    display.fast_blit_borders_vec(subject.texture, pos, list(radius), override_color, thickness= root.relm(border_width), flip=True)
        
        with EnumValidator(RenderReturnType) as validator:
            validator.Null = True
            validator.Outside = True
            validator.Raw = True
            validator.Modify = True
            validator.CreateNew = True

        match return_type:
            case RenderReturnType.Null: 
                assert isinstance(root.surface, NvRenderTexture), "root.surface must be a nevu ui render texture"
                nv_texture: NvRenderTexture = root.surface 
                _draw_on_texture(nv_texture)
            case RenderReturnType.Outside: return subject, border_width, radius, override_color, no_borders
            case RenderReturnType.Raw: return subject, border_width, kwargs.get("radius", root.style.border_radius), override_color, no_borders
            case RenderReturnType.Modify:
                texture = kwargs.get("modify_object")
                assert texture, "Modify return type selected but no object provided"
                _draw_on_texture(texture)
            case RenderReturnType.CreateNew:
                texture = self.core.create_clear(self.root._csize)
                _draw_on_texture(texture)
                return texture