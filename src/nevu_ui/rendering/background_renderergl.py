import pygame
import contextlib

from nevu_ui.color import Color
from nevu_ui.nevuobj import NevuObject
from nevu_ui.fast.nvvector2 import NvVector2
from nevu_ui.style import Style
import moderngl as gl
from nevu_ui.core.state import nevu_state
from PIL import Image
from nevu_ui.nevusurface.nevusurf import NevuSurface

class _DrawNamespaceGl:
    __slots__ = ["_renderer"]
    def __init__(self, renderer):
        self._renderer = renderer
        
    @property
    def root(self) -> NevuObject: return self._renderer.root
    @property
    def style(self): return self.root.style
    
    @property
    def ctx(self):
        ctx = nevu_state.renderer
        assert isinstance(ctx, gl.Context)
        return ctx
    
    def gradient(self, surface: pygame.Surface, transparency = None, style: Style | None = None) -> Gradient: # type: ignore
        raise NotImplementedError("GL gradient is not implemented yet.")

    def create_clear(self, size, data = None) -> gl.Texture:
        texture = self.ctx.texture(size, 4, data)
        return texture
    
    def create_nevusurf(self, size) -> NevuSurface:
        return NevuSurface(size)
    
    def load_image(self, path) -> gl.Texture:
        img = Image.open(path).convert('RGBA')
        img = img.transpose(Image.Transpose.FLIP_TOP_BOTTOM)
        img_data = img.tobytes()
        return self.create_clear(img.size, img_data)

#!Warning: Code will be cooked soon!