import pygame
import copy
from typing import Any
import contextlib

from nevu_ui.widgets import Widget
from nevu_ui.menu import Menu
from nevu_ui.nevuobj import NevuObject
from nevu_ui.fast.nvvector2 import NvVector2
from nevu_ui.layouts import LayoutType

from nevu_ui.color import SubThemeRole

from nevu_ui.style import (
    Style, default_style
)
from nevu_ui.core_types import (
    Align, ScrollBarType
)
from nevu_ui.utils import (
    keyboard, mouse
)

class ScrollableBase(LayoutType):
    arrow_scroll_power: float | int
    wheel_scroll_power: float | int
    inverted_scrolling: bool
    append_key: Any #Realizes in the children
    descend_key: Any #Realizes in the children

    class ScrollBar(Widget):
        def __init__(self, size, style, orientation: ScrollBarType, master = None, **constant_kwargs):
            super().__init__(size, style, **constant_kwargs)
            if not isinstance(master, ScrollableBase):
                print("WARNING: this class is intended to be used in ScrollableBase layout.")
            
            self.master = master
            
            if orientation not in ScrollBarType:
                raise ValueError("Orientation must be 'vertical' or 'horizontal'")
            self.orientation = orientation
            
        def _init_numerical(self):
            super()._init_numerical()
            self._percentage = 0.0

        def _init_booleans(self):
            super()._init_booleans()
            self.scrolling = False
            self.clickable = True

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
            
            scaled_track_path_val = (self.track_path[axis] * self._resize_ratio[axis]) - self.rel(self.size)[axis]
            if scaled_track_path_val == 0: return 0.0
            
            start_coord = self.track_start_coordinates[axis] - self.offset[axis]
            current_path = self.coordinates[axis] - start_coord
            
            perc = (current_path / scaled_track_path_val) * 100
            return max(0.0, min(perc, 100.0))

        @percentage.setter
        def percentage(self, value: float | int):
            axis = self._orientation_to_int()
            
            self._percentage = max(0.0, min(float(value), 100.0))
            scaled_track_path = (self.track_path * self._resize_ratio) - self.rel(self.size)
            start_coord = self.track_start_coordinates[axis] - self.offset[axis]
            
            if scaled_track_path[axis] == 0:
                self.coordinates[axis] = start_coord
                return

            path_to_add = scaled_track_path[axis] * (self._percentage / 100)
            self.coordinates[axis] = start_coord + path_to_add
            
            if self.master:
                assert self.master.first_parent_menu.window, "Menu is not valid"
                self.master.first_parent_menu.window.mark_dirty()
        
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
                    mouse_relative_to_track = mouse.pos[axis] - self.track_start_coordinates[axis]
                    self.percentage = (mouse_relative_to_track / scaled_track_path_val) * 100
            else:
                self.percentage = self._percentage

        def move_by_percents(self, percents: int | float):
            self.percentage += percents
            self.scrolling = False

        def set_percents(self, percents: int | float):
            self.percentage = percents
            self.scrolling = False
            
    def __init__(self, size: NvVector2 | list, style: Style = default_style, content: list[tuple[Align, NevuObject]] | None = None, **constant_kwargs):
        super().__init__(size, style, **constant_kwargs)
        self._lazy_kwargs = {'size': size, 'content': content}
        
    def _init_test_flags(self):
        super()._init_test_flags()
        self._test_debug_print = False
        self._test_rect_calculation = True
        self._test_always_update = False
        
    def _init_numerical(self):
        super()._init_numerical()
        self.max_secondary = 0
        self.max_main = 0
        self.actual_max_main = 1
        self.padding = 30
        
    def _init_lists(self):
        super()._init_lists()
        self.widgets_alignment = []
        self._coordinates = NvVector2()
        
    @property
    def coordinates(self):
        return self._coordinates
    @coordinates.setter
    def coordinates(self, value: NvVector2):
        self._coordinates = value
        self.cached_coordinates = None
        if self.booted == False: return
        self._update_scroll_bar()
        
    def _add_constants(self):
        super()._add_constants()
        self._add_constant('arrow_scroll_power', int, 5)
        self._add_constant('wheel_scroll_power', int, 5)
        self._add_constant('inverted_scrolling', bool, False)
        
    def _lazy_init(self, size: NvVector2 | list, content: list[tuple[Align, NevuObject]] | None = None):
        super()._lazy_init(size, content)
        self.original_size = self.size.copy()
        self._init_scroll_bar()
        if content and isinstance(self, ScrollableBase):
            for mass in content:
                assert len(mass) == 2
                align, item = mass
                assert type(align) == Align and isinstance(item, NevuObject)
                self.add_item(item, align)
        self._update_scroll_bar()
        
    def _update_scroll_bar(self):
        pass
    
    def _init_scroll_bar(self):
        if self._test_debug_print:
            print(f"in {self} used init scroll bars")
            
        self.scroll_bar = self._create_scroll_bar()
        assert self.scroll_bar, "You CANT use ScrollableBase"
        self._boot_scrollbar(self.scroll_bar)

    def _boot_scrollbar(self, scroll_bar: ScrollBar):
        scroll_bar.subtheme_role = SubThemeRole.TERTIARY
        scroll_bar._boot_up()
        scroll_bar._init_start()
        scroll_bar.booted = True
        
    def _create_scroll_bar(self) -> ScrollBar:
        return None # type: ignore
        
    def _connect_to_layout(self, layout: LayoutType):
        if self._test_debug_print:
            print(f"in {self} used connect to layout: {layout}")
            
        super()._connect_to_layout(layout)
        
    def _connect_to_menu(self, menu: Menu):
        if self._test_debug_print:
            print(f"in {self} used connect to menu: {menu}")
            
        super()._connect_to_menu(menu)
        assert self.menu is not None
        need_resize = False
        if menu.size[0] < self.size[0]:
            self.size[0] = menu.size[0]
            need_resize = True
        if menu.size[1] < self.size[1]:
            self.size[1] = menu.size[1]
            need_resize = True
        if need_resize:
            self.menu._set_layout_coordinates(self)
            
    def _is_widget_drawable(self, item: NevuObject):
        if self._test_debug_print:
            print(f"in {self} used is drawable for", item)
            
        item_rect = item.get_rect()
        self_rect = self.get_rect()
        return bool(item_rect.colliderect(self_rect))
    
    def _is_widget_drawable_optimized(self, item: NevuObject):
        raise DeprecationWarning("Not supported anymore, use _is_widget_drawable instead")
    
    def secondary_draw(self):
        if self._test_debug_print: print(f"Used secondary_draw in {self}")
            
        super().secondary_draw()
        for item in self.items:
            assert isinstance(item, (Widget, LayoutType))
            if drawable := self._is_widget_drawable(item):
                self._draw_widget(item)
            
        if self.actual_max_main > 0:
            self._draw_widget(self.scroll_bar)
            
    def _set_item_main(self, item: NevuObject, align: Align):
        pass
    
    def get_offset(self) -> int | float:
        percentage = self.scroll_bar.percentage
        return self.actual_max_main / 100 * percentage
    
    def secondary_update(self): 
        if self._test_debug_print:
            print(f"in {self} used update")
            for name, data in self.__dict__.items(): print(f"{name}: {data}")
            
        super().secondary_update()
        self.base_light_update()    
        
        if self.actual_max_main > 0:
            self.scroll_bar.update()
            self.scroll_bar.coordinates = self._get_scrollbar_coordinates() # type: ignore
            self.scroll_bar.master_coordinates = self._get_item_master_coordinates(self.scroll_bar)
            self.scroll_bar._master_z_handler = self._master_z_handler
        if type(self) == ScrollableBase: self._dirty_rect = self._read_dirty_rects()
    
    def _get_scrollbar_coordinates(self): 
        return
    
    def _regenerate_coordinates(self):
        pass
            
    def logic_update(self):
        super().logic_update()
        inverse = -1 if self.inverted_scrolling else 1
        with contextlib.suppress(Exception):
            if keyboard.is_fdown(self.append_key):
                self.scroll_bar.move_by_percents(self.arrow_scroll_power * -inverse)
            if keyboard.is_fdown(self.descend_key):
                self.scroll_bar.move_by_percents(self.arrow_scroll_power * inverse)
            
    def _on_scroll_system(self, side: bool):
        super()._on_scroll_system(side)

        direction = 1 if side else -1

        if self.inverted_scrolling:
            direction *= -1
        self.scroll_bar.move_by_percents(self.wheel_scroll_power * direction)
            
    def resize(self, resize_ratio: NvVector2):
        if self._test_debug_print:
            print(f"in {self} used resize, current ratio: {resize_ratio}")
            
        prev_percentage = self.scroll_bar.percentage if hasattr(self, "scroll_bar") else 0.0

        super().resize(resize_ratio)
        self.scroll_bar.resize(resize_ratio)
        self._resize_scrollbar()
        
        self.cached_coordinates = None
        self._regenerate_coordinates()
        
        self.scroll_bar.scrolling = False
        self._update_scroll_bar()
        new_actual_max_main = self.actual_max_main

        if new_actual_max_main > 0:
            new_percentage = max(0.0, min(prev_percentage, 100.0))
        else:
            new_percentage = 0.0

        self.scroll_bar.set_percents(new_percentage)
        self.base_light_update()

    def base_light_update(self, add_x: int | float = 0, add_y: int | float = 0): # type: ignore
        super().base_light_update(add_x, add_y)
    
    def _resize_scrollbar(self):
        pass
    
    def _event_on_add_item(self):
        if self._test_debug_print:
            print(f"in {self} used event on add widget")
        
        self.cached_coordinates = None
        if self.booted == False: return
        self._init_scroll_bar()
        self._update_scroll_bar()

    def _regenerate_max_values(self):
        pass
    
    def add_item(self, item: NevuObject, alignment: Align): # type: ignore
        if not self._parse_align(alignment): return
        if not self._test_debug_print:
            print(f"in {self} added widget: {item} at {alignment}.")
            
        if item.single_instance is False: item = item.clone()
        item._master_z_handler = self._master_z_handler
        self.read_item_coords(item)
        self._start_item(item)
        self.items.append(item)
        self.widgets_alignment.append(alignment)

        self._event_on_add_item()
        
        if self.layout:
            self.layout._event_on_add_item()
    
    def _parse_align(self, align: Align):
        pass

    def clear(self):
        self.items.clear()
        self.widgets_alignment.clear()
        self._restart_coordinates()

    def _restart_coordinates(self):
        pass

    def apply_style_to_childs(self, style: Style):
        super().apply_style_to_childs(style)
        self._apply_style_to_scroll_bar(style)
    
    def _apply_style_to_scroll_bar(self, style: Style):
        self.scroll_bar.style = style
