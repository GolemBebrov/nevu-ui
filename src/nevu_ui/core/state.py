from __future__ import annotations

from typing import TYPE_CHECKING, final

from nevu_ui.core.enums import Backend

if TYPE_CHECKING:
    from pygame._sdl2 import Renderer

    from nevu_ui.fast.zsystem import ZSystem
    from nevu_ui.manager import Manager
    from nevu_ui.overlay import OverlayManager
    from nevu_ui.window import Window

@final
class NevuState:
    __slots__ = [
        "backend",
        "current_dirty_rects",
        "current_events",
        "dirty_mode",
        "manager",
        "overlay",
        "renderer",
        "tooltip_active",
        "window",
        "z_system",
    ]

    def __init__(self):
        self.reset()

    def reset(self):
        self.dirty_mode: bool = False

        self.current_events: list | None = None

        self.window: Window = None  # type: ignore
        self.z_system: ZSystem | None = None
        self.manager: Manager | None = None
        self.renderer: Renderer | None = None
        self.overlay: OverlayManager | None = None

        self.backend: Backend | None = None

    def clear_events(self):
        if self.current_events:
            self.current_events.clear()

nevu_state = NevuState()

def _analize_bg(self):
    if not nevu_state.window.renderer_type.raylib:
        return False
    transparent = False
    if self.style.gradient:
        gr = self.style.gradient

        for color in gr.raw_colors:
            if len(color) == 4 and color[3] < 255:
                transparent = True

    if self.style.bg_image:
        transparent = True

    return transparent
