import pygame 
import pyray as rl
from pygame._sdl2.video import (Window as SDL2Window, Renderer, Texture)
from nevu_ui.color.color import ColorAnnotation
from nevu_ui.fast.shaders import SdfShader, BorderShader
from nevu_ui.fast.nvrect import NvRect

class DisplayAnnotation:
    RectLike = tuple[int, int, int, int] | list[int]
    CoordLike = tuple[int, int] | RectLike
    ColorLike = ColorAnnotation.RGBLikeColor
    RadLike = tuple[float, float, float, float] | tuple[int, int, int, int]

class DisplayBase:
    def __init__(self, root): self.root = root
    def begin_frame(self): pass
    def get_rect(self): raise NotImplementedError
    def get_size(self): raise NotImplementedError
    def get_width(self): raise NotImplementedError
    def get_height(self): raise NotImplementedError
    def blit(self, source, dest): raise NotImplementedError
    def clear(self, color: ColorAnnotation.RGBLikeColor = (0, 0, 0)): raise NotImplementedError
    def fill(self, color: ColorAnnotation.RGBLikeColor): self.clear(color)
    def update(self): raise NotImplementedError
    def load_image(self, path: str): raise NotImplementedError
    def end_frame(self): pass

class DisplaySdl(DisplayBase):
    def __init__(self, title: str, size: DisplayAnnotation.CoordLike, root, **kwargs):
        super().__init__(root)
        resizable = kwargs.get('resizable', False)
        self.window = SDL2Window(title, (size[0], size[1]), resizable=resizable)
        self.renderer = Renderer(self.window, accelerated=True, target_texture=True)
        self.surface = self.window.get_surface()
    def get_rect(self): return pygame.Rect(0, 0, *self.get_size())
    def get_size(self): return self.window.size
    def get_width(self): return self.window.size[0]
    def get_height(self): return self.window.size[1]
    def set_target(self, texture): self.renderer.target = texture
    def update(self): self.renderer.present()
    
    def blit(self, source, dest_rect): #type: ignore
        dest = dest_rect
        if isinstance(source, pygame.Surface):
            source = Texture.from_surface(self.renderer, source)
        if not isinstance(dest, pygame.Rect):
            dest = pygame.Rect(dest, (source.width, source.height))
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

    def load_image(self, path: str): return pygame.image.load(path)

