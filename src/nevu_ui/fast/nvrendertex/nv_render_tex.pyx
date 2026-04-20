import nevu_ui.core.modules as md
from nevu_ui.fast.nvvector2.nvvector2 cimport NvVector2
from nevu_ui.fast.nvrect.nvrect cimport NvRect
from nevu_ui.presentation.color import Color
from nevu_ui.core.state import nevu_state
from nevu_ui.core.annotations import Annotations      
from nevu_ui.fast.raylib.nevu_raylib cimport begin_blend_mode, end_blend_mode, begin_texture_mode, end_texture_mode, c_draw_texture_rec, c_draw_texture_vec, clear_background, c_clear_background

cdef class NvRenderTexture:
    cdef public object render_texture 
    cdef public NvVector2 size
    cdef public bint loaded
    @staticmethod
    def from_rl_render_texture(rl_render_texture):
        cdef NvRenderTexture new_self = NvRenderTexture.__new__(NvRenderTexture)
        new_self.render_texture = rl_render_texture
        new_self.size = NvVector2.new(rl_render_texture.texture.width, rl_render_texture.texture.height)
        new_self.loaded = True # type: ignore
        return new_self
    
    def __init__(self, size: NvVector2):
        self.render_texture = md.rl.load_render_texture(int(size.x), int(size.y)) # type: ignore
        self.size = size
        self.loaded = True # type: ignore
    
    @property
    def texture(self): return self.render_texture.texture
    
    @property
    def id(self): return self.render_texture.id
    
    @property
    def depth(self): return self.render_texture.depth
    
    cpdef void blit(self, NvRenderTexture nv_texture, dest: Annotations.dest_like, int blend_mode = 0, bint flip = True, tuple color = Color.White):
        assert self.loaded, "Render texture not loaded"
        begin_blend_mode(blend_mode)
        begin_texture_mode(self.render_texture) # type: ignore
        self.c_fast_blit(nv_texture, dest, flip, color)
        end_texture_mode()
        end_blend_mode()
    
    cdef inline void c_fast_blit(self, NvRenderTexture nv_texture, tuple dest, bint flip = True, tuple color = Color.White):
        h = -nv_texture.height if flip else nv_texture.height
        cdef Py_ssize_t dest_len = <Py_ssize_t>len(dest)
        if dest_len == 2:
            c_draw_texture_vec(nv_texture.render_texture.texture, dest, color, flip)
        elif dest_len == 4:
            c_draw_texture_rec(nv_texture.render_texture.texture, (0,0, nv_texture.width, h), dest, color)
        else:
            raise ValueError(f"Invalid dest argument - {dest}, must be (x, y) or (x, y, width, height)")

    cpdef void fast_blit(self, NvRenderTexture nv_texture, tuple dest, bint flip = True, tuple color = Color.White):
        self.c_fast_blit(nv_texture, dest, flip, color)
    
    cpdef void blit_texture(self, texture: object, dest: Annotations.dest_like, int blend_mode = 0, bint flip = True, tuple color = Color.White):
        assert self.loaded, "Render texture not loaded"
        begin_texture_mode(self.render_texture) # type: ignore
        self.fast_blit_texture(texture, dest, flip, color)
        end_texture_mode()
    
    cpdef void fast_blit_texture(self, texture: object, dest: Annotations.dest_like, bint flip = True, tuple color = Color.White):
        display = nevu_state.window.display
        assert nevu_state.window.is_raylib(display)
        display.fast_blit_pro(texture, dest, flip, color)

    cdef inline void c_fast_clear(self, tuple color):
        c_clear_background(color)
    
    cdef inline void c_clear(self, tuple color):
        begin_texture_mode(self.render_texture) # type: ignore
        self.c_fast_clear(color)
        end_texture_mode()

    cpdef void clear(self, tuple color):
        assert self.loaded, "Render texture not loaded"
        self.c_clear(color)
    
    cpdef void fast_clear(self, tuple color):
        assert self.loaded, "Render texture not loaded"
        self.c_fast_clear(color)
    
    cpdef void fill(self, tuple color): 
        assert self.loaded, "Render texture not loaded"
        self.c_clear(color)
        
    cpdef void kill(self):
        assert self.loaded, "Render texture not loaded"
        md.rl.unload_render_texture(self.render_texture) # type: ignore
        self.loaded = False # type: ignore
    
    cpdef NvRect get_rect(self):
        return NvRect.new(0, 0, self.size.x, self.size.y)
    
    cpdef double get_height(self): return self.size.y
    cpdef double get_width(self): return self.size.x

    @property
    def width(self): return self.size.x
    @property
    def height(self): return self.size.y

    cpdef NvRenderTexture copy(self, bint flip = True):
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
        begin_texture_mode(self.render_texture) # type: ignore
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        end_texture_mode()