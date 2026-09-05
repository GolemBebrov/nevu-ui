import sys
from typing import TYPE_CHECKING, NotRequired, TypeGuard, Unpack, final

from typing_extensions import TypedDict, deprecated

from nevu_ui.core.callbacks import Callbacks

if TYPE_CHECKING:
    from pygame import Surface
    from pygame._sdl2.video import Renderer
    from pygame._sdl2.video import Window as SDL2Window

import nevu_ui.core.modules as md
from nevu_ui.core.classes import ConfigType, Counter
from nevu_ui.core.enums import Backend, BindType, ResizeType
from nevu_ui.core.modules import init_modules
from nevu_ui.core.state import nevu_state
from nevu_ui.fast.nvdisplay.display import (
    WindowRendererBase,
    WindowRendererPygame,
    WindowRendererRaylib,
    WindowRendererSdl,
)
from nevu_ui.fast.nvrect import NvRect
from nevu_ui.fast.nvvector2 import NvVector2
from nevu_ui.fast.zsystem import ZRequest, ZSystem
from nevu_ui.overlay import overlay
from nevu_ui.parser.base import standart_config
from nevu_ui.utils import keyboard, mouse, set_keyboard, set_mouse, time
from nevu_ui.utils.keys import init_keys


@final
class _IsNamespace:
    __slots__ = ("_cached_result", "master", "pygame", "pygame_like", "raylib", "sdl")

    def __init__(self, master: "Window"):
        self.master = master
        self._cached_result = None
        self.pygame: bool = False
        self.sdl: bool = False
        self.raylib: bool = False
        self.pygame_like: bool = False

    def _initial_check(self) -> None:
        if self._cached_result is None:
            self._cached_result = self.master.backend
        self.pygame = self._cached_result == Backend.Pygame
        self.sdl = self._cached_result == Backend.Sdl
        self.raylib = self._cached_result == Backend.RayLib
        self.pygame_like = self.pygame or self.sdl


class WindowKwargs(TypedDict):
    title: NotRequired[str]
    minsize: NotRequired[NvVector2]
    resizable: NotRequired[bool]
    ratio: NotRequired[NvVector2]
    resize_type: NotRequired[ResizeType]
    backend: NotRequired[Backend]
    base_fps: NotRequired[int]
    debounce: NotRequired[bool]

window_resize_type = ResizeType.CropToRatio
window_specific_update = lambda *args, **kwargs: print(
    "Unexpected something happened in window specific update"
)
window_update_utils = lambda *args, **kwargs: print(
    "Unexpected something happened in window update utils"
)

window_initialized = False

_kwargs_to_param = {
    "title": ("_title", str, "nevu window"),
    "minsize": ("minsize", NvVector2 | type(None) | tuple | list, None),
    "resizable": ("resizable", bool, True),
    "ratio": ("_ratio", NvVector2 | type(None) | tuple | list, None),
    # "resize_type": ("_resize_type", ResizeType, ResizeType.CropToRatio),
    "backend": ("backend", Backend, Backend.Pygame),
    "base_fps": ("_fps", int, 60),
    "debounce": ("debounce", bool, True),
}

