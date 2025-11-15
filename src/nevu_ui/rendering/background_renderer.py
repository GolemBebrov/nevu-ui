import pygame
import contextlib

from nevu_ui.color import Color
from nevu_ui.nevuobj import NevuObject
from nevu_ui.fast.nvvector2 import NvVector2
from nevu_ui.style import Style

from nevu_ui.core_types import (
    _QUALITY_TO_RESOLUTION, CacheType, HoverState, Align
)
from nevu_ui.rendering import (
    OutlinedRoundedRect, RoundedRect, AlphaBlit, Gradient
)

class _DrawNamespace:
    __slots__ = ["_renderer"]
    def __init__(self, renderer: "BackgroundRenderer"):
        self._renderer = renderer
        
    @property
    def root(self):
        return self._renderer.root
    
    @property
    def style(self):
        return self.root.style
    
    def gradient(self, surface: pygame.Surface, transparency = None, style: Style | None = None) -> Gradient:
        style = style or self.style
        assert isinstance(style.gradient, Gradient), "Gradient not set"
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
    
class BackgroundRenderer:
    __slots__ = ["_root", "draw"]
    def __init__(self, root: NevuObject):
        assert isinstance(root, NevuObject), "Root must be NevuObject"
        self._root = root
        self.draw = _DrawNamespace(self)
    
    @property
    def root(self):
        return self._root
    
    def _draw_gradient(self):
        root = self.root
        
        if not root.style.gradient: return
        
        gradient = self.draw.create_clear(root.size * _QUALITY_TO_RESOLUTION[root.quality], flags = pygame.SRCALPHA)
        self.draw.gradient(gradient, transparency = root.style.transparency)
        
        return gradient
    
    def _create_surf_base(self, size = None, alt = False, radius = None, standstill = False, override_color = None, sdf = True): 
        root = self.root
        
        needed_size = size or root._csize
        needed_size.to_round()
        
        surf = self.draw.create_clear(needed_size.to_tuple(), flags = pygame.SRCALPHA)
        
        color = root.subtheme_border if alt else root.subtheme_content
        
        if not standstill:
            if root._hover_state == HoverState.CLICKED and not root.fancy_click_style and root.clickable: 
                color = Color.lighten(color, 0.2)
            elif root._hover_state == HoverState.HOVERED and root.hoverable: 
                color = Color.darken(color, 0.2)
        
        if override_color:
            color = override_color
        
        if root.will_resize:
            avg_scale_factor = _QUALITY_TO_RESOLUTION[root.quality]
        else:
            avg_scale_factor = (root._resize_ratio.x + root._resize_ratio.y) / 2
        
        radius = (root._style.borderradius * avg_scale_factor) if radius is None else radius
        if sdf:
            surf.blit(RoundedRect.create_sdf(needed_size.to_tuple(), round(radius), color), (0, 0))
        else:
            pygame.draw.rect(surf, color, pygame.rect.Rect(0, 0, *needed_size.to_tuple()), 0, round(radius))
        
        return surf
    
    def _create_outlined_rect(self, size = None, radius = None, width = None, sdf = False): 
        root = self.root
        
        needed_size = size or root._csize
        needed_size.to_round()
        
        if root.will_resize:
            avg_scale_factor = _QUALITY_TO_RESOLUTION[root.quality]
        else:
            avg_scale_factor = (root._resize_ratio[0] + root._resize_ratio[1]) / 2
            
        radius = radius or root._style.borderradius * avg_scale_factor
        width = width or root._style.borderwidth * avg_scale_factor
        
        if sdf:
            result = OutlinedRoundedRect.create_sdf(needed_size.to_tuple(), round(radius), round(width), root.subtheme_border)
        else:
            result = self.draw.create_clear(needed_size.to_tuple(), flags = pygame.SRCALPHA)
            pygame.draw.rect(result, root.subtheme_border, pygame.rect.Rect(0, 0, *needed_size.to_tuple()), round(width), round(radius))
        return result
    
    def _get_correct_mask(self): 
        root = self.root
        size = root._csize.to_round().copy()
        if root.style.borderwidth > 0:
            size -= NvVector2(2,2)
        
        return self._create_surf_base(size, root.alt, root.relm(root.style.borderradius))
    
    def _generate_background(self, sdf = True): 
        root = self.root
        resize_factor = _QUALITY_TO_RESOLUTION[root.quality] if root.will_resize else root._resize_ratio
        
        rounded_size = (root.size * resize_factor).to_round()
        tuple_size = rounded_size.to_tuple()
        
        coords = (0,0) if root.style.borderwidth <= 0 else (1,1)
        
        if root.style.borderwidth > 0:
            correct_mask: pygame.Surface = self._create_surf_base(rounded_size, sdf = sdf)
            offset = NvVector2(2,2) if sdf else  NvVector2(4,4) 
            mask_surf: pygame.Surface = root.cache.get_or_exec(CacheType.Surface, lambda: self._create_surf_base(rounded_size - offset, sdf = sdf)) # type: ignore
            
        else:
            mask_surf = correct_mask = self._create_surf_base(rounded_size, sdf = sdf)
            offset = NvVector2(0,0)
        final_surf = self.draw.create_clear(tuple_size, flags = pygame.SRCALPHA)
        
        if isinstance(root.style.gradient, Gradient):
            content_surf = root.cache.get_or_exec(CacheType.Scaled_Gradient, lambda: self._scale_gradient(rounded_size - offset))
        elif root.style.bgimage:
            content_surf = root.cache.get_or_exec(CacheType.Scaled_Image, lambda: self._scale_image(rounded_size - offset))
        else: content_surf = None
        
        if content_surf:
            AlphaBlit.blit(content_surf, correct_mask, (0,0))
            final_surf.blit(content_surf, coords)
        else:
            final_surf.blit(mask_surf, coords)
        
        if root._style.borderwidth > 0:
            cache_type = CacheType.Scaled_Borders if root.will_resize else CacheType.Borders
            if border := root.cache.get_or_exec(cache_type, lambda: self._create_outlined_rect(rounded_size, sdf = sdf)):
                if root._draw_borders:
                    final_surf.blit(border, (0, 0))
                
        if root.style.transparency: final_surf.set_alpha(root.style.transparency)
        return final_surf
    
    def _generate_image(self):
        root = self.root
        assert root.style.bgimage, "Bgimage not set"
        return self.draw.load_image(root.style.bgimage)

    def min_size(self, size: NvVector2): 
        return (max(1, int(size.x)), max(1, int(size.y)))
    
    def _scale_image(self, size = None): 
        root = self.root
        
        size = size or root._csize
        return self.draw.scale(root.cache.get_or_exec(CacheType.Image, self._generate_image), self.min_size(size))
    
    def _scale_gradient(self, size = None): 
        root = self.root
        
        size = size or root._csize
        return self.draw.scale(root.cache.get_or_exec(CacheType.Gradient, self._draw_gradient), self.min_size(size))

    def _scale_background(self, size = None): 
        root = self.root
        
        size = size or root._csize
        return self.draw.scale(root.cache.get_or_exec(CacheType.Background, self._generate_background), self.min_size(size))
    
    @staticmethod
    def _split_words(words: list, font: pygame.font.Font, x, marg = " "):
        current_line = ""
        force_next_line = False
        lines = []

        for word in words:
            if word == '\n': force_next_line = True
            with contextlib.suppress(Exception):
                w = word[0] + word[1]
                if w == '\\' + "n": force_next_line = True
            if force_next_line:
                lines.append(current_line)
                current_line = ""
                test_line = ""
                text_size = 0
                force_next_line = False
                continue

            test_line = current_line + word + marg
            text_size = font.size(test_line)
            if text_size[0] > x:
                lines.append(current_line)
                current_line = word + marg
            else: current_line = test_line
        lines.append(current_line)
        return lines
    
    def bake_text(self, text: str, unlimited_y: bool = False, words_indent: bool = False,
                  alignx: Align = Align.CENTER, aligny: Align = Align.CENTER, size: NvVector2 | None = None, color = None):
        root = self.root
        
        color = color or root.subtheme_font
        size = size or root._csize

        renderFont = root.get_font() 
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

        root._text_baked = "\n".join(lines)

        if is_cropped and not unlimited_y:
            root._text_baked = f"{root._text_baked[:-3]}..."

        root._text_surface = renderFont.render(root._text_baked, True, color)
        
        container_rect = pygame.Rect(root.coordinates.to_round().to_tuple(), root._csize.to_round()) if root.inline else root.surface.get_rect()
            
        text_rect = root._text_surface.get_rect()

        if alignx == Align.LEFT: text_rect.left = container_rect.left
        elif alignx == Align.CENTER: text_rect.centerx = container_rect.centerx
        elif alignx == Align.RIGHT: text_rect.right = container_rect.right

        if aligny == Align.TOP: text_rect.top = container_rect.top
        elif aligny == Align.CENTER: text_rect.centery = container_rect.centery
        elif aligny == Align.BOTTOM: text_rect.bottom = container_rect.bottom

        root._text_rect = text_rect