class DisplayRayLib(DisplayBase):
    def __init__(self, title, size, root, **kwargs): 
        super().__init__(root)
        if kwargs.get('resizable', False):
            rl.set_config_flags(rl.ConfigFlags.FLAG_WINDOW_RESIZABLE)
        rl.init_window(int(size[0]), int(size[1]), title)
        self._sdf_shader = rl.load_shader_from_memory(SdfShader.VERTEX_SHADER, SdfShader.FRAGMENT_SHADER)
        self._sdf_locs = {
            "texture0": rl.get_shader_location(self._sdf_shader, "texture0"),
            "colDiffuse": rl.get_shader_location(self._sdf_shader, "colDiffuse"),
            "rectSize": rl.get_shader_location(self._sdf_shader, "rectSize"),
            "radius": rl.get_shader_location(self._sdf_shader, "radius"),
            }
        rl.set_shader_value(self._sdf_shader, self._sdf_locs['colDiffuse'], rl.Vector4(1.0, 1.0, 1.0, 1.0), rl.ShaderUniformDataType.SHADER_UNIFORM_VEC4)
        self._border_shader = rl.load_shader_from_memory(BorderShader.VERTEX_SHADER, BorderShader.FRAGMENT_SHADER)
        self._border_locs = {
            "texture0": rl.get_shader_location(self._border_shader, "texture0"),
            "colDiffuse": rl.get_shader_location(self._border_shader, "colDiffuse"),
            "rectSize": rl.get_shader_location(self._border_shader, "rectSize"),
            "radius": rl.get_shader_location(self._border_shader, "radius"),
            "borderColor": rl.get_shader_location(self._border_shader, "borderColor"),
            "thickness": rl.get_shader_location(self._border_shader, "thickness"),
        }
        rl.set_shader_value(self._border_shader, self._border_locs['colDiffuse'], rl.Vector4(1.0, 1.0, 1.0, 1.0), rl.ShaderUniformDataType.SHADER_UNIFORM_VEC4)
    
    def blit(self, source: rl.Texture, dest: DisplayAnnotation.RectLike, flip = True, color: DisplayAnnotation.ColorLike = rl.WHITE, angle: int | float | None = None): 
        if isinstance(color, tuple) and len(color) == 3:
            color = (*color, 255)
        self.blit_rect_pro(source, (dest[0], dest[1], source.width, source.height), flip, color, angle)
        
    def blit_rect_pro(self, source: rl.Texture, dest: DisplayAnnotation.RectLike, flip = True, color: DisplayAnnotation.ColorLike = rl.WHITE, angle: int | float | None = None, source_rect: DisplayAnnotation.RectLike | None = None):
        if source_rect: source_rec = source_rect
        elif flip: source_rec = (0, 0, source.width, -source.height)
        else: source_rec = (0, 0, source.width, source.height)
        angle = angle or 0.0
        rl.begin_blend_mode(rl.BlendMode.BLEND_ALPHA_PREMULTIPLY)
        rl.draw_texture_pro(source, source_rec, dest, (0,0), angle, color)
        rl.end_blend_mode()
    
    def blit_rect_vec(self, source: rl.Texture, coordinates: DisplayAnnotation.CoordLike, flip = True, color: DisplayAnnotation.ColorLike = rl.WHITE, source_rect: DisplayAnnotation.RectLike | None = None): 
        if source_rect: source_rec = source_rect
        elif flip: source_rec = (0, 0, source.width, -source.height)
        else: source_rec = (0, 0, source.width, source.height)
        rl.begin_blend_mode(rl.BlendMode.BLEND_ALPHA)
        rl.draw_texture_rec(source, source_rec, coordinates, color)
        rl.end_blend_mode()
    
    def _begin_sdf(self, width, height, radii):
        rl.begin_blend_mode(rl.BlendMode.BLEND_ALPHA)
        rl.begin_shader_mode(self._sdf_shader)
        size_vec = rl.Vector2(width, height)
        rl.set_shader_value(self._sdf_shader, self._sdf_locs['rectSize'], size_vec, rl.ShaderUniformDataType.SHADER_UNIFORM_VEC2)
        radii_vec = rl.Vector4(*radii)
        rl.set_shader_value(self._sdf_shader, self._sdf_locs['radius'], radii_vec, rl.ShaderUniformDataType.SHADER_UNIFORM_VEC4)
        
    def _end_shader(self): 
        rl.end_shader_mode()
        rl.end_blend_mode()
    
    def blit_sdf(self, source: rl.Texture, dest: DisplayAnnotation.RectLike, radii: DisplayAnnotation.RadLike, flip = True):
        self._begin_sdf(dest[2], dest[3], radii)
        self.blit_rect_pro(source, dest, flip)
        self._end_shader()
    
    def blit_sdf_vec(self, source: rl.Texture, coordinates: DisplayAnnotation.CoordLike, radii: DisplayAnnotation.RadLike, flip = True):
        self._begin_sdf(source.width, source.height, radii)
        self.blit_rect_vec(source, coordinates, flip)
        self._end_shader()

    def _begin_borders(self, width, height, radii, border_color, thickness):
        rl.begin_blend_mode(rl.BlendMode.BLEND_ALPHA)
        rl.begin_shader_mode(self._border_shader)
        rl.set_shader_value(self._border_shader, self._border_locs['rectSize'], rl.Vector2(width, height), rl.ShaderUniformDataType.SHADER_UNIFORM_VEC2)
        rl.set_shader_value(self._border_shader, self._border_locs['radius'], rl.Vector4(*radii), rl.ShaderUniformDataType.SHADER_UNIFORM_VEC4)
        r, g, b, a = 255, 255, 255, 255
        if hasattr(border_color, 'r'): 
            r, g, b, a = border_color.r, border_color.g, border_color.b, border_color.a
        elif len(border_color) >= 3:
            r, g, b = border_color[0], border_color[1], border_color[2]
            if len(border_color) > 3: a = border_color[3]
        b_color_vec = rl.Vector4(r / 255.0, g / 255.0, b / 255.0, a / 255.0)
        rl.set_shader_value(self._border_shader, self._border_locs['borderColor'], b_color_vec, rl.ShaderUniformDataType.SHADER_UNIFORM_VEC4)
        thickness_ptr = rl.ffi.new("int *", int(thickness))
        rl.set_shader_value(self._border_shader, self._border_locs['thickness'], thickness_ptr, rl.ShaderUniformDataType.SHADER_UNIFORM_INT)
        
        
    def blit_borders(self, source: rl.Texture, dest_rect: DisplayAnnotation.RectLike, radii: DisplayAnnotation.RadLike, border_color: DisplayAnnotation.ColorLike, thickness: int, flip = True):
        self._begin_borders(dest_rect[2], dest_rect[3], radii, border_color, thickness)
        self.blit_rect_pro(source, dest_rect, flip)
        self._end_shader()
        
    def blit_borders_vec(self, source: rl.Texture, coordinates: DisplayAnnotation.CoordLike, radii: DisplayAnnotation.RadLike, border_color: DisplayAnnotation.ColorLike, thickness: int, flip = True):
        self._begin_borders(source.width, source.height, radii, border_color, thickness)
        self.blit_rect_vec(source, coordinates, flip)
        self._end_shader()
        
    def get_width(self): return rl.get_screen_width()
    def get_height(self): return rl.get_screen_height()
    def get_rect(self): return NvRect(0, 0, *self.get_size())
    def get_size(self): return (rl.get_screen_width(), rl.get_screen_height())
    def clear(self, color: DisplayAnnotation.ColorLike = (0, 0, 0)): rl.clear_background(color)
    def begin_frame(self): rl.begin_drawing()
    def update(self): pass
    def end_frame(self): rl.end_drawing()
    def load_image(self, path: str): return rl.load_texture(path)
    
class DisplayClassic(DisplayBase):
    def __init__(self, title, size, root, flags = 0, **kwargs):
        super().__init__(root)
        self.window = pygame.display.set_mode(size, flags, **kwargs)
        pygame.display.set_caption(title)
    def get_rect(self): return self.window.get_rect()
    def get_size(self): return self.window.size
    def get_width(self): return self.window.width
    def get_height(self): return self.window.height
    def clear(self, color: ColorAnnotation.RGBLikeColor = (0, 0, 0)): self.window.fill(color)
    def update(self): pygame.display.update()
    def flip(self): pygame.display.flip()
    def blit(self, source, dest: DisplayAnnotation.CoordLike): self.window.blit(source, dest)
    def load_image(self, path: str): return pygame.image.load(path)