import copy
from typing import Unpack

from nevu_ui.components.layouts.layout_base import LayoutType, LayoutTypeKwargs
from nevu_ui.components.nevuobj import NevuObject
from nevu_ui.components.widgets import Widget
from nevu_ui.core.enums import (
    Align,
    CacheType,
    CustomFunctions,
    FlexDirection,
    FlexJustify,
)
from nevu_ui.fast.logic.fast_logic import (
    base_light_update,
    draw_widgets_optimized,
    py_get_item_abs_coords,
)
from nevu_ui.fast.nvvector2 import NvVector2

MAIN_LEN_STR = "main_len"
SEC_LEN_STR = "sec_len"
ITEMS_STR = "items"

class FlexLayoutKwargs(LayoutTypeKwargs, total=False):
    direction: FlexDirection
    wrap: bool
    justify_content: FlexJustify
    align_items: Align
    gap: int | float | NvVector2
    max_wrap_size: int | float

class FlexLayout(LayoutType):
    _supports_global_size = False
    content_type = list[NevuObject]

    # === Params ===
    direction: FlexDirection
    wrap: bool
    justify_content: FlexJustify
    align_items: Align
    gap: int | float | NvVector2
    max_wrap_size: int | float
    # ==============

    def __init__(
        self,
        *content,
        style=None,
        **constant_kwargs: Unpack[FlexLayoutKwargs],
    ):
        super().__init__(content, size = NvVector2(0, 0), style = style, **constant_kwargs)

    def _init_booleans(self):
        super()._init_booleans()
        self._add_custom_flags(
            CustomFunctions.secondary_draw_content |
            CustomFunctions.secondary_update
        )

    def _add_params(self):
        super()._add_params()
        self._add_param("direction", FlexDirection, FlexDirection.Row)
        self._add_param("wrap", bool, True)
        self._add_param("justify_content", FlexJustify, FlexJustify.Start)
        self._add_param("align_items", Align, Align.CENTER)
        self._add_param("gap", int | float | NvVector2, 10)
        self._add_param("max_wrap_size", int | float, 0)

    def _boot_up(self):
        super()._boot_up()
        self._sync_layout()

    def add_items(self, content):
        for item in content:
            if not isinstance(item, NevuObject):
                raise TypeError(f"FlexLayout content must be NevuObject, got {type(item)}")
            self.add_item(item)

    def _coordinates_setter(self, coordinates: NvVector2) -> bool:
        if self.coordinates.x != coordinates.x or self.coordinates.y != coordinates.y:
            delta = coordinates - self.coordinates
            if self.cached_coordinates is not None:
                for i, item in enumerate(self.items):
                    if i < len(self.cached_coordinates):
                        self.cached_coordinates[i] += delta
                    if isinstance(item, LayoutType):
                        item.set_coordinates(item.coordinates + delta)
                        item.absolute_coordinates += delta
                    else:
                        item.coordinates += delta
                        item.absolute_coordinates += delta
        return True

    def _connect_to_layout(self, layout: LayoutType):
        super()._connect_to_layout(layout)
        self._sync_layout()

    def _connect_to_menu(self, menu):
        super()._connect_to_menu(menu)
        self._sync_layout()

    def _item_add(self, item: NevuObject):
        item = super()._item_add(item)
        if self.booted:
            item._resize(NvVector2.from_xy(1.0, 1.0))
            if isinstance(item, LayoutType):
                item._regenerate_coordinates()
        return item

    def _on_item_add(self, item: NevuObject):
        self._sync_layout()
        if isinstance(item, LayoutType):
            item._regenerate_coordinates()
        if self.layout:
            self.layout._on_item_add(item)

    def add_item(self, item: NevuObject):
        item = super().add_item(item)
        self.cached_coordinates = None
        self._sync_layout()
        if isinstance(item, LayoutType):
            item._regenerate_coordinates()
        return item

    def _regenerate_coordinates(self):
        super()._regenerate_coordinates()
        self._sync_layout()

    def _resize_content(self, resize_ratio: NvVector2):
        self._resize_ratio = resize_ratio
        self.cached_coordinates = None
        self._border_font_surface = None
        self._need_update_overlay = True

        fixed_ratio = NvVector2.from_xy(1.0, 1.0)
        for item in self._all_items():
            assert isinstance(item, (Widget, LayoutType))
            item._resize(fixed_ratio)

        self._sync_layout()

    def _get_gap_vec(self) -> NvVector2:
        gap = self.gap
        if isinstance(gap, int | float):
            return NvVector2.from_xy(gap, gap)
        return gap

    def _get_available_space(self, is_row: bool) -> float:
        max_wrap = self.max_wrap_size
        if max_wrap > 0:
            return float(max_wrap)

        if self.layout is not None and hasattr(self.layout, "current_size"):
            val = self.layout.current_size.x if is_row else self.layout.current_size.y
            if val > 0: return val - 20.0

        if self.first_parent_menu is not None:
            val = self.first_parent_menu._rel_size.x if is_row else self.first_parent_menu._rel_size.y
            if val > 0: return val

        if self.first_parent_menu and self.first_parent_menu._window:
            win_size = self.first_parent_menu._window.size
            return float(win_size.x if is_row else win_size.y)

        return float("inf")

    def _sync_layout(self):
        if not self.booted or any(not x.booted for x in self.items):
            return
        self._recalculate_layout()

    def _create_line_dicts(self, is_row: bool, gap_size: NvVector2):
        available_space = self._get_available_space(is_row)

        wrap = self.wrap

        lines = []
        curr_line = []
        curr_main_size = 0
        curr_sec_max = 0

        def next_line():
            nonlocal curr_line, curr_main_size, curr_sec_max
            if not curr_line: return
            lines.append({
                ITEMS_STR: curr_line,
                MAIN_LEN_STR: curr_main_size - gap_size.x,
                SEC_LEN_STR: curr_sec_max,
            })
            curr_line = []
            curr_main_size = 0
            curr_sec_max = 0

        items = self.items
        for item in items:
            item_size = item.size
            if is_row:
                main_width = item_size.x
                sec_width = item_size.y
            else:
                main_width = item_size.y
                sec_width = item_size.x

            if wrap and curr_line and curr_main_size + main_width > available_space:
                next_line()

            curr_line.append(item)
            curr_main_size += main_width + gap_size.x
            curr_sec_max = max(sec_width, curr_sec_max)

        next_line()
        return lines

    def _recalculate_layout(self):
        for item in self.items:
            if isinstance(item, LayoutType) and hasattr(item, "_recalculate_size"):
                item._recalculate_size()

        direction = self.direction
        justify = self.justify_content
        align = self.align_items

        is_row = (direction == FlexDirection.Row)
        gap_size = self._get_gap_vec()
        if not is_row:
            gap_size = gap_size.yx

        lines = self._create_line_dicts(is_row, gap_size)

        if is_row:
            total_size_vec = NvVector2.from_xy(
                max((line[MAIN_LEN_STR] for line in lines), default=0.0),
                sum(line[SEC_LEN_STR] for line in lines) + (len(lines) - 1) * gap_size.y if lines else 0.0
            )
        else:
            total_size_vec = NvVector2.from_xy(
                sum(line[SEC_LEN_STR] for line in lines) + (len(lines) - 1) * gap_size.y if lines else 0.0,
                max((line[MAIN_LEN_STR] for line in lines), default=0.0)
            )

        ratio_vec = NvVector2.from_xy(
            self._resize_ratio.x if self._resize_ratio.x != 0 else 1.0,
            self._resize_ratio.y if self._resize_ratio.y != 0 else 1.0
        )

        old_size = self.size.xy
        self.size = total_size_vec / ratio_vec

        self.cache.clear_selected(whitelist=[CacheType.RelSize])

        cached_coordinates = []
        current_sec_pos = 0.0

        self_coordinates = self.coordinates

        total_main_len = total_size_vec.x if is_row else total_size_vec.y

        for line in lines:
            start_main_pos = 0.0
            spacing = gap_size.x
            main_len = line[MAIN_LEN_STR]
            items = line[ITEMS_STR]
            sec_len = line[SEC_LEN_STR]
            n_items = len(items)

            if justify is FlexJustify.Center:
                start_main_pos = (total_main_len - main_len) / 2.0
            elif justify is FlexJustify.End:
                start_main_pos = total_main_len - main_len
            elif justify is FlexJustify.SpaceBetween and len(items) > 1:
                items_sum = sum((it.size.x if is_row else it.size.y) for it in items)
                spacing = (total_main_len - items_sum) / (len(items) - 1)
            elif justify is FlexJustify.SpaceAround:
                if n_items > 0:
                    items_sum = sum((it.size.x if is_row else it.size.y) for it in items)
                    free_space = total_main_len - items_sum
                    unit = free_space / n_items
                    spacing = unit
                    start_main_pos = unit / 2.0
            elif justify is FlexJustify.SpaceEvenly and n_items > 0:
                items_sum = sum((it.size.x if is_row else it.size.y) for it in items)
                free_space = total_main_len - items_sum
                unit = free_space / (n_items + 1)
                spacing = unit
                start_main_pos = unit
            current_main_pos = start_main_pos

            for item in items:
                item_sec = item.size.y if is_row else item.size.x
                sec_offset = 0.0

                if align == Align.CENTER:
                    sec_offset = (sec_len - item_sec) / 2.0
                elif align in (Align.BOTTOM, Align.RIGHT):
                    sec_offset = sec_len - item_sec

                if is_row:
                    target_x = self_coordinates.x + current_main_pos
                    target_y = self_coordinates.y + current_sec_pos + sec_offset
                else:
                    target_x = self_coordinates.x + current_sec_pos + sec_offset
                    target_y = self_coordinates.y + current_main_pos

                new_coords = NvVector2.from_xy(target_x, target_y)

                item.coordinates = new_coords
                item.set_coordinates(new_coords)
                if isinstance(item, LayoutType):
                    item._regenerate_coordinates()

                item.absolute_coordinates = py_get_item_abs_coords(self, item)
                cached_coordinates.append(item.coordinates.copy())

                current_main_pos += (item.size.x if is_row else item.size.y) + spacing

            current_sec_pos += sec_len + gap_size.y

        self.cached_coordinates = cached_coordinates

        parent = self.layout

        if (old_size.x != self.size.x or old_size.y != self.size.y) and parent:
            if hasattr(parent, "_recalculate_size"):
                parent._recalculate_size()
            if hasattr(parent, "_regenerate_coordinates") and parent.booted:
                parent.cached_coordinates = None
                parent._regenerate_coordinates()
            else:
                parent.cached_coordinates = None

    def secondary_update(self, *args): base_light_update(self)

    def secondary_draw_content(self):
        draw_widgets_optimized(self, self.items, LayoutType, Widget)

    def _create_clone(self):
        return self.__class__(
            *copy.deepcopy(self._template["content"]),
            style = copy.deepcopy(self.style),
            **self.constant_kwargs,
        )
