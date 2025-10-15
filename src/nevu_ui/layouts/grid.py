import copy

from nevu_ui.widgets import Widget
from nevu_ui.nevuobj import NevuObject
from nevu_ui.fast.nvvector2 import NvVector2 
from nevu_ui.layouts import LayoutType

from nevu_ui.style import (
    Style, default_style
)

class Grid(LayoutType):
    row: int | float
    column: int | float
    def __init__(self, size: NvVector2 | list, style: Style = default_style, content: dict[tuple[int, int] , NevuObject] | None = None, **constant_kwargs):
        super().__init__(size, style, **constant_kwargs)
        self._lazy_kwargs = {'size': size, 'content': content}
        
    def _add_constants(self):
        super()._add_constants()
        self._add_constant("column", (int, float), 1)
        self._add_constant("row", (int, float), 1)
        self._add_constant_link("y", "row")
        self._add_constant_link("x", "column")
        #print(self.constant_defaults)
    
    def _init_lists(self):
        super()._init_lists()
        self.grid_coordinates = []
    
    def _lazy_init(self, size: NvVector2 | list, content: dict[tuple[int, int] , NevuObject] | None = None): # type: ignore
        super()._lazy_init(size)
        self.cell_height = self.size[1] / self.row
        self.cell_width = self.size[0] / self.column
        if not content:
            return
        if type(self) != Grid: return
        for coords, item in content.items():
            self.add_item(item, coords[0], coords[1])
            
    def _regenerate_coordinates(self):
        super()._regenerate_coordinates()
        self.cached_coordinates = []
        for i in range(len(self.items)):
            item = self.items[i]
            x, y = self.grid_coordinates[i]
            if not self.menu:
                cw = self.relx(self.cell_width)
                ch = self.rely(self.cell_height)
            else: 
                cw = self._rsize[0] / self.column
                ch = self._rsize[1] / self.row
                
            coordinates = NvVector2(self.coordinates[0] + self._rsize_marg[0] + x * cw + (cw - self.relx(item.size[0])) / 2 ,
                           self.coordinates[1] + self._rsize_marg[1] +y * ch + (ch -  self.rely(item.size[1])) / 2)
            item.coordinates = coordinates
            item.master_coordinates = self._get_item_master_coordinates(item)
            self.cached_coordinates.append(coordinates)
            
    def secondary_update(self, *args):
        super().secondary_update()
        self.base_light_update()
        if isinstance(self, Grid): self._dirty_rect = self._read_dirty_rects()
        
    def add_item(self, item: NevuObject, x: int, y: int):  # type: ignore
        range_error = ValueError("Grid index out of range x: {x}, y: {y} ".format(x=x,y=y)+f"Grid size: {self.column}x{self.row}")
        if x > self.column or y > self.row or x < 1 or y < 1: raise range_error
        for coordinates in self.grid_coordinates:
            if coordinates == (x-1, y-1): raise ValueError("Grid item already exists")
        self.grid_coordinates.append((x-1,y-1))
        super().add_item(item)
        if self.layout: self.layout._event_on_add_item()

    def secondary_draw_content(self):
        super().secondary_draw_content()
        for item in self.items: 
            assert isinstance(item, (Widget, LayoutType))
            self._draw_widget(item)

    def get_row(self, x: int) -> list[NevuObject]:
        return [item for item, coords in zip(self.items, self.grid_coordinates) if coords[0] == x - 1]

    def get_column(self, y: int) -> list[NevuObject]:
        return [item for item, coords in zip(self.items, self.grid_coordinates) if coords[1] == y - 1]

    def get_item(self, x: int, y: int) -> NevuObject | None:
        try:
            index = self.grid_coordinates.index((x - 1, y - 1))
            return self.items[index]
        except ValueError:
            return None
        
    def clone(self):
        return Grid(self._lazy_kwargs['size'], copy.deepcopy(self.style), self._lazy_kwargs['content'], **self.constant_kwargs)
