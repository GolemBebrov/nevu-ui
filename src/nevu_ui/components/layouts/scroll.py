from __future__ import annotations

import weakref
from abc import ABC
from typing import Any, TypeGuard, Unpack

from nevu_ui.components._typehints import _AlignTemplate, _ScrollableKwargs
from nevu_ui.components.layouts import LayoutType
from nevu_ui.components.nevuobj import NevuObject
from nevu_ui.components.widgets import Widget
from nevu_ui.core import Annotations
from nevu_ui.core.enums import (
    Align,
    BindType,
    CustomFunctions,
    HoverState,
    Orientation,
)
from nevu_ui.core.state import nevu_state
from nevu_ui.fast.logic.fast_logic import (
    _very_light_update_helper,
    draw_widgets_optimized,
    py_get_item_abs_coords,
    rl_predraw_widgets,
)
from nevu_ui.fast.nvspecific.nvspec import (
    scrollable_recollide_items,
    scrollable_update_collided,
)
from nevu_ui.fast.nvvector2 import NvVector2
from nevu_ui.presentation.color import SubThemeRole
from nevu_ui.presentation.style import Style
from nevu_ui.utils import keyboard, mouse
from nevu_ui.utils.keys import Keys

class ScrollBar(Widget):
    def __init__(
        self,
        size,
        style,
        orientation: Orientation,
        master: ScrollableBase | None = None,
        **params: Unpack[_ScrollableKwargs],
    ):
        super().__init__(size, style, **params)
        self.master: ScrollableBase = master  # type: ignore
        self.orientation = orientation
        self._add_custom_flags(CustomFunctions.update_main)

    def _add_params(self):
        super()._add_params()
        self._change_param_default("clickable", True)
        self._change_param_default("hoverable", True)
        self._change_param_default("subtheme_role", SubThemeRole.TERTIARY)

    def _init_numerical(self):
        super()._init_numerical()
        self._percentage = 0.0
        self.z = 99
        self._drag_start_mouse = 0.0
        self._drag_start_percentage = 0.0

    def _init_booleans(self):
        super()._init_booleans()
        self.scrolling = False

    def _init_lists(self):
        super()._init_lists()
        self.track_start_local = NvVector2(0, 0)
        self.track_start_abs = NvVector2(0, 0)
        self.track_length = NvVector2(0, 0)

    def _orientation_to_int(self):
        return self.orientation.axis

    def _system_callback_binds(self):
        super()._system_callback_binds()
        self._system_callbacks.bind(BindType.Click, _scrollbar_on_click)
        self._system_callbacks.bind(BindType.KeyUp, _scrollbar_on_keyup)
        self._system_callbacks.bind(BindType.KeyUpAbandon, _scrollbar_on_keyup_abandon)

    @property
    def percentage(self) -> float:
        return self._percentage

    @percentage.setter
    def percentage(self, value: float):
        axis = self._orientation_to_int()
        self._percentage = max(0.0, min(float(value), 100.0))
        movable_area = self.track_length[axis] - self.current_size[axis]
        if movable_area <= 0:
            self.coordinates[axis] = self.track_start_local[axis]
            return
        path_to_add = movable_area * (self._percentage / 100.0)
        self.coordinates[axis] = self.track_start_local[axis] + path_to_add

    def set_scroll_params(
        self, start_local: NvVector2, start_abs: NvVector2, length: NvVector2
    ):
        self.track_start_local = start_local
        self.track_start_abs = start_abs
        self.track_length = length

    def _update_main(self):
        super()._update_main()
        axis = self._orientation_to_int()
        if self.scrolling:
            movable_area = self.track_length[axis] - self.current_size[axis]
            if movable_area > 0:
                mouse_delta = mouse.pos[axis] - self._drag_start_mouse
                perc_delta = (mouse_delta / movable_area) * 100.0
                self.percentage = self._drag_start_percentage + perc_delta

    def move_by_percents(self, percents: float):
        self.percentage = self.percentage + percents
        self.scrolling = False

    def set_percents(self, percents: float):
        self.percentage = percents
        self.scrolling = False


