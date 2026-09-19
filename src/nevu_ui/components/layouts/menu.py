from __future__ import annotations

from itertools import chain
from typing import TYPE_CHECKING, Unpack

from nevu_ui.core.state import nevu_state
from nevu_ui.fast.logic.fast_logic import draw_widgets_optimized
from nevu_ui.fast.raylib.nevu_raylib import begin_blend_mode, end_blend_mode
from nevu_ui.presentation.color.color import Color

if TYPE_CHECKING:
    from nevu_ui import NevuObject, Window
from nevu_ui.components._typehints import _MenuKwargs
from nevu_ui.components.layouts.layout_base import LayoutType
from nevu_ui.components.widgets.widget import Widget
from nevu_ui.core.annotations import Annotations
from nevu_ui.core.enums import Backend, BindType, ParamLayer
from nevu_ui.fast.nvvector2 import NvVector2
from nevu_ui.presentation.color.color_theme import PairColorRole


class _MenuBgWidget(Widget):
    @property
    def subtheme_content(self):
        return self.style.get_pair_color(PairColorRole.BACKGROUND, inverted = self.inverted)

class Menu(LayoutType):
    main_layout: LayoutType | None
    def __init__(self, window: Window, size: Annotations.nevuobj_size = None, style: Annotations.nevuobj_style = None, **params: Unpack[_MenuKwargs]):
        if size is None:
            size = window.size.copy()
        self.surface = None
        super().__init__(None, size, style, **params)

        self._window = window
        self._window.callbacks.bind(BindType.Resize, self._on_window_resize)
        size = self._normalize(size)
        self._lazy_init_wrapper(size = size, content = None)
        self.booted = True
        self._boot_up()
        backends_to_draw = {
            Backend.Pygame: 0,
            Backend.Sdl: 1,
            Backend.RayLib: 2,
        }
        self._main_draw = backends_to_draw.get(nevu_state.window.backend)

    def _all_items(self):
        items_iter = super()._all_items()
        if self.main_layout is not None:
            return chain(items_iter, [self.main_layout])
        return items_iter

    def _draw_start(self):
        draw_widgets_optimized(self, self.floating_items, LayoutType, Widget)

    def _create_bg_widget(self):
        bg = _MenuBgWidget(
            self.size.xy,
            self.style,
            single_instance=True,
            clickable=False,
            hoverable=False,
            draw_borders=False,
            z=-999,
            bg_variant=True,
        )
        bg.set_coordinates(NvVector2.from_xy(0, 0))
        bg._sended_z_link = True
        self.bg_widget = bg
        return bg

    def _lazy_init(self, size: NvVector2 | list, content: None = None):
        self._cached_start_pos = self.start_pos
        self.start_pos = self._normalize(self.start_pos)
        super()._lazy_init(size, content)
        self.surface = self.renderer.core.create_clear(self.current_size)
        if self.bg_widget is None:
            self._create_bg_widget()

    def _on_window_resize(self, size: NvVector2):
        first_window_size = self._window.original_size
        resize_ratio = NvVector2.from_xy(
            size[0] / first_window_size.x, size[1] / first_window_size.y
        )
        self._resize(resize_ratio)

    def _coordinates_setter(self, coordinates: NvVector2) -> bool:
        result = super()._coordinates_setter(coordinates)
        self.absolute_coordinates = self.coordinates + self._window.offset
        return result

    def _resize_content(self, resize_ratio: NvVector2):
        self.surface = self.renderer.core.create_clear(self.size*resize_ratio)
        if self._start_pos_relative_placed:
            self.set_coordinates(self._normalize(self._cached_start_pos))
        self.absolute_coordinates = self.coordinates + self._window.offset
        super()._resize_content(resize_ratio)
        if layout := self.main_layout:
            layout._resize(resize_ratio)
            layout.set_coordinates((self.current_size - layout.current_size) / 2)
            layout.absolute_coordinates = layout.coordinates + self.absolute_coordinates

    def _add_params(self):
        super()._add_params()
        self._add_param("main_layout", LayoutType | type(None), None, setter = self._main_layout_setter, layer = ParamLayer.Lazy)
        self._change_param_default("z", -999)

    def _main_layout_setter(self, value):
        if self.main_layout is not None:
            self.main_layout.kill()
        if not value: return
        if not value._can_be_main_layout:
            raise ValueError(f"Layout {type(value).__name__} can't be main")

        value._template["size"] = self._normalize(value._template["size"])

        value._connect_to_menu(self)

        value._init_start()
        value._boot_up()
        value._lazy_init_wrapper(**value._template.__dict__)

        value.first_parent_menu = self

        value._resize(self._resize_ratio)
        value.set_coordinates((self.current_size - value.current_size) / 2)
        value.absolute_coordinates = value.coordinates + self.absolute_coordinates

        value.update()
        return value

    def draw(self):
        if not self._visible or self._wait_mode or self._dead or not self.surface:
            return

        dtype = nevu_state.window.renderer_type

        surf = self.surface
        if dtype.raylib:
            self._rl_predraw_widgets()

            with surf:
                surf.fast_clear(Color.Blank)
                begin_blend_mode(5)
                super().draw()
                if self.main_layout:
                    self.main_layout.draw()
                end_blend_mode()
            self._window.renderer.blit(surf.texture, self.absolute_coordinates.get_int_tuple())

        elif dtype.pygame:
            surf.fill((0, 0, 0, 0))
            super().draw()
            if self.main_layout:
                self.main_layout.draw()
            self._window.renderer.blit(surf, self.absolute_coordinates.get_int_tuple())

    def update(self):
        super().update()
        main_layout = self.main_layout
        if not main_layout: return
        main_layout.update()

    def _init_booleans(self):
        super()._init_booleans()
        self._can_be_main_layout = False

    def _init_objects(self):
        super()._init_objects()
        self.first_parent_menu = self
        self.menu = self

    def _kill_base(self):
        super()._kill_base()
        self._window = None
        if self.main_layout:
            self.main_layout.kill()
        self.main_layout = None

    def _connect_to_layout(self, layout: LayoutType):
        raise NotImplementedError("Menu can not be connected to another layout.")
    def _connect_to_menu(self, menu: Menu):
        raise NotImplementedError("Menu can not be connected to another menu.")
    def add_item(self, item: NevuObject):
        raise NotImplementedError("Menu doesn't support adding items. Use add_floating_item if you really want to add an item inside.")
    def clone(self):
        raise NotImplementedError("Menu can not be cloned.")
