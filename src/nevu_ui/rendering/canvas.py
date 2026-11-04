from __future__ import annotations

import copy
from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, Any
from weakref import ReferenceType, ref

from nevu_ui.core.annotations import Annotations
from nevu_ui.core.enums import RenderReturnType
from nevu_ui.core.size.base import _SizeRule
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
    _all_gcx,
)
from nevu_ui.core.state import nevu_state
from nevu_ui.cython.surface.surface import Surface
from nevu_ui.cython.vector2.vector2 import Vector2
from nevu_ui.presentation.style import Style, default_style

if TYPE_CHECKING:
    from nevu_ui.components.nevuobj import NevuObject
    from nevu_ui.rendering.base_renderer import BaseRenderer

def _percent(total: float, value: float) -> float: return total * value / 100.0

def _resolve_rule(rule: _SizeRule, pos_idx: int, root: NevuObject | None) -> float:
    rule_type = type(rule)
    window = nevu_state.window
    val = rule.value

    if rule_type is Cvw and window is not None:
        return _percent(window.size.x, val)
    if rule_type is Cvh and window is not None:
        return _percent(window.size.y, val)
    if rule_type is Vw and window is not None:
        return _percent(window.original_size.x, val)
    if rule_type is Vh and window is not None:
        return _percent(window.original_size.y, val)

    if root is not None:
        if rule_type is Fill:
            return _percent(root.size[pos_idx], val)
        if rule_type is FillW:
            return _percent(root.size.x, val)
        if rule_type is FillH:
            return _percent(root.size.y, val)
        if rule_type is CFill:
            return _percent(root._no_borders_current_size[pos_idx], val)
        if rule_type is CFillW:
            return _percent(root._no_borders_current_size.x, val)
        if rule_type is CFillH:
            return _percent(root._no_borders_current_size.y, val)

    if rule_type in _all_gcx:
        raise ValueError(f"Handling for SizeRule '{rule_type.__name__}' is only Grid feature")

    return float(val)

def _resolve_coord(val: Any, pos_idx: int, root: NevuObject | None) -> float:
    if isinstance(val, _SizeRule):
        return _resolve_rule(val, pos_idx, root)
    if isinstance(val, int | float):
        return float(val)
    return 0

def _resolve_vec2_like(val: Annotations.vec2_all, root: NevuObject | None) -> Vector2:
    if isinstance(val, Vector2):
        return Vector2.from_xy(
            _resolve_coord(val.x, 0, root),
            _resolve_coord(val.y, 1, root)
        )
    if isinstance(val, tuple | list) and len(val) >= 2:
        return Vector2.from_xy(
            _resolve_coord(val[0], 0, root),
            _resolve_coord(val[1], 1, root)
        )
    return Vector2.from_xy(0, 0)

class _CanvasDataType(ABC):
    def __init__(
        self,
        *,
        style: Style,
        id: str | None = None,
        relative: bool = True,
    ):
        self.style = style
        self.id = id
        self.relative = relative

    @abstractmethod
    def resolve(self, root: NevuObject | None) -> None: ...
    @abstractmethod
    def draw(self, surface: Surface, renderer: BaseRenderer, root: NevuObject) -> None: ...
    @abstractmethod
    def copy(self) -> _CanvasDataType: ...


