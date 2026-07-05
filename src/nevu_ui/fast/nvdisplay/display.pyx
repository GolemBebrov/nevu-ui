import nevu_ui.core.modules as md
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from pyray import Texture
from nevu_ui.core import Annotations
from nevu_ui.presentation.color import Color
from nevu_ui.fast.shaders import SdfShader, BorderShader
from nevu_ui.fast.nvrect.nvrect cimport NvRect
from nevu_ui.fast.nvvector2.nvvector2 cimport NvVector2
from nevu_ui.fast.raylib.nevu_raylib cimport (
    init_raylib_pointers, begin_blend_mode, end_blend_mode, begin_texture_mode, end_texture_mode, 
    c_draw_texture_pro, c_draw_texture_rec, c_draw_texture_vec, set_nvshader_value, begin_nvshader_mode, end_shader_mode, begin_drawing, end_drawing,
    get_nvshader_location, set_nvshader_value_float, set_nvshader_value_vec2_nvvec, set_nvshader_value_vec4_tuple, set_nvshader_value_vec2_tuple
)
from nevu_ui.fast.nvshader.nvshader cimport NvShader

# SDL
cdef type sdl_window_t, sdl_renderer_t, sdl_texture_t, sdl_image_t #type: ignore

# Pygame
cdef type pg_surface_t, pg_rect_t #type: ignore

cdef bint window_renderer_created = False
cdef tuple fill_color = Color.White

cdef inline void check_singleton() noexcept:
    global window_renderer_created
    #if window_renderer_created: raise RuntimeError("Window renderer already created")
    window_renderer_created = True

cdef class WindowRendererBase:
    cdef int bug
    def __init__(self):
        pass #Used for typehints :D

cdef class WindowRendererSdl:
    cdef public object window, renderer, surface, root
    
    @staticmethod
    def create_initialized(window, sdl_window, renderer):
        cdef WindowRendererSdl self = WindowRendererSdl.__new__(WindowRendererSdl)
        check_singleton()
        self._init_types()
        self.window = sdl_window
        self.renderer = renderer
        self._init_base(window)
        return self

    def __init__(self, str title, tuple size, object root not None, **kwargs):
        check_singleton()
        self._init_types()
        self._init_window(title, size, kwargs.get('resizable', False))
        self._init_base(root)
        
    cdef inline void _init_window(self, title, size, bint resizable):
        self.window = sdl_window_t(title, (size[0], size[1]), resizable = resizable)
        self.renderer = sdl_renderer_t(self.window, accelerated = True, target_texture = True)
    
    cdef inline void _init_types(self):
        global sdl_window_t, sdl_renderer_t, sdl_texture_t, sdl_image_t, pg_surface_t, pg_rect_t

        from pygame._sdl2.video import (Window as SDL2Window, Renderer, Texture, Image)
        
        sdl_window_t = SDL2Window
        sdl_renderer_t = Renderer
        sdl_texture_t = Texture
        sdl_image_t = Image
        
        pg_surface_t = md.pygame.Surface
        pg_rect_t = md.pygame.Rect
    
    cdef inline void _init_base(self, root):
        self.root = root
        self.surface = self.window.get_surface()

    # === Sizes ===
    cpdef tuple get_tuple_rect(self): return (0, 0, self.c_get_width(), self.c_get_height())
    cpdef NvRect get_nvrect(self): return NvRect.new(0, 0, self.c_get_width(), self.c_get_height())
    
    cdef inline tuple c_get_tuple_size(self) noexcept: return self.window.size
    cdef inline NvVector2 c_get_nvvec_size(self): return NvVector2.cfrom_ints(self.window.size[0], self.window.size[1])
    cdef inline int c_get_width(self) noexcept: return self.window.size[0]
    cdef inline int c_get_height(self) noexcept: return self.window.size[1]

    cpdef tuple get_size_tuple(self): return self.c_get_tuple_size()
    cpdef NvVector2 get_size_nvvec(self): return self.c_get_nvvec_size()
    
    cpdef int get_width(self): return self.c_get_width()
    cpdef int get_height(self): return self.c_get_height()
    
    # === Blit ===
    cpdef void blit(self, source, dest): #type: ignore
        renderer = self.renderer
        cdef int len_dest
        if isinstance(source, pg_surface_t):
            source = sdl_image_t(sdl_texture_t.from_surface(renderer, source))
        elif isinstance(source, sdl_texture_t):
            source = sdl_image_t(source)
        if not isinstance(dest, pg_rect_t):
            len_dest = len(dest)
            if len_dest == 4: dest = pg_rect_t(*dest)
            elif len_dest == 2: 
                if isinstance(dest[0], tuple | list): 
                    dest = pg_rect_t(*dest)
                else:
                    dest = pg_rect_t(*dest, source.texture.width, source.texture.height)
        renderer.blit(source, dest)

    # === Misc ===
    @property
    def screen(self): return self.window
    cpdef void set_target(self, texture): self.renderer.target = texture
    cpdef void set_title(self, str title): self.window.title = title
    cpdef void update(self): pass
    cpdef void begin_frame(self): pass
    cpdef void end_frame(self): self.renderer.present()
    cpdef void clear(self, color = fill_color):
        renderer = self.renderer
        old_color = renderer.draw_color
        renderer.draw_color = color
        renderer.clear()
        renderer.draw_color = old_color
    cpdef create_target_texture(self, int width, int height): return sdl_texture_t(self.renderer, size = (width, height), target = True)
    cpdef load_image(self, str path): return md.pygame.image.load(path)
    
