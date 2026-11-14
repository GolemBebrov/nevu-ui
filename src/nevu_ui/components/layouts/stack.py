from __future__ import annotations

import copy
from typing import Unpack

from nevu_ui.components._typehints import _StackKwargs
from nevu_ui.components.layouts import BaseLayout
from nevu_ui.components.layouts.menu import Menu
from nevu_ui.components.nevuobject import NevuObject
from nevu_ui.components.widgets import Widget
from nevu_ui.core import Annotations
from nevu_ui.core.enums import Align, CacheType, CustomFunctions, Orientation
from nevu_ui.core.error_formats import format_nvtype_nvobject_error
from nevu_ui.core.size import _SizeRule
from nevu_ui.core.size.rules import _all_fillx
from nevu_ui.cython.logic.logic import (
    draw_items,
    get_absolute_coordinates,
    update_items,
)
from nevu_ui.cython.vector2 import Vector2

_still_offset = Vector2()

# Nnna nanachi approved!
class Stack(BaseLayout):
    _supports_global_size = False
    type content_type = list[tuple[Align, NevuObject] | NevuObject]

    spacing: float
    basic_alignment: Align
    orientation: Orientation

    def __init__(
        self,
        content: content_type | None = None,
        style: Annotations.nevuobj_style = None,
        **params: Unpack[_StackKwargs],
    ):
        super().__init__(content = content, size = Vector2(), style = style, **params)

    def add_items(self, content: content_type | None):
        if not content: return

        for content_item in content:
            if isinstance(content_item, tuple):
                align, item = content_item
            elif isinstance(content_item, NevuObject):
                align, item = self.basic_alignment, content_item
            else:
                raise TypeError(format_nvtype_nvobject_error("list[tuple[Align, NevuObject] or NevuObject]", "content", f"{content}.\nWrong part: {content_item}", self))
            assert type(align) is Align and isinstance(item, NevuObject), (
                f"Incorrect align or item ({align}, {item})"
            )
            self.add_item(item, align)

    def _init_lists(self):
        super()._init_lists()
        self.widgets_alignment = []
        self._visible_items = []
        self._hidden_items = []

    def _add_params(self):
        super()._add_params()
        self._add_param("spacing", int | float, 10)
        self._add_param("basic_alignment", Align, Align.CENTER)
        self._add_param("orientation", Orientation, Orientation.Row)

    def _init_booleans(self):
        super()._init_booleans()
        self._add_custom_flags(
            CustomFunctions.draw_main
        )

    def _parse_fillx(self, fill_rule: _SizeRule, fill_type: type[_SizeRule], pos: int) -> float | None:
        if fill_rule in _all_fillx:
            raise ValueError(
                f"Handling for SizeRule '{fill_type.__name__}' is not supported in {type(self).__name__}"
            )

    def add_item(self, item: NevuObject, alignment: Align = Align.CENTER):
        self.widgets_alignment.append(alignment)
        try:
            item = super().add_item(item)
        except Exception:
            self.widgets_alignment.pop()
            raise
        self.cached_coordinates = None
        return item

    def _on_item_kill(self, item: NevuObject) -> None:
        super()._on_item_kill(item)
        if item in self.items:
            idx = self.items.index(item)
            if idx < len(self.widgets_alignment):
                self.widgets_alignment.pop(idx)

    def insert_item(self, item: NevuObject, id: int = -1):
        try:
            n = len(self.items)
            idx = n + id if id < 0 else id
            self.kill_item(self.items[idx])
            item = self._item_add(item)
            self.items.insert(idx, item)
            self.widgets_alignment.insert(idx, Align.CENTER)
            self._recalculate_size()
            if self._parent_layout:
                self._parent_layout._on_item_add(item)
        except Exception as e:
            raise RuntimeError(f"Cannot insert item in {self.__class__.__name__} with {self.get_param('id')}") from e

    def _connect_to_layout(self, layout: BaseLayout):
        super()._connect_to_layout(layout)
        self._recalculate_item_coordinates()

    def _connect_to_menu(self, menu: Menu):
        super()._connect_to_menu(menu)
        self._recalculate_item_coordinates()

    def _on_item_add(self, item: NevuObject):
        self.cached_coordinates = None
        if self._parent_layout:
            self._parent_layout.cached_coordinates = None
        self._recalculate_size()
        if self._parent_layout:
            self._parent_layout._on_item_add(item)

    def _update_main(self):
        if not self.items or not self.cached_coordinates or not self.first_parent_menu:
            return

        need_rebuild = False
        for item in self._visible_items:
            if not item.visible:
                need_rebuild = True
                break
        if not need_rebuild:
            for item in self._hidden_items:
                if item.visible:
                    need_rebuild = True
                    break

        if need_rebuild:
            self._regenerate_coordinates()

        update_items(
            self.items,
            self.cached_coordinates,
            self.first_parent_menu.absolute_coordinates,
            _still_offset,
            self,
            False,
        )

    def _draw_main(self):
        draw_items(self, self.items, BaseLayout, Widget)

    def _regenerate_coordinates(self):
        super()._regenerate_coordinates()
        old_size = self.size.copy() if hasattr(self, "size") else None
        self._recalculate_size()
        if old_size is not None and (old_size.x != self.size.x or old_size.y != self.size.y) and self._parent_layout:
            self._parent_layout.cached_coordinates = None
        self._recalculate_item_coordinates()

    def _create_clone(self):
        return self.__class__(
            copy.deepcopy(self._template["content"]),
            copy.deepcopy(self.style),
            **self.kwargs,
        )

    def _recalculate_size(self):
        if not hasattr(self, "size"): return
        items = self.items
        size = self.size

        self._visible_items = [item for item in items if item.visible]
        self._hidden_items = [item for item in items if not item.visible]

        if not items or not self._visible_items:
            size[0] = 0
            size[1] = 0
            self.cache.clear_selected(whitelist=[CacheType.RelSize])
            return

        if any(not item.booted for item in items): return
        orientation = self.orientation
        main_axis = orientation.axis
        cross_axis = orientation.cross_axis

        size[main_axis] = sum(item.size[main_axis] for item in self._visible_items) + len(self._visible_items) * self.spacing
        size[cross_axis] = max(item.size[cross_axis] for item in self._visible_items)
        self.cache.clear_selected(whitelist=[CacheType.RelSize])
        if self.bg_widget and self.bg_widget.booted:
            self.bg_widget.size = self.size.xy
            self.bg_widget._regen_surface()
            self.bg_widget._changed = True
            self.bg_widget.clear_all()

    def _get_align_offset(self, item: NevuObject, alignment: Align) -> float:
        cross_axis = self.orientation.cross_axis
        size_diff = self.current_size[cross_axis] - item.current_size[cross_axis]

        match alignment:
            case Align.CENTER:
                offset = size_diff * 0.5
            case Align.RIGHT | Align.BOTTOM:
                offset = size_diff
            case _:
                offset = 0.0

        return offset

    def _boot_up(self):
        super()._boot_up()
        self._recalculate_size()
        if self._parent_layout:
            self._parent_layout.cached_coordinates = None
            if hasattr(self._parent_layout, "_regenerate_coordinates") and self._parent_layout.booted:
                self._parent_layout._regenerate_coordinates()

    def _recalculate_item_coordinates(self):
        if not self.booted: return
        cached_coordinates = []
        main_axis = self.orientation.axis
        cross_axis = self.orientation.cross_axis
        main_ratio = self._resize_ratio[main_axis]

        spacing = self.spacing * main_ratio
        current_main = 0

        items = self.items
        alignments = self.widgets_alignment
        self_coordinates = self.coordinates

        for i in range(len(items)):
            item, alignment = items[i], alignments[i]

            if not item.visible:
                cached_coordinates.append(item.coordinates.copy())
                continue

            new_coords = Vector2()
            new_coords[main_axis] = self_coordinates[main_axis] + current_main + (spacing * 0.5)
            new_coords[cross_axis] = self_coordinates[cross_axis] + self._get_align_offset(item, alignment)
            item.set_coordinates(new_coords)
            item.absolute_coordinates = get_absolute_coordinates(self, item)

            current_main += item.get_actual_size()[main_axis] + spacing
            cached_coordinates.append(new_coords.copy())

        self.cached_coordinates = cached_coordinates

class VStack(Stack):
    def _add_params(self):
        super()._add_params()
        self._change_param_default("orientation", Orientation.Column)
        self._block_param("orientation")

class HStack(Stack):
    def _add_params(self):
        super()._add_params()
        self._change_param_default("orientation", Orientation.Row)
        self._block_param("orientation")