class CanvasRectData(_CanvasDataType):
    def __init__(
        self,
        *,
        pos: Annotations.vec2_all,
        size: Annotations.vec2_all,
        style: Style,
        id: str | None = None,
        relative: bool = True,
    ):
        super().__init__(style=style, id=id, relative=relative)
        self.raw_pos = copy.deepcopy(pos)
        self.raw_size = copy.deepcopy(size)
        self.pos = Vector2()
        self.size = Vector2()
        self._cached_surface: Surface | None = None
        self._cached_key: tuple | None = None

    def resolve(self, root: NevuObject | None) -> None:
        self.pos = _resolve_vec2_like(self.raw_pos, root)
        self.size = _resolve_vec2_like(self.raw_size, root)
        self._cached_surface = None

    def draw(self, surface: Surface, renderer: BaseRenderer, root: NevuObject) -> None:
        from nevu_ui.rendering.base_renderer import DrawBgCall

        pos = root.rel(self.pos) if self.relative else self.pos
        size = root.rel(self.size) if self.relative else self.size

        if size.x <= 0 or size.y <= 0: return

        subtheme_role = root.subtheme_role
        inverted = getattr(root, "inverted", False)
        bg_variant = root.bg_variant

        bg_color = self.style.get_content_color(subtheme_role, inverted=inverted, swap=bg_variant)
        border_color = self.style.get_border_color(subtheme_role, inverted=inverted, swap=bg_variant)

        correct_size = (int(size.x), int(size.y))
        state_key = (
            correct_size,
            id(self.style),
            bg_color,
            border_color,
            inverted,
            bg_variant,
        )

        if self._cached_surface is None or self._cached_key != state_key:
            self._cached_surface = renderer.run_bg(
                call=DrawBgCall(
                    size=size,
                    style=self.style,
                    bg_color=bg_color,
                    border_color=border_color,
                    image_support=True,
                    radius_support=True,
                    gradient_support=True,
                    return_type=RenderReturnType.CreateNew,
                )
            )
            self._cached_key = state_key

        surface.blit(self._cached_surface, pos)

    def copy(self) -> CanvasRectData:
        return CanvasRectData(
            pos=copy.deepcopy(self.raw_pos),
            size=copy.deepcopy(self.raw_size),
            style=copy.deepcopy(self.style),
            id=self.id,
            relative=self.relative,
        )


class CanvasLineData(_CanvasDataType):
    def __init__(
        self,
        *,
        pos_from: Annotations.vec2_all,
        pos_to: Annotations.vec2_all,
        width: int | float,
        color: Annotations.rgba_color | None = None,
        style: Style,
        id: str | None = None,
        relative: bool = True,
    ):
        super().__init__(style=style, id=id, relative=relative)
        self.raw_pos_from = copy.deepcopy(pos_from)
        self.raw_pos_to = copy.deepcopy(pos_to)
        self.width = width
        self.color = color
        self.pos_from = Vector2()
        self.pos_to = Vector2()

    def resolve(self, root: NevuObject | None) -> None:
        self.pos_from = _resolve_vec2_like(self.raw_pos_from, root)
        self.pos_to = _resolve_vec2_like(self.raw_pos_to, root)

    def draw(self, surface: Surface, renderer: BaseRenderer, root: NevuObject) -> None:
        pos_from = root.rel(self.pos_from) if self.relative else self.pos_from
        pos_to = root.rel(self.pos_to) if self.relative else self.pos_to

        subtheme_role = root.subtheme_role
        inverted = getattr(root, "inverted", False)
        bg_variant = root.bg_variant

        color = self.color or self.style.get_border_color(subtheme_role, inverted=inverted, swap=bg_variant)

        renderer.core.draw_line(
            surface,
            pos_from,
            pos_to,
            radius=self.style.border_radius,
            color=color,
            width=self.width,
            relative=self.relative,
        )

    def copy(self) -> CanvasLineData:
        return CanvasLineData(
            pos_from=copy.deepcopy(self.raw_pos_from),
            pos_to=copy.deepcopy(self.raw_pos_to),
            width=self.width,
            color=self.color,
            style=copy.deepcopy(self.style),
            id=self.id,
            relative=self.relative,
        )


