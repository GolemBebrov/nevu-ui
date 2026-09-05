from __future__ import annotations

import copy
from dataclasses import dataclass
from typing import TYPE_CHECKING
from weakref import ReferenceType, ref

from typing_extensions import Any

from nevu_ui.core.annotations import Annotations
from nevu_ui.core.enums import CanvasType
from nevu_ui.core.size.base import SizeRule
from nevu_ui.core.size.rules import (
    CFill,
    CFillH,
    CFillW,
    Cvh,
    Cvw,
    Fill,
    FillH,
    FillW,
    Vh,
    Vw,
    _all_fillx,
    _all_gcx,
    _all_vx,
)
from nevu_ui.core.state import nevu_state
from nevu_ui.fast.nvvector2.nvvector2 import NvVector2
from nevu_ui.presentation.color.color import Color
from nevu_ui.presentation.style.style import Style, default_style

if TYPE_CHECKING:
    from nevu_ui.components.nevuobj.nevuobj import NevuObject

@dataclass(kw_only=True)
class CanvasBaseData:
    style: Style
    id: str | None = None
    relative: bool = True


@dataclass(kw_only=True)
class CanvasRectData(CanvasBaseData):
    pos: NvVector2
    size: NvVector2

@dataclass(kw_only=True)
class CanvasLineData(CanvasBaseData):
    pos_from: NvVector2
    pos_to: NvVector2
    width: int
    color: Annotations.rgba_color | None = None

