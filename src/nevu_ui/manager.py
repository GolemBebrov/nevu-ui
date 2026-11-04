import sys

import nevu_ui.core.modules as md
from nevu_ui.components.layouts.menu import Menu
from nevu_ui.core.annotations import Annotations
from nevu_ui.core.callbacks import Callbacks
from nevu_ui.cython.logic.logic import fast_cycle_in_list
from nevu_ui.cython.logic.logic import (
    _manager_main_loop_main,
)
from nevu_ui.window import Window

manager_created = False

class Manager:
    __slots__ = (
        "_background",
        "_fps",
        "_started",
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
            raise RuntimeError("Nevu UI Manager was already created.")
        return super(Manager, cls).__new__(cls)

    def __init__(
        self,
        window: Window,
        menus: Menu | list[Menu] | None = None,
        *,
        callbacks: Callbacks | dict | None = None,
        force_quit: bool = True,
        draw_overlay: bool = True,
        background_color: Annotations.rgb_like_color | None = None,
        fps: int = 60,
    ):
        self._window = window
        self.running = True
        self._started = False
        self.force_quit = force_quit
        self.draw_overlay = draw_overlay
        self._background = background_color or (0, 0, 0, 255)
        self._fps = fps

        self.menus = None
        if menus is None:
            self.menus = None
        elif isinstance(menus, Menu):
            self.add_menu(menus)
        elif isinstance(menus, list):
            self.add_menus(*menus)
        else:
            raise TypeError("menu must be Menu or list of Menu.")

        if callbacks is None:
            self.callbacks = None
        elif isinstance(callbacks, dict):
            self.callbacks = Callbacks(callbacks)
        elif isinstance(callbacks, Callbacks):
            self.callbacks = callbacks
        else:
            raise TypeError("callbacks must be Callbacks or dict.")

        global manager_created
        manager_created = True

    def before_draw(self): ...
    def on_draw(self): ...

    def before_update(self): ...
    def on_update(self): ...

    def on_start(self): ...
    def on_exit(self): ...

    def first_update(self): ...
    def first_draw(self): ...

    def add_menu(self, menu: Menu):
        if not isinstance(menu, Menu):
            raise TypeError("menu must be a Menu instance.")
        if self.menus is not None:
            if menu in self.menus:
                raise ValueError("Cannot add menu into manager twice.")
            self.menus.append(menu)
            return
        self.menus = [menu]

    def add_menus(self, *menus: Menu):
        if any(not isinstance(menu, Menu) for menu in menus):
            raise TypeError("One or more menus are NOT menus.")
        if self.menus is not None:
            if any(menu in self.menus for menu in menus):
                raise ValueError("One or more menus are already in the manager.")
            self.menus.extend(menus)
            return
        else:
            self.menus = list(menus)

    def remove_menu(self, menu: Menu):
        if not isinstance(self.menus, list):
            raise ValueError("Manager does not contain specified menu.")

        if menu in self.menus:
            self.menus.remove(menu)
        else:
            raise ValueError("Manager does not contain specified menu.")

    def has_menu(self, menu: Menu):
        if not self.menus:
            return False
        return menu in self.menus

    @property
    def background(self) -> Annotations.rgb_like_color:
        return self._background

    @background.setter
    def background(self, color: Annotations.rgb_like_color):
        self._background = color

    @property
    def fps(self):
        return self._fps

    @fps.setter
    def fps(self, fps: int):
        self._fps = fps

    @property
    def window(self):
        return self._window

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
        self.on_start()
        self._started = True
        if self.menus is not None:
            fast_cycle_in_list("update", self.menus)
        self.first_update()
        if self.menus is not None:
            fast_cycle_in_list("draw", self.menus)
        self.first_draw()
        end_frame()

    def run(self):
        _manager_main_loop_main(self)
