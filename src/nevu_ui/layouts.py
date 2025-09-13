import pygame
import numpy as np
import copy
from .widgets import Vector2
from .style import Style,Align
from .widgets import *
from .menu import Menu
from .nevuobj import NevuObject
from .fast_logic import _light_update_helper
import typing
from .core_types import (
    SizeRule, Vh, Vw, Fill
)
default_style = Style()

class LayoutType(NevuObject):
    items: list[NevuObject]
    freedom_items: list[NevuObject]
    def _get_item_master_coordinates(self, item: NevuObject):
        return Vector2(item.coordinates[0] + self.first_parent_menu.coordinatesMW[0], item.coordinates[1] + self.first_parent_menu.coordinatesMW[1])

    def _draw_widget(self, item: NevuObject, multiply: NvVector2 | None = None, add: NvVector2 | None = None):
        if not isinstance(item, (LayoutType, Widget)) or not isinstance(self.surface, pygame.Surface): return
        if item._wait_mode:
            self.read_item_coords(item)
            self._start_item(item)
            #("started item", item)
            return
        item.draw()
        if self.is_layout(item) or not isinstance(item.surface, pygame.Surface): return
        coordinates = item.coordinates
        if multiply: coordinates = coordinates * multiply
        if add: coordinates = coordinates + add
        self.surface.blit(item.surface, (int(coordinates[0]),int(coordinates[1])))

    def _boot_up(self):
        #print("booted layout", self)
        self.booted = True
        for item in self.items + self.freedom_items:
            assert isinstance(item, (Widget, LayoutType))
            item.booted = True
            self.read_item_coords(item)
            item._boot_up()

            self._start_item(item)

    @property
    def _rsize(self) -> NvVector2:
        bw = self.menu.style.borderwidth if self.menu else self.first_parent_menu.style.borderwidth
        return self._csize - NvVector2(bw, bw) if self.menu else self._csize

    @property
    def _rsize_marg(self) -> NvVector2:
        bw = self.menu.style.borderwidth if self.menu else self.first_parent_menu.style.borderwidth
        bw = int(self.relm(bw))
        if self.menu: return (self._csize - (self._csize - Vector2(bw,bw)))/2
        return NvVector2(0,0)

    def __init__(self, size: NvVector2 | list, style: Style = default_style, content: list | None  = None, **constant_kwargs):
        super().__init__(size, style, **constant_kwargs)
        self._lazy_kwargs = {'size': size, 'content': content}
        self.border_name = " "
        
    def _init_lists(self):
        super()._init_lists()
        self.freedom_items = []
        self.items = []
        self.cached_coordinates = None
        self.all_layouts_coords = [0,0]
        
    def _init_booleans(self):
        super()._init_booleans()
        self._can_be_main_layout = True
        self._borders = False
        
    def _init_objects(self):
        super()._init_objects()
        self.first_parent_menu = Menu(None, (1,1), default_style)
        self.menu = None
        self.layout = None
        self.surface = None
        
    def _lazy_init(self, size: NvVector2 | list, content: list | None = None):
        super()._lazy_init(size)
        if content and type(self) == LayoutType:
            for i in content:
                self.add_item(i)

    def _light_update(self, add_x: int | float = 0, add_y: int | float = 0 ):
        _light_update_helper(
            self.items,
            self.cached_coordinates,
            self.first_parent_menu,
            self.relx,
            self.rely,
            add_x,
            add_y
        )

    @property
    def coordinates(self): return self._coordinates
    @coordinates.setter
    def coordinates(self, value):
        self._coordinates = value
        self.cached_coordinates = None

    @property
    def borders(self):return self._borders
    @borders.setter
    def borders(self,bool: bool): self._borders = bool

    @property
    def border_name(self) -> str: return self.border_name
    @border_name.setter
    def border_name(self, name: str):
        self._border_name = name
        if self.first_parent_menu:
            try:
                self.border_font = pygame.sysfont.SysFont("Arial", int(self.first_parent_menu._style.fontsize*self._resize_ratio.x))
                self.border_font_surface = self.border_font.render(self._border_name, True, (255,255,255))
            except Exception as e: print(e)

    def _convert_item_coord(self, coord, i: int = 0):
        if not isinstance(coord, SizeRule):
            return coord, False
        if isinstance(coord, (Vh, Vw)):
            if self.first_parent_menu is None: raise ValueError(f"Cant use Vh or Vw in unconnected layout {self}")
            if self.first_parent_menu.window is None: raise ValueError(f"Cant use Vh or Vw in uninitialized layout {self}")
            if type(coord) == Vh: return self.first_parent_menu.window.size[1]/100 * coord.value, True
            elif type(coord) == Vw: return self.first_parent_menu.window.size[0]/100 * coord.value, True
        elif type(coord) == Fill: return self._rsize[i]/ 100 * coord.value, True
        return coord, False

    def read_item_coords(self, item: NevuObject):
        if self.booted == False: return
        w_size = item._lazy_kwargs['size']
        x, y = w_size
        x, is_x_rule = self._convert_item_coord(x, 0)
        y, is_y_rule = self._convert_item_coord(y, 1)

        item._lazy_kwargs['size'] = [x,y]

    def _start_item(self, item: NevuObject):
        if isinstance(item, LayoutType):
            item._connect_to_layout(self)
        if self.booted == False:  return
        item._wait_mode = False; item._init_start()

    def resize(self, resize_ratio: NvVector2):
        super().resize(resize_ratio)
        self.cached_coordinates = None
        for item in self.items + self.freedom_items:
            assert isinstance(item, (Widget, LayoutType))
            item.resize(self._resize_ratio)
        self.border_name = self._border_name

    @staticmethod
    def is_layout(item: NevuObject) -> typing.TypeGuard['LayoutType']:
        return isinstance(item, LayoutType)
    
    @staticmethod
    def is_widget(item: NevuObject) -> typing.TypeGuard['Widget']:
        return isinstance(item, Widget)
    
    def _event_on_add_item(self): pass

    def add_item(self, item: NevuObject):
        #print(item)
        if item.single_instance is False: item = item.clone()
        if self.is_layout(item): 
            assert self.is_layout(item)
            item._connect_to_layout(self)
        elif self.is_widget(item):
            self.read_item_coords(item)
            self._start_item(item)
            if item.floating: 
                self.freedom_items.append(item)
            else:
                self.items.append(item)
            return
        self.read_item_coords(item)
        self._start_item(item)
        self.items.append(item)
        self.cached_coordinates = None
        return item

    def apply_style_to_childs(self, style: Style):
        for item in self.items:
            assert isinstance(item, (Widget, LayoutType))
            if self.is_widget(item): 
                item.style = style
            elif self.is_layout(item): 
                item.apply_style_to_childs(style)

    def primary_draw(self):
        super().primary_draw()
        if self.borders and hasattr(self, "border_font_surface"):
            #sschc = [1,1] if self.layout!=None else self._resize_ratio
            assert self.surface
            self.surface.blit(self.border_font_surface, [self.coordinates[0], self.coordinates[1]-self.border_font_surface.get_height()])
            pygame.draw.rect(self.surface,(255,255,255),[self.coordinates[0], self.coordinates[1],int(self.size[0]*self._resize_ratio[0]),int(self.size[1]*self._resize_ratio[1])],1)
        for item in self.freedom_items: #+ self.items:
            self._draw_widget(item, item.coordinates * self._resize_ratio)

    def _read_dirty_rects(self):
        dirty_rects = []
        for item in self.items + self.freedom_items:
            assert isinstance(item, (Widget, LayoutType))
            if len(item._dirty_rect) > 0:
                dirty_rects.extend(item._dirty_rect)
                item._dirty_rect = []
        return dirty_rects

    def secondary_update(self):
        super().secondary_update()
        if self.menu:self.surface = self.menu.surface;self.all_layouts_coords = [0,0]
        elif self.layout: self.surface = self.layout.surface;self.all_layouts_coords = [self.layout.all_layouts_coords[0]+self.coordinates[0],self.layout.all_layouts_coords[1]+self.coordinates[1]];self.first_parent_menu = self.layout.first_parent_menu
        for item in self.freedom_items:
            item.master_coordinates = Vector2(item.coordinates[0]+self.first_parent_menu.coordinatesMW[0],item.coordinates[1]+self.first_parent_menu.coordinatesMW[1])
            item.update()
        if self.cached_coordinates is None and self.booted:
            self._regenerate_coordinates()
        if type(self) == LayoutType: self._dirty_rect = self._read_dirty_rects()
    def _regenerate_coordinates(self):
        for item in self.items + self.freedom_items:
            if item._wait_mode:
                self.read_item_coords(item)
                self._start_item(item)
                #print("started item", item)
                return
    def _connect_to_menu(self, menu: Menu):
        #print(f"in {self} used connect to menu: {menu}")
        self.cached_coordinates = None
        self.menu = menu
        self.surface = self.menu.surface
        self.first_parent_menu = menu
        self.border_name = self._border_name

    def _connect_to_layout(self, layout):
        #print(f"in {self} used connect to layout: {layout}")
        self.surface = layout.surface
        self.layout = layout
        self.first_parent_menu = layout.first_parent_menu
        self.border_name = self._border_name
        self.cached_coordinates = None

    def get_item_by_id(self, id: str) -> NevuObject | None:
        mass = self.items + self.freedom_items
        if id is None: return None
        return next((item for item in mass if item.id == id), None)
    def clone(self):
        return LayoutType(self._lazy_kwargs['size'], copy.deepcopy(self.style), self._lazy_kwargs['content'], **self.constant_kwargs)

