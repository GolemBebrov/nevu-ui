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
from nevu_ui.core.enums import Align
from nevu_ui.core.size.base import SizeRule
from nevu_ui.fast.logic.fast_logic import base_light_update, draw_widgets_optimized
from nevu_ui.fast.nvvector2 import NvVector2


class _StackKwargs(TypedDict):
    spacing: NotRequired[int | float]


class StackKwargs(_StackKwargs, LayoutTypeKwargs):
    pass


# Nnna nanachi approved!
class StackBase(LayoutType, ABC):
    _supports_global_size = False
    content_type = list[tuple[Align, NevuObject]]

    def __init__(
        self,
        content: content_type | None = None,
        style: Annotations.nevuobj_style = None,
        **constant_kwargs: Unpack[StackKwargs],
    ):
        super().__init__(content, NvVector2(), style, **constant_kwargs)

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

    def _init_booleans(self):
        super()._init_booleans()
        self._custom_secondary_draw_content = True

    def add_item(self, item: NevuObject, alignment: Align = Align.CENTER):  # type: ignore
        super().add_item(item)
        self.widgets_alignment.append(alignment)
        self.cached_coordinates = None

    def _parse_fillx(self, coord: SizeRule, pos: int) -> tuple[float, bool] | None:
        raise ValueError(
            f"Handling for SizeRule '{type(coord).__name__}' is not supported in {type(self).__name__}"
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
        self._recalculate_size()
        if self.layout:
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
