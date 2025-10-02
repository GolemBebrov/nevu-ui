import pygame
import copy

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

class Scrollable(LayoutType):
    arrow_scroll_power: float | int
    wheel_scroll_power: float | int
    inverted_scrolling: bool
    """A highly configurable layout that provides scrollable containers for content
    that exceeds its visible boundaries.

    This class creates a scrollable area with a vertical scrollbar, allowing for the
    display of a large number of widgets. It is designed to be highly customizable,
    offering control over scroll speed, direction, and behavior.

    The component is built on top of the base `LayoutType` and uses a nested
    `ScrollBar` widget to manage the scrolling logic. It leverages the custom

    `Mouse` and `Keyboard` APIs for clean, high-level input handling.

    :param size: The size of the scrollable area, as a `NvVector2`, `list`, or `tuple`.
    :param style: The `Style` object that defines the appearance of the layout and
                  its scrollbar. Defaults to `default_style`.
    :param content: An optional initial list of widgets to add to the layout. Each
                    item should be a tuple of `(Align, NevuObject)`. Defaults to `None`.
    :param draw_scroll_area: If `True`, draws a debug rectangle around the scrollable
                             area. Defaults to `False`.
    :param id: An optional string identifier for the object. Defaults to `None`.
    :param arrow_scroll_power: The percentage to scroll when an arrow key is pressed.
                               Defaults to `5`.
    :param wheel_scroll_power: The percentage to scroll per one "tick" of the mouse
                               wheel. Defaults to `5`.
    :param inverted_scrolling: If `True`, inverts the direction of the mouse wheel and
                               arrow key scrolling. Defaults to `False`.

    **Nested Class:**

    * `ScrollBar`: A private widget class that implements the logic and visuals for
                   the scroll handle and track. It operates on a percentage-based
                   system for maximum flexibility.

    **Key Features:**

    * **Configurable Input:** Fully adjustable scroll speed for keyboard arrows and
      the mouse wheel, including inverted scrolling.
    * **Robust Scrolling Logic:** Utilizes a nested `ScrollBar` with a percentage-based
      positioning system that is resilient to resizing.
    * **Performance-Oriented:** Caches widget coordinates and only recalculates them
      when necessary to ensure high performance.
    * **Clean API:** Manages complex scrolling logic internally, exposing simple
      methods like `add_item()` and `clear()`.

    **Usage Example:**
    
    .. code-block:: python

        # Create a scrollable layout with inverted scrolling and fast wheel speed
        my_scroll_area = Scrollable(
            size=(300, 400),
            style=my_custom_style,
            wheel_scroll_power=10,
            inverted_scrolling=True
        )

        # Add widgets to the scrollable area
        #for i in range(20):
            #label = Label(text=f"Item #{i+1}")
            #my_scroll_area.add_item(label, alignment=Align.CENTER)
    """
    class ScrollBar(Widget):
        def __init__(self, size, style, orientation: ScrollBarType, master = None):
            super().__init__(size, style)
            self.z = 100
            if not isinstance(master, Scrollable):
                print("WARNING: this class is intended to be used in Scrollable layout.")
            
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
            
    def __init__(self, size: NvVector2 | list, style: Style = default_style, content: tuple[list[Align | NevuObject]] | None = None, **constant_kwargs):
        super().__init__(size, style, **constant_kwargs)
        self._lazy_kwargs = {'size': size, 'content': content}
        
    def _init_test_flags(self):
        super()._init_test_flags()
        self._test_debug_print = False
        self._test_rect_calculation = True
        self._test_always_update = False
        
    def _init_numerical(self):
        super()._init_numerical()
        self.max_x = 0
        self.max_y = 0
        self.actual_max_y = 1
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
        self._update_scroll_bars()
        
    def _add_constants(self):
        super()._add_constants()
        self._add_constant('arrow_scroll_power', int, 5)
        self._add_constant('wheel_scroll_power', int, 5)
        self._add_constant('inverted_scrolling', bool, False)
        
    def _lazy_init(self, size: NvVector2 | list, content: list[tuple[Align, NevuObject]] | None = None):
        super()._lazy_init(size, content)
        self.original_size = self.size.copy()
        self.__init_scroll_bars__()
        if content and type(self) == Scrollable:
            for mass in content:
                assert len(mass) == 2
                align, item = mass
                #print(align, item)
                assert type(align) == Align and isinstance(item, NevuObject)
                self.add_item(item, align)
        self._update_scroll_bars()
        
    def _update_scroll_bars(self):
        if self._test_debug_print:
            print("used first update bars")
        
        track_start_y = self.master_coordinates[1]
        track_path_y = self.size[1]
        offset = NvVector2(self.first_parent_menu.window._crop_width_offset,self.first_parent_menu.window._crop_height_offset) if self.first_parent_menu.window else NvVector2(0,0)
        #print(offset)
        self.scroll_bar_y.set_scroll_params(NvVector2(self.coordinates[0] + self.relx(self.size[0] - self.scroll_bar_y.size[0]) , track_start_y), 
                                            NvVector2(0,track_path_y),
                                            offset/2)

        #------ TODO ------
        #track_start_x = self._coordinates[0] + self.first_parent_menu.coordinatesMW[0]
        #track_length_x = self.size[0]
        #self.scroll_bar_x.set_scroll_params(track_start_x, track_length_x) #old code
        
    def __init_scroll_bars__(self):
        if self._test_debug_print:
            print(f"in {self} used init scroll bars")
        self.scroll_bar_y = self.ScrollBar([self.size[0]/40,self.size[1]/20], self.style, ScrollBarType.Vertical, self)
        self.scroll_bar_y.subtheme_role = SubThemeRole.TERTIARY
        #self.scroll_bar_x = self.ScrollBar([self.size[0]/20,self.size[1]/40],default_style(bgcolor=(100,100,100)), 'horizontal', self)
        self.scroll_bar_y._boot_up()
        self.scroll_bar_y._init_start()
        self.scroll_bar_y.booted = True
        #self.scroll_bar_x._boot_up()
        #self.scroll_bar_x._init_start()
        
    def _connect_to_layout(self, layout: LayoutType):
        
        if self._test_debug_print:
            print(f"in {self} used connect to layout: {layout}")
        super()._connect_to_layout(layout)
        #self.__init_scroll_bars__()
        
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
        #if self._test_debug_print:
        #    print("in {self} used is drawable optimized(test) for", item)
        #overdose_right = item.coordinates[0] + self.relx(item._anim_coordinates[0]) > self.coordinates[0] + self.size[0]
        #overdose_left = item.coordinates[0] + self.relx(item._anim_coordinates[0] + item.size[0]) < self.coordinates[0]
        #overdose_bottom = item.coordinates[1] + self.rely(item._anim_coordinates[1]) > self.coordinates[1] + self.size[1]
        #overdose_top = item.coordinates[1] + self.rely(item._anim_coordinates[1] + item.size[1]) < self.coordinates[1]
        #overall = overdose_right or overdose_left or overdose_bottom or overdose_top
        #return not overall
    
    def secondary_draw(self):
        if self._test_debug_print:
            print("used draw")
        super().secondary_draw()
        for item in self.items:
            assert isinstance(item, (Widget, LayoutType))
            drawable = self._is_widget_drawable(item) if self._test_rect_calculation else self._is_widget_drawable_optimized(item)
            if drawable: self._draw_widget(item)
        if self.actual_max_y > 0:
            self._draw_widget(self.scroll_bar_y)
            
    def _set_item_x(self, item: NevuObject, align: Align):
        container_width = self.relx(self.size[0])
        widget_width = self.relx(item.size[0])
        padding = self.relx(self.padding)

        match align:
            case Align.LEFT:
                item.coordinates.x = self._coordinates.x + padding
            case Align.RIGHT:
                item.coordinates.x = self._coordinates.x + (container_width - widget_width - padding)
            case Align.CENTER:
                item.coordinates.x = self._coordinates.x + (container_width / 2 - widget_width / 2)
    
    def get_offset(self) -> int | float:
        percentage = self.scroll_bar_y.percentage
        return self.actual_max_y / 100 * percentage
    
    def secondary_update(self): 
        if self._test_debug_print:
            print(f"in {self} used update")
            for name, data in self.__dict__.items():
                print(f"{name}: {data}")
        super().secondary_update()
        offset = self.get_offset()
        self._light_update(0, -offset)    
        
        if self.actual_max_y > 0:
            self.scroll_bar_y.update()
            self.scroll_bar_y.coordinates = NvVector2(self._coordinates.x + self.relx(self.size.x - self.scroll_bar_y.size.x), self.scroll_bar_y.coordinates.y)
            self.scroll_bar_y.master_coordinates = self._get_item_master_coordinates(self.scroll_bar_y)
            self.scroll_bar_y._master_z_handler = self._master_z_handler
        if type(self) == Scrollable: self._dirty_rect = self._read_dirty_rects()
            
    def _regenerate_coordinates(self):
        super()._regenerate_coordinates()
        self.cached_coordinates = []
        self._regenerate_max_values()
        padding_offset = self.rely(self.padding)
        for i in range(len(self.items)):
            item, align = self.items[i], self.widgets_alignment[i]
            
            self._set_item_x(item, align)
            item.coordinates.y = self._coordinates.y + padding_offset
            self.cached_coordinates.append(item.coordinates)
            item.master_coordinates = self._get_item_master_coordinates(item)
            padding_offset += item._csize.y + self.rely(self.padding)
            
    def logic_update(self):
        super().logic_update()
        inverse = -1 if self.inverted_scrolling else 1
        if keyboard.is_fdown(pygame.K_UP):
            self.scroll_bar_y.move_by_percents(self.arrow_scroll_power * -inverse)
        if keyboard.is_fdown(pygame.K_DOWN):
            self.scroll_bar_y.move_by_percents(self.arrow_scroll_power * inverse)
            
    def _on_scroll_system(self, side: bool):
        super()._on_scroll_system(side)

        direction = 1 if side else -1

        if self.inverted_scrolling:
            direction *= -1
        self.scroll_bar_y.move_by_percents(self.wheel_scroll_power * direction)
            
    def resize(self, resize_ratio: NvVector2):
        if self._test_debug_print:
            print(f"in {self} used resize, current ratio: {resize_ratio}")
        prev_percentage = self.scroll_bar_y.percentage if hasattr(self, "scroll_bar_y") else 0.0

        if hasattr(self, "scroll_bar_y"):
            self.scroll_bar_y.scrolling = False

        super().resize(resize_ratio)
        self.scroll_bar_y.resize(resize_ratio)
        self.scroll_bar_y.coordinates.y = self.rely(self.scroll_bar_y.size.y)
        
        self.cached_coordinates = None
        self._regenerate_coordinates()
        
        self.scroll_bar_y.scrolling = False
        self._update_scroll_bars()
        new_actual_max_y = self.actual_max_y if hasattr(self, "actual_max_y") else 1

        if new_actual_max_y > 0:
            new_percentage = max(0.0, min(prev_percentage, 100.0))
        else:
            new_percentage = 0.0

        self.scroll_bar_y.set_percents(new_percentage)
        self._light_update(0, -self.get_offset())

    def _event_on_add_item(self):
        self.cached_coordinates = None
        if self._test_debug_print:
            print(f"in {self} used event on add widget")
        if self.booted == False: return
        self.__init_scroll_bars__()
        self._update_scroll_bars()

    def _regenerate_max_values(self):
        total_content_height = self.rely(self.padding)
        for item in self.items:
            total_content_height += self.rely(item.size[1]) + self.rely(self.padding)
            
        visible_height = self.rely(self.size[1])
        
        self.actual_max_y = max(0, total_content_height - visible_height)

    def add_item(self, item: NevuObject, alignment: Align = Align.LEFT):
        """Adds a widget to the scrollable layout with the specified alignment.

        This method inserts a new item into the scrollable area, updates the
        internal list of items and alignments, and recalculates the scrollable
        region to accommodate the new widget.

        Args:
            item: The widget to add to the scrollable layout.
            alignment: The alignment for the widget (e.g., Align.LEFT, Align.CENTER, Align.RIGHT).

        Returns:
            None
        """
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
            
    def clear(self):
        self.items.clear()
        self.widgets_alignment.clear()
        self.max_x = 0
        self.max_y = self.padding
        self.actual_max_y = 0

    def apply_style_to_childs(self, style: Style):
        super().apply_style_to_childs(style)
        self.scroll_bar_y.style = style

    def clone(self):
        return Scrollable(self._lazy_kwargs['size'], copy.deepcopy(self.style), self._lazy_kwargs['content'], **self.constant_kwargs)