class Grid(LayoutType):
    row: int | float
    column: int | float
    def __init__(self, size: NvVector2 | list, style: Style = default_style, content: dict[tuple[int] , NevuObject] | None = None, **constant_kwargs):
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
                
            coordinates = Vector2(self.coordinates[0] + self._rsize_marg[0] + x * cw + (cw - self.relx(item.size[0])) / 2 ,
                           self.coordinates[1] + self._rsize_marg[1] +y * ch + (ch -  self.rely(item.size[1])) / 2)
            item.coordinates = coordinates
            item.master_coordinates = self._get_item_master_coordinates(item)
            self.cached_coordinates.append(coordinates)
            
    def secondary_update(self, *args):
        super().secondary_update()
        self._light_update()
        if type(self) == Grid: self._dirty_rect = self._read_dirty_rects()
        
    def add_item(self, item: NevuObject, x: int, y: int):  # type: ignore
        range_error = ValueError("Grid index out of range x: {x}, y: {y} ".format(x=x,y=y)+f"Grid size: {self.column}x{self.row}")
        if x > self.column or y > self.row or x < 1 or y < 1: raise range_error
        for coordinates in self.grid_coordinates:
            if coordinates == (x-1, y-1): raise ValueError("Grid item already exists")
        self.grid_coordinates.append((x-1,y-1))
        super().add_item(item)
        if self.layout: self.layout._event_on_add_item()

    def secondary_draw(self):
        super().secondary_draw()
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

