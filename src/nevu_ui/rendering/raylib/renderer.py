from __future__ import annotations

import math
import weakref
import pyray as rl

from typing import TYPE_CHECKING
if TYPE_CHECKING: 
    from nevu_ui.components.nevuobj import NevuObject
    from nevu_ui.presentation.style import Style
    from nevu_ui.rendering.gradient import GradientRaylib
from nevu_ui.presentation.color import Color
from nevu_ui.fast.nvvector2 import NvVector2
from nevu_ui.fast.nvrect import NvRect
from nevu_ui.core.state import nevu_state
from nevu_ui.core.enums import CacheType, Align

from nevu_ui.core.enums import (
    CacheType, HoverState, Align
)

class _DrawNamespaceRayLib:
    __slots__ = ["_renderer"]
    def __init__(self, renderer):
        self._renderer = renderer
        
    @property
    def root(self) -> NevuObject: return self._renderer.root
    @property
    def style(self): return self.root.style
    
    def gradient(self, coordinates: tuple[int, int], style: Style | None = None) -> rl.Texture: # type: ignore
        style = style or self.style
        if not style.gradient: raise ValueError("Gradient not set")
        gr: GradientRaylib = style.gradient
        return gr.generate_texture(coordinates[0], coordinates[1])
        
    def create_clear(self, size) -> rl.RenderTexture:
        return rl.load_render_texture(size[0], size[1])

    def load_image(self, path: str, size: tuple[int, int]) -> rl.Texture:
        image = rl.load_image(path)
        rl.image_resize(image, size[0], size[1])
        texture = rl.load_texture_from_image(image)
        rl.unload_image(image)
        return texture