@final
class Window:
    _renderer: WindowRendererBase
    __slots__ = [
        "_clock",
        "_crop_height_offset",
        "_crop_width_offset",
        "_debouncing",
        "_events",
        "_fps",
        "_old_fps",
        "_original_size",
        "_ratio",
        "_renderer",
        "_title",
        "_x2_offset",
        "backend",
        "begin_frame",
        "callbacks",
        "debounce",
        "minsize",
        "offset",
        "on_resize",
        "on_update",
        "pygame_unicode",
        "renderer_type",
        "resizable",
        "size",
        "z_system"
    ]

    @staticmethod
    def crop_to_ratio(width: int, height: int, ratio: NvVector2, default: tuple[float, float] | None = None):
        default = default or (0, 0)
        if height == 0 or ratio.y == 0:
            return default
        aspect_ratio = width / height
        if abs(aspect_ratio - (ratio.x / ratio.y)) < 1e-6:
            return default
        if aspect_ratio > ratio.x / ratio.y:
            return width - (height * ratio.x / ratio.y), default[1]
        crop_height = height - (width * ratio.y / ratio.x)
        return default[0], crop_height

    backend: Backend
    _title: str
    resizable: bool
    minsize: NvVector2
    _ratio: NvVector2
    _fps: int
    debounce: bool

    def _init_base(self):
        global window_update_utils
        self.renderer_type = _IsNamespace(self)
        nevu_state.window = self
        self._debouncing = Counter(0, 0.1)
        self._old_fps = None
        self.pygame_unicode = None
        window_update_utils = self._update_utils

    def __init__(self, size, **kwargs: Unpack[WindowKwargs]):
        self._init_base()
        self._init_kwargs(**kwargs)

        init_modules()

        self._init_hooks()
        self._init_lists(size)
        self._init_graphics()

        nevu_state.current_events = []

        if window_resize_type == ResizeType.CropToRatio:
            self._recalculate_render_area()

        self.z_system = ZSystem()
        self.callbacks = Callbacks()
        self._reset_nevu_state()

        init_keys()
        self._init_globals()
        if not self.renderer_type.raylib:
            self._clock = md.pygame.time.Clock()

        self.begin_frame = self._renderer.begin_frame

    def _init_hooks(self):
        self.on_update = []
        self.on_resize = []

    def _init_kwargs(self, **kwargs):
        kw_keys = list(_kwargs_to_param.keys())
        for key, type_of, default in _kwargs_to_param.values():
            val = kwargs.get(kw_keys.pop(0), default)
            if isinstance(val, type_of):
                setattr(self, key, val)
                continue
            else:
                raise TypeError(
                    f"Expected {type_of} for {key}, got {type(val).__name__}"
                )
        if "resize_type" in kwargs:
            global window_resize_type
            window_resize_type = kwargs["resize_type"]

    def _init_globals(self):
        global mouse, keyboard
        set_mouse(self.backend)
        set_keyboard(self.backend)

    def set_title(self, title: str):
        self._renderer.set_title(title)

    def _init_lists(self, size):
        minsize = self.minsize
        ratio = self._ratio
        ratio = NvVector2(0, 0) if ratio is None else NvVector2(ratio)
        self._ratio = ratio
        self._original_size = NvVector2(size)
        self.size = NvVector2(size)
        if self.minsize:
            self.minsize = NvVector2(minsize)

        self._crop_width_offset = 0
        self._crop_height_offset = 0
        self.offset = NvVector2(0, 0)
        self._x2_offset = NvVector2(0, 0)

    def _init_graphics(self):
        global window_specific_update
        kwargs = self._get_graphics_kwargs()
        back_to_class = {
            Backend.Pygame: WindowRendererPygame,
            Backend.Sdl: WindowRendererSdl,
            Backend.RayLib: WindowRendererRaylib,
            Backend.Opengl: None,
        }
        back_to_update = {
            Backend.RayLib: self._update_raylib,
            Backend.Pygame: self._update_pygame,
            Backend.Sdl: self._update_pygame,
            Backend.Opengl: None
        }
        window_specific_update = back_to_update[self.backend]
        if not window_specific_update:
            raise RuntimeError(f"Backend {self.backend} is not supported -w-")
        self._renderer = back_to_class[self.backend](**kwargs)

        self.renderer_type._initial_check()

    def _reset_nevu_state(self):
        nevu_state.window = self
        nevu_state.z_system = self.z_system
        nevu_state.backend = self.backend
        nevu_state.overlay = overlay
        match self.backend:
            case Backend.Sdl:
                nevu_state.renderer = self._renderer.renderer  # type: ignore
            case _:
                nevu_state.renderer = None

    def _get_graphics_kwargs(self):
        kwargs = {"title": self.title, "size": self.size.get_int_tuple(), "root": self}
        match self.backend:
            case Backend.Pygame:
                flags = 16 if self.resizable else 0
                flags |= 1 | 1073741824
                kwargs["flags"] = flags
            case Backend.Sdl | Backend.RayLib:
                kwargs["resizable"] = self.resizable
        return kwargs

    @property
    def screen(self):
        """Currently useful only for pygame-like backends."""
        screen = self._renderer.screen
        if screen is None:
            raise ValueError("Screen cannot be uptained with selected backend.")
        return screen

    @property
    def renderer(self) -> WindowRendererBase:
        return self._renderer

    def uninitialize(self):
        global window_initialized
        window_initialized = False

    def is_raylib(self, renderer) -> TypeGuard[WindowRendererRaylib]:
        return isinstance(self._renderer, WindowRendererRaylib)

    def is_sdl(self, renderer) -> TypeGuard[WindowRendererSdl]:
        return isinstance(self._renderer, WindowRendererSdl)

    def is_legacy(self, renderer) -> TypeGuard[WindowRendererPygame]:
        return isinstance(self._renderer, WindowRendererPygame)

    def clear(self, color=(0, 0, 0, 0)):
        self._renderer.clear(color)

    def _recalculate_render_area(self):
        current_w, current_h = self._renderer.get_size_tuple()
        target_ratio = self._ratio or self._original_size
        self._crop_width_offset, self._crop_height_offset = self.crop_to_ratio(
            current_w, current_h, target_ratio
        )
        self.offset = NvVector2(
            self._crop_width_offset / 2, self._crop_height_offset / 2
        )
        self._x2_offset = NvVector2(self._crop_width_offset, self._crop_height_offset)

    def add_request(self, z_request: ZRequest):
        self.z_system.add(z_request)

    def end_frame(self):
        self._renderer.end_frame()
        nevu_state._hovered = 0
        nevu_state._clicked_recently = 0

    @property
    def gui_hovered(self) -> bool:
        return self.z_system.last_hovered_request is not None

    @property
    def keyboard_available(self) -> bool:
        return not nevu_state.keyboard_focused

    def mark_dirty(self):
        self.z_system.mark_dirty()

    def _update_raylib(self, events=None, fps: int | None = None):
        fps = fps or self._fps
        rl = md.rl
        assert rl
        if fps != self._old_fps:
            rl.set_target_fps(fps)
            self._old_fps = fps
        if rl.window_should_close():
            rl.close_window()
            sys.exit()
        if rl.is_window_resized():
            self.size = NvVector2(rl.get_screen_width(), rl.get_screen_height())
            self._debouncing.val = 0

    def _update_pygame(self, events, fps: int | None = None):
        fps = fps or self._fps
        pygame = md.pygame
        unicoded = False
        for event in events:
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                self.pygame_unicode = event.unicode
                unicoded = True
            if (
                event.type == pygame.VIDEORESIZE
                and window_resize_type != ResizeType.ResizeFromOriginal
            ):
                w, h = event.w, event.h
                self.size = NvVector2(w, h)
                self._debouncing.val = 0
        if unicoded == False:
            self.pygame_unicode = None
        self._clock.tick(fps)

    def update(self, events=None, fps: int | None = None):
        """Events required only for pygame backend"""
        if events is None and self.renderer_type.pygame_like:
            events = md.pygame.event.get()
        nevu_state.current_events = events
        window_update_utils(events)
        window_specific_update(events, fps)

        debounce = self._debouncing
        if 0 <= debounce.val < debounce.max_val:
            if self.debounce:
                debounce.inc(1 * time.dt)
            else:
                debounce.ended = True
        if debounce.ended:
            self._resize()
            debounce.reset(-1)

        self.z_system.cycle(
            mouse.pos,
            mouse.left_fdown,
            mouse.left_up,
            mouse.any_wheel,
            mouse.wheel_down,
        )
        self.callbacks.run(BindType.Update, self)
        if on_update := self.on_update:
            self._hook_cycle(on_update)
        self.renderer.update()

    def _resize(self):
        if window_resize_type == ResizeType.CropToRatio:
            self._recalculate_render_area()
            render_width = self.size[0] - self._crop_width_offset
            render_height = self.size[1] - self._crop_height_offset
            self.callbacks.run(BindType.Resize, NvVector2(render_width, render_height))
        else:
            self.callbacks.run(BindType.Resize, self.size)

        if on_resize := self.on_resize:
            self._hook_cycle(on_resize)

    def draw_overlay(self):
        texture = overlay.get_result(self.size)
        if self.renderer_type.raylib:
            texture = texture.texture  # type: ignore
            md.rl.begin_blend_mode(md.rl.BlendMode.BLEND_ALPHA_PREMULTIPLY)

        renderer = self.renderer
        if self.renderer_type.raylib:
            assert self.is_raylib(renderer)
            renderer.fast_blit(texture, (0, 0))
        else:
            renderer.blit(texture, (0, 0))
        if self.renderer_type.raylib:
            md.rl.end_blend_mode()

    def _update_utils(self, events):
        mouse.update(events)  # type: ignore
        time.update()
        keyboard.update()

    @property
    def title(self):
        return self._title

    @title.setter
    def title(self, text: str):
        self._title = text
        if self.renderer_type.raylib:
            md.rl.set_window_title(text)
        else:
            md.pygame.display.set_caption(self._title)

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

    def _hook_cycle(self, hook_list: list):
        for hook in hook_list:
            if hook:
                hook()

    @property
    def rel(self):
        return NvVector2((self.size - self._x2_offset) / self.original_size)

    def get_nvrect(self):
        return NvRect(0, 0, self.size[0], self.size[1])


