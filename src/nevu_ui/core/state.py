from __future__ import annotations
from typing import TYPE_CHECKING
from pygame._sdl2 import Renderer

if TYPE_CHECKING:
    from nevu_ui.window import Window
    from nevu_ui.fast.zsystem import ZSystem
    from nevu_ui.ui_manager import Manager

class NevuState:
    __slots__ = ["tooltip_active", "dirty_mode", "window", "manager", "current_events", "current_dirty_rects", "z_system", "renderer", "_renderer_type"]
    def __init__(self) -> None:
        self.reset()
        
    def reset(self):
        self.tooltip_active: bool = False
        self.dirty_mode: bool = False

        self.current_events: list | None = None
        self.current_dirty_rects: list | None = None
        
        self.window: Window | None = None
        self.z_system: ZSystem | None = None
        self.manager: Manager | None = None
        self.renderer: Renderer | None = None

        self._renderer_type: str | None = None
    def gpu_render(self) -> bool:
        return self.window != None and self.renderer != None
    
    def clear_events(self):
        if self.current_events:
            self.current_events.clear()
    
    def clear_dirty_rects(self):
        if self.current_dirty_rects:
            self.current_dirty_rects.clear()
    
    @property
    def renderer_type(self): return self._renderer_type
    
nevu_state = NevuState()