class BackgroundRendererRayLib:
    __slots__ = ["_renderer"]
    __slots__ = ["_root", "draw"]
    def __init__(self, root: NevuObject):
        self._root = weakref.proxy(root) 
        self.draw = _DrawNamespaceRayLib(self)
        
    @property
    def root(self) -> NevuObject: return self._root
    
    def _create_surf_base(self, size = None, alt = False, radius = None, standstill = False, override_color = None, sdf = False, _clipped = False, blitmode = None): 
        assert nevu_state.window
        root = self.root
        size = size or root._csize 
        style = root._style
        color = root.subtheme_border if alt else root.subtheme_content
        if not standstill:
            hover_state = root._hover_state
            if hover_state == HoverState.CLICKED and not root.get_param_strict("fancy_click_style").value and root.get_param_strict("clickable").value: 
                color = Color.lighten(color, 0.2)
            elif hover_state == HoverState.HOVERED and root.get_param_strict("hoverable").value: 
                color = Color.darken(color, 0.2)
        if override_color: color = override_color
        base_texture = rl.load_render_texture(int(size[0]), int(size[1]))
        if len(color) == 3: color = (*color, 255)
        if radius:
            add_texture = rl.load_render_texture(int(size[0]), int(size[1]))
            rl.begin_texture_mode(add_texture)
            rl.begin_blend_mode(blitmode or rl.BlendMode.BLEND_ALPHA_PREMULTIPLY)
            nevu_state.window.display.clear(rl.BLANK) 
            nevu_state.window.display.clear(color)
            rl.end_blend_mode()
            rl.end_texture_mode()
        rl.begin_texture_mode(base_texture)
        nevu_state.window.display.clear(rl.BLANK)
        if radius is None:
            nevu_state.window.display.clear(color)
        else:
            nevu_state.window.display.blit_sdf_vec(add_texture.texture, (0, 0), radius, mode = rl.BlendMode.BLEND_ALPHA)
            rl.unload_render_texture(add_texture)
        rl.end_texture_mode()
        return base_texture
    
    def _create_rect(self, size: tuple[int, int], radius = 0, color = Color.White):
        rtext = rl.load_render_texture(size[0], size[1])
        if len(color) == 3: color = (*color, 255)
        rl.begin_texture_mode(rtext)
        nevu_state.window.display.fill(rl.BLANK)
        rl.draw_rectangle_rounded(size, radius, 2, color)
        rl.end_texture_mode()
        return rtext
    
    def _create_outlined_rect(self, size = None, radius = None, width = None, sdf = False):
        return None

    def _generate_background(self, sdf = True, only_content = False) -> rl.RenderTexture: 
        root = self.root
        style = root.style
        cache = root.cache
        rounded_size = root._csize.to_round()
        tuple_size = rounded_size.get_int_tuple()
        flip = True

        if style.gradient:
            old_content_text = cache.get(CacheType.Scaled_Gradient)
            content_text = cache.get_or_exec(CacheType.Scaled_Gradient, lambda: self.draw.gradient(tuple_size, style))
            if old_content_text is not content_text and old_content_text is not None:
                rl.unload_texture(old_content_text)
            hoverstate = root._hover_state
            add_color = NvRect(255,255,255,255)
            def _add(value):
                for i in range(3): add_color[i] += value
            _add(-25)
            if hoverstate == HoverState.CLICKED and root.get_param_strict("clickable").value:
                _add(-25)
            elif hoverstate == HoverState.HOVERED and root.get_param_strict("hoverable").value:
                _add(25)
        elif style.bgimage:
            content_text = cache.get_or_exec(CacheType.Image, lambda: self.draw.load_image(style.bgimage, rounded_size.get_int_tuple()))
            add_color = NvRect(255,255,255,255)
            flip = False
        else:
            content_text = cache.get_or_exec(CacheType.Surface, lambda: self._create_surf_base(rounded_size))
            add_color = NvRect(255,255,255,255)
        final_surf = rl.load_render_texture(*tuple_size)
        display = nevu_state.window.display
        assert content_text
        assert nevu_state.window.is_raylib(display)
        final_content_text = content_text.texture if hasattr(content_text, "texture") else content_text
        rl.begin_texture_mode(final_surf)
        nevu_state.window.display.clear(rl.BLANK)
        if isinstance(style.borderradius, int|float):
            borderradius = [root.relm(style.borderradius)]*4
        else:
            borderradius = tuple(map(root.relm, style.borderradius))
        if style.borderwidth > 0 and only_content:
            display.blit_borders(final_content_text, (0, 0, tuple_size[0], tuple_size[1]), borderradius, root.subtheme_border, color=add_color.get_int_tuple(), thickness= root.relm(style.borderwidth), flip=flip, mode=rl.BlendMode.BLEND_ALPHA_PREMULTIPLY)
        elif style.borderwidth > 0 and not only_content:
            display.blit_sdf(final_content_text, (0, 0, tuple_size[0], tuple_size[1]), borderradius, flip=flip, mode=rl.BlendMode.BLEND_ALPHA_PREMULTIPLY)
        else:
            display.blit_rect_pro(final_content_text, (0, 0, tuple_size[0], tuple_size[1]), flip=flip, mode=rl.BlendMode.BLEND_ALPHA_PREMULTIPLY)
        rl.end_texture_mode()
        return final_surf

    @staticmethod
    def _split_words(words: list, font: rl.Font, font_size: float, spacing: float, max_width: float, marg=" "):
        current_line = ""
        lines = []
        
        for word in words:
            force_next_line = False
            if word == '\n': force_next_line = True
            elif len(word) >= 2 and word[0] == '\\' and word[1] == 'n': force_next_line = True
            
            if force_next_line:
                lines.append(current_line)
                current_line = ""
                continue

            test_line = current_line + word + marg
            text_size_vec = rl.measure_text_ex(font, test_line, font_size, spacing)
            
            if text_size_vec.x > max_width:
                lines.append(current_line)
                current_line = word + marg
            else: 
                current_line = test_line
                
        lines.append(current_line)
        return lines

    def bake_text(self, text: str, unlimited_y: bool = False, words_indent: bool = False, 
                  style: Style | None = None, size: NvVector2 | None = None, 
                  color = None, outside = False, outside_rect = None, override_font_size = None, modify: rl.RenderTexture | None = None, continuous = False, render = True):
        root = self.root
        style = style or root.style
        assert style
        
        alignx = style.text_align_x
        aligny = style.text_align_y
        
        color = color or root.subtheme_font
        if len(color) == 3: color = (*color, 255)
        size = size or root._csize
        assert size

        current_font_size = override_font_size or root.relm(style.fontsize)
        current_font_size = round(current_font_size * 1.25)
        renderFont = root._get_raylib_font() 
        
        spacing = 0
        if not continuous:
            dims = rl.measure_text_ex(renderFont, "A", current_font_size, spacing)
            line_height = dims.y

            if words_indent:
                words = text.strip().split()
                marg = " "
            else:
                words = list(text)
                marg = ""
                
            is_cropped = False
            
            lines = self._split_words(words, renderFont, current_font_size, spacing, size.x, marg)
            
            if not unlimited_y:
                while len(lines) * line_height > size.y:
                    lines.pop(-1)
                    is_cropped = True
                    
            baked_text_str = "\n".join(lines)

            if is_cropped and not unlimited_y:
                baked_text_str = f"{baked_text_str[:-3]}..."

            text_dims = rl.measure_text_ex(renderFont, baked_text_str, current_font_size, spacing)
            text_w = text_dims.x
            text_h = text_dims.y

            if outside and outside_rect: 
                container_rect = outside_rect 
            elif root.inline: 
                c_coords = root.coordinates.to_round()
                c_size = root._csize.to_round()
                container_rect = (c_coords.x, c_coords.y, c_size.x, c_size.y)
            else: 
                container_rect = (0, 0, size.x, size.y) 

            final_x = container_rect[0]
            final_y = container_rect[1]

            if alignx == Align.LEFT:
                final_x = container_rect[0]
            elif alignx == Align.CENTER:
                final_x = container_rect[0] + (container_rect[2] - text_w) / 2
            elif alignx == Align.RIGHT:
                final_x = container_rect[0] + container_rect[2] - text_w

            if aligny == Align.TOP:
                final_y = container_rect[1]
            elif aligny == Align.CENTER:
                final_y = container_rect[1] + (container_rect[3] - text_h) / 2
            elif aligny == Align.BOTTOM:
                final_y = container_rect[1] + container_rect[3] - text_h

            final_x, final_y = round(final_x), round(final_y)
            text_w, text_h = text_w, text_h 
            
            result_text_rect = (final_x, final_y, text_w, text_h)
        else:
            result_text_rect = (0, 0)
            baked_text_str = text
            text_vec = rl.measure_text_ex(renderFont, text, current_font_size, spacing)
            text_w = text_vec.x
            text_h = text_vec.y
        if outside:
            return None, result_text_rect, baked_text_str

        if modify:
            assert nevu_state.window.is_raylib(nevu_state.window.display)
            rl.begin_texture_mode(modify)
            rl.begin_blend_mode(rl.BlendMode.BLEND_ALPHA)
            rl.draw_text_ex(renderFont, baked_text_str, (result_text_rect[0], result_text_rect[1]), current_font_size, spacing, color)
            rl.end_blend_mode()
            rl.end_texture_mode()
            
            return
        
        if render:
            target = rl.load_render_texture(math.ceil(text_w), math.ceil(text_h))
            rl.set_texture_filter(target.texture, rl.TextureFilter.TEXTURE_FILTER_BILINEAR)
            rl.set_texture_wrap(target.texture, rl.TextureWrap.TEXTURE_WRAP_CLAMP)
            rl.begin_blend_mode(rl.BlendMode.BLEND_ALPHA)
            rl.begin_texture_mode(target)
            rl.clear_background(rl.BLANK) 
            
            rl.draw_text_ex(renderFont, baked_text_str, (0, 0), current_font_size, spacing, color)
            
            rl.end_texture_mode()
            rl.end_blend_mode()
            if root._text_surface:
                rl.unload_render_texture(root._text_surface)
            root._text_surface = target # type: ignore
        root._text_rect = result_text_rect # type: ignore
        root._text_baked = baked_text_str # type: ignore
        if not render:
            return (renderFont, baked_text_str, result_text_rect, current_font_size, spacing, color)