from __future__ import annotations

from itertools import chain
from typing import TYPE_CHECKING, Unpack

from nevu_ui.core.state import nevu_state
from nevu_ui.cython.logic.logic import draw_items, predraw_raylib_widgets
from nevu_ui.cython.raylib.raylib import begin_blend_mode, end_blend_mode
from nevu_ui.presentation import color

if TYPE_CHECKING:
    from nevu_ui import NevuObject, Window
from nevu_ui.components._typehints import _MenuKwargs
from nevu_ui.components.layouts.base import BaseLayout
from nevu_ui.components.widgets.widget import Widget
from nevu_ui.core.annotations import Annotations
from nevu_ui.core.enums import Backend, BindType, ParamLayer
from nevu_ui.core.size import _SizeRule
from nevu_ui.core.size.rules import (
    CFill,
    CFillH,
    CFillW,
    Fill,
    FillH,
    FillW,
)
from nevu_ui.cython.vector2 import Vector2
from nevu_ui.presentation.theme import PairColorRole

class _MenuBgWidget(Widget):
    @property
    def subtheme_content(self):
        return self.style.get_pair_color(PairColorRole.Background, inverted = self.inverted)

class Menu(BaseLayout):
    main_layout: BaseLayout | None
    def __init__(self, window: Window, size: Annotations.nevuobj_size = None, style: Annotations.nevuobj_style = None, **params: Unpack[_MenuKwargs]):
        if size is None:
            size = window.size.copy()
        self.surface = None
        super().__init__(None, size, style, **params)

        self._window: Window = window
        self._window.callbacks.bind(BindType.Resize, self._on_window_resize)
        size = self._normalize(size)
        self._lazy_init_wrapper(size = size, content = None)
        self.booted = True
        self._boot_up()

    def _init_lists(self):
        super()._init_lists()
        self._main_layout_list = []

    def _all_items(self):
        items_iter = super()._all_items()
        if self.main_layout is not None:
            return chain(items_iter, [self.main_layout])
        return items_iter

    def _draw_start(self):
        draw_items(self, self.floating_items, BaseLayout, Widget)

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
        bg.set_coordinates(Vector2.from_xy(0, 0))
        bg._sended_z_link = True
        self.bg_widget = bg
        return bg

    def _lazy_init(self, size: Vector2 | list, content: None = None):
        self._cached_start_pos = self.start_pos
        self.start_pos = self._normalize(self.start_pos)
        super()._lazy_init(size, content)
        self._on_window_resize(self.size * self._window.rel)
        self.surface = self.renderer.core.create_surface(self.current_size)
        if self.bg_widget is None:
            self._create_bg_widget()

    def _on_window_resize(self, size: Vector2):
        first_window_size = self._window.original_size
        resize_ratio = Vector2.from_xy(
            size[0] / first_window_size.x, size[1] / first_window_size.y
        )
        self._resize(resize_ratio)

    def _coordinates_setter(self, coordinates: Vector2) -> bool:
        result = super()._coordinates_setter(coordinates)
        self.absolute_coordinates = coordinates + self._window.offset
        if self.main_layout:
            self.main_layout.absolute_coordinates = self.main_layout.coordinates + self.absolute_coordinates
        return result

    def _resize_content(self, resize_ratio: Vector2):
        scaled = self.size * resize_ratio
        self.surface = self.renderer.core.create_surface(
            Vector2.from_xy(max(1.0, scaled.x), max(1.0, scaled.y))
        )
        if self._start_pos_relative_placed:
            self.set_coordinates(self._normalize(self._cached_start_pos))
        self.absolute_coordinates = self.coordinates + self._window.offset
        if layout := self.main_layout:
            layout.surface = self.surface
        super()._resize_content(resize_ratio)
        self.cached_coordinates = 10
        if layout := self.main_layout:
            layout.set_coordinates((self.current_size - layout.current_size) / 2)
            layout.absolute_coordinates = layout.coordinates + self.absolute_coordinates

    def _add_params(self):
        super()._add_params()
        self._add_param("main_layout", BaseLayout | type(None), None, setter = self._main_layout_setter, layer = ParamLayer.Lazy)
        self._change_param_default("z", -999)

    def _system_callback_binds(self):
        super()._system_callback_binds()
        self._system_callbacks.bind(BindType.StyleChange, _menu_on_style_change)

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
        if value._wait_mode:
            value._lazy_init_wrapper(**value._template.__dict__)

        value.first_parent_menu = self

        value._resize(self._resize_ratio)
        value.set_coordinates((self.current_size - value.current_size) / 2)
        value.absolute_coordinates = value.coordinates + self.absolute_coordinates

        value.update()
        self._main_layout_list = [value]
        return value

    def _parse_fillx(self, fill_rule: _SizeRule, fill_type: type[_SizeRule], pos: int) -> float | None:
        base_size = self.original_size if (hasattr(self, "original_size") and self.original_size.x > 0) else self._window.original_size
        current_size = self.current_size if (hasattr(self, "current_size") and self.current_size.x > 0) else self._window.size

        if fill_type is Fill:
            return self._percent_helper(base_size[pos], fill_rule.value)
        elif fill_type is FillW:
            return self._percent_helper(base_size.x, fill_rule.value)
        elif fill_type is FillH:
            return self._percent_helper(base_size.y, fill_rule.value)
        elif fill_type is CFill:
            return self._percent_helper(current_size[pos], fill_rule.value)
        elif fill_type is CFillW:
            return self._percent_helper(current_size.x, fill_rule.value)
        elif fill_type is CFillH:
            return self._percent_helper(current_size.y, fill_rule.value)

    def draw(self):
        if not self._visible or self._wait_mode or self._dead or not self.surface:
            return

        rtype = nevu_state.window.renderer_type

        surf = self.surface
        if rtype.raylib:
            self._rl_predraw_widgets()
            predraw_raylib_widgets(self._main_layout_list or [], None, None)
            if self.canvas:
                for c_item in self.canvas._content:
                    if hasattr(c_item, "_cached_surface") and c_item._cached_surface is None:
                        c_item.draw(surf, self.renderer, self)

            with surf:
                surf.clear(color.Blank)
                begin_blend_mode(5)
                super().draw()
                if self.main_layout:
                    self.main_layout.draw()
                end_blend_mode()
            self._window.renderer.blit(surf.native.texture, self.absolute_coordinates.get_int_tuple())
        elif rtype.pygame:
            surf.fill(color.Blank)
            super().draw()
            if self.main_layout:
                self.main_layout.draw()
            self._window.renderer.blit(surf.native, self.absolute_coordinates.get_int_tuple())

    def update(self):
        super().update()
        main_layout = self.main_layout
        if not main_layout: return
        main_layout.update()

    def _init_booleans(self):
        super()._init_booleans()
        self._can_be_main_layout = False
        self._sended_z_link = True

    def _init_objects(self):
        super()._init_objects()
        self.first_parent_menu = self
        self._parent_menu = self

    def _kill_base(self):
        super()._kill_base()
        if self._window:
            self._window.callbacks.unbind(BindType.Resize, self._on_window_resize)
            self._window = None
        if self.main_layout:
            self.main_layout.kill()
            self._main_layout_list = None
        self.main_layout = None

    def _connect_to_layout(self, layout: BaseLayout):
        raise NotImplementedError("Menu can not be connected to another layout.")
    def _connect_to_menu(self, menu: Menu):
        raise NotImplementedError("Menu can not be connected to another menu.")
    def add_item(self, item: NevuObject):
        raise NotImplementedError("Menu doesn't support adding items. Use add_floating_item if you really want to add an item inside.")
    def clone(self):
        raise NotImplementedError("Menu can not be cloned.")

def _menu_on_style_change(self: Menu):
    if self.bg_widget is not None:
        self.bg_widget.style = self.style
        self.bg_widget.clear_all()
        self.bg_widget._changed = True
