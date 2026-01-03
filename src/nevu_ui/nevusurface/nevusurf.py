import moderngl
import pygame
from nevu_ui.fast.nvvector2 import NvVector2
from nevu_ui.core.state import nevu_state
from typing import overload

#! Can be imported only from nevu_ui.nevusurface.nevusurf

class NevuSurface:
    def __init__(self, size: NvVector2 | tuple | list):
        if nevu_state.renderer_type != "opengl":
            raise ValueError("NevuSurface can only be used with opengl renderer")
        assert isinstance(nevu_state.renderer, moderngl.Context)
        size = NvVector2(size).to_int()
        self.size = size
        self.ctx = nevu_state.renderer
        assert isinstance(self.ctx, moderngl.Context)
        self.texture = self.ctx.texture((int(self.size.x), int(self.size.y)), 4)
        self.fbo = self.ctx.framebuffer(color_attachments=[self.texture])
    
    @staticmethod
    def from_data(data, size: NvVector2 | tuple | list):
        surface = NevuSurface(size)
        surface.texture.write(data)
        return surface
    
    @staticmethod
    def from_texture(texture: moderngl.Texture, size: NvVector2 | tuple | list):
        surface = NevuSurface(size)
        surface.texture = texture
        return surface
    
    @staticmethod
    def from_surface(surface: pygame.Surface):
        texture_data = pygame.image.tobytes(surface, 'RGB', True)
        return NevuSurface.from_data(texture_data, NvVector2(surface.get_size()))
        
    def use(self):
        self.fbo.use()
    
    def use_texture(self, location: int = 0):
        self.texture.use(location)
        
    def clear(self, color=(0.0, 0.0, 0.0, 0.0)):
        self.fbo.clear(color[0], color[1], color[2], color[3])

    def clear_rgba(self, color = (0, 0, 0, 0)):
        self.clear((color[0] / 255.0, color[1] / 255.0, color[2] / 255.0, color[3] / 255.0))

    def fill(self, color = (0, 0, 0, 0)):
        self.clear_rgba(color)
    
    def blit_selected_texture(self, x, y, width, height, tex_x=0.0, tex_y=0.0, tex_width=1.0, tex_height=1.0):
        display = nevu_state.window.display
        if nevu_state.window.is_gl(display):
            display.u_resolution.value = self.size
            display.u_pos.value = (x, y)
            display.u_size.value = (width, height)
            display.u_tex_pos.value = (tex_x, 1.0 - tex_y)
            display.u_tex_size.value = (tex_width, -tex_height)
            display.vao.render(moderngl.TRIANGLE_STRIP)

    def blit(self, nevu_surface, dest):
        texture = nevu_surface.texture
        if not isinstance(dest, pygame.Rect):
            if len(dest) == 4:
                dest = pygame.Rect(dest)
            elif len(dest) == 2:
                dest = pygame.Rect(dest, (0, 0))
        if dest.size == (0, 0):
            dest.size = texture.size
        texture.use(0)
        self.fbo.use() 
        self.blit_selected_texture(dest.x, dest.y, dest.w, dest.h, 0.0, 0.0, 1.0, 1.0)
