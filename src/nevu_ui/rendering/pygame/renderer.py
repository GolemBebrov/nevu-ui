from __future__ import annotations
import pygame
import weakref

from typing import TYPE_CHECKING
if TYPE_CHECKING: from nevu_ui.components.nevuobj import NevuObject

from nevu_ui.presentation.color import Color
from nevu_ui.fast.nvvector2 import NvVector2
from nevu_ui.presentation.style import Style
from nevu_ui.rendering import AlphaBlit, GradientPygame
from nevu_ui.fast.shapes import _create_rounded_rect_surface_optimized, transform_into_outlined_rounded_rect

from nevu_ui.core.enums import (
    CacheType, HoverState, Align
)



class _DrawNamespace:
    __slots__ = ["_renderer"]
    def __init__(self, renderer: "BackgroundRendererPygame"):
        self._renderer = renderer
        
    @property
    def root(self) -> NevuObject: return self._renderer.root
    
    @property
    def style(self): return self.root.style
    
    def gradient(self, surface: pygame.Surface, transparency = None, style: Style | None = None) -> GradientPygame:
        style = style or self.style
        assert style
        assert isinstance(style.gradient, GradientPygame), "Gradient not set"
        if transparency is None or transparency >= 255:
            gr = style.gradient
        else:
            gr = style.gradient.with_transparency(transparency)
        return gr.apply_gradient(surface)

    def create_clear(self, size, flags) -> pygame.Surface:
        surf = pygame.Surface(size, flags = flags)
        surf.fill((0,0,0,0))
        return surf
    
    def load_image(self, path) -> pygame.Surface:
        img = pygame.image.load(path)
        img.convert_alpha()
        return img
    
    def scale(self, surface: pygame.Surface | None, size: list | tuple) -> pygame.Surface | None:
        if surface is None: return
        return pygame.transform.smoothscale(surface, size)
    
    def _round_radius(self, radius: int | float | tuple):
        if isinstance(radius, tuple):
            return tuple(map(round, radius))
        else:
            return round(radius)
    
    def _mult_radius(self, radius: int | float | tuple, mult: float):
        if isinstance(radius, tuple):
            return tuple(map(lambda x: x * mult, radius))
        else:
            return radius * mult
    
    def _normalize_radius(self, radius: int | float | tuple, _clipped = False) -> tuple:
        if isinstance(radius, (int,float)):
            radius = (radius, radius, radius, radius)
        if _clipped:
            radius = tuple(map(lambda x: max(0, x-1), radius))
        return radius
    
