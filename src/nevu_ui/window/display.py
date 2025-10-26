from pygame._sdl2.video import (
    Window as SDL2Window, Renderer,
)
from nevu_ui.rendering.shader import Shader, DEFAULT_VERTEX_SHADER, DEFAULT_FRAGMENT_SHADER
from pygame._sdl2 import Renderer, Texture
import pygame 
from nevu_ui.color.color import ColorAnnotation
import moderngl
from sdl2 import SDL_WINDOW_OPENGL
from sdl2.video import SDL_GL_GetDrawableSize
import numpy as np

import pygame_shaders

class DisplayBase:
    def get_rect(self):
        raise NotImplementedError
    
    def get_size(self):
        raise NotImplementedError
    
    def get_width(self):
        raise NotImplementedError
    
    def get_height(self):
        raise NotImplementedError
    
    def blit(self, source, dest_rect: pygame.Rect | tuple[int, int]):
        raise NotImplementedError
    
    def clear(self, color: ColorAnnotation.RGBLikeColor = (0, 0, 0)):
        raise NotImplementedError
    
    def fill(self, color: ColorAnnotation.RGBLikeColor):
        self.clear(color)
    
    def update(self):
        raise NotImplementedError


class DisplaySdl(DisplayBase):
    def __init__(self, title, size, **kwargs):
        resizable = kwargs.get('resizable', False)
        self.window = SDL2Window(title, size, resizable=resizable)
        self.renderer = Renderer(self.window, accelerated=True, target_texture=True)
        self.surface = self.window.get_surface()

    def get_rect(self):
        return pygame.Rect(0, 0, *self.get_size())
    
    def get_size(self):
        return self.window.size
    
    def get_width(self):
        return self.window.size[0]
    
    def get_height(self):
        return self.window.size[1]
    
    def blit(self, source, dest_rect):
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
        else:
            self.renderer.clear()
    
    def update(self):
        self.renderer.present()

    def create_texture_target(self, width, height):
        texture = Texture(self.renderer, size=(width, height), target=True)
        return texture
    

class DisplayGL(DisplayBase):
    #WARNING: not stable, use at your own risk, fps can be very low and graphics can be strange
    def __init__(self, title, size, **kwargs):
        flags = pygame.OPENGL | pygame.DOUBLEBUF
        if kwargs.get('resizable', False):
            flags |= pygame.RESIZABLE

        pygame.display.set_caption(title)
        pygame.display.gl_set_attribute(pygame.GL_CONTEXT_MAJOR_VERSION, 3)
        pygame.display.gl_set_attribute(pygame.GL_CONTEXT_MINOR_VERSION, 3)
        pygame.display.gl_set_attribute(pygame.GL_CONTEXT_PROFILE_MASK, pygame.GL_CONTEXT_PROFILE_CORE)

        self.surface = pygame.display.set_mode(size, flags)
        
        self.renderer = moderngl.create_context()
        self.main_fbo = self.renderer.screen

        quad_vertices = np.array([-1.0, -1.0, 1.0, -1.0, 1.0, 1.0, -1.0, 1.0], dtype='f4')
        quad_indices = np.array([0, 1, 2, 0, 2, 3], dtype='i4')

        self.prog = self.renderer.program(
            vertex_shader='''
                #version 330
                uniform bool flip_y = false;
                in vec2 in_vert;
                out vec2 v_text;
                void main() {
                    gl_Position = vec4(in_vert, 0.0, 1.0);
                    float y = flip_y ? -in_vert.y : in_vert.y;
                    v_text = vec2(in_vert.x, y) * 0.5 + 0.5;
                }
            ''',
            fragment_shader='''
                #version 330
                uniform sampler2D Texture;
                in vec2 v_text;
                out vec4 f_color;
                void main() {
                    f_color = texture(Texture, v_text);
                }
            '''
        )
        
        self.vbo = self.renderer.buffer(quad_vertices)
        self.ibo = self.renderer.buffer(quad_indices)
        
        self.vao = self.renderer.vertex_array(
            self.prog,
            [(self.vbo, '2f', 'in_vert')],
            self.ibo
        )
        
        size_int = tuple(map(int, size))
        self.screen_texture = self.renderer.texture(size_int, 4)
        self.fbo = self.renderer.framebuffer(color_attachments=[self.screen_texture])
        
        self.texture_fbos = {}
        self.current_fbo = self.fbo

    def get_rect(self):
        return pygame.Rect(0, 0, *self.get_size())

    def get_size(self):
        return pygame.display.get_window_size()

    def get_width(self):
        return self.get_size()[0]

    def get_height(self):
        return self.get_size()[1]
    
    def set_target(self, texture=None):
        if texture is None:
            self.current_fbo = self.fbo
        elif isinstance(texture, moderngl.Texture):
            if texture not in self.texture_fbos:
                raise ValueError("Target texture was not created with create_texture_target")
            self.current_fbo = self.texture_fbos[texture]
        else:
            raise TypeError(f"Target must be a moderngl.Texture or None, not {type(texture)}")
        
        self.current_fbo.use()

    def blit(self, source, dest_rect):
        self.current_fbo.use()
        
        is_surface = isinstance(source, pygame.Surface)
        
        if is_surface:
            texture_data = source.get_view('1')
            tex = self.renderer.texture(source.get_size(), 4, texture_data)
            tex.swizzle = 'BGRA'
            self.prog['flip_y'].value = True
        else:
            tex = source
            self.prog['flip_y'].value = False
        
        self.prog['Texture'].value = 0
        tex.use(location=0)
        self.vao.render(moderngl.TRIANGLES)
        
        if is_surface:
            tex.release()

    def clear(self, color=None):
        self.current_fbo.use()
        if color:
            normalized_color = (color[0] / 255.0, color[1] / 255.0, color[2] / 255.0)
            self.renderer.clear(*normalized_color)
        else:
            self.renderer.clear()

    def update(self):
        self.main_fbo.use()
        self.renderer.clear()
        
        self.prog['Texture'].value = 0
        self.prog['flip_y'].value = False
        self.screen_texture.use(location=0)
        self.vao.render(moderngl.TRIANGLES)
        
        pygame.display.flip()

    def create_texture_target(self, width, height):
        width, height = int(width), int(height)
        texture = self.renderer.texture((width, height), 4)
        fbo = self.renderer.framebuffer(color_attachments=[texture])
        self.texture_fbos[texture] = fbo
        return texture
    
class DisplayClassic(DisplayBase):
    def __init__(self, title, size, flags = 0, **kwargs):
        self.window = pygame.display.set_mode(size, flags, **kwargs)
        pygame.display.set_caption(title)
        
    def get_rect(self):
        return self.window.get_rect()
    
    def get_size(self):
        return self.window.get_size()
    
    def get_width(self):
        return self.window.get_width()
    
    def get_height(self):
        return self.window.get_height()
    
    def blit(self, source, dest_rect: pygame.Rect): #type: ignore
        self.window.blit(source, dest_rect)

    def clear(self, color: ColorAnnotation.RGBLikeColor = (0, 0, 0)):
        self.window.fill(color)
    
    def update(self):
        pygame.display.update()