class ScrollableBase(LayoutType, ABC):
    key_power: float | int
    scroll_power: float | int
    append_key: Any
    descend_key: Any
    scrollbar_relative_size: NvVector2
    content_type = list[tuple[Align, NevuObject] | NevuObject]
    basic_alignment: Align
    orientation: Orientation

    def __init__(
        self,
        content: content_type | None = None,
        size: Annotations.nevuobj_size = None,
        style: Annotations.nevuobj_style = None,
        **params: Unpack[_ScrollableKwargs],
    ):
        super().__init__(content, size, style, **params)

    def _create_template(  # type: ignore
        self, size: Annotations.nevuobj_size, content: content_type | None,
    ):
        return _AlignTemplate(size, content)  # type: ignore

    def _init_booleans(self):
        super()._init_booleans()
        self._scroll_needs_update = False

    def _init_numerical(self):
        super()._init_numerical()
        self.actual_max_main = 0

    def _init_lists(self):
        super()._init_lists()
        self.widgets_alignment = []
        self.collided_items = []
        self._offset = NvVector2()
        self._last_known_abs_coords = NvVector2(-9999, -9999)
        self._last_window_size = NvVector2(-9999, -9999)

    def _coordinates_setter(self, coordinates: NvVector2) -> bool:
        if self.booted is False:
            return True
        self.cached_coordinates = None
        self._update_scroll_bar()
        self._update_offset()
        return True

    def _add_params(self):
        super()._add_params()
        self._add_param("key_power", int, 5)
        self._add_param("scroll_power", int, 5)
        self._add_param("inverted_scrolling", bool, False)
        self._add_param("scrollbar_relative_size", NvVector2 | type(None), None)
        self._add_param("basic_alignment", Align | type(None), None)
        self._add_param("append_key", Any, Keys.A)
        self._add_param("descend_key", Any, Keys.D)
        self._add_param("spacing", float, 30, layer=1)
        self._add_param("orientation", Orientation, Orientation.Column)

    def _system_callback_binds(self):
        super()._system_callback_binds()
        self._system_callbacks.bind(BindType.Scroll, _scrollable_on_scroll)

    def _lazy_init(self, content: content_type | None = None, size: NvVector2 | list | None = None):  # type: ignore
        super()._lazy_init(size, content)  # type: ignore
        self._init_scroll_bar()
        self._update_scroll_bar()

    def add_items(self, content: content_type | None):
        if not content: return
        for content_item in content:
            if isinstance(content_item, tuple):
                align, item = content_item
            elif isinstance(content_item, NevuObject):
                align, item = self.basic_alignment, content_item
            else:
                raise TypeError(Annotations.format_nvtype_nvobject_error("list[tuple[Align, NevuObject] or NevuObject]", "content", f"{content}.\nWrong part: {content_item}", self))
            assert type(align) is Align and isinstance(item, NevuObject), (
                f"Incorrect align or item ({align}, {item})"
            )
            self.add_item(item, align)

    def _init_scroll_bar(self):
        self.scroll_bar = self._create_scroll_bar()
        self._boot_scrollbar(self.scroll_bar)

    def _boot_up(self):
        super()._boot_up()
        self._regenerate_coordinates()

    def _boot_scrollbar(self, scroll_bar: ScrollBar):
        scroll_bar._boot_up()
        scroll_bar._init_start()
        scroll_bar.booted = True

    def get_offset(self) -> int | float:
        return self.actual_max_main / 100 * self.scroll_bar.percentage

    def _widget_drawable(self, item: NevuObject):
        rect1 = item.get_nvrect()
        rect2 = self.get_nvrect()
        return rect1.collide_rect(rect2)

    def _rl_predraw_widgets(self):
        need_recollide = (
            self.absolute_coordinates.x != self._last_known_abs_coords.x
            or self.absolute_coordinates.y != self._last_known_abs_coords.y
        )
        if need_recollide:
            self.collided_items = scrollable_recollide_items(self, self.items)
            self._last_known_abs_coords.x = self.absolute_coordinates.x
            self._last_known_abs_coords.y = self.absolute_coordinates.y

        rl_predraw_widgets(self.collided_items, LayoutType, Widget)
        if self.floating_items:
            rl_predraw_widgets(self.floating_items, LayoutType, Widget)

        if self.actual_max_main > 0:
            self.scroll_bar.draw()

    @staticmethod
    def _is_scrollable(layout: NevuObject) -> TypeGuard["ScrollableBase"]:
        return isinstance(layout, ScrollableBase)

    def _draw_main(self):
        draw_widgets_optimized(self, self.collided_items, LayoutType, Widget)
        if self.actual_max_main > 0:
            draw_widgets_optimized(self, [self.scroll_bar], LayoutType, Widget)

    def _update_main(self):
        super()._update_main()
        assert self.scroll_bar
        scroll_bar = self.scroll_bar

        if self.first_parent_menu and self.first_parent_menu._window:
            win_size = self.first_parent_menu._window.size
            if (
                win_size.x != self._last_window_size.x
                or win_size.y != self._last_window_size.y
            ):
                self._last_window_size = NvVector2.from_xy(win_size.x, win_size.y)
                self._regenerate_max_values()
                self._update_scroll_bar()
                self._scroll_needs_update = True

        if self.actual_max_main > 0:
            old_percentage = scroll_bar.percentage
            scroll_bar.update()
            if old_percentage != scroll_bar.percentage:
                self._scroll_needs_update = True

        if self._scroll_needs_update:
            self._update_offset()
            _very_light_update_helper(
                self.items,
                self.cached_coordinates or [],
                self.first_parent_menu.absolute_coordinates,
                self._offset,
                self,
            )
            self.collided_items = scrollable_recollide_items(self, self.items)
            if self.actual_max_main > 0:
                coords = self._get_scrollbar_coordinates()
                if coords:
                    scroll_bar.coordinates = coords
                    scroll_bar.absolute_coordinates = py_get_item_abs_coords(self, scroll_bar)
            self._scroll_needs_update = False
        scrollable_update_collided(self.collided_items)

    def _recollide_items(self):
        drawable = self._widget_drawable
        true_rect = self.get_nvrect()
        self.absolute_coordinates = NvVector2.from_xy(true_rect.x, true_rect.y)
        for item in self.items:
            item.absolute_coordinates = py_get_item_abs_coords(self, item)
        self.collided_items = [item for item in self.items if drawable(item)]

    def _get_align_offset(self, item: NevuObject, alignment: Align) -> float:
        cross_axis = self.orientation.cross_axis
        size_diff = self.size[cross_axis] - item.size[cross_axis]

        match alignment:
            case Align.CENTER:
                offset = size_diff * 0.5
            case Align.RIGHT | Align.BOTTOM:
                offset = size_diff
            case _:
                offset = 0.0

        rel = self._resize_ratio[cross_axis]
        return offset * rel

    def _regenerate_coordinates(self):
        super()._regenerate_coordinates()
        self._regenerate_max_values()
        spacing = self.spacing
        main_axis = self.orientation.axis
        cross_axis = self.orientation.cross_axis
        main_ratio = self._resize_ratio[main_axis]
        spacing = self.spacing * main_ratio

        items = self.items
        widgets_alignment = self.widgets_alignment

        cached_coordinates = []
        current_main = spacing

        for item, align in zip(items, widgets_alignment):
            new_coords = NvVector2()
            new_coords[main_axis] = self.coordinates[main_axis] + current_main + (spacing * 0.5)
            new_coords[cross_axis] = self.coordinates[cross_axis] + self._get_align_offset(item, align)
            item.set_coordinates(new_coords)
            item.absolute_coordinates = py_get_item_abs_coords(self, item)
            current_main += item.current_size[main_axis] + spacing

            cached_coordinates.append(item.coordinates.copy())

        self.cached_coordinates = cached_coordinates
        self._update_offset()

        _very_light_update_helper(
            items,
            self.cached_coordinates or [],
            self.first_parent_menu.absolute_coordinates,
            self._offset,
            self,
        )
        self.collided_items = scrollable_recollide_items(self, self.items)

    def _update_start(self):
        super()._update_start()
        if self.hover_state == HoverState.NotHovered: return
        if nevu_state.keyboard_focused: return
        assert self.scroll_bar
        inverse = -1 if self.inverted_scrolling else 1
        fdown = keyboard.is_fdown
        if fdown(self.append_key):
            scroll_bar = self.scroll_bar
            scroll_bar._percentage += self.key_power * -inverse
            scroll_bar._percentage = max(0, min(100, scroll_bar._percentage))
            self._scroll_needs_update = True
        if fdown(self.descend_key):
            scroll_bar = self.scroll_bar
            scroll_bar._percentage += self.key_power * inverse
            scroll_bar._percentage = max(0, min(100, scroll_bar._percentage))
            self._scroll_needs_update = True

    def _update_scroll_bar(self):
        if not self.first_parent_menu: return
        assert self.first_parent_menu._window
        main_axis = self.orientation.axis
        cross_axis = self.orientation.cross_axis

        absolute_coords = self.absolute_coordinates
        local_start = NvVector2.from_xy(0, 0)
        assert self.scroll_bar
        local_start[cross_axis] = (absolute_coords + self.current_size - self.scroll_bar.current_size)[cross_axis]
        local_start[main_axis] = absolute_coords[main_axis]
        track_length = NvVector2.from_xy(0, 0)
        track_length[main_axis] = self.current_size[main_axis]
        self.scroll_bar.set_scroll_params(local_start, absolute_coords, track_length)

    def _resize_content(self, resize_ratio: NvVector2):
        assert self.scroll_bar
        old_percentage = self.scroll_bar.percentage
        super()._resize_content(resize_ratio)
        self.scroll_bar._resize(resize_ratio)
        self._update_scroll_bar()
        self.scroll_bar.set_percents(old_percentage)
        self.cached_coordinates = None
        self._scroll_needs_update = True
        self._regenerate_coordinates()
        self.scroll_bar.scrolling = False
        self._update_offset()
        assert self.first_parent_menu
        _very_light_update_helper(
            self.items,
            self.cached_coordinates or [],
            self.first_parent_menu.absolute_coordinates,
            self._offset,
            self,
        )

    def _on_item_add(self, item: NevuObject):
        self.cached_coordinates = None
        if self.booted is False: return
        self._update_scroll_bar()

    def turn_off(self, *, recursive=True):
        super().turn_off(recursive=recursive)
        if recursive and hasattr(self, "scroll_bar") and self.scroll_bar:
            self.scroll_bar.turn_off()

    def turn_on(self, *, recursive=True):
        super().turn_on(recursive=recursive)
        if recursive and hasattr(self, "scroll_bar") and self.scroll_bar:
            self.scroll_bar.turn_on()

    def add_item(self, item: NevuObject, alignment: Align | None = None):  # type: ignore
        alignment = alignment or self.basic_alignment or Align.CENTER
        super().add_item(item)
        self.widgets_alignment.append(alignment)

    def clear(self):
        self.items.clear()
        self.widgets_alignment.clear()
        self._restart_coordinates()

    def apply_style_to_childs(self, style: Style):
        super().set_items_style(style)
        self.apply_scroll_bar_style(style)

    def apply_scroll_bar_style(self, style: Style):
        assert self.scroll_bar is not None
        self.scroll_bar.style = style

    def _restart_coordinates(self):
        self.actual_max_main = 0

    def _create_scroll_bar(self) -> ScrollBar:
        if not self.scrollbar_relative_size:
            percentage = NvVector2.from_xy(0, 0)
            percentage[self.orientation.axis] = 4
            percentage[self.orientation.cross_axis] = 2
        else:
            percentage = self.scrollbar_relative_size
        size = self.size / 100 * percentage
        return ScrollBar(size, self.style, self.orientation, weakref.ref(self))

    def _kill_base(self):
        super()._kill_base()
        if hasattr(self, "scroll_bar") and self.scroll_bar:
            self.scroll_bar.kill()
            del self.scroll_bar
            self.scroll_bar = None

    def _get_scrollbar_coordinates(self) -> NvVector2:
        main_axis = self.orientation.axis
        main_ratio = self._resize_ratio[main_axis]
        coordinates = self.coordinates
        size = self.size
        scroll_bar = self.scroll_bar
        assert scroll_bar
        coordinates = NvVector2.from_xy(
            coordinates.x + self.relx(size.x - scroll_bar.size.x),
            coordinates.y
        )
        coordinates[main_axis] = coordinates[main_axis] + main_ratio * (size.y - scroll_bar.size.y) / 100 * scroll_bar.percentage
        return coordinates

    def _update_offset(self):
        main_axis = self.orientation.axis
        main_ratio = self._resize_ratio[main_axis]
        offset = NvVector2.from_xy(0, 0)
        offset[main_axis] = main_ratio * self.get_offset()
        self._offset = offset

    def _regenerate_max_values(self):
        assert nevu_state.window, "Window is not initialized"
        main_axis = self.orientation.axis
        main_ratio = self._resize_ratio[main_axis]
        spacing = self.spacing * main_ratio
        total_height = spacing

        for item in self.items:
            total_height += item.current_size[main_axis] + spacing

        visible_height = self.current_size[main_axis]

        self.actual_max_main = max(
            0, (total_height - visible_height) / main_ratio
        )

