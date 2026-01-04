import pygame 
import moderngl
import numpy as np

from pygame._sdl2.video import (
    Window as SDL2Window, Renderer, Texture
)

from nevu_ui.color.color import ColorAnnotation
from nevu_ui.core.state import nevu_state

class DisplayBase:
    def __init__(self, root): self.root = root
    def get_rect(self): raise NotImplementedError
    def get_size(self): raise NotImplementedError
    def get_width(self): raise NotImplementedError
    def get_height(self): raise NotImplementedError
    def blit(self, source, dest: pygame.Rect | tuple[int, int]): raise NotImplementedError
    def clear(self, color: ColorAnnotation.RGBLikeColor = (0, 0, 0)): raise NotImplementedError
    def fill(self, color: ColorAnnotation.RGBLikeColor): self.clear(color)
    def update(self): raise NotImplementedError

class DisplaySdl(DisplayBase):
    def __init__(self, title, size, root, **kwargs):
        super().__init__(root)
        resizable = kwargs.get('resizable', False)
        self.window = SDL2Window(title, size, resizable=resizable)
        self.renderer = Renderer(self.window, accelerated=True, target_texture=True)
        self.surface = self.window.get_surface()

    def get_rect(self):
        return pygame.Rect(0, 0, *self.get_size())
    
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

class DisplayGL(DisplayBase):
    def __init__(self, title, size, root, **kwargs):
        super().__init__(root)
        flags = pygame.OPENGL | pygame.DOUBLEBUF
        if kwargs.get('resizable', False):
            flags |= pygame.RESIZABLE

        pygame.display.set_caption(title)
        pygame.display.gl_set_attribute(pygame.GL_CONTEXT_MAJOR_VERSION, 3)
        pygame.display.gl_set_attribute(pygame.GL_CONTEXT_MINOR_VERSION, 3)
        pygame.display.gl_set_attribute(pygame.GL_CONTEXT_PROFILE_MASK, pygame.GL_CONTEXT_PROFILE_CORE)

        self.surface = pygame.display.set_mode(size, flags)
        self.renderer = moderngl.create_context()
        self.last_used = None

        self.program = self.renderer.program(
            vertex_shader='''
                #version 330
                in vec2 in_vert;
                out vec2 v_text;
                uniform vec2 u_pos;
                uniform vec2 u_size;
                uniform vec2 u_resolution;
                void main() {
                    vec2 pos = in_vert * u_size + u_pos;
                    vec2 ndc = pos / u_resolution * 2.0 - 1.0;
                    gl_Position = vec4(ndc.x, -ndc.y, 0.0, 1.0);
                    v_text = in_vert;
                }''',
            fragment_shader='''
                #version 330
                in vec2 v_text;
                out vec4 f_color;
                uniform sampler2D u_texture;
                uniform vec2 u_tex_pos;
                uniform vec2 u_tex_size;
                void main() {
                    f_color = texture(u_texture, u_tex_pos + v_text * u_tex_size);
                }''')
        prog = self.program
        self.u_resolution = prog['u_resolution']
        self.u_pos = prog['u_pos']
        self.u_size = prog['u_size']
        self.u_texture = prog['u_texture']
        self.u_tex_pos = prog['u_tex_pos']
        self.u_tex_size = prog['u_tex_size']
        
        self.u_texture.value = 0
        self.u_resolution.value = self.get_size()
        quad_buffer = np.array([
            0.0, 0.0,
            1.0, 0.0,
            0.0, 1.0,
            1.0, 1.0], dtype='f4')

        self.vbo = self.renderer.buffer(quad_buffer)
        self.vao = self.create_vao()

    def create_vao(self):
        return self.renderer.vertex_array(self.program, [(self.vbo, '2f', 'in_vert')])
    def get_rect(self): return pygame.Rect(0, 0, *self.get_size())
    def get_size(self):
        return nevu_state.window.size if nevu_state.window else self.surface.get_size()
    def get_width(self): return self.get_size()[0]
    def get_height(self): return self.get_size()[1]
    def use(self, fbo: moderngl.Framebuffer ):
        self.last_used = fbo
        fbo.use()

    def blit_selected_texture(self, x, y, width, height, tex_x=0.0, tex_y=0.0, tex_width=1.0, tex_height=1.0):
        self.u_pos.value = (x, y)
        self.u_size.value = (width, height)
        self.u_tex_pos.value = (tex_x, 1 - tex_y)
        self.u_tex_size.value = (tex_width, -tex_height)
        self.u_resolution.value = self.get_size()
        self.renderer.screen.use()
        self.vao.render(moderngl.TRIANGLE_STRIP)
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
        self.blit_selected_texture(dest.x, dest.y, dest.w, dest.h, 0.0, 0.0, 1.0, 1.0)

    def clear_normalized(self, color = (0, 0, 0)):
        if color:
            normalized_color = (color[0] / 255.0, color[1] / 255.0, color[2] / 255.0)
            self.renderer.clear(*normalized_color)
        else: self.renderer.clear()
    def clear(self, color: tuple[float, float, float] | tuple[float, float, float, float] = (0, 0, 0, 1)): #type: ignore
        if len(color) == 4: r, g, b, a = color
        elif len(color) == 3: 
            r, g, b = color
            a = 1
        else: raise ValueError("Invalid color format")
        self.renderer.clear(r, g, b, a)
    def fill(self, color = None): self.clear_normalized(color)
    
    def update(self):
        self.u_resolution.value = self.get_size()
        self.renderer.viewport = (0, 0, *self.get_size())
        pygame.display.flip()
    
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
    def blit(self, source, dest: pygame.Rect): #type: ignore
        self.window.blit(source, dest)