class CanvasCircleData(_CanvasDataType):
    def __init__(
        self,
        *,
        pos: Annotations.vec2_all,
        radius: Annotations.rad_like,
        style: Style,
        id: str | None = None,
        relative: bool = True,
    ):
        super().__init__(style=style, id=id, relative=relative)
        self.raw_pos = copy.deepcopy(pos)
        self.raw_radius = copy.deepcopy(radius)
        self.pos = Vector2()
        self.radius = 0.0
        self._cached_surface: Surface | None = None
        self._cached_key: tuple | None = None

    def resolve(self, root: NevuObject | None) -> None:
        self.pos = _resolve_vec2_like(self.raw_pos, root)
        self.radius = _resolve_coord(self.raw_radius, 0, root)
        self._cached_surface = None

    def draw(self, surface: Surface, renderer: BaseRenderer, root: NevuObject) -> None:
        from nevu_ui.rendering.base_renderer import DrawBgCall

        center = root.rel(self.pos) if self.relative else self.pos
        radius = root.relx(self.radius) if self.relative else self.radius

        if radius <= 0: return

        diameter = radius * 2.0
        size = Vector2.from_xy(diameter, diameter)
        top_left = center - Vector2.from_xy(radius, radius)

        circle_style = self.style(border_radius=radius)

        subtheme_role = root.subtheme_role
        inverted = getattr(root, "inverted", False)
        bg_variant = root.bg_variant

        bg_color = self.style.get_content_color(subtheme_role, inverted=inverted, swap=bg_variant)
        border_color = self.style.get_border_color(subtheme_role, inverted=inverted, swap=bg_variant)

        correct_size = (int(size.x), int(size.y))
        state_key = (
            correct_size,
            id(circle_style),
            bg_color,
            border_color,
            inverted,
            bg_variant,
        )

        if self._cached_surface is None or self._cached_key != state_key:
            self._cached_surface = renderer.run_bg(
                call=DrawBgCall(
                    size=size,
                    style=circle_style,
                    bg_color=bg_color,
                    border_color=border_color,
                    image_support=True,
                    radius_support=True,
                    gradient_support=True,
                    return_type=RenderReturnType.CreateNew,
                )
            )
            self._cached_key = state_key

        surface.blit(self._cached_surface, top_left.get_int_tuple())

    def copy(self) -> CanvasCircleData:
        return CanvasCircleData(
            pos=copy.deepcopy(self.raw_pos),
            radius=copy.deepcopy(self.raw_radius),
            style=copy.deepcopy(self.style),
            id=self.id,
            relative=self.relative,
        )