class Row(Grid):
    def __init__(self, size: NvVector2 | list, style: Style = default_style, content: dict[int , NevuObject] | None = None, **constant_kwargs):
        super().__init__(size, style, None, **constant_kwargs)
        self._lazy_kwargs = {'size': size, 'content': content}
        
    def _add_constants(self):
        super()._add_constants()
        self._block_constant("row")
        
    def _lazy_init(self, size: NvVector2 | list, content: dict[int , NevuObject] | None = None): # type: ignore
        super()._lazy_init(size)
        self.cell_height = self.size[1] / self.row
        self.cell_width = self.size[0] / self.column
        if not content:
            return
        for xcoord, item in content.items():
            self.add_item(item, xcoord)
    def clone(self):
        return Row(self._lazy_kwargs['size'], copy.deepcopy(self.style), self._lazy_kwargs['content'], **self.constant_kwargs)
            
    def add_item(self, item: NevuObject, x: int): # type: ignore
        return super().add_item(item, x, 1)
    
    def get_item(self, x: int) -> NevuObject | None: # type: ignore
        return super().get_item(x, 1)

class Column(Grid):
    def __init__(self, size: NvVector2 | list, style: Style = default_style, content: dict[int , NevuObject] | None = None, **constant_kwargs):
        super().__init__(size, style, None, **constant_kwargs)
        self._lazy_kwargs = {'size': size, 'content': content}
        
    def _add_constants(self):
        super()._add_constants()
        self._block_constant("column")
        
    def _lazy_init(self, size: NvVector2 | list, content: dict[int , NevuObject] | None = None): # type: ignore
        super()._lazy_init(size)
        self.cell_height = self.size[1] / self.row
        self.cell_width = self.size[0] / self.column
        if not content:
            return
        for ycoord, item in content.items():
            self.add_item(item, ycoord)
            
    def add_item(self, item: NevuObject, y: int): # type: ignore
        return super().add_item(item, 1, y)
    
    def get_item(self, y: int) -> NevuObject | None: # type: ignore
        return super().get_item(1, y)
    def clone(self):
        return Column(self._lazy_kwargs['size'], copy.deepcopy(self.style), self._lazy_kwargs['content'], **self.constant_kwargs)

            
