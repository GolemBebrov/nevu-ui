import math

from typing import (
    Unpack, NotRequired, TypedDict, overload
)

from nevu_ui.widgets import Widget
from nevu_ui.nevuobj import NevuObject
from nevu_ui.fast.nvvector2 import NvVector2 
from nevu_ui.layouts import LayoutType, LayoutTypeKwargs
from nevu_ui.style import Style, default_style
from nevu_ui.layouts.typehints import GridTemplate

from nevu_ui.size.rules import (
    Gc, Gcw, Gch, Cgc, Cgcw, Cgch
)

class _Grid_Specifics_rc(TypedDict):
    row: NotRequired[int | float]
    column: NotRequired[int | float]
class _Grid_Specifics_xy(TypedDict):
    x: NotRequired[int | float]
    y: NotRequired[int | float]
class GridKwargs_rc(_Grid_Specifics_rc, LayoutTypeKwargs): pass
class GridKwargs_xy(_Grid_Specifics_xy, LayoutTypeKwargs): pass
class GridKwargs_uni(GridKwargs_rc, GridKwargs_xy, LayoutTypeKwargs): pass

class Grid(LayoutType):
    row: int | float
    column: int | float
    any_number = int | float
    content_type = dict[tuple[any_number, any_number], NevuObject]
    @overload
    def __init__(self, size: NvVector2 | list, style: Style = default_style, content: content_type | None = None, **constant_kwargs: Unpack[GridKwargs_rc]): ...
    @overload
    def __init__(self, size: NvVector2 | list, style: Style = default_style, content: content_type | None = None, **constant_kwargs: Unpack[GridKwargs_xy]): ...
    def __init__(self, size: NvVector2 | list, style: Style = default_style, content: content_type | None = None, **constant_kwargs: Unpack[GridKwargs_uni]):
        super().__init__(size, style, content, **constant_kwargs) # type: ignore
    
    def _create_template(self, size: NvVector2 | list, content: content_type | None): # type: ignore
        return GridTemplate(size, content)
    
    def _add_params(self):
        super()._add_params()
        self._add_param("column", (int, float), 1)
        self._add_param("row", (int, float), 1)
        self._add_param_link("y", "row")
        self._add_param_link("x", "column")
    
    def _init_lists(self):
        super()._init_lists()
        self.grid_coordinates = []
    
    def _lazy_init(self, size: NvVector2 | list, content: content_type | None = None): # type: ignore
        super()._lazy_init(size)
        self.cell_height = self.size[1] / self.row
        self.cell_width = self.size[0] / self.column
        self.add_items(content)

    def add_items(self, content: content_type | None): # type: ignore
        if not content: return
        for coords, item in content.items():
            self.add_item(item, coords[0], coords[1])
    
    def _regenerate_coordinates(self):
        super()._regenerate_coordinates()
        self.cached_coordinates = []
        c_vec = NvVector2(self._rsize.x / self.column, self._rsize.y / self.row) if self.menu else NvVector2(self.relx(self.cell_width), self.rely(self.cell_height))
        coords_marg_vec = self.coordinates + self._rsize_marg
        for i in range(len(self.items)):
            item = self.items[i]
            gr_vec = self.grid_coordinates[i]
            curr_cell_vec = gr_vec * c_vec
            size_adapt_vec = (c_vec - item._csize) / 2
            coordinates = coords_marg_vec + curr_cell_vec + size_adapt_vec
            item.coordinates = coordinates
            item.absolute_coordinates = self._get_item_abs_coords(item)
            self.cached_coordinates.append(coordinates)
            
    def secondary_update(self, *args):
        super().secondary_update()
        self._base_light_update()
        #print(self, self.get_param_strict("id").value)
        #if self.get_param_value("id") == "secret_test":
        #    print(self.coordinates)
        #    print("--")
        #    print(self.absolute_coordinates)
        #    print(self.items, self.cached_coordinates)

    def _parse_gcx(self, coord, pos: int): # type: ignore
        if self.first_parent_menu is None: raise self._unconnected_layout_error("Gcx coords")
        if self.first_parent_menu._window is None: raise self._uninitialized_layout_error("Gcx coords")
        if type(coord) == Gc: return self._percent_helper((self.cell_width, self.cell_height)[pos], coord.value), True
        elif type(coord) == Gcw: return self._percent_helper((self.cell_width), coord.value), True
        elif type(coord) == Gch: return self._percent_helper((self.cell_height), coord.value), True
        elif type(coord) == Cgc: return self._percent_helper(self.rel(NvVector2(self.cell_width, self.cell_height))[pos], coord.value), True
        elif type(coord) == Cgcw: return self._percent_helper(self.relx(self.cell_width), coord.value), True
        elif type(coord) == Cgch: return self._percent_helper(self.rely(self.cell_height), coord.value), True

    def add_item(self, item: NevuObject, x: any_number, y: any_number):  # type: ignore
        range_error = ValueError("Grid index out of range x: {x}, y: {y} ".format(x=x,y=y)+f"Grid size: {self.column}x{self.row}")
        if x > self.column or y > self.row or x < 1 or y < 1: raise range_error
        for coordinates in self.grid_coordinates:
            if coordinates == (x - 1, y - 1): raise ValueError("Grid item already exists")
        super().add_item(item)
        self.grid_coordinates.append(NvVector2(x - 1,y - 1))

    def secondary_draw_content(self):
        super().secondary_draw_content()
        for item in self.items: 
            assert isinstance(item, (Widget, LayoutType))
            self._draw_widget(item)

    def get_row(self, x: any_number) -> list[NevuObject]:
        return [item for item, coords in zip(self.items, self.grid_coordinates) if coords[0] == x - 1]

    def get_column(self, y: any_number) -> list[NevuObject]:
        return [item for item, coords in zip(self.items, self.grid_coordinates) if coords[1] == y - 1]

    def get_item(self, x: any_number, y: any_number) -> NevuObject | None:
        target_coords = (x - 1, y - 1)
        for i, coords in enumerate(self.grid_coordinates):
            if math.isclose(coords[0], target_coords[0]) and math.isclose(coords[1], target_coords[1]): return self.items[i]