cdef class WindowRendererRaylib:
    cdef public NvShader _sdf_shader, _border_shader
    cdef public dict _sdf_locs, _border_locs
    cdef public object root

    @staticmethod
    def create_initialized(window):
        cdef WindowRendererRaylib self = WindowRendererRaylib.__new__(WindowRendererRaylib)
        check_singleton()
        self._init_base(window)
        return self

    def __init__(self, title, size, root, **kwargs):
        check_singleton()
        self._init_window(title, size, kwargs.get('resizable', False))
        self._init_base(root)

    cdef inline void _init_window(self, str title, tuple size, bint resizable):
        if resizable:
            md.rl.set_config_flags(md.rl.ConfigFlags.FLAG_WINDOW_RESIZABLE)
        md.rl.init_window(int(size[0]), int(size[1]), title)
    
    cdef inline void _init_base(self, root):
        self.root = root
        self.load_raylib_fast_bindings()
        self._sdf_shader = NvShader.c_create_from_code(SdfShader.VERTEX_SHADER, SdfShader.FRAGMENT_SHADER)
        self._sdf_locs = {
            "texture0": get_nvshader_location(self._sdf_shader, "texture0"),
            "colDiffuse": get_nvshader_location(self._sdf_shader, "colDiffuse"),
            "rectSize": get_nvshader_location(self._sdf_shader, "rectSize"),
            "radius": get_nvshader_location(self._sdf_shader, "radius"),
            }
        set_nvshader_value_vec4_tuple(self._sdf_shader, self._sdf_locs['colDiffuse'], (1.0, 1.0, 1.0, 1.0))
        self._border_shader = NvShader.c_create_from_code(BorderShader.VERTEX_SHADER, BorderShader.FRAGMENT_SHADER)
        self._border_locs = {
            "texture0": get_nvshader_location(self._border_shader, "texture0"),
            "colDiffuse": get_nvshader_location(self._border_shader, "colDiffuse"),
            "rectSize": get_nvshader_location(self._border_shader, "rectSize"),
            "radius": get_nvshader_location(self._border_shader, "radius"),
            "borderColor": get_nvshader_location(self._border_shader, "borderColor"),
            "thickness": get_nvshader_location(self._border_shader, "thickness"),
        }
        set_nvshader_value_vec4_tuple(self._border_shader, self._border_locs['colDiffuse'], (1.0, 1.0, 1.0, 1.0),)

    cpdef load_raylib_fast_bindings(self):
        functions_to_load = [
            "DrawTextureRec",
            "DrawTexturePro",
            "BeginBlendMode",
            "EndBlendMode",
            "BeginTextureMode",
            "EndTextureMode",
            "ClearBackground",
            "BeginShaderMode",
            "EndShaderMode",
            "SetShaderValue",
            "GetShaderLocation",
            "BeginDrawing",
            "EndDrawing",
            "SetShaderValueV"]
        pointer_dict = {}
        for func_name in functions_to_load:
            try:
                from raylib import ffi, rl as rlc_code
                c_ptr = ffi.addressof(rlc_code, func_name)
                addr = int(ffi.cast("uintptr_t", c_ptr))
                pointer_dict[func_name] = addr
            except AttributeError:
                print(f"Warning: Could not load function {func_name} from raylib backend")
        init_raylib_pointers(pointer_dict) # type: ignore
        print(f"Successfully loaded {len(pointer_dict)} fast raylib functions.")

    # === Blit ===
    cpdef blit(self, source, tuple dest, bint flip = True, tuple color = Color.White, double angle = 0.0): 
        if isinstance(color, tuple) and len(color) == 3:
            color = (*color, 255)
        self.blit_rect_pro(source, (dest[0], dest[1], source.width, source.height), flip, color, angle)
    
    cpdef fast_blit(self, source, tuple dest, tuple color = Color.White): 
        c_draw_texture_vec(source, dest, color, True)
    
    cpdef fast_blit_pro(self, source, tuple dest, bint flip = True, tuple color = Color.White):
        if isinstance(color, tuple) and len(color) == 3:
            color = (*color, 255)
        h = -source.height if flip else source.height
        c_draw_texture_rec(source, (0,0, source.width, h), dest, color)

    cpdef blit_rect_pro(self, source, tuple dest, bint flip = True, tuple color = Color.White, double angle = 0.0, source_rect: Annotations.rect_like | None = None, int mode = 0):
        if source_rect: source_rec = source_rect
        elif flip: source_rec = (0, 0, source.width, -source.height)
        else: source_rec = (0, 0, source.width, source.height)
        begin_blend_mode(mode or md.rl.BlendMode.BLEND_ALPHA)
        c_draw_texture_pro(source, <tuple>source_rec, dest, (0,0), angle, color)
        end_blend_mode()
    
    cpdef blit_rect_vec(self, source, tuple coordinates, bint flip = True, tuple color = Color.White, source_rect: Annotations.rect_like | None = None, int mode = 0): 
        if source_rect: source_rec = source_rect
        elif flip: source_rec = (0, 0, source.width, -source.height)
        else: source_rec = (0, 0, source.width, source.height)
        begin_blend_mode(mode or md.rl.BlendMode.BLEND_ALPHA)
        c_draw_texture_rec(source, source_rec, coordinates, color)
        end_blend_mode()
    
    cpdef blit_sdf(self, source, tuple dest, object radii, bint flip = True, int mode = 0):
        if isinstance(radii, int | float): radii = (radii, radii, radii, radii)
        self._begin_sdf(dest[2], dest[3], <tuple>radii)
        self.blit_rect_pro(source, dest, flip, mode=mode)
        self._end_shader()
    
    cpdef blit_sdf_vec(self, source, tuple coordinates, object radii, bint flip = True, int mode = 0):
        if isinstance(radii, int | float): radii = (radii, radii, radii, radii)
        self._begin_sdf(source.width, source.height, <tuple>radii)
        self.blit_rect_vec(source, coordinates, flip, mode=mode)
        self._end_shader()

    cpdef fast_blit_sdf_vec(self, source, tuple coordinates, object radii, bint flip = True, tuple color = Color.White):
        if isinstance(radii, int | float): radii = (radii, radii, radii, radii)
        self._begin_sdf(source.width, source.height, <tuple>radii)
        self.fast_blit_pro(source, coordinates, flip, color = color)
        self._end_shader()

    cpdef blit_borders(self, source, tuple dest_rect, tuple radii, tuple border_color, tuple color = Color.White, double thickness = 1, bint flip = True, int mode = 0):
        self._begin_borders(dest_rect[2], dest_rect[3], radii, border_color, thickness)
        self.blit_rect_pro(source, dest_rect, flip, color, mode=mode)
        self._end_shader()
        
    cpdef blit_borders_vec(self, source, tuple coordinates, tuple radii, tuple border_color, tuple color = Color.White, double thickness = 1, bint flip = True):
        self._begin_borders(source.width, source.height, radii, border_color, thickness)
        self.blit_rect_vec(source, coordinates, flip, color)
        self._end_shader()
    
    cpdef fast_blit_borders_vec(self, source, tuple coordinates, tuple radii, tuple border_color, double thickness = 1, bint flip = True):
        self._begin_borders(source.width, source.height, radii, border_color, thickness)
        self.fast_blit_pro(source, coordinates, flip)
        self._end_shader()

    # === Shaders ===
    cpdef _begin_sdf(self, float width, float height, tuple radii):
        cdef list list_radii
        list_radii = list(radii)
        minside = min(width, height) / 2
        minrad = min(radii)
        if minrad > minside:
            for i in range(4): 
                list_radii[i] = min(radii[i], minside)
        begin_nvshader_mode(self._sdf_shader)
        set_nvshader_value_vec2_tuple(self._sdf_shader, self._sdf_locs['rectSize'], (width, height))
        set_nvshader_value_vec4_tuple(self._sdf_shader, self._sdf_locs['radius'], tuple(list_radii))

    cpdef _begin_borders(self, double width, double height, tuple radii, tuple border_color, double thickness):
        begin_nvshader_mode(self._border_shader)
        cdef list list_radii
        list_radii = list(radii)
        minside = min(width, height) / 2
        minrad = min(radii)
        if minrad > minside:
            for i in range(4): 
                list_radii[i] = min(radii[i], minside)
        cdef NvVector2 rec_size 
        rec_size = NvVector2.new(width, height)
        set_nvshader_value_vec2_nvvec(self._border_shader, self._border_locs['rectSize'], rec_size)
        set_nvshader_value_vec4_tuple(self._border_shader, self._border_locs['radius'], tuple(list_radii))
        r, g, b, a = 255, 255, 255, 255
        if hasattr(border_color, 'r'): 
            r, g, b, a = border_color.r, border_color.g, border_color.b, border_color.a
        elif len(border_color) >= 3:
            r, g, b = border_color[0], border_color[1], border_color[2]
            if len(border_color) > 3: a = border_color[3]
        b_color_vec = (r/255, g/255, b/255, a/255)
        set_nvshader_value_vec4_tuple(self._border_shader, self._border_locs['borderColor'], b_color_vec)
        set_nvshader_value_float(self._border_shader, self._border_locs['thickness'], <float>thickness)

    cdef inline void _end_shader(self) noexcept: end_shader_mode()

    # === Sizes ===
    cpdef tuple get_tuple_rect(self): return (0, 0, self.c_get_width(), self.c_get_height())
    cpdef NvRect get_nvrect(self): return NvRect.new(0, 0, self.c_get_width(), self.c_get_height())

    cdef inline tuple c_get_tuple_size(self) noexcept: return (md.rl.get_screen_width(), md.rl.get_screen_height())
    cdef inline NvVector2 c_get_nvvec_size(self): return NvVector2.cfrom_ints(md.rl.get_screen_width(), md.rl.get_screen_height())
    cdef inline int c_get_width(self) noexcept: return md.rl.get_screen_width()
    cdef inline int c_get_height(self) noexcept: return md.rl.get_screen_height()
    
    cpdef tuple get_size_tuple(self): return self.c_get_tuple_size()
    cpdef NvVector2 get_size_nvvec(self): return self.c_get_nvvec_size()

    cpdef int get_width(self): return md.rl.get_screen_width()
    cpdef int get_height(self): return md.rl.get_screen_height()

    # === Misc ===
    @property
    def screen(self): return None
    cpdef void set_title(self, str title): md.rl.set_window_title(title)
    cpdef void clear(self, color = fill_color): md.rl.clear_background(color)
    cpdef void begin_frame(self): begin_drawing()
    cpdef void update(self): pass
    cpdef void end_frame(self): end_drawing()
    cpdef load_image(self, str path): return md.rl.load_texture(path)
    
