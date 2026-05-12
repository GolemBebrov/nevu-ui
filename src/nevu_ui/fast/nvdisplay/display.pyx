import nevu_ui.core.modules as md
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from pyray import Texture
from nevu_ui.core import Annotations
from nevu_ui.presentation.color import Color
from nevu_ui.fast.shaders import SdfShader, BorderShader
from nevu_ui.fast.nvrect import NvRect
from nevu_ui.fast.nvvector2.nvvector2 cimport NvVector2
from nevu_ui.fast.raylib.nevu_raylib cimport (
    init_raylib_pointers, begin_blend_mode, end_blend_mode, begin_texture_mode, end_texture_mode, 
    c_draw_texture_pro, c_draw_texture_rec, c_draw_texture_vec, set_nvshader_value, begin_nvshader_mode, end_shader_mode, begin_drawing, end_drawing,
    get_nvshader_location, set_nvshader_value_float, set_nvshader_value_vec2_nvvec, set_nvshader_value_vec4_tuple, set_nvshader_value_vec2_tuple
)
from nevu_ui.fast.nvshader.nvshader cimport NvShader

cdef class DisplayBase:
    cdef object root
    cpdef void fill(self, tuple color): self.clear(color)

cdef class DisplaySdl():
    cdef public object window, renderer, surface, root
    def __init__(self, str title, tuple size, object root not None, **kwargs):
        self.root = root
        from pygame._sdl2.video import (Window as SDL2Window, Renderer)
        resizable = kwargs.get('resizable', False)
        self.window = SDL2Window(title, (size[0], size[1]), resizable = resizable)
        self.renderer = Renderer(self.window, accelerated = True, target_texture = True)
        self.surface = self.window.get_surface()
    cpdef get_rect(self): return NvRect(0, 0, *self.get_size())
    cpdef get_size(self): return self.window.size
    cpdef get_width(self): return self.window.size[0]
    cpdef get_height(self): return self.window.size[1]
    cpdef set_target(self, texture): self.renderer.target = texture
    cpdef update(self): pass
    cpdef begin_frame(self): pass
    cpdef end_frame(self): self.renderer.present()
    cpdef void blit(self, source, dest): #type: ignore
        from pygame._sdl2.video import (Window as SDL2Window, Renderer, Texture, Image)
        if isinstance(source, md.pygame.Surface):
            source = Image(Texture.from_surface(self.renderer, source))
        elif isinstance(source, Texture):
            source = Image(source)
        if not isinstance(dest, md.pygame.Rect):
            if len(dest) == 4: dest = md.pygame.Rect(*dest)
            elif len(dest) == 2: 
                if isinstance(dest[0], tuple|list): dest = md.pygame.Rect(*dest)
                else:
                    dest = md.pygame.Rect(*dest, source.texture.width, source.texture.height)
        self.renderer.blit(source, dest)
    cpdef void fill(self, tuple color): self.clear(color)
    cpdef void clear(self, color = (255, 255, 255, 255)):
        if color:
            old_color = self.renderer.draw_color 
            self.renderer.draw_color = color
            self.renderer.clear()
            self.renderer.draw_color = old_color
        else: self.renderer.clear()

    cpdef create_texture_target(self, int width, int height):
        return Texture(self.renderer, size = (width, height), target = True)

    cpdef load_image(self, str path): return md.pygame.image.load(path)
    
cdef class DisplayRayLib():
    cdef public NvShader _sdf_shader, _border_shader
    cdef public dict _sdf_locs, _border_locs
    cdef public object root
    def __init__(self, title, size, root, **kwargs):
        self.root = root
        if kwargs.get('resizable', False):
            md.rl.set_config_flags(md.rl.ConfigFlags.FLAG_WINDOW_RESIZABLE)
        md.rl.init_window(int(size[0]), int(size[1]), title)
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

    cpdef void fill(self, tuple color): self.clear(color)

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
    
    cpdef _begin_sdf(self, float width, float height, tuple radii):
        cdef list list_radii
        list_radii = list(radii)
        minside = min(width, height) / 2
        minrad = min(radii)
        if minrad > minside:
            for i in range(4): 
                list_radii[i] = min(radii[i], minside)
        begin_nvshader_mode(self._sdf_shader)
        #cdef NvVector2 rect_size
        #rect_size = NvVector2.new(width, height)
        set_nvshader_value_vec2_tuple(self._sdf_shader, self._sdf_locs['rectSize'], (width, height))
        set_nvshader_value_vec4_tuple(self._sdf_shader, self._sdf_locs['radius'], tuple(list_radii))
        
    cpdef _end_shader(self): 
        end_shader_mode()
    
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

    cpdef fast_blit_sdf_vec(self, source, tuple coordinates, object radii, bint flip = True):
        if isinstance(radii, int | float): radii = (radii, radii, radii, radii)
        self._begin_sdf(source.width, source.height, <tuple>radii)
        self.fast_blit_pro(source, coordinates, flip)
        self._end_shader()
    
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
    
    cpdef get_width(self): return md.rl.get_screen_width()
    cpdef get_height(self): return md.rl.get_screen_height()
    cpdef get_rect(self): return NvRect(0, 0, *self.get_size())
    cpdef get_size(self): return (md.rl.get_screen_width(), md.rl.get_screen_height())
    cpdef clear(self, color: Annotations.rgb_like_color = (0, 0, 0, 0)): md.rl.clear_background(color)
    cpdef begin_frame(self): begin_drawing()
    cpdef update(self): pass
    cpdef end_frame(self): end_drawing()
    cpdef load_image(self, str path): return md.rl.load_texture(path)
    
cdef class DisplayClassic():
    cdef public object window, root
    def __init__(self, title, size, root, flags = 0, **kwargs):
        self.root = root
        self.window = md.pygame.display.set_mode(size, flags, **kwargs)
        md.pygame.display.set_caption(title)
    cpdef get_rect(self): return self.window.get_rect()
    cpdef void end_frame(self): md.pygame.display.update()
    cpdef void begin_frame(self): pass
    cpdef tuple get_size(self): return self.window.size
    cpdef int get_width(self): return self.window.width
    cpdef int get_height(self): return self.window.height
    cpdef void clear(self, color: Annotations.rgb_like_color = (0, 0, 0, 0)): self.window.fill(color)
    cpdef void update(self): pass
    cpdef void fill(self, color: Annotations.rgb_like_color): self.window.fill(color)
    cpdef void flip(self): md.pygame.display.flip()
    cpdef void blit(self, source, dest: Annotations.dest_like): self.window.blit(source, dest)
    cpdef load_image(self, path: str): return md.pygame.image.load(path)