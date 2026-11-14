import copy
from typing import Unpack

from nevu_ui.components._typehints import _FlexKwargs
from nevu_ui.components.layouts.base import BaseLayout
from nevu_ui.components.nevuobject import NevuObject
from nevu_ui.components.widgets import Widget
from nevu_ui.core.enums import (
    Align,
    CacheType,
    CustomFunctions,
    FlexJustify,
    Orientation,
)
from nevu_ui.core.size.rules import (
    Auto,
    Px,
    _all_fillx,
    _all_gcx,
    _all_vx,
    _SizeRule,
)
from nevu_ui.cython.logic.logic import (
    update_items,
    draw_items,
    get_absolute_coordinates,
)
from nevu_ui.cython.vector2 import Vector2


_still_offset = Vector2()
MAIN_LEN_STR = "main_len"
SEC_LEN_STR = "sec_len"
ITEMS_STR = "items"
BASES_STR = "bases"
BASE_STR = "base"
GROW_STR = "grow"
SHRINK_STR = "shrink"
ALIGN_STR = "align"
MIN_MAIN_STR = "min_main"
MAX_MAIN_STR = "max_main"
MIN_SEC_STR = "min_sec"
MAX_SEC_STR = "max_sec"

FLEX_EPS = 0.01

class Flex(BaseLayout):
    _supports_global_size = False
    content_type = list[NevuObject]

    # === Params ===
    orientation: Orientation
    wrap: bool
    justify_content: FlexJustify
    align_items: Align
    gap: int | float | Vector2
    max_wrap_size: int | float
    # ==============

    def __init__(
        self,
        *content,
        style=None,
        **params: Unpack[_FlexKwargs],
    ):
        super().__init__(content, size = Vector2(0, 0), style = style, **params)

    def _init_booleans(self):
        super()._init_booleans()
        self._is_recalculating = False
        self._add_custom_flags(
            CustomFunctions.draw_main |
            CustomFunctions.update_main
        )

    def _add_params(self):
        super()._add_params()
        self._add_param("orientation", Orientation, Orientation.Row)
        self._add_param("wrap", bool, True)
        self._add_param("justify_content", FlexJustify, FlexJustify.Start)
        self._add_param("align_items", Align, Align.CENTER)
        self._add_param("gap", int | float | Vector2, 10)
        self._add_param("max_wrap_size", int | float, 0)

    def _boot_up(self):
        super()._boot_up()
        self._sync_layout()

    def add_items(self, content):
        for item in content:
            if not isinstance(item, NevuObject):
                raise TypeError(f"Flex content must be NevuObject, got {type(item)}")
            self.add_item(item)

    def _coordinates_setter(self, coordinates: Vector2) -> bool:
        if self.coordinates.x != coordinates.x or self.coordinates.y != coordinates.y:
            delta = coordinates - self.coordinates
            if self.cached_coordinates is not None:
                for i, item in enumerate(self.items):
                    if i < len(self.cached_coordinates):
                        self.cached_coordinates[i] += delta
                    if isinstance(item, BaseLayout):
                        item.set_coordinates(item.coordinates + delta)
                        item.absolute_coordinates += delta
                    else:
                        item.coordinates += delta
                        item.absolute_coordinates += delta
        return True

    def _connect_to_layout(self, layout: BaseLayout):
        super()._connect_to_layout(layout)
        self._sync_layout()

    def _connect_to_menu(self, menu):
        super()._connect_to_menu(menu)
        self._sync_layout()

    def _item_add(self, item: NevuObject):
        item = super()._item_add(item)
        if self.booted:
            item._resize(Vector2.from_xy(1.0, 1.0))
            if isinstance(item, BaseLayout):
                item._regenerate_coordinates()
        return item

    def _on_item_add(self, item: NevuObject):
        self._sync_layout()
        if isinstance(item, BaseLayout):
            item._regenerate_coordinates()
        if self._parent_layout:
            self._parent_layout._on_item_add(item)

    def add_item(self, item: NevuObject):
        item = super().add_item(item)
        self.cached_coordinates = None
        self._sync_layout()
        if isinstance(item, BaseLayout):
            item._regenerate_coordinates()
        return item

    def _regenerate_coordinates(self):
        super()._regenerate_coordinates()
        self._sync_layout()

    def _resize_content(self, resize_ratio: Vector2):
        self._resize_ratio = Vector2.from_xy(1.0, 1.0)
        self.cached_coordinates = None
        self._border_font_surface = None
        self._need_update_overlay = True

        fixed_ratio = Vector2.from_xy(1.0, 1.0)
        for item in self._all_items():
            assert isinstance(item, (Widget, BaseLayout))
            item._resize(fixed_ratio)

        self._sync_layout()

    def _get_gap_vec(self) -> Vector2:
        gap = self.gap
        if isinstance(gap, int | float):
            return Vector2.from_xy(gap, gap)
        return gap

    def _get_available_space(self, is_row: bool) -> float:
        max_wrap = self.max_wrap_size
        if max_wrap > 0:
            return float(max_wrap)

        if self._parent_layout is not None and hasattr(self._parent_layout, "current_size"):  # noqa: SIM102
            if getattr(self._parent_layout, "_supports_global_size", True):
                val = self._parent_layout.current_size.x if is_row else self._parent_layout.current_size.y
                if val > 0:
                    return val - 20.0

        if self.first_parent_menu is not None:
            val = self.first_parent_menu.current_size.x if is_row else self.first_parent_menu.current_size.y
            if val > 0: return val

        if self.first_parent_menu and self.first_parent_menu._window:
            win_size = self.first_parent_menu._window.size
            return float(win_size.x if is_row else win_size.y)

        return float("inf")

    def _sync_layout(self):
        if not self.booted or any(not x.booted for x in self.items):
            return
        self._recalculate_layout()

    def _resolve_flex_rule(self, rule, is_row_axis: bool) -> float | None:
        if rule is None:
            return None
        if not isinstance(rule, _SizeRule):
            return float(rule)
        if isinstance(rule, Px):
            return float(rule.value)
        if isinstance(rule, Auto):
            return None
        rule_type = type(rule)
        if rule_type in _all_vx:
            return self._parse_vx(rule, rule_type, 0)
        if rule_type in _all_fillx:
            if rule_type.__name__.endswith("W"):
                target_is_row = True
            elif rule_type.__name__.endswith("H"):
                target_is_row = False
            else:
                target_is_row = is_row_axis
            space = self._get_available_space(target_is_row)
            if space == float("inf"):
                return None
            return self._percent_helper(space, rule.value)
        if rule_type in _all_gcx:
            raise ValueError(
                f"Handling for SizeRule '{rule_type.__name__}' is only Grid feature"
            )
        raise ValueError(f"Handling for SizeRule '{rule_type.__name__}' is not implemented")

    def _resolve_config_size(self, size, is_row: bool) -> tuple[float | None, float | None]:
        if size is None:
            return None, None
        if isinstance(size, int | float):
            return float(size), float(size)
        try:
            x, y = size[0], size[1]
        except (TypeError, IndexError, KeyError):
            raise ValueError(f"Invalid FlexConfig size: {size}") from None
        main = self._resolve_flex_rule(x if is_row else y, is_row)
        sec = self._resolve_flex_rule(y if is_row else x, not is_row)
        return main, sec

    def _collect_flex_data(self, is_row: bool) -> dict:
        flex_data = {}
        main_pos = 0 if is_row else 1
        sec_pos = 1 if is_row else 0
        for item in self.items:
            config = item.flex_config
            if config is None:
                continue
            grow = max(0.0, float(config.grow))
            shrink = max(0.0, float(config.shrink))
            align_self = config.align_self
            basis = self._resolve_flex_rule(config.basis, is_row) if config.basis is not None else None
            min_main, min_sec = self._resolve_config_size(config.min_size, is_row)
            max_main, max_sec = self._resolve_config_size(config.max_size, is_row)
            if (
                not grow and not shrink
                and align_self is None and basis is None
                and min_main is None and min_sec is None
                and max_main is None and max_sec is None
            ):
                continue
            base = item.size.copy()
            if basis is not None:
                base[main_pos] = basis
            if min_main is not None and base[main_pos] < min_main:
                base[main_pos] = min_main
            if max_main is not None and base[main_pos] > max_main:
                base[main_pos] = max_main
            if min_sec is not None and base[sec_pos] < min_sec:
                base[sec_pos] = min_sec
            if max_sec is not None and base[sec_pos] > max_sec:
                base[sec_pos] = max_sec
            flex_data[item] = {
                BASE_STR: base,
                GROW_STR: grow,
                SHRINK_STR: shrink,
                ALIGN_STR: align_self,
                MIN_MAIN_STR: min_main,
                MAX_MAIN_STR: max_main,
                MIN_SEC_STR: min_sec,
                MAX_SEC_STR: max_sec,
            }
        return flex_data

    def _create_line_dicts(self, is_row: bool, gap_size: Vector2, flex_data: dict, available_space: float):
        wrap = self.wrap

        lines = []
        curr_line = []
        curr_bases = []
        curr_main_size = 0
        curr_sec_max = 0

        def next_line():
            nonlocal curr_line, curr_bases, curr_main_size, curr_sec_max
            if not curr_line: return
            lines.append({
                ITEMS_STR: curr_line,
                BASES_STR: curr_bases,
                MAIN_LEN_STR: curr_main_size - gap_size.x,
                SEC_LEN_STR: curr_sec_max,
            })
            curr_line = []
            curr_bases = []
            curr_main_size = 0
            curr_sec_max = 0

        items = self.items
        for item in items:
            data = flex_data.get(item)
            item_size = data[BASE_STR] if data is not None else item.size
            if is_row:
                main_width = item_size.x
                sec_width = item_size.y
            else:
                main_width = item_size.y
                sec_width = item_size.x

            if wrap and curr_line and curr_main_size + main_width > available_space:
                next_line()

            curr_line.append(item)
            curr_bases.append(data[BASE_STR] if data is not None else item.size.copy())
            curr_main_size += main_width + gap_size.x
            curr_sec_max = max(sec_width, curr_sec_max)

        next_line()
        return lines

    def _distribute_grow(self, bases, datas, free_space: float, is_row: bool):
        main_pos = 0 if is_row else 1
        active = [i for i, data in enumerate(datas) if data is not None and data[GROW_STR] > 0.0]
        while active and free_space > FLEX_EPS:
            total_grow = 0.0
            for i in active:
                total_grow += datas[i][GROW_STR]
            if total_grow <= 0.0:
                return
            unit = free_space / total_grow
            clamped = []
            for i in active:
                max_main = datas[i][MAX_MAIN_STR]
                if max_main is None:
                    continue
                if bases[i][main_pos] + unit * datas[i][GROW_STR] > max_main + FLEX_EPS:
                    clamped.append((i, max_main))
            if not clamped:
                for i in active:
                    bases[i][main_pos] += unit * datas[i][GROW_STR]
                return
            for i, limit in clamped:
                free_space -= limit - bases[i][main_pos]
                bases[i][main_pos] = limit
                active.remove(i)

    def _distribute_shrink(self, bases, datas, overflow: float, is_row: bool):
        main_pos = 0 if is_row else 1
        active = [i for i, data in enumerate(datas) if data is not None and data[SHRINK_STR] > 0.0]
        while active and overflow > FLEX_EPS:
            weighted = 0.0
            for i in active:
                weighted += datas[i][SHRINK_STR] * bases[i][main_pos]
            if weighted <= 0.0:
                return
            unit = overflow / weighted
            clamped = []
            for i in active:
                min_main = datas[i][MIN_MAIN_STR]
                floor = min_main if min_main is not None else 0.0
                if bases[i][main_pos] * (1.0 - unit * datas[i][SHRINK_STR]) < floor - FLEX_EPS:
                    clamped.append((i, floor))
            if not clamped:
                for i in active:
                    bases[i][main_pos] *= 1.0 - unit * datas[i][SHRINK_STR]
                return
            for i, floor in clamped:
                overflow -= bases[i][main_pos] - floor
                bases[i][main_pos] = floor
                active.remove(i)

    def _resolve_flex_sizes(self, lines, flex_data: dict, available_space: float, gap_size: Vector2, is_row: bool):
        main_pos = 0 if is_row else 1
        sec_pos = 1 if is_row else 0
        align = self.align_items
        for line in lines:
            items = line[ITEMS_STR]
            bases = line[BASES_STR]
            datas = [flex_data.get(item) for item in items]

            if available_space != float("inf"):
                free_space = available_space - line[MAIN_LEN_STR]
                if free_space > FLEX_EPS and any(data is not None and data[GROW_STR] > 0.0 for data in datas):
                    self._distribute_grow(bases, datas, free_space, is_row)
                elif free_space < -FLEX_EPS and any(data is not None and data[SHRINK_STR] > 0.0 for data in datas):
                    self._distribute_shrink(bases, datas, -free_space, is_row)

            sec_len = line[SEC_LEN_STR]
            for base, data in zip(bases, datas):
                item_align = data[ALIGN_STR] if data is not None and data[ALIGN_STR] is not None else align
                if item_align != Align.STRETCH:
                    continue
                target = sec_len
                if data is not None:
                    if data[MIN_SEC_STR] is not None and target < data[MIN_SEC_STR]:
                        target = data[MIN_SEC_STR]
                    if data[MAX_SEC_STR] is not None and target > data[MAX_SEC_STR]:
                        target = data[MAX_SEC_STR]
                base[sec_pos] = target

            line[MAIN_LEN_STR] = sum(base[main_pos] for base in bases) + (len(items) - 1) * gap_size.x

    def _apply_flex_sizes(self, lines):
        for line in lines:
            for item, base in zip(line[ITEMS_STR], line[BASES_STR]):
                if item.size != base:
                    item.size = base.copy()
                    item.cache.clear_selected(whitelist=[CacheType.RelSize])
                    if isinstance(item, Widget):
                        item.clear_surfaces()
                        item._regen_surface()
                        item._changed = True

    def _recalculate_layout(self):
        if self._is_recalculating: return
        self._is_recalculating = True
        for item in self.items:
            if isinstance(item, BaseLayout) and hasattr(item, "_recalculate_size"):
                item._recalculate_size()

        direction = self.orientation
        justify = self.justify_content
        align = self.align_items

        is_row = (direction == Orientation.Row)
        gap_size = self._get_gap_vec()
        if not is_row:
            gap_size = gap_size.yx

        available_space = self._get_available_space(is_row)
        flex_data = self._collect_flex_data(is_row)

        lines = self._create_line_dicts(is_row, gap_size, flex_data, available_space)
        self._resolve_flex_sizes(lines, flex_data, available_space, gap_size, is_row)

        if is_row:
            total_size_vec = Vector2.from_xy(
                max((line[MAIN_LEN_STR] for line in lines), default=0.0),
                sum(line[SEC_LEN_STR] for line in lines) + (len(lines) - 1) * gap_size.y if lines else 0.0
            )
        else:
            total_size_vec = Vector2.from_xy(
                sum(line[SEC_LEN_STR] for line in lines) + (len(lines) - 1) * gap_size.y if lines else 0.0,
                max((line[MAIN_LEN_STR] for line in lines), default=0.0)
            )

        old_size = self.size.xy
        self.size = total_size_vec.copy()

        self.cache.clear_selected(whitelist=[CacheType.RelSize])

        self._apply_flex_sizes(lines)

        cached_coordinates = []
        current_sec_pos = 0.0

        self_coordinates = self.coordinates

        total_main_len = total_size_vec.x if is_row else total_size_vec.y

        for line in lines:
            spacing = gap_size.x
            main_len = line[MAIN_LEN_STR]
            items = line[ITEMS_STR]
            bases = line[BASES_STR]
            sec_len = line[SEC_LEN_STR]
            n_items = len(items)

            match justify:
                case FlexJustify.Start: start_main_pos = 0.0
                case FlexJustify.Center:
                    start_main_pos = (total_main_len - main_len) / 2.0
                case FlexJustify.End:
                    start_main_pos = total_main_len - main_len
                case FlexJustify.SpaceBetween:
                    items_sum = sum((it.size.x if is_row else it.size.y) for it in items)
                    if n_items > 1:
                        spacing = (total_main_len - items_sum) / (n_items - 1)
                    start_main_pos = 0.0
                case FlexJustify.SpaceAround:
                    if not n_items: ...
                    items_sum = sum((it.size.x if is_row else it.size.y) for it in items)
                    free_space = total_main_len - items_sum
                    unit = free_space / n_items
                    spacing = unit
                    start_main_pos = unit / 2.0
                case FlexJustify.SpaceEvenly:
                    if not n_items: ...
                    items_sum = sum((it.size.x if is_row else it.size.y) for it in items)
                    free_space = total_main_len - items_sum
                    unit = free_space / (n_items + 1)
                    spacing = unit
                    start_main_pos = unit
                case _:
                    raise ValueError("Unknown flex justify content")

            current_main_pos = start_main_pos

            for item, base in zip(items, bases):
                data = flex_data.get(item)
                item_align = data[ALIGN_STR] if data is not None and data[ALIGN_STR] is not None else align
                item_sec = item.size.y if is_row else item.size.x
                sec_offset = 0.0

                if item_align == Align.CENTER:
                    sec_offset = (sec_len - item_sec) / 2.0
                elif item_align in (Align.BOTTOM, Align.RIGHT):
                    sec_offset = sec_len - item_sec

                if is_row:
                    target_x = self_coordinates.x + current_main_pos
                    target_y = self_coordinates.y + current_sec_pos + sec_offset
                else:
                    target_x = self_coordinates.x + current_sec_pos + sec_offset
                    target_y = self_coordinates.y + current_main_pos

                new_coords = Vector2.from_xy(target_x, target_y)

                item.coordinates = new_coords
                item.set_coordinates(new_coords)
                if isinstance(item, BaseLayout):
                    item._regenerate_coordinates()
                    if not item._supports_global_size and item.size != base:
                        item.size = base.copy()
                        item.cache.clear_selected(whitelist=[CacheType.RelSize])

                item.absolute_coordinates = get_absolute_coordinates(self, item)
                cached_coordinates.append(item.coordinates.copy())

                current_main_pos += (item.size.x if is_row else item.size.y) + spacing

            current_sec_pos += sec_len + gap_size.y

        self.cached_coordinates = cached_coordinates

        parent = self._parent_layout

        size_changed = (abs(old_size.x - self.size.x) > 0.5 or abs(old_size.y - self.size.y) > 0.5)

        if size_changed:
            if self.bg_widget:
                self.bg_widget.size = self.size.xy
                self.bg_widget._regen_surface()
                self.bg_widget._changed = True
                self.bg_widget.clear_all()

            if parent:
                if hasattr(parent, "_recalculate_size"):
                    parent._recalculate_size()
                if hasattr(parent, "_regenerate_coordinates") and parent.booted:
                    parent.cached_coordinates = None
                    parent._regenerate_coordinates()
                else:
                    parent.cached_coordinates = None

        self._is_recalculating = False

    def _update_main(self):
            if not self.items or not self.cached_coordinates or not self.first_parent_menu:
                return
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

    def _create_clone(self):
        return self.__class__(
            *copy.deepcopy(self._template["content"]),
            style = copy.deepcopy(self.style),
            **self.kwargs,
        )

class VFlex(Flex):
    def _add_params(self):
        super()._add_params()
        self._change_param_default("orientation", Orientation.Vertical)
        self._block_param("orientation")

class HFlex(Flex):
    def _add_params(self):
        super()._add_params()
        self._change_param_default("orientation", Orientation.Horizontal)
        self._block_param("orientation")

__all__ = ["Flex", "VFlex", "HFlex"]
