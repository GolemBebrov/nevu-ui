from pygame.window import Window as SDL2Window
from pygame._sdl2 import Renderer, Texture
import pygame 
from nevu_ui.color.color import ColorAnnotation
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
        self.window = SDL2Window(title, size, **kwargs)
        
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
    
    def blit(self, source: Texture | pygame.Surface, dest_rect: pygame.Rect | tuple[int, int]):
        dest = dest_rect
        if isinstance(source, pygame.Surface):
                print("----Blit warning----")
                print("Warning: VERY unoptimized operation! Please use Texture instead of Surface for better performance!")
                print(f"Source surface: {source}")
                print("--------------------")
                source = Texture.from_surface(self.renderer, source)
        if not isinstance(dest, pygame.Rect):
            dest = pygame.Rect(dest, (source.width, source.height))
        self.renderer.blit(source, dest)

    def clear(self, color: ColorAnnotation.RGBLikeColor | None = None):
        if color:
            old_color = self.renderer.draw_color 
            self.renderer.draw_color = color
            self.renderer.clear()
            self.renderer.draw_color = old_color
        else:
            self.renderer.clear()
    
    def update(self):
        self.renderer.present()
        
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