cdef class WindowRendererPygame:
    cdef public object window, root

    @staticmethod
    def create_initialized(window, screen):
        cdef WindowRendererPygame self = WindowRendererPygame.__new__(WindowRendererPygame)
        check_singleton()
        self.window = screen
        self._init_base(window)
        return self

    def __init__(self, title, size, root, flags = 0, **kwargs):
        check_singleton()
        self._init_window(title, size, flags)
        self._init_base(root)
    
    cdef inline void _init_base(self, object root): self.root = root
    cdef inline void _init_window(self, title, size, flags): 
        self.window = md.pygame.display.set_mode(size, flags)
        md.pygame.display.set_caption(title)

    # === Sizes ===
    cpdef tuple get_tuple_rect(self): return (0, 0, self.c_get_width(), self.c_get_height())
    cpdef NvRect get_nvrect(self): return NvRect.new(0, 0, self.c_get_width(), self.c_get_height())

    cdef inline tuple c_get_tuple_size(self) noexcept: return self.window.size
    cdef inline NvVector2 c_get_nvvec_size(self): return NvVector2.cfrom_ints(self.window.width, self.window.height)
    cdef inline int c_get_width(self) noexcept: return self.window.width
    cdef inline int c_get_height(self) noexcept: return self.window.height

    cpdef int get_width(self): return self.c_get_width()
    cpdef int get_height(self): return self.c_get_height()
    cpdef NvVector2 get_size_nvvec(self): return self.c_get_nvvec_size()
    cpdef tuple get_size_tuple(self): return self.c_get_tuple_size()

    # === Misc ===
    @property
    def screen(self): return self.window
    cpdef void end_frame(self): md.pygame.display.update()
    cpdef void begin_frame(self): pass
    cpdef void clear(self, color = fill_color): self.window.fill(color)
    cpdef void update(self): pass
    cpdef void flip(self): md.pygame.display.flip()
    cpdef void blit(self, source, dest): self.window.blit(source, dest)
    cpdef load_image(self, path: str): return md.pygame.image.load(path)
    cpdef set_title(self, title: str): md.pygame.display.set_caption(title)