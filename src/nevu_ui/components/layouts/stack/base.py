from __future__ import annotations

import copy
from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, NotRequired, TypedDict, Unpack

if TYPE_CHECKING:
    from nevu_ui.menu import Menu
from nevu_ui.components.layouts import LayoutType, LayoutTypeKwargs
from nevu_ui.components.nevuobj import NevuObject
from nevu_ui.components.widgets import Widget
from nevu_ui.core import Annotations
from nevu_ui.core.enums import Align, CustomFunctions
from nevu_ui.fast.logic.fast_logic import base_light_update, draw_widgets_optimized
from nevu_ui.fast.nvvector2 import NvVector2
from nevu_ui.core.size.rules import (
    SizeRule,
    _all_fillx,
)

class _StackKwargs(TypedDict):
    spacing: NotRequired[int | float]
    basic_alignment: NotRequired[Align]


class StackKwargs(_StackKwargs, LayoutTypeKwargs):
    pass


# Nnna nanachi approved!
class StackBase(LayoutType, ABC):
    _supports_global_size = False
    content_type = list[tuple[Align, NevuObject] | NevuObject]

    spacing: float
    basic_alignment: Align

    def __init__(
        self,
        content: content_type | None = None,
        style: Annotations.nevuobj_style = None,
        **constant_kwargs: Unpack[StackKwargs],
    ):
        super().__init__(content = content, size = NvVector2(), style = style, **constant_kwargs)

    def add_items(self, content: content_type | None):
        if not content: return

        for content_item in content:

            if isinstance(content_item, tuple):
                align, item = content_item
            elif isinstance(content_item, NevuObject):
                align, item = self.basic_alignment, content_item
            else:
                raise TypeError(Annotations.format_nvtype_nvobject_error("list[tuple[Align, NevuObject] or NevuObject]", "content", f"{content}.\nWrong part: {content_item}", self))
            assert type(align) == Align and isinstance(item, NevuObject), (
                f"Incorrect align or item ({align}, {item})"
            )
            self.add_item(item, align)

    def _init_lists(self):
        super()._init_lists()
        self.widgets_alignment = []

    def _add_params(self):
        super()._add_params()
        self._add_param("spacing", (int, float), 10)
        self._add_param("basic_alignment", Align, Align.CENTER)

    def _init_booleans(self):
        super()._init_booleans()
        self._add_custom_flags(
            CustomFunctions.secondary_draw_content
        )

    def add_item(self, item: NevuObject, alignment: Align = Align.CENTER):  # type: ignore
        super().add_item(item)
        self.widgets_alignment.append(alignment)
        self.cached_coordinates = None

    def _parse_fillx(self, fill_rule: SizeRule, fill_type: type[SizeRule], pos: int) -> float | None:
        if fill_rule in _all_fillx:
            raise ValueError(
                f"Handling for SizeRule '{fill_type.__name__}' is not supported in {type(self).__name__}"
            )

    def insert_item(self, item: Widget | LayoutType, id: int = -1):
        try:
            self.items.insert(id, item)
            self.widgets_alignment.insert(id, Align.CENTER)
            self._recalculate_size()
            if self.layout:
                self.layout._on_item_add(item)
        except Exception as e:
            raise e

    def _connect_to_layout(self, layout: LayoutType):
        super()._connect_to_layout(layout)
        self._recalculate_widget_coordinates()

    def _connect_to_menu(self, menu: Menu):
        super()._connect_to_menu(menu)
        self._recalculate_widget_coordinates()

    def _on_item_add(self, item: NevuObject):
        self.cached_coordinates = None
        if self.layout:
            self.layout.cached_coordinates = None
        self._recalculate_size()
        if self.layout:
            self.layout._on_item_add(item)

    def secondary_update(self, *args):
        base_light_update(self)

    def secondary_draw_content(self):
        draw_widgets_optimized(self, self.items, LayoutType, Widget)

    @property
    def spacing(self):
        return self.get_param_strict("spacing").value

    @spacing.setter
    def spacing(self, val):
        self.set_param_value("spacing", val)

    def _regenerate_coordinates(self):
        super()._regenerate_coordinates()
        old_size = self.size.copy() if hasattr(self, "size") else None
        self._recalculate_size()
        if old_size is not None and (old_size.x != self.size.x or old_size.y != self.size.y) and self.layout:
            self.layout.cached_coordinates = None
        self._recalculate_widget_coordinates()

    def _create_clone(self):
        return self.__class__(
            copy.deepcopy(self._template["content"]),
            copy.deepcopy(self.style),
            **self.constant_kwargs,
        )

    # === Placeholders ===
    @abstractmethod
    def _set_align_coords(self, item: NevuObject, alignment: Align):
        pass

    @abstractmethod
    def _recalculate_size(self):
        pass

    @abstractmethod
    def _recalculate_widget_coordinates(self):
        pass
