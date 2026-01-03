import moderngl
import pygame
from warnings import deprecated
@deprecated("Shader is not implemented yet.")
class Shader:
    def __init__(self, gl_context: moderngl.Context, vertex_shader=None, fragment_shader=None, todo = "TRUE"):
        raise NotImplementedError("Shader is not implemented yet.")

def convert_surface_to_gl_texture(gl_context: moderngl.Context, surface: pygame.Surface) -> moderngl.Texture:
    components = 4 if surface.get_flags() & pygame.SRCALPHA else 3
    flipped_surface_view = pygame.transform.flip(surface, False, True).get_view('1')
    return gl_context.texture(size=surface.get_size(), components=components, data=flipped_surface_view)