import sys

import nevu_ui.core.modules as md
from nevu_ui.components.layouts.menu import Menu
from nevu_ui.core.annotations import Annotations
from nevu_ui.core.callbacks import Callbacks
from nevu_ui.fast.logic.fast_logic import fast_cycle_in_list
from nevu_ui.fast.nvspecific.nvspec import (
    _manager_main_loop_main,
    _manager_main_loop_opt,
)
from nevu_ui.window import Window

manager_created = False


class Manager:
    __slots__ = (
        "_background",
        "_fps",
        "_started",
        "_static_run",
        "_window",
        "callbacks",
        "draw_overlay",
        "force_quit",
        "init",
        "menus",
        "running",
    )

    def __new__(cls, *args, **kwargs):
        global manager_created
        if manager_created:
            raise RuntimeError("Manager is already created!")
        manager_created = True
        return super(Manager, cls).__new__(cls)

    def __init__(
        self,
        window: Window,
        menu: Menu | list[Menu] | None = None,
        *,
        callbacks: Callbacks | dict | None = None,
        force_quit: bool = True,
        draw_overlay: bool = True,
        background_color: Annotations.rgb_like_color | None = None,
        fps: int = 60,
        static_run: bool = True
    ):
        self.window = window
        self.running = True
        self.force_quit = True
        self.draw_overlay = True
        self._static_run = True
        self._background = background_color or (0, 0, 0, 255)
        self._fps = 60
        self.menus = [menu] if isinstance(menu, Menu) else menu
        self._started = False
        if isinstance(callbacks, dict):
            self.callbacks = Callbacks(callbacks)
        else:
            self.callbacks = callbacks


    def before_draw(self): ...
    def on_draw(self): ...
    def before_update(self): ...
    def on_update(self): ...
    def on_start(self): ...
    def on_exit(self): ...
    def first_update(self): ...
    def first_draw(self): ...

    def add_menu(self, menu: Menu):
        if self.menus is not None:
            self.menus.append(menu)
            return
        self.menus = [menu]

    def add_menus(self, *menus):
        if self.menus is not None:
            self.menus.extend(menus)
            return
        else: self.menus = list(menus)

    @property
    def static_run(self):
        return self._static_run

    @static_run.setter
    def static_run(self, value):
        if self._started:
            raise RuntimeError("You can't change static_run after starting main loop!")
        self._static_run = value

    @property
    def background(self):
        return self._background

    @background.setter
    def background(self, color):
        if self._started and self.static_run:
            raise RuntimeError(
                "You can't change background after starting static main loop!"
            )
        self._background = color

    @property
    def fps(self):
        return self._fps

    @fps.setter
    def fps(self, fps):
        if self._started and self.static_run:
            raise RuntimeError("You can't change fps after starting static main loop!")
        self._fps = fps

    @property
    def window(self):
        return self._window

    @window.setter
    def window(self, window: Window):
        self._window = window

    def exit(self):
        self.running = False

    def _on_exit(self):
        if self.on_exit:
            self.on_exit()
        if self.force_quit:
            if self.window.renderer_type.pygame_like:
                md.pygame.quit()
            sys.exit()

    def _first_frame(self, begin_frame, end_frame):
        begin_frame()
        if self.on_start:
            self.on_start()
        self._started = True
        if self.menus is not None:
            fast_cycle_in_list("update", self.menus)
        if self.first_update is not None:
            self.first_update()
        if self.menus is not None:
            fast_cycle_in_list("draw", self.menus)
        if self.first_draw is not None:
            self.first_draw()
        end_frame()

    def run(self):
        if self.static_run:
            _manager_main_loop_opt(self)
        else:
            _manager_main_loop_main(self)
