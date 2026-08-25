from typing import Unpack, overload

from nevu_ui.components.layouts.grid.base import (
    Grid,
    GridKwargs_rc,
    GridKwargs_uni,
    GridKwargs_xy,
)
from nevu_ui.components.nevuobj import NevuObject
from nevu_ui.core import Annotations


class Column(Grid):
    content_type = dict[Grid.any_number, NevuObject]

    @overload
    def __init__(
        self,
        content: content_type | None = None,
        size: Annotations.nevuobj_size = None,
        style: Annotations.nevuobj_style = None,
        **constant_kwargs: Unpack[GridKwargs_rc],
    ):
        """
        Initializes a Column object.
        Parameters:
        column (int | float): **WARNING: column param cannot be changed in Column**
        """

    @overload
    def __init__(
        self,
        content: content_type | None = None,
        size: Annotations.nevuobj_size = None,
        style: Annotations.nevuobj_style = None,
        **constant_kwargs: Unpack[GridKwargs_xy],
    ):
        """
        Initializes a Column object.
        Parameters:
        x (int | float): **WARNING: x param cannot be changed in Column**
        """

    def __init__(
        self,
        content: content_type | None = None,
        size: Annotations.nevuobj_size = None,
        style: Annotations.nevuobj_style = None,
        **constant_kwargs: Unpack[GridKwargs_uni],
    ):
        super().__init__(content, size, style, **constant_kwargs)  # type: ignore

    def _add_params(self):
        super()._add_params()
        self._block_param("column")

    def add_items(self, content: content_type | None):  # type: ignore
        if not content:
            return
        for ycoord, item in content.items():
            self.add_item(item, ycoord)

    def kill_item_by_pos(self, y: Grid.any_number):  # type: ignore
        return super().kill_item_by_pos(1, y)

    def add_item(self, item: NevuObject, y: Grid.any_number):  # type: ignore
        return super().add_item(item, 1, y)

    def get_item(self, y: Grid.any_number) -> NevuObject | None:  # type: ignore
        return super().get_item(1, y)
