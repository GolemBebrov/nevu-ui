import contextlib
from abc import ABC, abstractmethod
from typing import Any, Unpack, NotRequired

from nevu_ui.fast.logic import _light_update_helper
from nevu_ui.widgets import Widget
from nevu_ui.nevuobj import NevuObject
from nevu_ui.fast.nvvector2 import NvVector2
from nevu_ui.layouts import LayoutType, LayoutTypeKwargs
from nevu_ui.fast.logic.fast_logic import collide_vector
from nevu_ui.color import SubThemeRole
from nevu_ui.core.state import nevu_state
from nevu_ui.fast.logic.fast_logic import _very_light_update_helper
from nevu_ui.style import Style, default_style
from nevu_ui.core.enums import Align, ScrollBarType
from nevu_ui.layouts.typehints import AlignTemplate
from nevu_ui.utils import keyboard, mouse

class _ScrollableKwargs(LayoutTypeKwargs):
    arrow_scroll_power: NotRequired[float | int]
    wheel_scroll_power: NotRequired[float | int]
    inverted_scrolling: NotRequired[bool]
    scrollbar_perc: NotRequired[NvVector2 | None]
    basic_alignment: NotRequired[Align]
    append_key: NotRequired[Any]
    descend_key: NotRequired[Any]
    spacing: NotRequired[int | float]

class ScrollableKwargs(_ScrollableKwargs, LayoutTypeKwargs): pass

