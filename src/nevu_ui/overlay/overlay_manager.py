from nevu_ui.fast.nvvector2 import NvVector2
from pygame import Surface
import pygame
from pygame._sdl2 import Texture
from nevu_ui.core.state import nevu_state

class OverlayManager:
    PipelineItem = tuple[Surface, NvVector2, int | float]
    def __init__(self):
        self.pipeline: dict[str, OverlayManager.PipelineItem] = {}
        self._init_markers()
        self._init_cache()

    def _init_markers(self):
        self._rendered = False
        self._rendered_sdl = False
        self._sorted = False
    
    def _init_cache(self):
        self._rendered_cache: Surface = None #type: ignore
        self._rendered_sdl_cache = None
        self._sorted_cache = {}
        self._cached_size = None

    def mark_unsorted(self):
        self._sorted = False
        self._sorted_cache = {}
    
    def mark_undone(self):
        self._rendered = False
        self.mark_sdl_undone()
    
    def mark_sdl_undone(self):
        self._rendered_sdl = False
    
    def mark_all(self):
        self.mark_unsorted()
        self.mark_undone()
        self.mark_sdl_undone()
        
    def add_action(self, name, surface, coordinates: NvVector2, layer: int | float = 0):
        self.pipeline[name] = (surface, coordinates, layer)
        self.mark_all()
    
    def remove_action(self, name, strict: bool = False):
        if name in self.pipeline:
            del self.pipeline[name]
            self.mark_all()
        elif strict:
            raise ValueError(f"Action {name} not found and cannot be removed")
    
    def change_action(self, name, surface, coordinates: NvVector2, layer: int | float = 0, strict: bool = False):
        if name in self.pipeline:
            self.pipeline[name] = (surface, coordinates, layer)
            self.mark_all()
        elif not strict:
            self.add_action(name, surface, coordinates, layer)
        else: raise ValueError(f"Action {name} not found and cannot be changed")
        
    @property
    def sorted_pipeline(self):
        if not self._sorted: 
            self._sorted = True
            self._sorted_cache = sorted(self.pipeline.items(), key=lambda x: x[1][2])
        return self._sorted_cache
    
    def draw_pipeline(self, surface: Surface):
        if surface.size != self._cached_size:
            self.mark_undone()
            self._cached_size = surface.size
        if self._rendered:
            surface.blit(self._rendered_cache, (0,0))
            return
        for action in self.sorted_pipeline:
            surf = action[1][0]
            coords: NvVector2 = action[1][1]
            surface.blit(surf, coords.to_int().to_tuple())
    
    def get_result(self, size):
        if size != self._cached_size:
            self.mark_undone()
            self._cached_size = size
        if self._rendered: return self._rendered_cache
        result = Surface(size, flags = pygame.SRCALPHA)
        self.draw_pipeline(result)
        self._rendered_cache = result
        return result
    
    def get_result_sdl(self, size):
        assert nevu_state.renderer, "Renderer not initialized!"
        if size != self._cached_size:
            self.mark_sdl_undone()
            self._cached_size = size
        if self._rendered_sdl: return self._rendered_sdl_cache
        result = self._rendered_cache if self._rendered else self.get_result(size)
        texture_result = Texture.from_surface(nevu_state.renderer, result)
        self._rendered_sdl_cache = texture_result
        return texture_result

overlay = OverlayManager()