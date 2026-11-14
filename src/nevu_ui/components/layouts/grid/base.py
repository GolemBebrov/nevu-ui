import math
from typing import Unpack, overload

from nevu_ui.components._typehints import (
    _GridKwargs_rc,
    _GridKwargs_uni,
    _GridKwargs_xy,
)
from nevu_ui.components.layouts import BaseLayout
from nevu_ui.components.nevuobject import NevuObject
from nevu_ui.components.widgets import Widget
from nevu_ui.core import Annotations
from nevu_ui.core.size import _SizeRule
from nevu_ui.core.size.rules import Cgc, Cgch, Cgcw, Gc, Gch, Gcw
from nevu_ui.cython.logic.logic import (
    update_items,
    draw_items,
    get_absolute_coordinates,
)
from nevu_ui.cython.vector2 import Vector2

_still_offset = Vector2()

class Grid(BaseLayout):
    row: int | float
    column: int | float
    any_number = int | float
    content_type = dict[tuple[any_number, any_number], NevuObject]

    @overload
    def __init__(
        self,
        content: content_type | None = None,
        size: Annotations.nevuobj_size = None,
        style: Annotations.nevuobj_style = None,
        **params: Unpack[_GridKwargs_rc],
    ): ...
    @overload
    def __init__(
        self,
        content: content_type | None = None,
        size: Annotations.nevuobj_size = None,
        style: Annotations.nevuobj_style = None,
        **params: Unpack[_GridKwargs_xy],
    ): ...
    def __init__(
        self,
        content: content_type | None = None,
        size: Annotations.nevuobj_size = None,
        style: Annotations.nevuobj_style = None,
        **params: Unpack[_GridKwargs_uni],
    ):
        super().__init__(content, size, style, **params)  # type: ignore

    def _add_params(self):
        super()._add_params()
        self._add_param("column", int | float, 1)
        self._add_param("row", int | float, 1)
        self._add_param_link("y", "row")
        self._add_param_link("x", "column")

    def _init_lists(self):
        super()._init_lists()
        self.grid_coordinates = []

    def _lazy_init(self, size: Vector2 | list, content: content_type | None = None):  # type: ignore
        super()._lazy_init(size)
        self.cell_height = self.size[1] / self.row
        self.cell_width = self.size[0] / self.column

    def add_items(self, content: content_type | None):  # type: ignore
        if not content:
            return
        for coords, item in content.items():
            self.add_item(item, coords[0], coords[1])

    def _regenerate_coordinates(self):
        super()._regenerate_coordinates()
        if not self.booted: return
        self.cached_coordinates = []
        c_vec = Vector2.from_xy(
            self._no_borders_current_size.x / self.column,
            self._no_borders_current_size.y / self.row,
        )
        coords_marg_vec = self.coordinates + self._borders_of_current_size
        cached_coords_append = self.cached_coordinates.append
        for item, gr_vec in zip(self.items, self.grid_coordinates):
            curr_cell_vec = gr_vec * c_vec
            size_adapt_vec = (c_vec - item.get_actual_size()) / 2
            coordinates = coords_marg_vec + curr_cell_vec + size_adapt_vec
            item.set_coordinates(coordinates.copy())
            item.absolute_coordinates = get_absolute_coordinates(self, item)
            cached_coords_append(coordinates.copy())

    def _update_main(self):
        items = self.items
        cached_coordinates = self.cached_coordinates
        menu = self.first_parent_menu
        if not items or not cached_coordinates or not menu:
            return
        update_items(items, cached_coordinates, menu.absolute_coordinates, _still_offset, self, False)

    def _parse_gcx(self, grid_cell_rule: _SizeRule, grid_cell_type: type[_SizeRule], pos: int):  # type: ignore
        if self.first_parent_menu is None:
            raise self._unconnected_layout_error("Gcx coords")
        if self.first_parent_menu._window is None:
            raise self._uninitialized_layout_error("Gcx coords")
        coord_type = type(grid_cell_rule)
        if coord_type is Gc:
            return self._percent_helper(
                (self.cell_width, self.cell_height)[pos], grid_cell_rule.value
            )
        elif coord_type is Gcw:
            return self._percent_helper((self.cell_width), grid_cell_rule.value)
        elif coord_type is Gch:
            return self._percent_helper((self.cell_height), grid_cell_rule.value)
        elif coord_type is Cgc:
            return self._percent_helper(
                self.rel(Vector2(self.cell_width, self.cell_height))[pos], grid_cell_rule.value
            )
        elif coord_type is Cgcw:
            return self._percent_helper(self.relx(self.cell_width), grid_cell_rule.value)
        elif coord_type is Cgch:
            return self._percent_helper(self.rely(self.cell_height), grid_cell_rule.value)

    def add_item(self, item: NevuObject, x: any_number, y: any_number):  # type: ignore
        range_error = ValueError(
            f"Grid index out of range x: {x}, y: {y} "
            + f"Grid size: {self.column}x{self.row}"
        )
        if x > self.column or y > self.row or x < 1 or y < 1:
            raise range_error
        for coordinates in self.grid_coordinates:
            if Vector2(coordinates) == Vector2(x - 1, y - 1):
                raise ValueError("Grid item already exists")
        self.grid_coordinates.append(Vector2.from_xy(x - 1, y - 1))
        try:
            super().add_item(item)
        except Exception:
            self.grid_coordinates.pop()
            raise

    def _draw_main(self):
        draw_items(self, self.items, BaseLayout, Widget)

    def get_column(self, x: any_number) -> list[NevuObject]:
        return [
            item
            for item, coords in zip(self.items, self.grid_coordinates)
            if coords[0] == x - 1
        ]

    def get_row(self, y: any_number) -> list[NevuObject]:
        return [
            item
            for item, coords in zip(self.items, self.grid_coordinates)
            if coords[1] == y - 1
        ]

    def _on_item_kill(self, item: NevuObject) -> None:
        super()._on_item_kill(item)
        if item in self.items:
            idx = self.items.index(item)
            self.items.pop(idx)
            self.grid_coordinates.pop(idx)

    def kill_item_by_pos(self, x: any_number, y: any_number) -> None:
        widget = self.get_item(x, y)
        if widget:
            self.kill_item(widget)

    def get_item_grid(self, item: NevuObject) -> Vector2 | None:
        for i, coords in enumerate(self.grid_coordinates):
            if self.items[i] == item:
                return coords
        return None

    def get_item(self, x: any_number, y: any_number) -> NevuObject | None:
        target_coords = (x - 1, y - 1)
        for i, coords in enumerate(self.grid_coordinates):
            if math.isclose(coords[0], target_coords[0]) and math.isclose(
                coords[1], target_coords[1]
            ):
                return self.items[i]

__all__ = []
