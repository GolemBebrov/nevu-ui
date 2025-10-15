from __future__ import annotations
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from nevu_ui.window import Window
    from nevu_ui.fast.zsystem import ZSystem
    from nevu_ui.ui_manager import Manager

class NevuState:
    __slots__ = ["tooltip_active", "dirty_mode", "window", "manager", "current_events", "current_dirty_rects", "z_system"]
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

nevu_state = NevuState()