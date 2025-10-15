import pygame
import contextlib

from nevu_ui.color import Color
from nevu_ui.nevuobj import NevuObject
from nevu_ui.fast.nvvector2 import NvVector2

from nevu_ui.core_types import (
    _QUALITY_TO_RESOLUTION, CacheType, HoverState, Align
)
from nevu_ui.rendering import (
    OutlinedRoundedRect, RoundedRect, AlphaBlit, Gradient
)
class BackgroundRenderer:
    def __init__(self, root: NevuObject):
        assert isinstance(root, NevuObject)
        self.root = root
        
    def _draw_gradient(renderer): # type: ignore
        self = renderer.root
        
        if not self.style.gradient: return
        
        cached_gradient = pygame.Surface(self.size * _QUALITY_TO_RESOLUTION[self.quality], flags = pygame.SRCALPHA)
        cached_gradient.fill((0,0,0,0))
        
        if self.style.transparency: cached_gradient = self.style.gradient.with_transparency(self.style.transparency).apply_gradient(cached_gradient)
        else: cached_gradient =  self.style.gradient.apply_gradient(cached_gradient)
        
        return cached_gradient
    
    def _scale_gradient(renderer, size = None): # type: ignore
        self = renderer.root
        
        if not self.style.gradient: return
        
        size = size or self._csize
        cached_gradient = self.cache.get_or_exec(CacheType.Gradient, renderer._draw_gradient)
        if cached_gradient is None: return
        
        target_size_vector = size
        target_size_tuple = (
            max(1, int(target_size_vector.x)), 
            max(1, int(target_size_vector.y))
        )
        
        cached_gradient = pygame.transform.smoothscale(cached_gradient, target_size_tuple)
        return cached_gradient
    
    def _create_surf_base(renderer, size = None, alt = False, radius = None, standstill = False, override_color = None): # type: ignore
        self = renderer.root
        
        needed_size = size or self._csize
        needed_size.to_round()
        
        surf = pygame.Surface(needed_size.to_tuple(), pygame.SRCALPHA)
        surf.fill((0,0,0,0))
        
        color = self._subtheme_border if alt else self._subtheme_content
        
        if not standstill:
            if self._hover_state == HoverState.CLICKED and not self.fancy_click_style and self.clickable: 
                color = Color.lighten(color, 0.2)
            elif self._hover_state == HoverState.HOVERED and self.hoverable: 
                color = Color.darken(color, 0.2)
        
        if override_color:
            color = override_color
        
        if self.will_resize:
            avg_scale_factor = _QUALITY_TO_RESOLUTION[self.quality]
        else:
            avg_scale_factor = (self._resize_ratio.x + self._resize_ratio.y) / 2
        
        radius = (self._style.borderradius * avg_scale_factor) if radius is None else radius
        surf.blit(RoundedRect.create_sdf(needed_size.to_tuple(), round(radius), color), (0, 0))
        
        return surf
    
    def _create_outlined_rect(renderer, size = None, radius = None, width = None): # type: ignore
        self = renderer.root
        
        needed_size = size or self._csize
        needed_size.to_round()
        
        if self.will_resize:
            avg_scale_factor = _QUALITY_TO_RESOLUTION[self.quality]
        else:
            avg_scale_factor = (self._resize_ratio[0] + self._resize_ratio[1]) / 2
            
        radius = radius or self._style.borderradius * avg_scale_factor
        width = width or self._style.borderwidth * avg_scale_factor
        
        return OutlinedRoundedRect.create_sdf(needed_size.to_tuple(), round(radius), round(width), self._subtheme_border)
    
    def _get_correct_mask(renderer): # type: ignore
        self = renderer.root
        size = self._csize.to_round().copy()
        if self.style.borderwidth > 0:
            size -= NvVector2(2,2)
        
        return renderer._create_surf_base(size, self.alt, self.relm(self.style.borderradius))
    
    def _generate_background(renderer): # type: ignore
        self = renderer.root
        resize_factor = _QUALITY_TO_RESOLUTION[self.quality] if self.will_resize else self._resize_ratio
        
        rounded_size = (self.size * resize_factor).to_round()
        tuple_size = rounded_size.to_tuple()
        
        coords = (0,0) if self.style.borderwidth <= 0 else (1,1)
        
        if self.style.borderwidth > 0:
            correct_mask: pygame.Surface = renderer._create_surf_base(rounded_size)
            mask_surf: pygame.Surface = self.cache.get_or_exec(CacheType.Surface, lambda: renderer._create_surf_base(rounded_size - NvVector2(2,2))) # type: ignore
            offset = NvVector2(2,2)
        else:
            mask_surf = correct_mask = renderer._create_surf_base(rounded_size)
            offset = NvVector2(0,0)
        final_surf = pygame.Surface(tuple_size, flags = pygame.SRCALPHA)
        final_surf.fill((0,0,0,0))
        
        if isinstance(self.style.gradient, Gradient):
            content_surf = self.cache.get_or_exec(CacheType.Scaled_Gradient, lambda: renderer._scale_gradient(rounded_size - offset))
        elif self.style.bgimage:
            content_surf = self.cache.get_or_exec(CacheType.Scaled_Image, lambda: renderer._scale_image(rounded_size - offset))
        else: content_surf = None
        
        if content_surf:
            AlphaBlit.blit(content_surf, correct_mask, (0,0))
            final_surf.blit(content_surf, coords)
        else:
            final_surf.blit(mask_surf, coords)
        
        if self._style.borderwidth > 0:
            cache_type = CacheType.Scaled_Borders if self.will_resize else CacheType.Borders
            if border := self.cache.get_or_exec(cache_type, lambda: renderer._create_outlined_rect(rounded_size)):
                if self._draw_borders:
                    final_surf.blit(border, (0, 0))
                
        if self.style.transparency: final_surf.set_alpha(self.style.transparency)
        return final_surf
    
    def _generate_image(renderer): # type: ignore
        self = renderer.root
        assert self.style.bgimage, "Bgimage not set"
        img = pygame.image.load(self.style.bgimage)
        img.convert_alpha()
        return img
    
    def _scale_image(renderer, size = None): # type: ignore
        self = renderer.root
        size = size or self._csize
        
        img = self.cache.get_or_exec(CacheType.Image, renderer._generate_image)
        assert img
        
        return pygame.transform.smoothscale(img, (max(1, int(size.x)), max(1, int(size.y))))
    
    def _scale_background(renderer, size = None): # type: ignore
        self = renderer.root
        size = size or self._csize
        
        surf = self.cache.get_or_exec(CacheType.Background, renderer._generate_background)
        assert surf
        
        return pygame.transform.smoothscale(surf, (max(1, int(size.x)), max(1, int(size.y))))
    
    def bake_text(renderer, text: str, unlimited_y: bool = False, words_indent: bool = False,
                  alignx: Align = Align.CENTER, aligny: Align = Align.CENTER, continuous: bool = False, size_x = None, size_y = None, color = None):
        self = renderer.root
        if continuous: 
            self._bake_text_single_continuous(text)
            return
        color = color or self._subtheme_font
        size_x = size_x or self.relx(self.size.x)
        size_y = size_y or self.rely(self.size.y)
        is_popped = False
        ifnn = False

        current_line = ""
        marg = ""
        words = list(text)
        lines = []

        renderFont = self.get_font() 
        line_height = renderFont.size("a")[1]

        if words_indent:
            words = text.strip().split()
            marg = " "

        for word in words:
            if word == '\n': ifnn = True
            with contextlib.suppress(Exception):
                w = word[0] + word[1]
                if w == '\ '.strip()+"n": ifnn = True # type: ignore
            if ifnn:
                lines.append(current_line)
                current_line = ""
                test_line = ""
                text_size = 0
                ifnn = False
                continue

            test_line = current_line + word + marg
            text_size = renderFont.size(test_line)
            if text_size[0] > size_x:
                lines.append(current_line)
                current_line = word + marg
            else: current_line = test_line
        lines.append(current_line)

        if not unlimited_y:
            while len(lines) * line_height > size_y:
                lines.pop(-1)
                is_popped = True

        self._text_baked = "\n".join(lines)

        if is_popped and not unlimited_y:
                 self._text_baked = f"{self._text_baked[:-3]}..."

        self._text_surface = renderFont.render(self._text_baked, True, color)
        
        container_rect = pygame.Rect(self.coordinates.to_round().to_tuple(), self._csize.to_round()) if self.inline else self.surface.get_rect()
            
        text_rect = self._text_surface.get_rect()

        if alignx == Align.LEFT: text_rect.left = container_rect.left
        elif alignx == Align.CENTER: text_rect.centerx = container_rect.centerx
        elif alignx == Align.RIGHT: text_rect.right = container_rect.right

        if aligny == Align.TOP: text_rect.top = container_rect.top
        elif aligny == Align.CENTER: text_rect.centery = container_rect.centery
        elif aligny == Align.BOTTOM: text_rect.bottom = container_rect.bottom

        self._text_rect = text_rect

    def _bake_text_single_continuous(renderer, text: str): # type: ignore
        self = renderer.root  
        assert hasattr(self, "_entered_text")
              
        renderFont = self.get_font()
        self.font_size = renderFont.size(text)
        self._text_surface = renderFont.render(self._entered_text, True, self._subtheme_font) #type: ignore
        
        if not self.font_size[0] + self.relx(10) >= self._csize[0]: 
            self._text_rect = self._text_surface.get_rect(left = self.relx(10), centery = self._csize.y / 2)
        else: self._text_rect = self._text_surface.get_rect(right = self.relx(self._csize.x - 10), centery = self._csize.y / 2)
