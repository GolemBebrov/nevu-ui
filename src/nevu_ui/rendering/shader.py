import pygame
import moderngl
import numpy as np
from pygame._sdl2.video import Texture as SdlTexture
from pygame._sdl2 import Renderer as SdlRenderer

DEFAULT_VERTEX_SHADER = """
    #version 330
    in vec2 in_vert;
    in vec2 in_uv; // <-- Второй атрибут!
    out vec2 v_text;

    void main() {
        gl_Position = vec4(in_vert, 0.0, 1.0);
        v_text = in_uv;
    }
"""

DEFAULT_FRAGMENT_SHADER = """
    #version 330
    uniform sampler2D Texture;
    in vec2 v_text;
    out vec4 f_color;
    void main() {
        f_color = texture(Texture, v_text);
    }
"""

class Shader:
    def __init__(self, gl_context: moderngl.Context, 
                 vertex_shader=None, fragment_shader=None):

        self.gl_context = gl_context
        
        vs = vertex_shader or DEFAULT_VERTEX_SHADER
        fs = fragment_shader or DEFAULT_FRAGMENT_SHADER
        self.prog = self.gl_context.program(vertex_shader=vs, fragment_shader=fs)

        quad_buffer = np.array([
            -1.0, -1.0, 0.0, 0.0,
             1.0, -1.0, 1.0, 0.0,
             1.0,  1.0, 1.0, 1.0,
            -1.0,  1.0, 0.0, 1.0,
        ], dtype='f4')

        quad_indices = np.array([0, 1, 2, 0, 2, 3], dtype='i4')

        self.vbo = self.gl_context.buffer(quad_buffer)
        self.ibo = self.gl_context.buffer(quad_indices)

        self.vao = self.gl_context.vertex_array(
            self.prog,
            [(self.vbo, '2f 2f', 'in_vert', 'in_uv')],
            self.ibo
        )
    def render(self, 
               source: pygame.Surface | SdlTexture,
               target: moderngl.Framebuffer,
               uniforms: dict|None = None):

        if isinstance(source, SdlTexture):
            source_surface = source.renderer.to_surface(source, pygame.Rect(0, 0, source.width, source.height))
            
        elif isinstance(source, pygame.Surface):
            source_surface = source
        else:
            raise TypeError(f"Unsupported source type: {type(source)}")
        #flipped_surface = pygame.transform.flip(source_surface, True, True)
        source_mgl_texture = self.gl_context.texture(
            source_surface.get_size(), 4, source_surface.get_view('1')
        )
        source_mgl_texture.swizzle = 'BGRA'
        target.use()
        
        if uniforms:
            for key, value in uniforms.items():
                if key in self.prog:
                    self.prog[key].value = value

        if 'Texture' in self.prog:
            self.prog['Texture'].value = 0
            source_mgl_texture.use(location=0)
        
        self.vao.render(moderngl.TRIANGLES)

        source_mgl_texture.release()

    def release(self):
        self.prog.release()
        self.vbo.release()
        self.vao.release()


def convert_sdl_to_gl_texture(
    gl_context: moderngl.Context, 
    sdl_texture: SdlTexture) -> moderngl.Texture:

    surface = sdl_texture.renderer.to_surface(sdl_texture, sdl_texture.get_rect())
    

    gl_texture = gl_context.texture(
        size=surface.get_size(),
        components=4, 
        data=surface.get_view('1')
    )
    
    
    return gl_texture

def convert_surface_to_gl_texture(
    gl_context: moderngl.Context, 
    surface: pygame.Surface
) -> moderngl.Texture:

    if surface.get_flags() & pygame.SRCALPHA:
        components = 4
    else:
        components = 3
    
    flipped_surface_view = pygame.transform.flip(surface, False, True).get_view('1')

    gl_texture = gl_context.texture(
        size=surface.get_size(),
        components=components,
        data=flipped_surface_view
    )
    
    return gl_texture