class IntPickerGrid(Grid):
    def __init__(self, amount_of_colors: int = 3, item_size: int = 50, y_size: int = 50, margin:int = 0, title: str = "", 
                 color_widget_style: Style = default_style, title_label_style: Style = default_style, on_change_function=None):
        if amount_of_colors <= 0: raise Exception("Amount of colors must be greater than 0")
        if item_size <= 0: raise Exception("Item size must be greater than 0")
        if margin < 0: raise Exception("Margin must be greater or equal to 0")
        self._widget_line = 1
        if title.strip() != "": self._widget_line = 2
        self.size = (amount_of_colors*item_size+margin*(amount_of_colors-1), y_size*self._widget_line+margin*(self._widget_line-1))
        self.on_change_function = on_change_function  
        super().__init__(self.size,amount_of_colors,self._widget_line)
        for i in range(amount_of_colors): 
            self.add_item(Input((item_size,y_size),color_widget_style(text_align_x=Align.CENTER),"","0",None,Input_Type.NUMBERS,on_change_function=self._return_colors,max_characters=3),i+1,self._widget_line)
        if self._widget_line == 2:
            if amount_of_colors % 2 == 0: offset = 0.5
            else: offset = 1
            self.label = Label((self.size[0],y_size),title,title_label_style(text_align_x=Align.CENTER))
            self.add_item(self.label,amount_of_colors//2+offset,1)
    def _return_colors(self, *args):
        c = self.get_color()
        if self.on_change_function: self.on_change_function(c)
    def get_color(self) -> tuple:
        c = []
        for item in self.items: 
            if isinstance(item,Input): c.append(int(item.text))
        return tuple(c)
    def set_color(self, color: tuple|list):
        for i in range(len(color)):
            if i == len(self.items): break
            self.items[i].text = str(color[i])
class Pages(LayoutType):
    def __init__(self, size: list | NvVector2, style: Style = default_style, content: list | None = None, **constant_kwargs):
        super().__init__(size, style, content, **constant_kwargs)
        self.selected_page = None
        self.selected_page_id = 0
    def _lazy_init(self, size: NvVector2 | list, content: list | None = None):
        super()._lazy_init(size, content)
        if content:
            for item in content:
                self.add_item(item)
    def add_item(self, item: LayoutType): # type: ignore
        if self.is_widget(item): raise ValueError("Widget must be Layout")
        super().add_item(item)
        if self.layout: self.layout._event_on_add_item()
        if not self.selected_page:
            self.selected_page = item
            self.selected_page_id = 0
    def secondary_draw(self):
        super().secondary_draw()
        assert self.surface
        pygame.draw.line(self.surface,(0,0,0),[self.coordinates[0]+self.relx(10),self.coordinates[1]+self.rely(20)],[self.coordinates[0]+self.relx(40),self.coordinates[1]+self.rely(20)],2)
        pygame.draw.line(self.surface,(0,0,0),[self.coordinates[0]+self.relx(10),self.coordinates[1]+self.rely(20)],[self.coordinates[0]+self.relx(20),self.coordinates[1]+self.rely(40)],2)
        
        self.items[self.selected_page_id].draw()
        for i in range(len(self.items)):
            if i != self.selected_page_id: pygame.draw.circle(self.surface,(0,0,0),[self.coordinates[0]+self.relx(20+i*20),self.coordinates[1]+self.rely(self.size[1]-10)],self.relm(5))
            else: pygame.draw.circle(self.surface,(255,0,0),[self.coordinates[0]+self.relx(20+i*20),self.coordinates[1]+self.rely(self.size[1]-10)],self.relm(5))
    def move_by_point(self, point: int):
        self.selected_page_id += point
        if self.selected_page_id < 0: self.selected_page_id = len(self.items)-1
        self.selected_page = self.items[self.selected_page_id]
        if self.selected_page_id >= len(self.items): self.selected_page_id = 0
        self.selected_page = self.items[self.selected_page_id]
    def get_left_rect(self):
        return pygame.Rect(self.coordinates[0]+(self.first_parent_menu.coordinatesMW[0]),self.coordinates[1]+self.first_parent_menu.coordinatesMW[1],
                           self.relx(self.size[0]/10),self.rely(self.size[1]))
    def get_right_rect(self):
        return pygame.Rect(self.coordinates[0]+self.relx(self.size[0]-self.size[0]/10)+self.first_parent_menu.coordinatesMW[0],self.coordinates[1]+self.first_parent_menu.coordinatesMW[1],
                           self.relx(self.size[0]/10),self.rely(self.size[1]))
    def secondary_update(self, *args):
        super().secondary_update()
        if mouse.left_fdown:
            rectleft = self.get_left_rect()
            rectright = self.get_right_rect()
            if rectleft.collidepoint(mouse.pos): self.move_by_point(-1)
            if rectright.collidepoint(mouse.pos): self.move_by_point(1)
        selected_page = self.items[self.selected_page_id]
        assert isinstance(selected_page, LayoutType)
        selected_page.coordinates = [self.coordinates[0]+self.relx(self.size[0]/2-self.items[self.selected_page_id].size[0]/2),
                                                         self.coordinates[1]+self.rely(self.size[1]/2-self.items[self.selected_page_id].size[1]/2),]
        selected_page.first_parent_menu = self.first_parent_menu
        if not selected_page.booted: selected_page._boot_up()
        selected_page.update()
        
    def get_selected(self): return self.items[self.selected_page_id]
    
    def clone(self):
        return Pages(self._lazy_kwargs['size'], copy.deepcopy(self.style), self._lazy_kwargs['content'], **self.constant_kwargs)
class Gallery_Pages(Pages):
    def __init__(self, size: Vector2 | list):
        super().__init__(size)
        
    def add_item(self, item: Widget): # type: ignore
        if self.is_layout(item): raise ValueError("Widget must not be Layout, layout creates automatically")
        if isinstance(item, (ImageWidget, GifWidget)):
            g = Grid(self.size)
            g.add_item(item, 1, 1)
            super().add_item(g)

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

    :param size: The size of the scrollable area, as a `Vector2`, `list`, or `tuple`.
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
        def __init__(self, size, style, orientation: str, master = None):
            super().__init__(size, style)

            if not isinstance(master, Scrollable):
                print("WARNING: this class is intended to be used in Scrollable layout.")
            
            self.master = master
            
            if orientation not in ['vertical', 'horizontal']:
                raise ValueError("Orientation must be 'vertical' or 'horizontal'")
            self.orientation = orientation
            
            self.is_scrolling = False
            self.offset = Vector2(0, 0)
            self._percentage = 0.0
        
            self.track_start_coordinates = Vector2(0, 0)
            self.track_path = Vector2(0, 0)

        @property
        def percentage(self) -> float:
            axis = 1 if self.orientation == 'vertical' else 0
            scaled_track_path_val = (self.track_path[axis] * self._resize_ratio[axis]) - self.rel(self.size)[axis]
            
            if scaled_track_path_val == 0:
                return 0.0
                
            start_coord = self.track_start_coordinates[axis] - self.offset[axis]
            current_path = self.coordinates[axis] - start_coord
            
            perc = (current_path / scaled_track_path_val) * 100
            return max(0.0, min(perc, 100.0))

        @percentage.setter
        def percentage(self, value: float | int):
            self._percentage = max(0.0, min(float(value), 100.0))
            axis = 1 if self.orientation == 'vertical' else 0
            scaled_track_path = (self.track_path * self._resize_ratio) - self.rel(self.size)

            start_coord = self.track_start_coordinates[axis] - self.offset[axis]
            
            if scaled_track_path[axis] == 0:
                self.coordinates[axis] = start_coord
                return

            path_to_add = scaled_track_path[axis] * (self._percentage / 100)
            self.coordinates[axis] = start_coord + path_to_add
        
        def set_scroll_params(self, track_start_abs, track_path, offset: Vector2):
            self.track_path = track_path
            self.track_start_coordinates = track_start_abs
            self.offset = offset

        def secondary_update(self, *args):
            super().secondary_update()
            axis = 1 if self.orientation == 'vertical' else 0

            if mouse.left_fdown and not self.is_scrolling:
                if self.get_rect().collidepoint(mouse.pos):
                    self.is_scrolling = True
            if mouse.left_up:
                self.is_scrolling = False

            if self.is_scrolling:
                scaled_track_path_val = (self.track_path[axis] * self._resize_ratio[axis]) - self.rel(self.size)[axis]
                if scaled_track_path_val != 0:
                    mouse_relative_to_track = mouse.pos[axis] - self.track_start_coordinates[axis]
                    self.percentage = (mouse_relative_to_track / scaled_track_path_val) * 100
            else:
                self.percentage = self._percentage

        def move_by_percents(self, percents: int | float):
            self.percentage += percents
            self.is_scrolling = False

        def set_percents(self, percents: int | float):
            self.percentage = percents
            self.is_scrolling = False
            
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
        self._coordinates = Vector2(0, 0)
        
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
        offset = Vector2(self.first_parent_menu.window._crop_width_offset,self.first_parent_menu.window._crop_height_offset) if self.first_parent_menu.window else Vector2(0,0)
        #print(offset)
        self.scroll_bar_y.set_scroll_params(Vector2(self.coordinates[0] + self.relx(self.size[0] - self.scroll_bar_y.size[0]) , track_start_y), 
                                            Vector2(0,track_path_y),
                                            offset/2)

        #------ TODO ------
        #track_start_x = self._coordinates[0] + self.first_parent_menu.coordinatesMW[0]
        #track_length_x = self.size[0]
        #self.scroll_bar_x.set_scroll_params(track_start_x, track_length_x) #old code
        
    def __init_scroll_bars__(self):
        if self._test_debug_print:
            print(f"in {self} used init scroll bars")
        self.scroll_bar_y = self.ScrollBar([self.size[0]/40,self.size[1]/20],default_style(bgcolor=(100,100,100)), 'vertical', self)
        #self.scroll_bar_x = self.ScrollBar([self.size[0]/20,self.size[1]/40],default_style(bgcolor=(100,100,100)), 'horizontal', self)
        self.scroll_bar_y._boot_up()
        self.scroll_bar_y._init_start()
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
        if self._test_debug_print:
            print("in {self} used is drawable optimized(test) for", item)
        overdose_right = item.coordinates[0] + self.relx(item._anim_coordinates[0]) > self.coordinates[0] + self.size[0]
        overdose_left = item.coordinates[0] + self.relx(item._anim_coordinates[0] + item.size[0]) < self.coordinates[0]
        overdose_bottom = item.coordinates[1] + self.rely(item._anim_coordinates[1]) > self.coordinates[1] + self.size[1]
        overdose_top = item.coordinates[1] + self.rely(item._anim_coordinates[1] + item.size[1]) < self.coordinates[1]
        overall = overdose_right or overdose_left or overdose_bottom or overdose_top
        return not overall
    
    def secondary_draw(self):
        if self._test_debug_print:
            print("used draw")
        super().secondary_draw()
        for item in self.items:
            assert isinstance(item, (Widget, LayoutType))
            drawable = self._is_widget_drawable(item) if self._test_rect_calculation else self._is_widget_drawable_optimized(item)
            if drawable or True: self._draw_widget(item)
        if self.actual_max_y > 0:
            self._draw_widget(self.scroll_bar_y)
            
            
    def _set_item_x(self, item: NevuObject, align: Align):
        container_width = self.relx(self.size[0])
        widget_width = self.relx(item.size[0])
        padding = self.relx(self.padding)

        match align:
            case Align.LEFT:
                item.coordinates[0] = self._coordinates[0] + padding
            case Align.RIGHT:
                item.coordinates[0] = self._coordinates[0] + (container_width - widget_width - padding)
            case Align.CENTER:
                item.coordinates[0] = self._coordinates[0] + (container_width / 2 - widget_width / 2)
    
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
            self.scroll_bar_y.coordinates = Vector2(self._coordinates[0] + self.relx(self.size[0] - self.scroll_bar_y.size[0]), self.scroll_bar_y.coordinates[1])
            self.scroll_bar_y.master_coordinates = self._get_item_master_coordinates(self.scroll_bar_y)
        if type(self) == Scrollable: self._dirty_rect = self._read_dirty_rects()
            
    def _regenerate_coordinates(self):
        super()._regenerate_coordinates()
        self.cached_coordinates = []
        self._regenerate_max_values()
        padding_offset = self.rely(self.padding)
        for i in range(len(self.items)):
            item = self.items[i]
            align = self.widgets_alignment[i]
            
            self._set_item_x(item, align)
            item.coordinates[1] = self._coordinates[1] + padding_offset
            self.cached_coordinates.append(item.coordinates)
            item.master_coordinates = self._get_item_master_coordinates(item)
            padding_offset += item._csize[1] + self.rely(self.padding)
            
    def logic_update(self):
        super().logic_update()
        inverse = -1 if self.inverted_scrolling else 1
        if keyboard.is_fdown(pygame.K_UP):
            self.scroll_bar_y.move_by_percents(self.arrow_scroll_power * -inverse)
        if keyboard.is_fdown(pygame.K_DOWN):
            self.scroll_bar_y.move_by_percents(self.arrow_scroll_power * inverse)
        if mouse.wheel_up: 
            self.scroll_bar_y.move_by_percents(self.wheel_scroll_power * -inverse)
        if mouse.wheel_down: 
            self.scroll_bar_y.move_by_percents(self.wheel_scroll_power * inverse)
            
    def resize(self, resize_ratio: Vector2):
        if self._test_debug_print:
            print(f"in {self} used resize, current ratio: {resize_ratio}")
        prev_percentage = self.scroll_bar_y.percentage if hasattr(self, "scroll_bar_y") else 0.0

        if hasattr(self, "scroll_bar_y"):
            self.scroll_bar_y.is_scrolling = False

        super().resize(resize_ratio)
        self.scroll_bar_y.resize(resize_ratio)
        self.scroll_bar_y.coordinates[1] = self.rely(self.scroll_bar_y.size[1])
        self.cached_coordinates = None
        self._regenerate_coordinates()
        self.scroll_bar_y.is_scrolling = False
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
        if item.single_instance is False:
            item = item.clone()
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

class Appending_Layout_Type(LayoutType):
    _margin: int | float
    def __init__(self, style: Style = default_style, content: list[tuple[Align, NevuObject]] | None = None, **constant_kwargs):
        super().__init__(Vector2(0,0), style, None, **constant_kwargs)
        self._lazy_kwargs = {'size': Vector2(0,0), 'content': content}
        
    def _lazy_init(self, size: Vector2 | list, content: list[tuple[Align, NevuObject]] | None = None):
        super()._lazy_init(size, content)
        if content is None:
            return
        if len(content) == 0: return
        for inner_tuple in content:
            align, item = inner_tuple
            self.add_item(item, align)
            
    def _init_lists(self):
        super()._init_lists()
        self.widgets_alignment = []
        
    def _add_constants(self):
        super()._add_constants()
        self._add_constant("margin",(int, float), 10)
        
    def _init_test_flags(self):
        super()._init_test_flags()
        self._test_always_update = True
    
    def _recalculate_size(self):
        pass
    
    def _recalculate_widget_coordinates(self):
        pass
    
    def add_item(self, item: NevuObject, alignment: Align = Align.CENTER):
        #print(self.first_parent_menu.window)
        super().add_item(item)
        self.widgets_alignment.append(alignment)
        self.cached_coordinates = None
        if self.layout: self.layout._event_on_add_item()
        
    def insert_item(self, item: Widget | LayoutType, id: int = -1):
        try:
            self.items.insert(id,item)
            self.widgets_alignment.insert(id,Align.CENTER)
            self._recalculate_size()
            if self.layout: self.layout._event_on_add_item()
        except Exception as e: raise e #TODO
        
    def _connect_to_layout(self, layout: LayoutType):
        super()._connect_to_layout(layout)
        self._recalculate_widget_coordinates()
        
    def _connect_to_menu(self, menu: Menu):
        super()._connect_to_menu(menu)
        self._recalculate_widget_coordinates() 
        
    def _event_on_add_item(self):
        self._recalculate_size()
        if self.layout: self.layout._event_on_add_item()
        
    def secondary_update(self, *args):
        super().secondary_update()
        self._light_update()
    def secondary_draw(self):
        super().secondary_draw()
        for item in self.items:
            assert isinstance(item, (Widget, LayoutType))
            self._draw_widget(item)
    @property
    def margin(self): return self._margin
    @margin.setter
    def margin(self, val):
        self._margin = val
    def _regenerate_coordinates(self):
        super()._regenerate_coordinates()
        self._recalculate_size()
        self._recalculate_widget_coordinates()
class Appending_Layout_H(Appending_Layout_Type):
    def _recalculate_size(self):
        self.size.x = sum(item.size[0]+self._margin for item in self.items) if len(self.items) > 0 else 0
        self.size.y = max(x.size[1] for x in self.items) if len(self.items) > 0 else 0

    def _recalculate_widget_coordinates(self):
        if self.booted == False: return
        self.cached_coordinates = []
        m = self.relx(self.margin)
        current_x = 0 
        for i in range(len(self.items)):
            item = self.items[i]
            alignment = self.widgets_alignment[i]
            widget_local_x = current_x + m / 2
            item.coordinates[0] = self.coordinates[0] + widget_local_x 
            if alignment == Align.CENTER:
                item.coordinates[1] = self.coordinates[1] + self.rely(self.size[1] / 2 - item.size[1] / 2)
            elif alignment == Align.LEFT:
                item.coordinates[1] = self.coordinates[1]
            elif alignment == Align.RIGHT:
                item.coordinates[1] = self.coordinates[1] + self.rely(self.size[1] - item.size[1])
            item.master_coordinates = self._get_item_master_coordinates(item)
            current_x += self.relx(item.size[0] + self.margin)
            self.cached_coordinates.append(item.coordinates)
    def clone(self):
        return Appending_Layout_H(copy.deepcopy(self.style), self._lazy_kwargs['content'], **self.constant_kwargs)

class Appending_Layout_V(Appending_Layout_Type):
    def _recalculate_size(self):
        self.size[1] = sum(item.size[1]+self._margin for item in self.items) if len(self.items) > 0 else 0
        self.size[0] = max(x.size[0] for x in self.items) if len(self.items) > 0 else 0
    def _recalculate_widget_coordinates(self):
        if self.booted == False: return
        self.cached_coordinates = []
        m = self.rely(self.margin)
        current_y = 0
        for i in range(len(self.items)):
            item = self.items[i]
            alignment = self.widgets_alignment[i]
            widget_local_y = current_y + m
            item.coordinates[1] = self.coordinates[1] + widget_local_y 
            if alignment == Align.CENTER:
                item.coordinates[0] = self.coordinates[0] + self.relx(self.size[0] / 2 - item.size[0] / 2)
            elif alignment == Align.LEFT:
                item.coordinates[0] = self.coordinates[0]
            elif alignment == Align.RIGHT:
                item.coordinates[0] = self.coordinates[0] + self.relx(self.size[0] - item.size[0])
            item.master_coordinates = self._get_item_master_coordinates(item)
            current_y += self.rely(item.size[1] + self.margin)
            self.cached_coordinates.append(item.coordinates)
    def clone(self):
        return Appending_Layout_V(copy.deepcopy(self.style), self._lazy_kwargs['content'], **self.constant_kwargs)
    
class CheckBoxGroup():
    def __init__(self, checkboxes: list[RectCheckBox] | None = None):
        self._content: list[RectCheckBox] = []
        self._events: list[NevuEvent] = []
        if checkboxes is None: checkboxes = []
        for checkbox in checkboxes:
            self.add_checkbox(checkbox)
    def on_checkbox_added(self, checkbox: RectCheckBox):
        pass #hook
    def on_checkbox_toogled(self, included_checkboxes: list[RectCheckBox]):
        pass #hook
    def add_checkbox(self, checkbox: RectCheckBox):
        self._content.append(checkbox)
        self.on_checkbox_added(checkbox)
    def get_checkbox(self, id: str) -> RectCheckBox | None:
        return next((item for item in self._content if item.id == id), None)
    
    def add_event(self, event: NevuEvent):
        self._events.append(event)

    def _event_cycle(self, type: EventType, *args, **kwargs):
        for event in self._events:
            if event._type == type:
                event(*args, **kwargs)