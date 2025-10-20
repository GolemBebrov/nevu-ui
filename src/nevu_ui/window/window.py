import sys
import pygame
from pygame._sdl2 import Renderer
from nevu_ui.fast.nvvector2 import NvVector2
from warnings import deprecated

from nevu_ui.state import nevu_state
from nevu_ui.window.display import (
    DisplayClassic, DisplaySdl, DisplayBase
)
from nevu_ui.core_types import (
    ResizeType, EventType
)
from nevu_ui.utils import (
    mouse, keyboard, time, NevuEvent
)
from nevu_ui.fast.zsystem import (
    ZSystem, ZRequest
)


class Window:
    _display: DisplayBase
    @staticmethod
    def cropToRatio(width: int, height: int, ratio: NvVector2, default=(0, 0)):
        if height == 0 or ratio.y == 0: return default
        rx, ry = ratio
        aspect_ratio = width / height
        if abs(aspect_ratio - (rx / ry)) < 1e-6: return default
        
        if aspect_ratio > rx / ry:
            crop_width = width - (height * rx / ry)
            return crop_width, default[1]
        else:
            crop_height = height - (width * ry / rx)
            return default[0], crop_height
    
    def __init__(self, size, minsize=(10, 10), title="pygame window", resizable = True, ratio: NvVector2 | None = None, resize_type: ResizeType = ResizeType.CropToRatio, _gpu_mode = False):
        self._gpu_mode = _gpu_mode

        self.resize_type = resize_type
        
        self.resizable = resizable
        self._title = title
        
        self._init_lists(ratio, size, minsize)
        self._init_graphics()
        
        self._clock = pygame.time.Clock()
        self._events: list[NevuEvent] = []
        nevu_state.current_events = []

        if self.resize_type == ResizeType.CropToRatio:
            self._recalculate_render_area() 

        self._selected_context_menu = None
        self._next_update_dirty_rects = []
        
        self.z_system = ZSystem()
        
        self._set_nevu_state()

    def _set_nevu_state(self):
        nevu_state.window = self
        if self._gpu_mode:
            assert isinstance(self._display, DisplaySdl)
            nevu_state.renderer = self._display.renderer
        nevu_state.z_system = self.z_system
        
    def _init_lists(self, ratio, size, minsize):
        self._ratio = ratio or NvVector2(0, 0)
        self._original_size = NvVector2(size)
        self.size = NvVector2(size)
        self.minsize = NvVector2(minsize)
        
        self._crop_width_offset = 0
        self._crop_height_offset = 0
        self._offset = NvVector2(0, 0)
    def _init_graphics(self):
        if not self._gpu_mode:
            flags = pygame.RESIZABLE if self.resizable else 0
            flags |= pygame.HWSURFACE | pygame.DOUBLEBUF
            self._display = DisplayClassic(self.title, self.size.to_tuple(), flags)
        else:
            kwargs = {}
            if self.resizable:
                kwargs['resizable'] = True
            self._display = DisplaySdl(self.title, self.size.to_tuple(), **kwargs)
        
    @property
    @deprecated("Please use 'window.display' instead")
    def surface(self) -> DisplayBase:
        return self._display
    
    @property
    def display(self) -> DisplayBase:
        return self._display
    
    def clear(self, color = (0, 0, 0)):
        """
        Fill the entire surface with the given color
        Args:
            color (tuple[int, int, int], optional): RGB color to fill with. Defaults to (0, 0, 0).
        """
        self._display.fill(color)

    def _recalculate_render_area(self):
        current_w, current_h = self._display.get_size()
        target_ratio = self._ratio or self._original_size
        self._crop_width_offset, self._crop_height_offset = self.cropToRatio(current_w, current_h, target_ratio)
        self._offset = NvVector2(self._crop_width_offset // 2, self._crop_height_offset // 2)

    def add_request(self, z_request: ZRequest):
        self.z_system.add(z_request)
    
    def mark_dirty(self):
        self.z_system.mark_dirty()
    
    def update(self, events, fps: int = 60):
        """
        Updates the window state and processes events.

        Args:
            events (list[pygame.Event]): List of events to process.
            fps (int, optional): Desired frames per second. Defaults to 60.
        """
        self._next_update_dirty_rects.clear()
        self.display.clear()
        nevu_state.current_events = events
        
        self._update_utils(events)
        for event in events:
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
                
            if event.type == pygame.VIDEORESIZE and self.resize_type != ResizeType.ResizeFromOriginal:
                w, h = event.w, event.h
                self.size = NvVector2(w, h)
                self.z_system.mark_dirty()
                if self.resize_type == ResizeType.CropToRatio:
                    self._recalculate_render_area()
                    render_width = self.size[0] - self._crop_width_offset
                    render_height = self.size[1] - self._crop_height_offset
                    self._event_cycle(EventType.Resize, [render_width, render_height])
                else:
                    self._event_cycle(EventType.Resize, self.size)
                self._next_update_dirty_rects.append(pygame.Rect(0, 0, *self.size))

        self._clock.tick(fps)
        self.z_system.cycle(mouse.pos, mouse.left_fdown, mouse.left_up, mouse.any_wheel, mouse.wheel_down)
        self._event_cycle(EventType.Update)
        
    def _update_utils(self, events):
        mouse.update(events)
        time.update()
        keyboard.update()
    @property
    def offset(self):
        return self._offset

    @property
    def title(self):
        return self._title

    @title.setter
    def title(self, text:str):
        self._title = text
        pygame.display.set_caption(self._title)

    @property
    def ratio(self):
        return self._ratio

    @ratio.setter
    def ratio(self, ratio: NvVector2):
        self._ratio = ratio
        self._recalculate_render_area()

    @property
    def original_size(self):
        return self._original_size

    def add_event(self, event: NevuEvent):
        self._events.append(event)

    def _event_cycle(self, type: EventType, *args, **kwargs):
        for event in self._events:
            if event._type == type:
                event(*args, **kwargs)

    @property
    def rel(self):
        render_width = self.size[0] - self._crop_width_offset
        render_height = self.size[1] - self._crop_height_offset
        return NvVector2(render_width / self._original_size[0], render_height / self._original_size[1])