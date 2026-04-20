import nevu_ui.core.modules as md
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from pyray import Texture
from nevu_ui.core import Annotations
from nevu_ui.presentation.color import Color
from nevu_ui.fast.shaders import SdfShader, BorderShader
from nevu_ui.fast.nvrect import NvRect
from nevu_ui.fast.raylib import init_raylib_pointers, begin_blend_mode, end_blend_mode, begin_texture_mode, end_texture_mode, draw_texture_pro, draw_texture_rec

class DisplayBase:
    def __init__(self, root): self.root = root
    def begin_frame(self): pass
    def get_rect(self): raise NotImplementedError
    def get_size(self): raise NotImplementedError
    def get_width(self): raise NotImplementedError
    def get_height(self): raise NotImplementedError
    def blit(self, source, dest): raise NotImplementedError
    def clear(self, color: Annotations.rgba_color = (0, 0, 0, 0)): raise NotImplementedError
    def fill(self, color: Annotations.rgba_color): self.clear(color)
    def update(self): raise NotImplementedError
    def load_image(self, path: str): raise NotImplementedError
    def end_frame(self): pass

class DisplaySdl(DisplayBase):
    def __init__(self, title: str, size: Annotations.dest_like, root, **kwargs):
        super().__init__(root)
        from pygame._sdl2.video import (Window as SDL2Window, Renderer, Texture, Image)
        resizable = kwargs.get('resizable', False)
        self.window = SDL2Window(title, (size[0], size[1]), resizable=resizable)
        self.renderer = Renderer(self.window, accelerated=True, target_texture=True)
        self.surface = self.window.get_surface()
    def get_rect(self): return NvRect(0, 0, *self.get_size())
    def get_size(self): return self.window.size
    def get_width(self): return self.window.size[0]
    def get_height(self): return self.window.size[1]
    def set_target(self, texture): self.renderer.target = texture
    def update(self): self.renderer.present()
    
    def blit(self, source, dest_rect): #type: ignore
        dest = dest_rect
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

    def clear(self, color=None):
        if color:
            old_color = self.renderer.draw_color 
            self.renderer.draw_color = color
            self.renderer.clear()
            self.renderer.draw_color = old_color
        else: self.renderer.clear()

    def create_texture_target(self, width, height):
        return Texture(self.renderer, size=(width, height), target=True)

    def load_image(self, path: str): return md.pygame.image.load(path)
    