class VScroll(ScrollableBase):
    def _add_params(self):
        super()._add_params()
        self._change_param_default("append_key", Keys.Up)
        self._change_param_default("descend_key", Keys.Down)
        self._change_param_default("basic_alignment", Align.LEFT)
        self._change_param_default("orientation", Orientation.Column)
        self._block_param("orientation")

class HScroll(ScrollableBase):
    def _add_params(self):
        super()._add_params()
        self._change_param_default("append_key", Keys.Left)
        self._change_param_default("descend_key", Keys.Right)
        self._change_param_default("basic_alignment", Align.TOP)
        self._change_param_default("orientation", Orientation.Row)
        self._block_param("orientation")

# === NOT CLASS FUNCTIONS ===
def _scrollbar_on_click(self: ScrollBar):
    self.scrolling = True
    main_axis = self.orientation.axis
    self._drag_start_mouse = mouse.pos[main_axis]
    self._drag_start_percentage = self._percentage

def _scrollbar_on_keyup(self: ScrollBar):
    self.scrolling = False

def _scrollbar_on_keyup_abandon(self: ScrollBar):
    self.scrolling = False

def _scrollable_on_scroll(self: ScrollableBase, side: bool):
    direction = 1 if side else -1
    if self.inverted_scrolling:
        direction *= -1

    assert self.scroll_bar

    old_percentage = self.scroll_bar._percentage
    self.scroll_bar._percentage += self.scroll_power * direction
    self.scroll_bar._percentage = max(0, min(100, self.scroll_bar._percentage))

    if self.scroll_bar._percentage == old_percentage:
        if self._parent_layout is not None and isinstance(self._parent_layout, ScrollableBase):
            self._parent_layout._run_callbacks(BindType.Scroll, side)
        return

    self._scroll_needs_update = True