class ScrollableBase(LayoutType, ABC):
    arrow_scroll_power: float | int
    wheel_scroll_power: float | int
    inverted_scrolling: bool
    append_key: Any #Realizes in the children
    descend_key: Any #Realizes in the children
    scrollbar_perc: NvVector2
    content_type = list[tuple[Align, NevuObject]]
    basic_alignment: Align
    
    class ScrollBar(Widget):
        def __init__(self, size, style, orientation: ScrollBarType, master: ScrollableBase | None = None, **constant_kwargs: Unpack[ScrollableKwargs]):
            super().__init__(size, style, **constant_kwargs)
            if not isinstance(master, ScrollableBase):
                print("!WARNING!: this class is intended to be used in ScrollableBase layout.")
            
            self.master: ScrollableBase = master #type: ignore
            
            if orientation not in ScrollBarType: raise ValueError("Orientation must be 'vertical' or 'horizontal'")
            self.orientation = orientation
        
        def _add_params(self):
            super()._add_params()
            self._change_param_default("clickable", True)
            self._change_param_default("hoverable", True)
            self._change_param_default("subtheme_role", SubThemeRole.PRIMARY)
        
        def _primary_update(self, events: list | None = None):
            super()._primary_update(events)
        
        def _init_numerical(self):
            super()._init_numerical()
            self._percentage = 0.0
            self.z = 99

        def _init_booleans(self):
            super()._init_booleans()
            self.scrolling = False

        def _init_lists(self):
            super()._init_lists()
            self.offset = NvVector2(0, 0)
            self.track_start_coordinates = NvVector2(0, 0)
            self.track_path = NvVector2(0, 0)

        def _orientation_to_int(self):
            return 1 if self.orientation == ScrollBarType.Vertical else 0

        @property
        def percentage(self) -> float:
            axis = self._orientation_to_int()
            
            scaled_track_path_val = (self.track_path[axis] * self._resize_ratio[axis]) - self._csize[axis]
            if scaled_track_path_val == 0: return 0.0
            
            start_coord = self.track_start_coordinates[axis] - self.offset[axis]
            current_path = self.coordinates[axis] - start_coord
            
            perc = (current_path / scaled_track_path_val) * 100
            return max(0.0, min(perc, 100.0))

        @percentage.setter
        def percentage(self, value: float | int):
            axis = self._orientation_to_int()
            
            self._percentage = max(0.0, min(float(value), 100.0))
            scaled_track_path = (self.track_path * self._resize_ratio) - self._csize
            start_coord = self.track_start_coordinates[axis] - self.offset[axis]
            
            if scaled_track_path[axis] == 0:
                self.coordinates[axis] = start_coord; return

            path_to_add = scaled_track_path[axis] * (self._percentage / 100)
            self.coordinates[axis] = start_coord + path_to_add
        
        def set_scroll_params(self, track_start_abs, track_path, offset: NvVector2):
            self.track_path = track_path
            self.track_start_coordinates = track_start_abs
            self.offset = offset

        def _on_click_system(self):
            super()._on_click_system()
            self.scrolling = True
        def _on_keyup_system(self):
            super()._on_keyup_system()
            self.scrolling = False
        def _on_keyup_abandon_system(self):
            super()._on_keyup_abandon_system()
            self.scrolling = False
        
        def secondary_update(self):
            super().secondary_update()
            axis = self._orientation_to_int()

            if self.scrolling:
                scaled_track_path_val = (self.track_path[axis] * self._resize_ratio[axis]) - self.rel(self.size)[axis]
                if scaled_track_path_val != 0:
                    mouse_relative_to_track = mouse.pos[axis] - self.track_start_coordinates[axis] + (nevu_state.window.offset*3)[axis]
                    self.percentage = (mouse_relative_to_track / scaled_track_path_val) * 100
            else:
                self.percentage = self._percentage

        def move_by_percents(self, percents: int | float):
            self.percentage += percents
            self.scrolling = False

        def set_percents(self, percents: int | float):
            self.percentage = percents
            self.scrolling = False
            
    def __init__(self, size: NvVector2 | list, style: Style = default_style, content:  content_type | None = None, **constant_kwargs: Unpack[ScrollableKwargs]):
        super().__init__(size, style, content, **constant_kwargs)
    
    def _create_template(self, size: NvVector2 | list, content: content_type | None): # type: ignore
        return AlignTemplate(size, content)
        
    def _init_test_flags(self):
        super()._init_test_flags()
        self._test_debug_print = False
        self._test_rect_calculation = True
        self._test_always_update = False
    
    def _init_booleans(self):
        super()._init_booleans()
        self._scroll_needs_update = False
    
    def _init_numerical(self):
        super()._init_numerical()
        self.max_secondary = 0
        self.max_main = 0
        self.actual_max_main = 1
        
    def _init_lists(self):
        super()._init_lists()
        self.widgets_alignment = []
        self.collided_items = []
        
    def _coordinates_setter(self, coordinates: NvVector2):
        super()._coordinates_setter(coordinates)
        if self.booted == False: return True
        self._update_scroll_bar()
        return True
        
    def _add_params(self):
        super()._add_params()
        self._add_param('arrow_scroll_power', int, 5)
        self._add_param('wheel_scroll_power', int, 5)
        self._add_param('inverted_scrolling', bool, False)
        self._add_param('scrollbar_perc', (NvVector2, type(None)), None)
        self._add_param('basic_alignment', (Align, type(None)), None)
        self._add_param('append_key', Any, None)
        self._add_param('descend_key', Any, None)
        self._add_param('spacing', (int, float), 30, layer=1)
        
    def _lazy_init(self, size: NvVector2 | list, content: content_type | None = None):
        super()._lazy_init(size, content)
        self.add_items(content)
        self._init_scroll_bar()
        self._update_scroll_bar()
        
    def add_items(self, content: content_type | None):
        if content:
            for mass in content:
                align, item = mass
                assert type(align) == Align and isinstance(item, NevuObject), f"Incorrect align or item ({align}, {item})"
                self.add_item(item, align)
                
    def _init_scroll_bar(self):
        self.scroll_bar = self._create_scroll_bar()
        self.scroll_bar.constant_kwargs['z'] = 99
        self._boot_scrollbar(self.scroll_bar)

    def _boot_scrollbar(self, scroll_bar: ScrollBar):
        scroll_bar.get_param_strict("subtheme_role").value = SubThemeRole.TERTIARY
        scroll_bar._boot_up()
        
        scroll_bar._init_start()
        scroll_bar.booted = True
        
    def get_offset(self) -> int | float: return self.actual_max_main / 100 * self.scroll_bar.percentage

    def _is_widget_drawable(self, item: NevuObject):
        coords_1 = item.absolute_coordinates
        coords_2 = coords_1 + item._csize
        
        viewport_tl = self.absolute_coordinates
        viewport_br = self.absolute_coordinates + self._csize
        return collide_vector(viewport_tl, viewport_br, coords_1, coords_2)
    
    def _is_widget_drawable_optimized(self, item: NevuObject):
        rect1 = item.get_nvrect()
        rect2 = self.get_nvrect()
        return rect1.collide_rect(rect2)
    
    def _rl_predraw_widgets(self):
        for item in self.collided_items:
            if self.is_layout(item):
                item._rl_predraw_widgets()
            elif self.is_widget(item):
                item.draw()
        if self.actual_max_main > 0:
            self.scroll_bar.draw()
    
    def _secondary_draw(self):
        super()._secondary_draw()
        for item in self.collided_items:
            assert isinstance(item, (Widget, LayoutType))
            self._draw_widget(item)
            
        if self.actual_max_main > 0:
            self._draw_widget(self.scroll_bar)
    
    def _base_light_update(self, add_x: int | float = 0, add_y: int | float = 0, items = None):
        assert self.first_parent_menu, self._unconnected_layout_error(items or self.collided_items)
        _light_update_helper(
            items or self.items,
            self.cached_coordinates or [],
            self.first_parent_menu.absolute_coordinates,
            NvVector2(add_x, add_y))

    def secondary_update(self): 
        super().secondary_update()
        if self.actual_max_main > 0:
            old_percentage = self.scroll_bar.percentage
            self.scroll_bar.update()
            new_percentage = self.scroll_bar.percentage
            if old_percentage != new_percentage:
                self._scroll_needs_update = True
        self._very_light_update()
        for item in self.collided_items:
            item.update() 
        if self._scroll_needs_update:
            self._recollide_items()
            self._update_scroll_bar()
            self._scroll_needs_update = False 
        if self.actual_max_main > 0:
            self.scroll_bar.coordinates = self._get_scrollbar_coordinates() # type: ignore
            self.scroll_bar.absolute_coordinates = self._get_item_abs_coords(self.scroll_bar)

    def _recollide_items(self):
        drawable = self._is_widget_drawable_optimized
        self.collided_items = [item for item in self.items if drawable(item)]
        
    def _regenerate_coordinates(self):
        self.cached_coordinates = []
        self._regenerate_max_values()
        spacing = self.get_param_strict("spacing").value
        pad = self._main_coord(self.rel(NvVector2(spacing, spacing)))
        padding_offset = pad
        
        for i, item in enumerate(self.items):
            align = self.widgets_alignment[i]
            self._set_item_main(item, align)
            item.coordinates[self._main_axis] = padding_offset + self.coordinates[self._main_axis]*2

            self.cached_coordinates.append(item.coordinates.copy())
            item.absolute_coordinates = self._get_item_abs_coords(item) 
            padding_offset += self._main_coord(item._csize) + pad
        self._very_light_update()
        self._recollide_items()
    
    def _very_light_update(self):
        assert len(self.cached_coordinates or []) == len(self.items), "You need to regenerate coordinates first."
        _very_light_update_helper(
            self.items,
            self.cached_coordinates or [],
            self.get_relative_vector_offset(),
            self._get_item_abs_coords)

    def _logic_update(self):
        super()._logic_update()
        inverse = -1 if self.inverted_scrolling else 1
        with contextlib.suppress(Exception):
            if keyboard.is_fdown(self.append_key):
                self.scroll_bar.move_by_percents(self.arrow_scroll_power * -inverse)
                self._scroll_needs_update = True
            if keyboard.is_fdown(self.descend_key):
                self.scroll_bar.move_by_percents(self.arrow_scroll_power * inverse)
                self._scroll_needs_update = True
            
    def _on_scroll_system(self, side: bool):
        super()._on_scroll_system(side)
        direction = 1 if side else -1

        if self.inverted_scrolling: direction *= -1
        
        self.scroll_bar.move_by_percents(self.wheel_scroll_power * direction)
        self._scroll_needs_update = True

    def _update_scroll_bar(self):
        if not self.first_parent_menu: return
        assert self.first_parent_menu._window
        track_start, track_path_main = self.absolute_coordinates, self._main_coord(self.size)
        offset = NvVector2(self.first_parent_menu._window._crop_width_offset, self.first_parent_menu._window._crop_height_offset) if self.first_parent_menu._window else NvVector2(0,0)
        start_coords = NvVector2()
        start_coords[abs(self._main_axis - 1)] = self._sec_coord(self._global_coordinates + self.rel(self.size - self.scroll_bar.size))
        start_coords[self._main_axis] = self._main_coord(track_start) + self._global_coordinates[self._main_axis] + offset[self._main_axis] / 2
        track_path = NvVector2(0, track_path_main)
        offset[self._main_axis] += self._global_coordinates[self._main_axis]
        self.scroll_bar.set_scroll_params(start_coords, track_path, offset)

    def _resize(self, resize_ratio: NvVector2):
        old_scrbar_perc = self.scroll_bar.percentage
        super()._resize(resize_ratio)
        self.scroll_bar._resize(resize_ratio)
        self._update_scroll_bar()
        self._resize_scrollbar(old_scrbar_perc)
        self.cached_coordinates = None
        self._scroll_needs_update = True
        self._regenerate_coordinates()
        self.scroll_bar.scrolling = False
        self._base_light_update()

    def _on_item_add(self, item: NevuObject):
        self.cached_coordinates = None
        if self.booted == False: return
        self._update_scroll_bar()
    
    def add_item(self, item: NevuObject, alignment: Align | None = None):  # type: ignore
        alignment = alignment or self.basic_alignment
        if not self._parse_align(alignment): print(f"Warning: align {alignment} not supported in {type(self).__name__}, skipping.."); return
        super().add_item(item)
        self.widgets_alignment.append(alignment)

    def clear(self):
        self.items.clear()
        self.widgets_alignment.clear()
        self._restart_coordinates()
        
    def apply_style_to_childs(self, style: Style):
        super().apply_style_to_childs(style)
        self.apply_scroll_bar_style(style)
        
    def _resize_scrollbar(self, old_percentage: int | float):
        self.scroll_bar.set_percents(old_percentage)
        
    def apply_scroll_bar_style(self, style: Style): self.scroll_bar.style = style

    def _restart_coordinates(self):
        self.max_main = self.get_param_strict("spacing").value
        self.actual_max_main = 0
        
#=== PLACEHOLDERS ===
    @property
    def _main_axis(self) -> int: pass
    @abstractmethod
    def _main_coord(self, coordinates: NvVector2) -> int | float: pass
    @abstractmethod
    def _sec_coord(self, coordinates: NvVector2) -> int | float: pass
    @abstractmethod
    def _parse_align(self, align: Align) -> bool: return False
    @abstractmethod
    def _regenerate_max_values(self): pass
    @abstractmethod
    def _get_scrollbar_coordinates(self) -> NvVector2: return NvVector2()
    @abstractmethod
    def _set_item_main(self, item: NevuObject, align: Align): pass
    @abstractmethod
    def get_relative_vector_offset(self) -> NvVector2: return NvVector2()
    @abstractmethod
    def _create_scroll_bar(self) -> ScrollBar: return None # type: ignore
    @property
    @abstractmethod
    def _collide_function(self): return collide_vector