_origin = (0, 0)
class DisplayRayLib(DisplayBase):
    def __init__(self, title, size, root, **kwargs): 
        super().__init__(root)
        
        if kwargs.get('resizable', False):
            md.rl.set_config_flags(md.rl.ConfigFlags.FLAG_WINDOW_RESIZABLE)
        md.rl.init_window(int(size[0]), int(size[1]), title)
        md.rl.rl_set_blend_mode(md.rl.BlendMode.BLEND_ALPHA_PREMULTIPLY)
        self.load_raylib_fast_bindings()
        self._sdf_shader = md.rl.load_shader_from_memory(SdfShader.VERTEX_SHADER, SdfShader.FRAGMENT_SHADER)
        self._sdf_locs = {
            "texture0": md.rl.get_shader_location(self._sdf_shader, "texture0"),
            "colDiffuse": md.rl.get_shader_location(self._sdf_shader, "colDiffuse"),
            "rectSize": md.rl.get_shader_location(self._sdf_shader, "rectSize"),
            "radius": md.rl.get_shader_location(self._sdf_shader, "radius"),
            }
        md.rl.set_shader_value(self._sdf_shader, self._sdf_locs['colDiffuse'], md.rl.Vector4(1.0, 1.0, 1.0, 1.0), md.rl.ShaderUniformDataType.SHADER_UNIFORM_VEC4)
        self._border_shader = md.rl.load_shader_from_memory(BorderShader.VERTEX_SHADER, BorderShader.FRAGMENT_SHADER)
        self._border_locs = {
            "texture0": md.rl.get_shader_location(self._border_shader, "texture0"),
            "colDiffuse": md.rl.get_shader_location(self._border_shader, "colDiffuse"),
            "rectSize": md.rl.get_shader_location(self._border_shader, "rectSize"),
            "radius": md.rl.get_shader_location(self._border_shader, "radius"),
            "borderColor": md.rl.get_shader_location(self._border_shader, "borderColor"),
            "thickness": md.rl.get_shader_location(self._border_shader, "thickness"),
        }
        md.rl.set_shader_value(self._border_shader, self._border_locs['colDiffuse'], md.rl.Vector4(1.0, 1.0, 1.0, 1.0), md.rl.ShaderUniformDataType.SHADER_UNIFORM_VEC4)

    def load_raylib_fast_bindings(self):
        functions_to_load = [
            "DrawTextureRec",
            "DrawTexturePro",
            "BeginBlendMode",
            "EndBlendMode",
            "BeginTextureMode",
            "EndTextureMode",
            "ClearBackground",]
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

    def blit(self, source: "Texture", dest: Annotations.rect_like, flip = True, color: Annotations.rgba_color = Color.White, angle: int | float = 0.0): 
        if isinstance(color, tuple) and len(color) == 3:
            color = (*color, 255)
        self.blit_rect_pro(source, (dest[0], dest[1], source.width, source.height), flip, color, angle)
    
    def fast_blit(self, source: "Texture", dest: Annotations.dest_like, color: Annotations.rgba_color = Color.White): 
        md.rl.draw_texture_v(source, dest, color)
    
    def fast_blit_pro(self, source: "Texture", dest: Annotations.dest_like, flip: bool = True, color: Annotations.rgba_color = Color.White):
        if isinstance(color, tuple) and len(color) == 3:
            color = (*color, 255)
        h = -source.height if flip else source.height
        draw_texture_rec(source, (0,0, source.width, h), dest, color)
    
    def blit_rect_pro(self, source: "Texture", dest: Annotations.rect_like, flip = True, color: Annotations.rgba_color = Color.White, angle: int | float | None = None, source_rect: Annotations.rect_like | None = None, mode = None):
        if source_rect: source_rec = source_rect
        elif flip: source_rec = (0, 0, source.width, -source.height)
        else: source_rec = (0, 0, source.width, source.height)
        angle = angle or 0.0
        begin_blend_mode(mode or md.rl.BlendMode.BLEND_ALPHA)
        draw_texture_pro(source, source_rec, dest, (0,0), angle, color)
        end_blend_mode()
    
    def blit_rect_vec(self, source: "Texture", coordinates: Annotations.dest_like, flip = True, color: Annotations.rgba_color = Color.White, source_rect: Annotations.rect_like | None = None, mode = None): 
        if source_rect: source_rec = source_rect
        elif flip: source_rec = (0, 0, source.width, -source.height)
        else: source_rec = (0, 0, source.width, source.height)
        begin_blend_mode(mode or md.rl.BlendMode.BLEND_ALPHA)
        draw_texture_rec(source, source_rec, coordinates, color)
        end_blend_mode()
    
    
    def _begin_sdf(self, width, height, radii):
        radii = list(radii)
        minside = min(width, height) / 2
        minrad = min(radii)
        if minrad > minside:
            for i in range(4): 
                radii[i] = min(radii[i], minside)
        md.rl.begin_shader_mode(self._sdf_shader)
        size_vec = md.rl.Vector2(width, height)
        md.rl.set_shader_value(self._sdf_shader, self._sdf_locs['rectSize'], size_vec, md.rl.ShaderUniformDataType.SHADER_UNIFORM_VEC2)
        radii_vec = md.rl.Vector4(*radii)
        md.rl.set_shader_value(self._sdf_shader, self._sdf_locs['radius'], radii_vec, md.rl.ShaderUniformDataType.SHADER_UNIFORM_VEC4)
        
    def _end_shader(self): 
        md.rl.end_shader_mode()
    
    def blit_sdf(self, source: "Texture", dest: Annotations.rect_like, radii: Annotations.rect_like, flip = True, mode = None):
        if isinstance(radii, int|float): radii = (radii, radii, radii, radii)
        self._begin_sdf(dest[2], dest[3], radii)
        self.blit_rect_pro(source, dest, flip, mode=mode)
        self._end_shader()
    
    def blit_sdf_vec(self, source: "Texture", coordinates: Annotations.dest_like, radii: Annotations.rect_like, flip = True, mode = None):
        if isinstance(radii, int|float): radii = (radii, radii, radii, radii)
        self._begin_sdf(source.width, source.height, radii)
        self.blit_rect_vec(source, coordinates, flip, mode=mode)
        self._end_shader()

    def fast_blit_sdf_vec(self, source: "Texture", coordinates: Annotations.dest_like, radii: Annotations.rect_like, flip = True):
        if isinstance(radii, int|float): radii = (radii, radii, radii, radii)
        self._begin_sdf(source.width, source.height, radii)
        self.fast_blit_pro(source, coordinates, flip)
        self._end_shader()
    
    def _begin_borders(self, width, height, radii, border_color, thickness):
        md.rl.begin_shader_mode(self._border_shader)
        minside = min(width, height) / 2
        minrad = min(radii)
        if minrad > minside:
            for i in range(4): 
                radii[i] = min(radii[i], minside)
        md.rl.set_shader_value(self._border_shader, self._border_locs['rectSize'], md.rl.Vector2(width, height), md.rl.ShaderUniformDataType.SHADER_UNIFORM_VEC2)
        md.rl.set_shader_value(self._border_shader, self._border_locs['radius'], md.rl.Vector4(*radii), md.rl.ShaderUniformDataType.SHADER_UNIFORM_VEC4)
        r, g, b, a = 255, 255, 255, 255
        if hasattr(border_color, 'r'): 
            r, g, b, a = border_color.r, border_color.g, border_color.b, border_color.a
        elif len(border_color) >= 3:
            r, g, b = border_color[0], border_color[1], border_color[2]
            if len(border_color) > 3: a = border_color[3]
        b_color_vec = md.rl.Vector4(r / 255.0, g / 255.0, b / 255.0, a / 255.0)
        md.rl.set_shader_value(self._border_shader, self._border_locs['borderColor'], b_color_vec, md.rl.ShaderUniformDataType.SHADER_UNIFORM_VEC4)
        thickness_ptr = md.rl.ffi.new("float *", thickness)
        md.rl.set_shader_value(self._border_shader, self._border_locs['thickness'], thickness_ptr, md.rl.ShaderUniformDataType.SHADER_UNIFORM_FLOAT)
        
    def blit_borders(self, source: "Texture", dest_rect: Annotations.rect_like, radii: Annotations.rect_like, border_color: Annotations.rgb_like_color, color: Annotations.rgb_like_color = Color.White, thickness: float = 1, flip = True, mode = None):
        self._begin_borders(dest_rect[2], dest_rect[3], radii, border_color, thickness)
        self.blit_rect_pro(source, dest_rect, flip, color, mode=mode)
        self._end_shader()
        
    def blit_borders_vec(self, source: "Texture", coordinates: Annotations.dest_like, radii: Annotations.rect_like, border_color: Annotations.rgb_like_color, color: Annotations.rgb_like_color = Color.White,  thickness: float = 1, flip = True):
        self._begin_borders(source.width, source.height, radii, border_color, thickness)
        self.blit_rect_vec(source, coordinates, flip, color)
        self._end_shader()
    
    def fast_blit_borders_vec(self, source: "Texture", coordinates: Annotations.dest_like, radii: Annotations.rect_like, border_color: Annotations.rgb_like_color, thickness: float = 1, flip = True):
        self._begin_borders(source.width, source.height, radii, border_color, thickness)
        self.fast_blit_pro(source, coordinates, flip)
        self._end_shader()
    
    def get_width(self): return md.rl.get_screen_width()
    def get_height(self): return md.rl.get_screen_height()
    def get_rect(self): return NvRect(0, 0, *self.get_size())
    def get_size(self): return (md.rl.get_screen_width(), md.rl.get_screen_height())
    def clear(self, color: Annotations.rgb_like_color = (0, 0, 0)): md.rl.clear_background(color)
    def begin_frame(self): md.rl.begin_drawing()
    def update(self): pass
    def end_frame(self): md.rl.end_drawing()
    def load_image(self, path: str): return md.rl.load_texture(path)
    
class DisplayClassic(DisplayBase):
    def __init__(self, title, size, root, flags = 0, **kwargs):
        super().__init__(root)
        self.window = md.pygame.display.set_mode(size, flags, **kwargs)
        md.pygame.display.set_caption(title)
    def get_rect(self): return self.window.get_rect()
    def get_size(self): return self.window.size
    def get_width(self): return self.window.width
    def get_height(self): return self.window.height
    def clear(self, color: Annotations.rgb_like_color = (0, 0, 0)): self.window.fill(color)
    def update(self): md.pygame.display.update()
    def flip(self): md.pygame.display.flip()
    def blit(self, source, dest: Annotations.dest_like): self.window.blit(source, dest)
    def load_image(self, path: str): return md.pygame.image.load(path)