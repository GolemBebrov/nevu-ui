import nevu_ui.core.modules as md
from nevu_ui.fast.nvvector2.nvvector2 cimport NvVector2
from nevu_ui.fast.nvrect.nvrect cimport NvRect
from nevu_ui.presentation.color import Color
from nevu_ui.core.state import nevu_state
from nevu_ui.core.annotations import Annotations

cdef class NvRenderTexture:
    cdef public object render_texture 
    cdef public object size
    cdef public bint loaded
    @classmethod
    def from_rl_render_texture(cls, rl_render_texture: md.rl.RenderTexture): 
        cdef NvRenderTexture new_self = cls.__new__(cls)
        new_self.render_texture = rl_render_texture
        new_self.size = NvVector2.new(rl_render_texture.texture.width, rl_render_texture.texture.height)
        new_self.loaded = True # type: ignore
        return new_self
    
    def __init__(self, size: NvVector2):
        self.render_texture = md.rl.load_render_texture(int(size.x), int(size.y))
        self.size = size
        self.loaded = True # type: ignore
    
    @property
    def texture(self): return self.render_texture.texture # type: ignore
    
    @property
    def id(self): return self.render_texture.id # type: ignore
    
    @property
    def depth(self): return self.render_texture.depth # type: ignore
    
    cpdef void blit(self, nv_texture: NvRenderTexture, dest: Annotations.dest_like, blend_mode: int = 0, flip: bool = True, color: Annotations.rgba_color = Color.White):
        assert self.loaded, "Render texture not loaded"
        md.rl.begin_texture_mode(self.render_texture) # type: ignore
        self.fast_blit(nv_texture, dest, blend_mode, flip, color)
        md.rl.end_texture_mode()
    
    cpdef void fast_blit(self, nv_texture: NvRenderTexture, dest: Annotations.dest_like, blend_mode: int = 0, flip: bool = True, color: Annotations.rgba_color = Color.White):
        display = nevu_state.window.display
        assert nevu_state.window.is_raylib(display)
        display.blit_rect_vec(nv_texture.texture, dest, flip, color, mode=blend_mode)
        
    cpdef void clear(self, color: Annotations.rgba_color):
        assert self.loaded, "Render texture not loaded"
        md.rl.begin_texture_mode(self.render_texture) # type: ignore
        self.fast_clear(color)
        md.rl.end_texture_mode()
    
    cpdef void fast_clear(self, color: Annotations.rgba_color):
        display = nevu_state.window.display
        assert nevu_state.window.is_raylib(display)
        display.clear(color)
    
    cpdef void fill(self, color: Annotations.rgba_color): self.clear(color)
        
    cpdef void kill(self):
        assert self.loaded, "Render texture not loaded"
        md.rl.unload_render_texture(self.render_texture) # type: ignore
        self.loaded = False # type: ignore
    
    cpdef NvRect get_rect(self):
        return NvRect(0, 0, *self.size)
    
    def copy(self, flip: bool = True):
        assert self.loaded, "Render texture not loaded"
        new_nvtexture = NvRenderTexture(self.size) # type: ignore
        new_nvtexture.blit(self, (0, 0), md.rl.BlendMode.BLEND_ALPHA, flip)
        return new_nvtexture
    
    def __dealloc__(self):
        try:
            if hasattr(self, 'render_texture') and self.loaded and md.rl.is_window_ready():
                md.rl.unload_render_texture(self.render_texture) # type: ignore
        except Exception: pass
        
    def __enter__(self):
        assert self.loaded, "Render texture not loaded"
        md.rl.begin_texture_mode(self.render_texture) # type: ignore
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        md.rl.end_texture_mode()