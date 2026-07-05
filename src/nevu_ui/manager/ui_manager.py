import sys

import nevu_ui.core.modules as md
from nevu_ui.fast.logic.fast_logic import fast_cycle_in_list
from nevu_ui.menu import Menu
from nevu_ui.window import Window

manager_created = False


class Manager:
    __slots__ = (
        "_window",
        "running",
        "force_quit",
        "_background",
        "_fps",
        "_static_run",
        "init",
        "_started",
        "menus",
    )

    def __new__(cls, *args, **kwargs):
        global manager_created
        if manager_created:
            raise RuntimeError("Manager is already created!")
        manager_created = True
        return super(Manager, cls).__new__(cls)

    def __init__(self, window: Window, menu: Menu | list[Menu] | None = None):
        self.window = window
        self.running = True
        self.force_quit = True
        self._static_run = True
        self._background = (0, 0, 0, 255)
        self._fps = 60
        self.menus = [menu] if isinstance(menu, Menu) else menu
        self._started = False

    def on_draw(self):
        pass

    def on_update(self):
        pass

    def on_start(self):
        pass

    def on_exit(self):
        pass

    def first_update(self):
        pass

    def first_draw(self):
        pass

    def add_menu(self, menu: Menu):
        if self.menus is not None:
            self.menus.append(menu)
            return
        self.menus = [menu]

    def add_menus(self, *menus):
        if self.menus is not None:
            self.menus.extend(menus)
            return

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
        if not isinstance(window, Window):
            raise ValueError("Unexpected window type!")
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

    def __main_loop_opt(self):
        begin_frame = self.window.renderer.begin_frame
        end_frame = self.window.renderer.end_frame
        w_update = self.window.update
        w_clear = self.window.clear

        on_update = self.on_update
        on_draw = self.on_draw

        self._first_frame(begin_frame, end_frame)

        bg = self.background
        fps = self.fps

        while self.running:
            menus = self.menus
            begin_frame()
            w_clear(bg)
            w_update(None, fps)
            if menus is not None:
                fast_cycle_in_list("update", menus)
            if on_update is not None:
                on_update()
            if menus is not None:
                fast_cycle_in_list("draw", menus)
            if on_draw is not None:
                on_draw()
            end_frame()

        self._on_exit()

    def __main_loop_base(self):
        begin_frame = self.window.renderer.begin_frame
        end_frame = self.window.renderer.end_frame
        w_update = self.window.update
        w_clear = self.window.clear

        self._first_frame(begin_frame, end_frame)

        while self.running:
            menus = self.menus
            begin_frame()
            w_clear(self.background)
            w_update(None, self.fps)
            if menus is not None:
                fast_cycle_in_list("update", menus)
            if (on_update := self.on_update) is not None:
                on_update()
            if menus is not None:
                fast_cycle_in_list("draw", menus)
            if (on_draw := self.on_draw) is not None:
                on_draw()
            end_frame()

        self._on_exit()

    def run(self):
        if self.static_run:
            self.__main_loop_opt()
        else:
            self.__main_loop_base()