_initialized_window_kwargs_buffer = None


class InitializedWindow(Window):
    @staticmethod
    def from_raylib(**kwargs: Unpack[WindowKwargs]):
        window = InitializedWindow(backend=Backend.RayLib, **kwargs)
        return window

    @staticmethod
    def from_pygame(display: "Surface", **kwargs: Unpack[WindowKwargs]):
        global _initialized_window_kwargs_buffer
        _initialized_window_kwargs_buffer = {"screen": display}
        window = InitializedWindow(backend=Backend.Pygame, **kwargs)
        _initialized_window_kwargs_buffer = None
        return window

    @staticmethod
    def from_sdl(
        sdl_window: "SDL2Window", renderer: "Renderer", **kwargs: Unpack[WindowKwargs]
    ):
        global _initialized_window_kwargs_buffer
        _initialized_window_kwargs_buffer = {
            "sdl_window": sdl_window,
            "renderer": renderer,
        }
        window = InitializedWindow(backend=Backend.Sdl, **kwargs)
        _initialized_window_kwargs_buffer = None
        return window

    def _init_graphics(self):
        global window_specific_update
        kwargs = _initialized_window_kwargs_buffer
        back_to_class = {
            Backend.Pygame: WindowRendererPygame,
            Backend.Sdl: WindowRendererSdl,
            Backend.RayLib: WindowRendererRaylib,
        }
        back_to_update = {
            Backend.RayLib: self._update_raylib,
            Backend.Pygame: self._update_pygame,
            Backend.Sdl: self._update_pygame,
        }
        if kwargs is None:
            self._renderer = back_to_class[self.backend].create_initialized(self)
        else:
            self._renderer = back_to_class[self.backend].create_initialized(
                self, **kwargs
            )
        window_specific_update = back_to_update[self.backend]
        self.renderer_type._initial_check()

    def __init__(self, **kwargs):
        """Do not use as constructor, use from_raylib, from_pygame or from_sdl"""
        self._init_base()
        self._init_kwargs(**kwargs)

        init_modules()

        self._init_graphics()
        self._init_hooks()
        self._init_lists(self.renderer.get_size_tuple())

        nevu_state.current_events = []

        if window_resize_type == ResizeType.CropToRatio:
            self._recalculate_render_area()
        self.callbacks = Callbacks()
        self.z_system = ZSystem()
        self._reset_nevu_state()

        init_keys()
        self._init_globals()
        if not self.renderer_type.raylib:
            self._clock = md.pygame.time.Clock()

        self.begin_frame = self._renderer.begin_frame
        self.end_frame = self._renderer.end_frame


class ConfiguredWindow(Window):
    def __init__(self):
        size = standart_config.win_config["size"]
        display_type = standart_config.win_config["display"]
        display_type = ConfigType.Window.Display(display_type)
        ratio = standart_config.win_config["ratio"]
        title = standart_config.win_config["title"]
        resizeable = standart_config.win_config["resizable"]
        base_fps = standart_config.win_config["fps"]
        # fps = standart_config.win_config["fps"] TODO
        super().__init__(
            title=title,
            size=size,
            resize_type=ResizeType.CropToRatio,
            backend=display_type,
            ratio=ratio,
            resizable=resizeable,
            base_fps=base_fps,
        )