class BackgroundRendererPygame:
    __slots__ = ["_root", "draw"]
    def __init__(self, root: NevuObject):
        #assert isinstance(root, NevuObject), "Root must be NevuObject"
        self._root = weakref.proxy(root) 
        self.draw = _DrawNamespace(self)
        
    @property
    def root(self) -> NevuObject: return self._root
    
    def _draw_gradient(self):
        root = self.root
        style = root.style
        
        if not style.gradient: return
        
        gradient = self.draw.create_clear(root._csize, flags = pygame.SRCALPHA)
        self.draw.gradient(gradient, transparency = style.transparency)
        
        return gradient
    
    def _create_surf_base(self, size = None, alt = False, radius = None, standstill = False, override_color = None, sdf = False, _clipped = False): 
        root = self.root
        style = root._style
        needed_size = size or root._csize
        tuple_size = needed_size.to_round().to_tuple()
        
        surf = pygame.Surface(tuple_size, flags = pygame.SRCALPHA)
        
        color = root.subtheme_border if alt else root.subtheme_content
        
        if not standstill:
            hover_state = root._hover_state
            if hover_state == HoverState.CLICKED and not root.get_param_strict("fancy_click_style") and root.get_param_strict("clickable"): 
                color = Color.lighten(color, 0.2)
            elif hover_state == HoverState.HOVERED and root.get_param_strict("hoverable"): 
                color = Color.darken(color, 0.2)
        
        if override_color: color = override_color
        avg_scale_factor = (root._resize_ratio.x + root._resize_ratio.y) * 0.5
        
        radius = self.draw._mult_radius(style.borderradius, avg_scale_factor) if radius is None else radius
        r_radius = self.draw._round_radius(radius)
        
        if sdf: surf.blit(_create_rounded_rect_surface_optimized(tuple_size, r_radius, color), (0, 0)) #type: ignore
        else:
            r_radius = self.draw._normalize_radius(r_radius, _clipped = _clipped)
            #!to normalize with sdf
            pygame.draw.rect(surf, color, pygame.rect.Rect(0, 0, *tuple_size), 0, -1, r_radius[0], r_radius[1], r_radius[3], r_radius[2])
        return surf
    
    def _create_outlined_rect(self, size = None, radius = None, width = None, sdf = False): 
        root = self.root
        style = root._style
        
        needed_size = size or root._csize
        tuple_size = needed_size.to_round().to_tuple()
        avg_scale_factor = (root._resize_ratio.x + root._resize_ratio.y) * 0.5
            
        radius = radius or self.draw._mult_radius(style.borderradius, avg_scale_factor)
        width = width or style.borderwidth * avg_scale_factor
        
        r_radius = self.draw._round_radius(radius)
        r_width = max(1, round(width))

        if sdf: 
            result = self.draw.create_clear(tuple_size, flags = pygame.SRCALPHA)
            transform_into_outlined_rounded_rect(result, r_radius, r_width, root.subtheme_border)
        else:
            result = pygame.Surface(tuple_size, flags = pygame.SRCALPHA)
            r_radius = self.draw._normalize_radius(r_radius)
            pygame.draw.rect(result, root.subtheme_border, pygame.rect.Rect(0, 0, *tuple_size), r_width, -1, r_radius[0], r_radius[1], r_radius[3], r_radius[2])
        return result
    
    def _get_correct_mask(self, sdf=True, add = 0, radius = None): 
        root = self.root
        radius = radius or root.relm(root.style.borderradius)
        size = root._csize.to_round().copy()
        size -= NvVector2(add, add)
        if sdf: size -= NvVector2(2,2)
        if root.style.borderwidth > 0: size -= NvVector2(2,2)
        
        return self._create_surf_base(size, root.alt, radius)
    
    def _generate_background(self, sdf = True, only_content = False): 
        root = self.root
        style = root.style
        cache = root.cache
        rounded_size = root._csize.to_round()
        tuple_size = rounded_size.to_tuple()

        border_width = style.borderwidth
        coords = (0,0) if border_width <= 0 else (1,1)

        mask_surf = None
        correct_mask = None
        offset = NvVector2(0,0)
        
        if only_content:
            if border_width > 0:
                correct_mask = self._create_surf_base(rounded_size, sdf = False)
                offset = NvVector2(2, 2) if border_width * (root._resize_ratio.x + root._resize_ratio.y) > 1.5 / 0.5 else NvVector2(1, 1)
                mask_surf = cache.get_or_exec(CacheType.Surface, lambda: self._create_surf_base(rounded_size - offset, sdf = False, _clipped=True))
            else:
                mask_surf = correct_mask = self._create_surf_base(rounded_size, sdf = True)

        final_surf = pygame.Surface(tuple_size, flags = pygame.SRCALPHA)

        content_surf = None
        if style.gradient:
            content_surf = cache.get_or_exec(CacheType.Scaled_Gradient, lambda: self._scale_gradient(rounded_size - offset))
        elif style.bgimage:
            content_surf = cache.get_or_exec(CacheType.Scaled_Image, lambda: self._scale_image(rounded_size - offset))

        if only_content:
            if content_surf:
                assert correct_mask, "Invalid correct_mask"
                AlphaBlit.blit(content_surf, correct_mask, (0,0))
                final_surf.blit(content_surf, coords)
            else:
                assert mask_surf, "Invalid mask_surf"
                final_surf.blit(mask_surf, coords)
        elif content_surf:
            final_surf.blit(content_surf, (0,0))

        if border_width > 0:
            cache_type = CacheType.Borders
            if border := cache.get_or_exec(cache_type, lambda: self._create_outlined_rect(rounded_size, sdf = sdf)):
                if root._draw_borders:
                    final_surf.blit(border, (0, 0))

        if style.transparency: 
            final_surf.set_alpha(style.transparency)
        return final_surf
    
    def _generate_image(self):
        root = self.root
        assert root.style.bgimage, "Bgimage not set"
        return self.draw.load_image(root.style.bgimage)

    def min_size(self, size: NvVector2):  return (max(1, int(size.x)), max(1, int(size.y)))
    
    def _scale_image(self, size = None): 
        root = self.root
        size = size or root._csize
        return self.draw.scale(root.cache.get_or_exec(CacheType.Image, self._generate_image), self.min_size(size))
    
    def _scale_gradient(self, size = None): 
        root = self.root
        size = size or root._csize
        return self.draw.scale(root.cache.get_or_exec(CacheType.Gradient, self._draw_gradient), self.min_size(size))

    def _scale_background(self, size = None, only_content = False, sdf = True): 
        root = self.root
        size = size or root._csize
        return self.draw.scale(root.cache.get_or_exec(CacheType.Background, lambda: self._generate_background(sdf = sdf)), self.min_size(size))
    
    @staticmethod
    def _split_words(words: list, font: pygame.font.Font, x, marg = " "):
        current_line = ""
        lines = []
        font_size = font.size
        
        for word in words:
            force_next_line = False
            if word == '\n': force_next_line = True
            elif len(word) >= 2 and word[0] == '\\' and word[1] == 'n': force_next_line = True
            
            if force_next_line:
                lines.append(current_line)
                current_line = ""
                continue

            test_line = current_line + word + marg
            if font_size(test_line)[0] > x:
                lines.append(current_line)
                current_line = word + marg
            else: 
                current_line = test_line
                
        lines.append(current_line)
        return lines
    
    def bake_text(self, text: str, unlimited_y: bool = False, words_indent: bool = False, style: Style | None = None, size: NvVector2 | None = None, color = None, outside = False, outside_rect = None, override_font_size = None):
        root = self.root
        style = style or root.style
        assert style

        alignx = style.text_align_x
        aligny = style.text_align_y

        color = color or root.subtheme_font
        size = size or root._csize
        assert size

        renderFont = root.get_pygame_font(override_font_size)
        line_height = renderFont.get_linesize()

        if words_indent:
            words = text.strip().split()
            marg = " "
        else:
            words = list(text)
            marg = ""

        is_cropped = False
        lines = self._split_words(words, renderFont, size.x, marg)

        if not unlimited_y:
            while len(lines) * line_height > size.y:
                lines.pop(-1)
                is_cropped = True

        baked_text = "\n".join(lines)

        if is_cropped and not unlimited_y:
            baked_text = f"{baked_text[:-3]}..."

        text_surface: pygame.Surface = renderFont.render(baked_text, True, color)

        if outside and outside_rect: container_rect = outside_rect
        elif root.inline: container_rect = pygame.Rect(root.coordinates.to_round().to_tuple(), root._csize.to_round())
        else: container_rect = root.surface.get_rect()

        text_rect = text_surface.get_rect()

        if alignx == Align.LEFT: text_rect.left = container_rect.left
        elif alignx == Align.CENTER: text_rect.centerx = container_rect.centerx
        elif alignx == Align.RIGHT: text_rect.right = container_rect.right
        if aligny == Align.TOP: text_rect.top = container_rect.top
        elif aligny == Align.CENTER: text_rect.centery = container_rect.centery
        elif aligny == Align.BOTTOM: text_rect.bottom = container_rect.bottom

        if outside:
            return text_surface, text_rect, baked_text
        root._text_surface = text_surface # type: ignore
        root._text_rect = text_rect # type: ignore
        root._text_baked = baked_text # type: ignore