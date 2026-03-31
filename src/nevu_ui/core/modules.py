from nevu_ui.core.state import nevu_state
from nevu_ui.core.enums import Backend
rl = None
raylib = None
pygame = None

def init_modules():
    global rl, pygame
    dtype = nevu_state.window._backend
    if dtype == Backend.RayLib:
        try:
            import pyray
            rl = pyray
            import raylib
            raylib = raylib
            
        except ImportError:
            raise ImportError("Raylib is not installed, raylib backend is not available."
                              "try `pip install raylib`")
    if dtype == Backend.Pygame or dtype == Backend.Sdl:
        try:
            import pygame
            if not hasattr(pygame, "IS_CE"):
                raise ImportError        
        except ImportError:
            raise ImportError("Pygame-CE is not installed, pygame/sdl backends are not available.\n"
                                "If you have legacy pygame installed, try:\n"
                                "  1. `pip uninstall pygame`\n"
                                "  2. `pip install pygame-ce`")