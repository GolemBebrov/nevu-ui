import sys
from typing import TypeGuard
from warnings import deprecated
import pygame
import pyray as rl

from nevu_ui.core.state import nevu_state
from nevu_ui.json_parser.base import standart_config
from nevu_ui.core.classes import ConfigType
from nevu_ui.fast.nvvector2 import NvVector2
from nevu_ui.fast.zsystem import ZSystem, ZRequest
from nevu_ui.core.enums import ResizeType, EventType, Backend
from nevu_ui.overlay import overlay

from nevu_ui.window.display import (
    DisplayClassic, DisplaySdl, DisplayBase, DisplayRayLib
)
from nevu_ui.utils import (
    keyboard, time, NevuEvent, set_mouse, mouse, set_keyboard
)

class _IsNamespace:
    def __init__(self, master):
        self.master = master
    @property
    def pygame(self): return isinstance(self.master._display, DisplayClassic)
    @property
    def sdl(self): return isinstance(self.master._display, DisplaySdl)
    @property
    def raylib(self): return isinstance(self.master._display, DisplayRayLib)

class Window:
    _display: DisplayBase
    @staticmethod
    def cropToRatio(width: int, height: int, ratio: NvVector2, default=(0, 0)):
        if height == 0 or ratio.y == 0: return default
        aspect_ratio = width / height
        if abs(aspect_ratio - (ratio.x / ratio.y)) < 1e-6: return default
        if aspect_ratio > ratio.x / ratio.y:
            return width - (height * ratio.x / ratio.y), default[1]
        crop_height = height - (width * ratio.y / ratio.x)
        return default[0], crop_height
    
    def _unsupported_back_error(self, name: str):
        return TypeError(f"Backend {name} is not supported!")
    
    def __init__(self, size, minsize=(10, 10), title="pygame window", resizable = True, ratio: NvVector2 | None = None, resize_type: ResizeType = ResizeType.CropToRatio, backend: Backend = Backend.Pygame):
        self.is_dtype = _IsNamespace(self)
        self._backend = backend
        
        self._debouncing_limit = 0.1
        self._debouncing_limit_counter = 0

        self.resize_type = resize_type
        self.resizable = resizable
        self._title = title
        
        self._init_lists(ratio, size, minsize)
        self._init_graphics()
        
        if not self.is_dtype.raylib:
            self._clock = pygame.time.Clock()
        self._events: list[NevuEvent] = []
        nevu_state.current_events = []

        if self.resize_type == ResizeType.CropToRatio:
            self._recalculate_render_area() 

        self._selected_context_menu = None
        self._next_update_dirty_rects = []
        self.z_system = ZSystem()
        self._reset_nevu_state()
        self._init_globals()

    def _init_globals(self):
        global mouse, keyboard
        set_mouse(self._backend)
        set_keyboard(self._backend)
    def _reset_nevu_state(self):
        nevu_state.window = self
        nevu_state.z_system = self.z_system
        nevu_state.backend = self._backend
        match self._backend:
            case Backend.Sdl: nevu_state.renderer = self._display.renderer #type: ignore
            case _: nevu_state.renderer = None
        
    def _init_lists(self, ratio, size, minsize):
        ratio = NvVector2(0, 0) if ratio is None else NvVector2(ratio)
        self._ratio = ratio
        self._original_size = NvVector2(size)
        self.size = NvVector2(size)
        self.minsize = NvVector2(minsize)

        self._crop_width_offset = 0
        self._crop_height_offset = 0
        self._offset = NvVector2(0, 0)
        
    def _get_kwargs(self):
        kwargs = {"title": self.title, "size": self.size, "root": self}
        match self._backend:
            case Backend.Pygame:
                flags = pygame.RESIZABLE if self.resizable else 0
                flags |= pygame.HWSURFACE | pygame.DOUBLEBUF
                kwargs['flags'] = flags
            case Backend.Sdl | Backend.RayLib:
                kwargs['resizable'] = self.resizable

        return kwargs
    
    def _init_graphics(self):
        kwargs = self._get_kwargs()
        back_to_class = {
            Backend.Pygame: DisplayClassic,
            Backend.Sdl: DisplaySdl,
            Backend.RayLib: DisplayRayLib
        }
        self._display = back_to_class[self._backend](**kwargs)
        
    @property
    @deprecated("Please use 'window.display' instead")
    def surface(self) -> DisplayBase: return self._display
    @property
    def display(self) -> DisplayBase: return self._display
    
    def is_raylib(self, display) -> TypeGuard[DisplayRayLib]: return isinstance(self._display, DisplayRayLib)
    def is_sdl(self, display) -> TypeGuard[DisplaySdl]: return isinstance(self._display, DisplaySdl)
    def is_legacy(self, display) -> TypeGuard[DisplayClassic]: return isinstance(self._display, DisplayClassic) 
    
    def clear(self, color = (0, 0, 0)): self._display.fill(color)

    def _recalculate_render_area(self):
        current_w, current_h = self._display.get_size()
        target_ratio = self._ratio or self._original_size
        self._crop_width_offset, self._crop_height_offset = self.cropToRatio(current_w, current_h, target_ratio)
        self._offset = NvVector2(self._crop_width_offset / 2, self._crop_height_offset / 2)

    def add_request(self, z_request: ZRequest): self.z_system.add(z_request)
    def mark_dirty(self): self.z_system.mark_dirty()
    
    def begin_frame(self):
        """Use this method only for raylib backend"""
        self.display.begin_frame()
    def end_frame(self):
        """Use this method only for raylib backend"""
        self.display.end_frame()
        
    def update(self, events = None, fps: int = 60):
        self._next_update_dirty_rects.clear()
        #self.display.clear()
        nevu_state.current_events = events
        
        self._update_utils(events)
        if not self.is_dtype.raylib:
            events = events or pygame.event.get()
            for event in events:
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                    
                if event.type == pygame.VIDEORESIZE and self.resize_type != ResizeType.ResizeFromOriginal:
                    w, h = event.w, event.h
                    self.size = NvVector2(w, h)
                    self._debouncing_limit_counter = 0
            self._clock.tick(fps)
        else:
            if rl.window_should_close():
                rl.close_window()
                sys.exit()
            if rl.is_window_resized():
                self.size = NvVector2(rl.get_screen_width(), rl.get_screen_height())
                self._debouncing_limit_counter = 0
            
        if 0 <= self._debouncing_limit_counter < self._debouncing_limit:
            self._debouncing_limit_counter += 1 * time.dt
        if self._debouncing_limit_counter >= self._debouncing_limit:
            self._resize()
            self._debouncing_limit_counter = -1
        
        self.z_system.cycle(mouse.pos, mouse.left_fdown, mouse.left_up, mouse.any_wheel, mouse.wheel_down)
        self._event_cycle(EventType.Update)
        self.display.update()

    def _resize(self):
        if self.resize_type == ResizeType.CropToRatio:
            self._recalculate_render_area()
            render_width = self.size[0] - self._crop_width_offset
            render_height = self.size[1] - self._crop_height_offset
            self._event_cycle(EventType.Resize, [render_width, render_height])
        else: self._event_cycle(EventType.Resize, self.size)
    
    def draw_overlay(self):
        match self._backend:
            case Backend.Pygame:
                texture = overlay.get_result(self.size)
            case Backend.Sdl:
                texture = overlay.get_result_sdl(self.size)
            case _:
                raise self._unsupported_back_error(self._backend.value)
        self.display.blit(texture, (0, 0))
        
    def _update_utils(self, events):
        mouse.update(events)
        time.update()
        keyboard.update()
        
    @property
    def offset(self): return self._offset
    
    @property
    def title(self): return self._title
    @title.setter
    def title(self, text:str):
        self._title = text
        pygame.display.set_caption(self._title)
        
    @property
    def ratio(self): return self._ratio
    @ratio.setter
    def ratio(self, ratio: NvVector2):
        self._ratio = ratio
        self._recalculate_render_area()
    @property
    def original_size(self): return self._original_size

    def add_event(self, event: NevuEvent): self._events.append(event)

    def _event_cycle(self, type: EventType, *args, **kwargs):
        for event in self._events:
            if event._type == type: event(*args, **kwargs)

    @property
    def rel(self): return NvVector2((self.size - self._offset * 2) / self.original_size)

class ConfiguredWindow(Window):
    def __init__(self):
        size = standart_config.win_config["size"]
        display_type = standart_config.win_config["display"]
        display_type = ConfigType.Window.Display(display_type)
        ratio = standart_config.win_config["ratio"]
        title = standart_config.win_config["title"]
        resizeable = standart_config.win_config["resizable"]
        #fps = standart_config.win_config["fps"] TODO
        super().__init__(title=title, size=size, resize_type=ResizeType.CropToRatio, backend=display_type, ratio = ratio, resizable = resizeable)