import pygame

from nevu_ui.color import Color
from nevu_ui.nevuobj import NevuObject
from nevu_ui.fast.nvvector2 import NvVector2

from nevu_ui.core_types import (
    _QUALITY_TO_RESOLUTION, CacheType, HoverState
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
    
    def _create_surf_base(renderer, size = None, alt = False, radius = None): # type: ignore
        self = renderer.root
        
        needed_size = size or self._csize
        needed_size.to_round()
        
        surf = pygame.Surface(needed_size.to_tuple(), pygame.SRCALPHA)
        surf.fill((0,0,0,0))
        
        color = self._subtheme_font if alt else self._subtheme_content
        
        if self._hover_state == HoverState.CLICKED and not self.fancy_click_style and self.clickable: 
            color = Color.lighten(color, 0.2)
        elif self._hover_state == HoverState.HOVERED and self.hoverable: 
            color = Color.darken(color, 0.2)
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
        
        return OutlinedRoundedRect.create_sdf(needed_size.to_tuple(), round(radius), round(width), self._subtheme_font)
    
    def _generate_background(renderer): # type: ignore
        self = renderer.root
        resize_factor = _QUALITY_TO_RESOLUTION[self.quality] if self.will_resize else self._resize_ratio
        
        rounded_size = (self.size * resize_factor).to_round()
        tuple_size = rounded_size.to_tuple()
        
        coords = (0,0) if self.style.borderwidth <= 0 else (1,1)
        
        if self.style.borderwidth > 0:
            correct_mask: pygame.Surface = renderer._create_surf_base(rounded_size)
            mask_surf: pygame.Surface = self.cache.get_or_exec(CacheType.Surface, lambda: renderer._create_surf_base(rounded_size - NvVector2(2,2))) # type: ignore
        else:
            mask_surf = correct_mask = renderer._create_surf_base(rounded_size)
            
        final_surf = pygame.Surface(tuple_size, flags = pygame.SRCALPHA)
        final_surf.fill((0,0,0,0))
        
        if isinstance(self.style.gradient, Gradient):
            content_surf = self.cache.get_or_exec(CacheType.Scaled_Gradient, lambda: renderer._scale_gradient(rounded_size))
        elif self.style.bgimage:
            img = pygame.image.load(self.style.bgimage)
            img.convert_alpha()
            content_surf = pygame.transform.smoothscale(img, tuple_size)
        else: content_surf = None
        
        if content_surf:
            AlphaBlit.blit(content_surf, correct_mask, coords)
            final_surf.blit(content_surf, coords)
        else:
            final_surf.blit(mask_surf, coords)
        
        if self._style.borderwidth > 0:
            cache_type = CacheType.Scaled_Borders if self.will_resize else CacheType.Borders
            if border := self.cache.get_or_exec(cache_type, lambda: renderer._create_outlined_rect(rounded_size)):
                final_surf.blit(border, (0, 0))
                
        if self.style.transparency: final_surf.set_alpha(self.style.transparency)
        return final_surf
    
    def _scale_background(renderer, size = None): # type: ignore
        self = renderer.root
        size = size or self._csize
        
        surf = self.cache.get_or_exec(CacheType.Background, renderer._generate_background)
        assert surf
        
        return pygame.transform.smoothscale(surf, (max(1, int(size.x)), max(1, int(size.y))))