class Canvas:
    def __init__(
        self,
        style: Style = default_style,
        content: list[_CanvasDataType] | None = None,
        single_instance: bool = False,
    ):
        self._base_style = style
        self._content: list[_CanvasDataType] = [item.copy() for item in content] if content else []
        self._root: ReferenceType[NevuObject] | None = None
        self.single_instance = single_instance

    def _valid_root(self) -> NevuObject | None:
        if self._root is None:
            return None
        return self._root()

    def _connect_to_root(self, root: NevuObject) -> None:
        self._root = ref(root)
        self.resolve(root)

    def _mark_root_dirty(self) -> None:
        root = self._valid_root()
        if root is not None:
            root._changed = True
            root.clear_surfaces()

    def resolve(self, root: NevuObject | None = None) -> None:
        target_root = root or self._valid_root()
        for item in self._content:
            item.resolve(target_root)

    def draw(self, surface: Surface, renderer: BaseRenderer, root: NevuObject) -> None:
        for item in self._content:
            item.draw(surface, renderer, root)

    def reset(self) -> Canvas:
        self._content.clear()
        self._mark_root_dirty()
        return self

    def add_item(self, item: _CanvasDataType) -> Canvas:
        item.resolve(self._valid_root())
        self._content.append(item)
        self._mark_root_dirty()
        return self

    def get_item(self, id: str) -> _CanvasDataType:
        for item in self._content:
            if item.id == id:
                return item
        raise KeyError(f"Canvas item with id '{id}' not found")

    def remove_item(self, id: str) -> Canvas:
        item = self.get_item(id)
        self._content.remove(item)
        self._mark_root_dirty()
        return self

    def draw_rect(
        self,
        pos: Annotations.vec2_all,
        size: Annotations.vec2_all,
        *,
        style: Style | None = None,
        relative: bool = True,
        id: str | None = None,
    ) -> Canvas:
        item = CanvasRectData(
            pos=pos,
            size=size,
            style=style or self._base_style,
            id=id,
            relative=relative,
        )
        return self.add_item(item)

    def draw_line(
        self,
        pos_from: Annotations.vec2_all,
        pos_to: Annotations.vec2_all,
        width: int | float = 1,
        *,
        color: Annotations.rgba_color | None = None,
        style: Style | None = None,
        relative: bool = True,
        id: str | None = None,
    ) -> Canvas:
        item = CanvasLineData(
            pos_from=pos_from,
            pos_to=pos_to,
            width=width,
            color=color,
            style=style or self._base_style,
            id=id,
            relative=relative,
        )
        return self.add_item(item)

    def draw_circle(
        self,
        pos: Annotations.vec2_all,
        radius: Annotations.rad_like,
        *,
        style: Style | None = None,
        relative: bool = True,
        id: str | None = None,
    ) -> Canvas:
        item = CanvasCircleData(
            pos=pos,
            radius=radius,
            style=style or self._base_style,
            id=id,
            relative=relative,
        )
        return self.add_item(item)

    def change_rect(
        self,
        id: str,
        *,
        pos: Annotations.vec2_all | None = None,
        size: Annotations.vec2_all | None = None,
        style: Style | None = None,
        relative: bool | None = None,
    ) -> Canvas:
        item = self.get_item(id)
        if not isinstance(item, CanvasRectData):
            raise TypeError(f"Item with id '{id}' is not a CanvasRectData")
        if pos is not None:
            item.raw_pos = copy.deepcopy(pos)
        if size is not None:
            item.raw_size = copy.deepcopy(size)
        if style is not None:
            item.style = style
        if relative is not None:
            item.relative = relative
        item.resolve(self._valid_root())
        self._mark_root_dirty()
        return self

    def change_line(
        self,
        id: str,
        *,
        pos_from: Annotations.vec2_all | None = None,
        pos_to: Annotations.vec2_all | None = None,
        width: float | None = None,
        color: Annotations.rgba_color | None = None,
        style: Style | None = None,
        relative: bool | None = None,
    ) -> Canvas:
        item = self.get_item(id)
        if not isinstance(item, CanvasLineData):
            raise TypeError(f"Item with id '{id}' is not a CanvasLineData")
        if pos_from is not None:
            item.raw_pos_from = copy.deepcopy(pos_from)
        if pos_to is not None:
            item.raw_pos_to = copy.deepcopy(pos_to)
        if width is not None:
            item.width = width
        if color is not None:
            item.color = color
        if style is not None:
            item.style = style
        if relative is not None:
            item.relative = relative
        item.resolve(self._valid_root())
        self._mark_root_dirty()
        return self

    def change_circle(
        self,
        id: str,
        *,
        pos: Annotations.vec2_all | None = None,
        radius: Annotations.rad_like | None = None,
        style: Style | None = None,
        relative: bool | None = None,
    ) -> Canvas:
        item = self.get_item(id)
        if not isinstance(item, CanvasCircleData):
            raise TypeError(f"Item with id '{id}' is not a CanvasCircleData")
        if pos is not None:
            item.raw_pos = copy.deepcopy(pos)
        if radius is not None:
            item.raw_radius = copy.deepcopy(radius)
        if style is not None:
            item.style = style
        if relative is not None:
            item.relative = relative
        item.resolve(self._valid_root())
        self._mark_root_dirty()
        return self

    def copy(self) -> Canvas:
        new_instance = Canvas(
            style=copy.deepcopy(self._base_style),
            content=[item.copy() for item in self._content],
            single_instance=self.single_instance,
        )
        root = self._valid_root()
        if root is not None:
            new_instance._connect_to_root(root)
        return new_instance

    def __copy__(self) -> Canvas:
        return self.copy()

    def __deepcopy__(self, memo: Any) -> Canvas:
        return self.copy()


CanvasBaseData = _CanvasDataType

__all__ = [
    "Canvas",
    "_CanvasDataType",
    "CanvasBaseData",
    "CanvasRectData",
    "CanvasLineData",
    "CanvasCircleData",
]