class Canvas:
    def __init__(self, style: Style = default_style, content: list | None = None, single_instance = True):
        self._base_style = style
        self._content: list[CanvasBaseData] = content or []
        self._root: ReferenceType[NevuObject] | None = None
        self._single_instance = single_instance

    @staticmethod
    def _percent_helper(size, value):
        return size / 100 * value

    def _parse_vx(self, viewport_rule: SizeRule, viewport_type: type[SizeRule], pos: int) -> float | None:
        window = nevu_state.window
        if viewport_type is Cvw:
            return self._percent_helper(window.size.x, viewport_rule.value)
        elif viewport_type is Cvh:
            return self._percent_helper(window.size.y, viewport_rule.value)
        elif viewport_type is Vw:
            return self._percent_helper(window.original_size.x, viewport_rule.value)
        elif viewport_type is Vh:
            return self._percent_helper(window.original_size.y, viewport_rule.value)

    def _parse_fillx(self, fill_rule: SizeRule, fill_type: type[SizeRule], pos: int) -> float | None:
        root = self._valid_root()
        if not root: return
        if fill_type is Fill:
            return self._percent_helper(root.size[pos], fill_rule.value)
        elif fill_type is FillW:
            return self._percent_helper(root.size.x, fill_rule.value)
        elif fill_type is FillH:
            return self._percent_helper(root.size.y, fill_rule.value)
        elif fill_type is CFill:
            return self._percent_helper(root._no_borders_current_size[pos], fill_rule.value)
        elif fill_type is CFillW:
            return self._percent_helper(root._no_borders_current_size.x, fill_rule.value)
        elif fill_type is CFillH:
            return self._percent_helper(root._no_borders_current_size.y, fill_rule.value)

    def _parse_gcx(self, grid_cell_rule: SizeRule, grid_cell_type: type[SizeRule], pos: int):
        if grid_cell_type in _all_gcx:
            raise ValueError(
                f"Handling for SizeRule '{grid_cell_type.__name__}' is only Grid feature"
            )

    def _resolvable_value(self, value):
        if not isinstance(value, tuple | list): return False
        if len(value) != 2: return False
        if not isinstance(value[0], int | float | SizeRule) or not isinstance(value[1], int | float | SizeRule): return False
        return True

    def _resolve_number(self, size_rule, pos: int = 0) -> float | None:
        if not isinstance(size_rule, SizeRule):
            return size_rule
        result = None
        rule_type = type(size_rule)
        for parser in [self._parse_vx,
                       self._parse_fillx,
                       self._parse_gcx]:
            result = parser(size_rule, rule_type, pos)
            if result is not None:
                return result

    def _resolve_vector2(self, vec2_like: Any):
        vec_x = self._resolve_number(vec2_like[0])
        vec_y = self._resolve_number(vec2_like[1], 1)

        if vec_x is not None and vec_y is not None:
            return NvVector2.from_xy(vec_x, vec_y)

    def _resolve_data(self, data: CanvasBaseData):
        for name, value in data.__dict__.items():
            if not self._resolvable_value(value): continue
            resolved = self._resolve_vector2(value)
            if resolved:
                setattr(data, name, resolved)

    def _resolve_all(self):
        for data in self._content:
            self._resolve_data(data)

    def _valid_root(self):
        if not self._root: return
        root = self._root()
        if root: return root

    def _connect_to_root(self, root: NevuObject):
        self._root = ref(root)
        self._resolve_all()

    def _mark_root_dirty(self):
        root = self._valid_root()
        if root: root._changed = True

    def reset(self):
        self._content.clear()
        self._mark_root_dirty()
        return self

    def _add_data(self, data: CanvasBaseData):
        self._resolve_data(data)
        self._content.append(data)
        self._mark_root_dirty()

    def get_data(self, data_type: type, id: str):
        item = next((item for item in self._content if isinstance(item, data_type) and item.id == id), None)
        if item is None:
            raise KeyError(f"No element of type {data_type.__name__} found with id = {id}")
        return item

    def draw_rect(
        self,
        pos: NvVector2 | Annotations.dest_like,
        size: NvVector2 | Annotations.dest_like,
        *,
        style: Style | None = None,
        relative: bool = True,
        id: str | None = None
    ):
        self._add_data(
            CanvasRectData(
                id = id,
                style = style or self._base_style,
                pos = pos,
                size = size,
                relative = relative
            )
        )
        return self

    def draw_line(
        self,
        pos_from: NvVector2 | Annotations.dest_like,
        pos_to: NvVector2 | Annotations.dest_like,
        width: int,
        *,
        relative: bool = True,
        style: Style | None = None,
        color: Annotations.rgba_color | None = None,
        id: str | None = None
    ):
        self._add_data(
            CanvasLineData(
                id = id,
                style = style or self._base_style,
                pos_from = pos_from,
                pos_to = pos_to,
                width = width,
                color = color,
                relative = relative
            )
        )
        return self

    def _change_base(self, item: CanvasBaseData, style: Style | None = None, relative: bool | None = None):
        if relative is not None:
            item.relative = relative
        if style is not None:
            item.style = style

    def change_base(
        self,
        id: str,
        style: Style | None,
        relative: bool | None,
    ):
        item = self.get_data(CanvasBaseData, id)
        self._change_base(item, style, relative)
        self._mark_root_dirty()
        self._resolve_data(item)
        return self

    def change_rect(
        self,
        id: str,
        pos: NvVector2 | Annotations.dest_like | None = None,
        size: NvVector2 | Annotations.dest_like | None = None,
        style: Style | None = None,
        relative: bool | None = None,
    ):
        item = self.get_data(CanvasRectData, id)
        if pos is not None:
            item.pos = pos
        if size is not None:
            item.size = size
        self._change_base(item, style, relative)

        self._mark_root_dirty()
        self._resolve_data(item)
        return self

    def change_line(
        self,
        id: str,
        pos_from: NvVector2 | Annotations.dest_like | None = None,
        pos_to: NvVector2 | Annotations.dest_like | None = None,
        width: int | None = None,
        color: Annotations.rgba_color | None = None,
        style: Style | None = None,
        relative: bool | None = None,
    ):
        item = self.get_data(CanvasLineData, id)
        if pos_from is not None:
            item.pos_from = pos_from
        if pos_to is not None:
            item.pos_to = pos_to
        if width is not None:
            item.width = width
        if color is not None:
            item.color = color
        self._change_base(item, style, relative)

        self._mark_root_dirty()
        self._resolve_data(item)
        return self

    def copy(self):
        new_instance = self.__class__(copy.deepcopy(self._base_style), content = copy.deepcopy(self._content))
        if self._root:
            root = self._root()
            if root:
                new_instance._connect_to_root(root)
        return new_instance

    def __copy__(self):
        return self.copy()
