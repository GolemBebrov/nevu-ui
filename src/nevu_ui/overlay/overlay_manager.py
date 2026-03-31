from typing import Any, TYPE_CHECKING

if TYPE_CHECKING:
    from pygame import Surface

import nevu_ui.core.modules as md
from nevu_ui.fast.nvvector2 import NvVector2
from nevu_ui.core.state import nevu_state
from nevu_ui.core.enums import Backend, OvItemType

class OverlayManager:
    SurfaceType = Any
    PipelineItem = tuple[SurfaceType, NvVector2, int | float, OvItemType]
    layer_type = float | int
    def __init__(self):
        self.pipeline: dict[str, OverlayManager.PipelineItem] = {}
        self._init_markers()
        self._init_cache()

    def _init_markers(self):
        self._rendered = False
        self._sorted = False
    
    def _init_cache(self):
        self._rendered_cache: Any | None = None
        self._sorted_cache = {}
        self._cached_size = None

    def mark_unsorted(self):
        self._sorted = False
        self._sorted_cache = {}
    
    def mark_undone(self):
        self._rendered = False
    
    def mark_all(self):
        self.mark_unsorted()
        self.mark_undone()

    def add_element(self, name, surface, coordinates: NvVector2, layer: layer_type = 0):
        self.pipeline[name] = (surface, coordinates, layer, OvItemType.Texture)
        self.mark_all()
    
    def add_draw_call(self, name, func, coordinates: NvVector2, layer: layer_type = 0):
        self.pipeline[name] = (func, coordinates, layer, OvItemType.DrawCall)
        self.mark_all()
    
    def _validate_strict(self, name: Any, strict: bool, function = None):
        if not strict and function: function()
        else: raise ValueError(f"Element {name} not found and cannot be changed")
        
    def remove_element(self, name: Any, strict: bool = False):
        if self.has_element(name):
            del self.pipeline[name]
            self.mark_all()
        else: self._validate_strict(name, strict)
    
    def change_element(self, name: Any, surface, coordinates: NvVector2, layer: layer_type = 0, strict: bool = False, type: OvItemType | None = None):
        if self.has_element(name):
            self.pipeline[name] = (surface, coordinates, layer, type or self.pipeline[name][3])
            self.mark_all()
        else: self._validate_strict(name, strict, lambda: self.add_element(name, surface, coordinates, layer))
    
    def change_coordinates(self, name: Any, coordinates: NvVector2, strict: bool = False, type: OvItemType | None = None):
        if self.has_element(name):
            curr_item = self.pipeline[name]
            self.pipeline[name] = (curr_item[0], coordinates, curr_item[2], type or self.pipeline[name][3])
            self.mark_all()
        else: self._validate_strict(name, strict, lambda: print(f"Element {name} not found and cannot be changed"))
    
    def change_layer(self, name: Any, layer: layer_type, strict: bool = False, type: OvItemType | None = None):
        if self.has_element(name):
            curr_item = self.pipeline[name]
            self.pipeline[name] = (curr_item[0], curr_item[1], layer, type or self.pipeline[name][3])
            self.mark_all()
        else: self._validate_strict(name, strict, lambda: print(f"Element {name} not found and cannot be changed"))
    
    def change_surface(self, name: Any, surface: "Surface", strict: bool = False, type: OvItemType | None = None):
        if self.has_element(name):
            curr_item = self.pipeline[name]
            self.pipeline[name] = (surface, curr_item[1], curr_item[2], type or self.pipeline[name][3])
            self.mark_all() 
        else: self._validate_strict(name, strict, lambda: print(f"Element {name} not found and cannot be changed"))
    
    def has_element(self, name): return name in self.pipeline
    def get_element(self, name, default = None): return self.pipeline.get(name, default)
    def get_element_strict(self, name): return self.pipeline[name] 
    
    @property
    def sorted_pipeline(self):
        if not self._sorted: 
            self._sorted = True
            self._sorted_cache = sorted(self.pipeline.items(), key=lambda x: x[1][2])
        return self._sorted_cache
    
    def draw_pipeline(self, surface: Any):
        assert nevu_state.window
        if self._get_surf_size(surface) != self._cached_size:
            self.mark_undone()
            self._cached_size = self._get_surf_size(surface)
            
        if self._rendered:
            if nevu_state.window.is_dtype.raylib:
                display = nevu_state.window.display
                assert nevu_state.window.is_raylib(display)
                md.rl.begin_texture_mode(surface)
                display.blit(self._rendered_cache, (0,0))
                md.rl.end_texture_mode()
            else: surface.blit(self._rendered_cache, (0,0))
            return
        
        if not nevu_state.window.is_dtype.raylib:
            for element in self.sorted_pipeline:
                surf = element[1][0]
                coords: NvVector2 = element[1][1]
                surface.blit(surf, coords.to_tuple())
        else:
            md.rl.begin_texture_mode(surface)
            display = nevu_state.window.display
            assert nevu_state.window.is_raylib(display)
            for element in self.sorted_pipeline:
                surf = element[1][0]
                coords: NvVector2 = element[1][1]
                if element[1][3] == OvItemType.DrawCall:
                    func = element[1][0]
                    func()
                else:
                    display.blit(surf.texture, coords.to_tuple())
            md.rl.end_texture_mode()
            
    def get_result(self, size):
        if size.get_int_tuple() != self._cached_size:
            self.mark_undone()
            self._cached_size = size
        if self._rendered: 
            for element in self.sorted_pipeline:
                if element[1][3] == OvItemType.DrawCall:
                    func = element[1][0]
                    func()
                    
            return self._rendered_cache
        result = self._get_result_surface(size)
        self.draw_pipeline(result)
        if nevu_state.window.is_dtype.raylib and self._rendered_cache: 
            md.rl.unload_render_texture(self._rendered_cache)
        result = self._finish_result(result)
        self._rendered_cache = result
        self._rendered = True
        return result

    def _get_surf_size(self, surface):
        match nevu_state.window._backend:
            case Backend.Pygame | Backend.Sdl: return surface.size
            case Backend.RayLib: return (surface.texture.width, surface.texture.height)
    
    def _finish_result(self, result):
        match nevu_state.window._backend:
            case Backend.Pygame | Backend.RayLib: return result
            case Backend.Sdl: return md.pygame._sdl2.Texture.from_surface(nevu_state.renderer, result)
    
    def _get_result_surface(self, size):
        match nevu_state.window._backend:
            case Backend.Pygame | Backend.Sdl:
                return md.pygame.Surface(size, flags = md.pygame.SRCALPHA)
            case Backend.RayLib:
                txture = md.rl.load_render_texture(int(size[0]), int(size[1]))
                md.rl.set_texture_filter(txture.texture, md.rl.TextureFilter.TEXTURE_FILTER_BILINEAR)
                #md.rl.set_texture_wrap(txture.texture, md.rl.TextureWrap.TEXTURE_WRAP_CLAMP)
                md.rl.begin_texture_mode(txture)
                nevu_state.window.display.clear(md.rl.BLANK)
                md.rl.end_texture_mode()
                return txture

overlay = OverlayManager()