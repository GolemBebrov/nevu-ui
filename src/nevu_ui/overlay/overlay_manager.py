import pygame
from pygame._sdl2 import Texture
from typing import Any

from nevu_ui.fast.nvvector2 import NvVector2
from nevu_ui.core.state import nevu_state

class OverlayManager:
    PipelineItem = tuple[pygame.Surface, NvVector2, int | float]
    layer_type = float | int
    def __init__(self):
        self.pipeline: dict[str, OverlayManager.PipelineItem] = {}
        self._init_markers()
        self._init_cache()

    def _init_markers(self):
        self._rendered = False
        self._rendered_sdl = False
        self._sorted = False
    
    def _init_cache(self):
        self._rendered_cache: pygame.Surface = None #type: ignore
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

    def add_element(self, name, surface, coordinates: NvVector2, layer: layer_type = 0):
        self.pipeline[name] = (surface, coordinates, layer)
        self.mark_all()
    
    def _validate_strict(self, name: Any, strict: bool, function = None):
        if not strict and function: function()
        else: raise ValueError(f"Element {name} not found and cannot be changed")
        
    def remove_element(self, name: Any, strict: bool = False):
        if self.has_element(name):
            del self.pipeline[name]
            self.mark_all()
        else: self._validate_strict(name, strict)
    
    def change_element(self, name: Any, surface, coordinates: NvVector2, layer: layer_type = 0, strict: bool = False):
        if self.has_element(name):
            self.pipeline[name] = (surface, coordinates, layer)
            self.mark_all()
        else: self._validate_strict(name, strict, lambda: self.add_element(name, surface, coordinates, layer))
    
    def change_coordinates(self, name: Any, coordinates: NvVector2, strict: bool = False):
        if self.has_element(name):
            curr_item = self.pipeline[name]
            self.pipeline[name] = (curr_item[0], coordinates, curr_item[2])
            self.mark_all()
        else: self._validate_strict(name, strict, lambda: print(f"Element {name} not found and cannot be changed")) #TODO потом, в 0.9
    
    def change_layer(self, name: Any, layer: layer_type, strict: bool = False):
        if self.has_element(name):
            curr_item = self.pipeline[name]
            self.pipeline[name] = (curr_item[0], curr_item[1], layer)
            self.mark_all()
        else: self._validate_strict(name, strict, lambda: print(f"Element {name} not found and cannot be changed")) #TODO!!!!!!
    
    def change_surface(self, name: Any, surface: pygame.Surface, strict: bool = False):
        if self.has_element(name):
            curr_item = self.pipeline[name]
            self.pipeline[name] = (surface, curr_item[1], curr_item[2])
            self.mark_all() 
        else: self._validate_strict(name, strict, lambda: print(f"Element {name} not found and cannot be changed")) #Totya(#TODO#!#!#1!!!!!!)
    
    def has_element(self, name): return name in self.pipeline
    
    @property
    def sorted_pipeline(self):
        if not self._sorted: 
            self._sorted = True
            self._sorted_cache = sorted(self.pipeline.items(), key=lambda x: x[1][2])
        return self._sorted_cache
    
    def draw_pipeline(self, surface: pygame.Surface):
        if surface.size != self._cached_size:
            self.mark_undone()
            self._cached_size = surface.size
        if self._rendered:
            surface.blit(self._rendered_cache, (0,0))
            return
        for element in self.sorted_pipeline:
            surf = element[1][0]
            coords: NvVector2 = element[1][1]
            surface.blit(surf, coords.to_tuple())
    
    def get_result(self, size):
        if size != self._cached_size:
            self.mark_undone()
            self._cached_size = size
        if self._rendered: return self._rendered_cache
        result = pygame.Surface(size, flags = pygame.SRCALPHA)
        self.draw_pipeline(result)
        self._rendered_cache = result
        self._rendered = True
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