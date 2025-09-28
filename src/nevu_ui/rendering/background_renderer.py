import pygame

from nevu_ui.color import Color
from nevu_ui.nevuobj import NevuObject

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
    def _draw_gradient(renderer, _set = False):
        self = renderer.root
        if not self.style.gradient: return
        
        cached_gradient = pygame.Surface(self.size*_QUALITY_TO_RESOLUTION[self.quality], flags = pygame.SRCALPHA)
        if self.style.transparency: cached_gradient = self.style.gradient.with_transparency(self.style.transparency).apply_gradient(cached_gradient)
        else: cached_gradient =  self.style.gradient.apply_gradient(cached_gradient)
        if _set:
            self.cache.set(CacheType.Gradient, cached_gradient)
        else:
            return cached_gradient
    def _scale_gradient(renderer, size = None):
        self = renderer.root
        if not self.style.gradient: return
        size = size or self.size * self._resize_ratio
        cached_gradient = self.cache.get_or_exec(CacheType.Gradient, renderer._draw_gradient)
        if cached_gradient is None: return
        target_size_vector = size
        target_size_tuple = (
            max(1, int(target_size_vector.x)), 
            max(1, int(target_size_vector.y))
        )
        cached_gradient = pygame.transform.smoothscale(cached_gradient, target_size_tuple)
        return cached_gradient
    def _create_surf_base(renderer, size = None, alt = False, radius = None):
        self = renderer.root
        needed_size = (self.size*self._resize_ratio).xy if size is None else size
        surf = pygame.Surface((int(needed_size[0]), int(needed_size[1])), pygame.SRCALPHA)
        surf.fill((0,0,0,0))
        color = self._subtheme_content if not alt else self._subtheme_font
        if self.will_resize:
            avg_scale_factor = _QUALITY_TO_RESOLUTION[self.quality]
        else:
            avg_scale_factor = (self._resize_ratio[0] + self._resize_ratio[1]) / 2

        radius = (self._style.borderradius * avg_scale_factor) if radius is None else radius
        surf.blit(RoundedRect.create_sdf([int(needed_size[0]), int(needed_size[1])], int(radius), color), (0, 0))
        return surf
    
    def _create_outlined_rect(renderer, size = None):
        self = renderer.root
        needed_size = (self.size * self._resize_ratio).xy if size is None else size
        if self.will_resize:
            avg_scale_factor = _QUALITY_TO_RESOLUTION[self.quality]
        else:
            avg_scale_factor = (self._resize_ratio[0] + self._resize_ratio[1]) / 2
        radius = self._style.borderradius * avg_scale_factor
        width = self._style.borderwidth * avg_scale_factor
        return OutlinedRoundedRect.create_sdf([int(needed_size[0]), int(needed_size[1])], int(radius), int(width), self._subtheme_font)
    
    def _generate_background(renderer):
        self = renderer.root
        resize_factor = _QUALITY_TO_RESOLUTION[self.quality] if self.will_resize else self._resize_ratio
        bgsurface = pygame.Surface(self.size * resize_factor, flags = pygame.SRCALPHA)
        if isinstance(self.style.gradient, Gradient):
            content_surf = self.cache.get_or_exec(CacheType.Scaled_Gradient, lambda: renderer._scale_gradient(self.size * resize_factor))
            if self.style.transparency: bgsurface.set_alpha(self.style.transparency)
        else: content_surf = self.cache.get(CacheType.Scaled_Gradient)
        if content_surf:
            bgsurface.blit(content_surf,(0,0))
        elif self._hover_state == HoverState.UN_HOVERED or not self.hoverable: bgsurface.fill(self._subtheme_content)
        elif self._hover_state == HoverState.CLICKED and not self.fancy_click_style: bgsurface.fill(Color.lighten(self._subtheme_content))
        else: bgsurface.fill(Color.darken(self._subtheme_content, 0.2))
        if self._style.bgimage:
            img = pygame.image.load(self._style.bgimage)
            img.convert_alpha()
            bgsurface.blit(pygame.transform.smoothscale(img, self.size * resize_factor),(0,0))
        if self._style.borderwidth > 0:
            border = self.cache.get_or_exec(CacheType.Borders, lambda: renderer._create_outlined_rect(self.size * resize_factor))
            if border:
                bgsurface.blit(border,(0,0))
        if self._style.borderradius > 0:
            mask_surf = self.cache.get_or_exec(CacheType.Surface, lambda: renderer._create_surf_base(self.size * resize_factor))
            if mask_surf:
                AlphaBlit.blit(bgsurface, mask_surf,(0,0))
        return bgsurface
    
    def _scale_background(renderer, size = None):
        self = renderer.root
        size = size if size else self.size*self._resize_ratio
        surf = self.cache.get_or_exec(CacheType.Background, renderer._generate_background)
        assert surf
        surf = pygame.transform.smoothscale(surf, (max(1, int(size.x)), max(1, int(size.y))))
        return surf