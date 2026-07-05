from __future__ import annotations

import weakref
from abc import ABC, abstractmethod
from typing import Any, NotRequired, TypeGuard, Unpack

from nevu_ui.components.layouts import LayoutType, LayoutTypeKwargs
from nevu_ui.components.layouts.typehints import AlignTemplate
from nevu_ui.components.nevuobj import NevuObject
from nevu_ui.components.widgets import Widget
from nevu_ui.core import Annotations
from nevu_ui.core.enums import Align, HoverState, ScrollBarType
from nevu_ui.fast.logic.fast_logic import (
    _very_light_update_helper,
    base_light_update,
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


class _ScrollableKwargs(LayoutTypeKwargs):
    arrow_scroll_power: NotRequired[float | int]
    wheel_scroll_power: NotRequired[float | int]
    inverted_scrolling: NotRequired[bool]
    scrollbar_perc: NotRequired[NvVector2 | None]
    basic_alignment: NotRequired[Align]
    append_key: NotRequired[Any]
    descend_key: NotRequired[Any]
    spacing: NotRequired[int | float]


class ScrollableKwargs(_ScrollableKwargs, LayoutTypeKwargs):
    pass


class ScrollableBase(LayoutType, ABC):
    arrow_scroll_power: float | int
    wheel_scroll_power: float | int
    append_key: Any
    descend_key: Any
    scrollbar_perc: NvVector2
    content_type = list[tuple[Align, NevuObject]]
    basic_alignment: Align

    class ScrollBar(Widget):
        def __init__(
            self,
            size,
            style,
            orientation: ScrollBarType,
            master: ScrollableBase | None = None,
            **constant_kwargs: Unpack[ScrollableKwargs],
        ):
            super().__init__(size, style, **constant_kwargs)
            self.master: ScrollableBase = master  # type: ignore
            if orientation not in ScrollBarType:
                raise ValueError("Orientation must be 'vertical' or 'horizontal'")
            self.orientation = orientation
            self._custom_secondary_update = True

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
            return 1 if self.orientation == ScrollBarType.Vertical else 0

        @property
        def percentage(self) -> float:
            return self._percentage

        @percentage.setter
        def percentage(self, value: float | int):
            if value != value:
                return
            axis = self._orientation_to_int()
            self._percentage = max(0.0, min(float(value), 100.0))

            movable_area = self.track_length[axis] - self._csize[axis]

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

        def _on_click_system(self):
            super()._on_click_system()
            self.scrolling = True
            axis = self._orientation_to_int()
            self._drag_start_mouse = mouse.pos[axis]
            self._drag_start_percentage = self._percentage

        def _on_keyup_system(self):
            super()._on_keyup_system()
            self.scrolling = False

        def _on_keyup_abandon_system(self):
            super()._on_keyup_abandon_system()
            self.scrolling = False

        def secondary_update(self):
            super().secondary_update()
            axis = self._orientation_to_int()

            if self.scrolling:
                movable_area = self.track_length[axis] - self._csize[axis]
                if movable_area > 0:
                    mouse_delta = mouse.pos[axis] - self._drag_start_mouse
                    perc_delta = (mouse_delta / movable_area) * 100.0
                    self.percentage = self._drag_start_percentage + perc_delta

        def move_by_percents(self, percents: int | float):
            self.percentage = self.percentage + percents
            self.scrolling = False

        def set_percents(self, percents: int | float):
            self.percentage = percents
            self.scrolling = False

    @property
    def inverted_scrolling(self) -> bool:
        return self.get_param_strict("inverted_scrolling").value

    def __init__(
        self,
        size: Annotations.nevuobj_size,
        style: Annotations.nevuobj_style = None,
        content: content_type | None = None,
        **constant_kwargs: Unpack[ScrollableKwargs],
    ):
        super().__init__(size, style, content, **constant_kwargs)

    def _create_template(
        self, size: Annotations.nevuobj_size, content: content_type | None
    ):  # type: ignore
        return AlignTemplate(size, content)

    def _init_booleans(self):
        super()._init_booleans()
        self._scroll_needs_update = False

    def _init_numerical(self):
        super()._init_numerical()
        self.max_secondary = 0
        self.max_main = 0
        self.actual_max_main = 0

    def _init_lists(self):
        super()._init_lists()
        self.widgets_alignment = []
        self.collided_items = []
        self._offset = NvVector2()
        self._last_known_abs_coords = NvVector2(-9999, -9999)
        self._last_window_size = NvVector2(-9999, -9999)

    def _coordinates_setter(self, coordinates: NvVector2):
        if self.booted == False:
            return True
        self.cached_coordinates = None
        self._update_scroll_bar()
        self._update_offset()
        return True

    def _add_params(self):
        super()._add_params()
        self._add_param("arrow_scroll_power", int, 5)
        self._add_param("wheel_scroll_power", int, 5)
        self._add_param("inverted_scrolling", bool, False)
        self._add_param("scrollbar_perc", (NvVector2, type(None)), None)
        self._add_param("basic_alignment", (Align, type(None)), None)
        self._add_param("append_key", Any, None)
        self._add_param("descend_key", Any, None)
        self._add_param("spacing", (int, float), 30, layer=1)

    def _lazy_init(self, size: NvVector2 | list, content: content_type | None = None):
        super()._lazy_init(size, content)
        self.add_items(content)
        self._init_scroll_bar()
        self._update_scroll_bar()

    def add_items(self, content: content_type | None):
        if not content:
            return
        for mass in content:
            align, item = mass
            assert type(align) == Align and isinstance(item, NevuObject), (
                f"Incorrect align or item ({align}, {item})"
            )
            self.add_item(item, align)

    def _init_scroll_bar(self):
        self.scroll_bar = self._create_scroll_bar()
        self._boot_scrollbar(self.scroll_bar)

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
        if self.actual_max_main > 0:
            self.scroll_bar.draw()

    @staticmethod
    def _is_scrollable(layout: NevuObject) -> TypeGuard["ScrollableBase"]:
        return isinstance(layout, ScrollableBase)

    def secondary_draw_content(self):
        draw_widgets_optimized(self, self.collided_items, LayoutType, Widget)
        if self.actual_max_main > 0:
            draw_widgets_optimized(self, [self.scroll_bar], LayoutType, Widget)

    def secondary_update(self):
        super().secondary_update()
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
            new_percentage = scroll_bar.percentage
            if old_percentage != new_percentage:
                self._scroll_needs_update = True

        if self._scroll_needs_update:
            self._update_offset()
            self._scroll_needs_update = False

        _very_light_update_helper(
            self.items,
            self.cached_coordinates or [],
            self.first_parent_menu.absolute_coordinates,
            self._offset,
            self,
        )

        scrollable_update_collided(self.collided_items)
        self.collided_items = scrollable_recollide_items(self, self.items)

        if self.actual_max_main > 0:
            coords = self._get_scrollbar_coordinates()
            if coords:
                scroll_bar.coordinates = coords
                scroll_bar.absolute_coordinates = py_get_item_abs_coords(
                    self, scroll_bar
                )

    def _recollide_items(self):
        drawable = self._widget_drawable
        true_rect = self.get_nvrect()
        self.absolute_coordinates = NvVector2.from_xy(true_rect.x, true_rect.y)
        for item in self.items:
            item.absolute_coordinates = py_get_item_abs_coords(self, item)
        self.collided_items = [item for item in self.items if drawable(item)]

    def _regenerate_coordinates(self):
        super()._regenerate_coordinates()
        self._regenerate_max_values()
        spacing = self.get_param_strict("spacing").value
        main_idx = self._main_axis
        pad = self.rel(NvVector2.from_xy(spacing, spacing))[main_idx]
        padding_offset = pad

        items = self.items
        widgets_alignment = self.widgets_alignment
        get_abs_coords = py_get_item_abs_coords
        set_main = self._set_item_main

        cached_coordinates = []

        for item, align in zip(items, widgets_alignment):
            orig_coords = item.coordinates.copy()

            set_main(item, align)
            new_coords = item.coordinates.copy()
            new_coords[main_idx] = self.coordinates[main_idx] + padding_offset
            item.coordinates = orig_coords
            item.set_coordinates(new_coords)

            cached_coordinates.append(item.coordinates.copy())
            item.absolute_coordinates = get_abs_coords(self, item)
            padding_offset += item._csize[main_idx] + pad

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

    def _logic_update(self):
        super()._logic_update()
        if self.hover_state == HoverState.NotHovered:
            return
        assert self.scroll_bar
        inverse = -1 if self.inverted_scrolling else 1
        fdown = keyboard.is_fdown
        get = self.get_param_value
        if fdown(get("append_key")):
            scroll_bar = self.scroll_bar
            scroll_bar._percentage += self.arrow_scroll_power * -inverse
            scroll_bar._percentage = max(0, min(100, scroll_bar._percentage))
            self._scroll_needs_update = True
        if fdown(get("descend_key")):
            scroll_bar = self.scroll_bar
            scroll_bar._percentage += self.arrow_scroll_power * inverse
            scroll_bar._percentage = max(0, min(100, scroll_bar._percentage))
            self._scroll_needs_update = True

    def _on_scroll_system(self, side: bool):
        super()._on_scroll_system(side)
        direction = 1 if side else -1
        if self.inverted_scrolling:
            direction *= -1

        assert self.scroll_bar

        old_perc = self.scroll_bar._percentage
        self.scroll_bar._percentage += self.wheel_scroll_power * direction
        self.scroll_bar._percentage = max(0, min(100, self.scroll_bar._percentage))

        if self.scroll_bar._percentage == old_perc:
            if self.layout is not None and isinstance(self.layout, ScrollableBase):
                self.layout._on_scroll_system(side)
            return

        self._scroll_needs_update = True

    def _update_scroll_bar(self):
        if not self.first_parent_menu:
            return
        assert self.first_parent_menu._window
        main_idx = self._main_axis
        sec_idx = self._sec_axis
        abs_coords = self.absolute_coordinates
        local_start = NvVector2.from_xy(0, 0)
        local_start[sec_idx] = (
            abs_coords + self.rel(self.size - self.scroll_bar.size)
        )[sec_idx]
        local_start[main_idx] = abs_coords[main_idx]
        track_length = NvVector2.from_xy(0, 0)
        track_length[self._main_axis] = self._csize[self._main_axis]
        assert self.scroll_bar
        self.scroll_bar.set_scroll_params(local_start, abs_coords, track_length)

    def _resize_content(self, resize_ratio: NvVector2):
        assert self.scroll_bar
        old_scrbar_perc = self.scroll_bar.percentage
        super()._resize_content(resize_ratio)
        self.scroll_bar._resize(resize_ratio)
        self._update_scroll_bar()
        self.scroll_bar.set_percents(old_scrbar_perc)
        self.cached_coordinates = None
        self._scroll_needs_update = True
        self._regenerate_coordinates()
        self.scroll_bar.scrolling = False
        self._update_offset()
        _very_light_update_helper(
            self.items,
            self.cached_coordinates or [],
            self.first_parent_menu.absolute_coordinates,
            self._offset,
            self,
        )

    def _on_item_add(self, item: NevuObject):
        self.cached_coordinates = None
        if self.booted == False:
            return
        self._update_scroll_bar()

    def add_item(self, item: NevuObject, alignment: Align | None = None):  # type: ignore
        alignment = alignment or self.basic_alignment or Align.CENTER
        if not self._parse_align(alignment):
            raise ValueError(
                f"align {alignment} not supported in {type(self).__name__}"
            )
        super().add_item(item)
        self.widgets_alignment.append(alignment)

    def clear(self):
        self.items.clear()
        self.widgets_alignment.clear()
        self._restart_coordinates()

    def apply_style_to_childs(self, style: Style):
        super().apply_style_to_childs(style)
        self.apply_scroll_bar_style(style)

    def apply_scroll_bar_style(self, style: Style):
        self.scroll_bar.style = style

    def _restart_coordinates(self):
        self.max_main = self.get_param_strict("spacing").value
        self.actual_max_main = 0

    def _create_scroll_bar(self) -> ScrollableBase.ScrollBar:
        if not self.scrollbar_perc:
            scr_perc = NvVector2.from_xy(0, 0)
            scr_perc[self._main_axis] = 4
            scr_perc[abs(self._main_axis - 1)] = 2
        else:
            scr_perc = self.scrollbar_perc
        size = self.size / 100 * scr_perc
        return self.ScrollBar(size, self.style, self._scrollbar_type, weakref.ref(self))

    def _kill_base(self):
        super()._kill_base()
        if hasattr(self, "scroll_bar") and self.scroll_bar:
            self.scroll_bar.kill()
            del self.scroll_bar
            self.scroll_bar = None

    # === PLACEHOLDERS ===
    @property
    @abstractmethod
    def _main_axis(self) -> int:
        return -1

    @property
    @abstractmethod
    def _sec_axis(self) -> int:
        return -1

    @property
    @abstractmethod
    def _scrollbar_type(self) -> ScrollBarType:
        pass

    @abstractmethod
    def _update_offset(self):
        pass

    @abstractmethod
    def _main_coord(self, coordinates: NvVector2) -> int | float:
        pass

    @abstractmethod
    def _sec_coord(self, coordinates: NvVector2) -> int | float:
        pass

    @abstractmethod
    def _parse_align(self, align: Align) -> bool:
        return False

    @abstractmethod
    def _regenerate_max_values(self):
        pass

    @abstractmethod
    def _get_scrollbar_coordinates(self) -> NvVector2:
        return NvVector2()

    @abstractmethod
    def _set_item_main(self, item: NevuObject, align: Align):
        pass
