import pygame
import numpy as np
import copy
from .style import Style,Align,SizeRule, vh, vw, fill
from .widgets import *
from .menu import Menu
from .nevuobj import NevuObject
default_style = Style()


class LayoutType(NevuObject):
    def _get_item_master_coordinates(self, item: NevuObject):
        return [item.coordinates[0] + self.first_parent_menu.coordinatesMW[0], item.coordinates[1] + self.first_parent_menu.coordinatesMW[1]]

    def _draw_widget(self, item: NevuObject, multiply: list = None, add: list = None):
        if item._wait_mode:
            #print("item", item, "wait mode")
            self.read_item_coords(item)
            self._start_item(item)
            return
        item.draw()
        if self.is_layout(item) or not self.surface: return
        coordinates = item.coordinates
        if multiply:
            coordinates = zip(coordinates, multiply)
            coordinates = [x * y for x, y in coordinates]
        if add: coordinates = zip(coordinates, add)
        self.surface.blit(item.surface,[int(coordinates[0]),int(coordinates[1])])

    def _boot_up(self):
        #print("booted layout", self)
        for item in self.items + self.freedom_items:
            self.read_item_coords(item)
            self._start_item(item)
            item.booted = True
            item._boot_up()
            

    @property
    def _rsize(self):
        bw = self.menu.style.borderwidth if self.menu else self.first_parent_menu.style.borderwidth
        #bw = int(self.relm(bw))
        if self.menu: return self._csize - Vector2(bw,bw)
        return self._csize
    @property
    def _rsize_marg(self):
        bw = self.menu.style.borderwidth if self.menu else self.first_parent_menu.style.borderwidth
        bw = int(self.relm(bw))
        if self.menu: return (self._csize - (self._csize - Vector2(bw,bw)))/2
        return Vector2(0,0)

    def __init__(self, size: Vector2|list, style: Style = default_style, content: list = None, floating: bool = False, id: str = None):
        super().__init__(size, style, floating, id)
        self.freedom_items = []
        self.items = []
        self._lazy_kwargs = {'size': size, 'content': content}
        
        self.menu = None
        self.layout = None
        self.surface = None
        self.cached_coordinates = None
        self.style = style
        
        self.first_parent_menu = Menu(None, (100,100), style)
        self.all_layouts_coords = [0,0]
        
        self._can_be_main_layout = True
        self._borders = False
        
        self.border_name = " "
        #if type(self) == LayoutType: self._init_start()

    def _lazy_init(self, size: Vector2|list, content: list = None):
        super()._lazy_init(size)
        if content and type(self) == LayoutType:
            for i in content:
                self.add_item(i)

    def _light_update(self, add_x: int = 0, add_y: int = 0 ):
        if len(self.items) != len(self.cached_coordinates): return
        for i in range(len(self.items)):
            item: NevuObject = self.items[i]
            item.animation_manager: AnimationManager
            coords = self.cached_coordinates[i]
            anim_coords = item.animation_manager.get_animation_value(AnimationType.POSITION)
            anim_coords = [0,0] if anim_coords is None else anim_coords
            item.coordinates = pygame.Vector2([coords[0] + self.relx(anim_coords[0]) + add_x,
                                              coords[1] + self.relx(anim_coords[1]) + add_y])
            item.master_coordinates = pygame.Vector2([item.coordinates[0] + self.first_parent_menu.coordinatesMW[0],
                                                      item.coordinates[1] + self.first_parent_menu.coordinatesMW[1]])
            try: item.update(self.first_parent_menu.window.last_events)
            except:item.update([])

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
            except: pass

    def _convert_item_coord(self, coord, i: int = 0):
        if isinstance(coord, SizeRule):
            if isinstance(coord, (Vh, Vw)):
                if self.first_parent_menu is None: raise ValueError("Cant use Vh or Vw in unconnected layout")
                if self.first_parent_menu.window is None: raise ValueError("Cant use Vh or Vw in uninitialized layout")
                if type(coord) == Vh: return self.first_parent_menu.window.size[1]/100 * coord.value, True
                elif type(coord) == Vw: return self.first_parent_menu.window.size[0]/100 * coord.value, True
            elif type(coord) == Fill: return self._rsize[i]/ 100 * coord.value, True
            return coord, False
        return coord, False

    def read_item_coords(self, item: NevuObject):
        if self.booted == False: print("Cant read item coords", item); return
        w_size = item._lazy_kwargs['size']
        x, y = w_size
        x, is_x_rule = self._convert_item_coord(x, 0)
        y, is_y_rule = self._convert_item_coord(y, 1)

        item._lazy_kwargs['size'] = [x,y]
        is_ruled = is_x_rule or is_y_rule

    def _start_item(self, item: NevuObject):
        if self.booted == False: return
        item._wait_mode = False; item._init_start()

    def resize(self, resize_ratio: Vector2):
        super().resize(resize_ratio)
        self.cached_coordinates = None
        for item in self.items + self.freedom_items:
            item.resize(self._resize_ratio)
        self.border_name = self._border_name

    def is_layout(self, item: NevuObject) -> bool:
        if isinstance(item, LayoutType): return True
        return False

    def _event_on_add_widget(self): pass

    def add_item(self, item: NevuObject):
        if isinstance(item,LayoutType):item._connect_to_layout(self)
        elif hasattr(item,"_freedom"):
            self.read_item_coords(item)
            self._start_item(item)
            if item._freedom:self.freedom_items.append(item)
            else:self.items.append(item)
            return
        self.read_item_coords(item)
        self._start_item(item)
        self.items.append(item)
        self.cached_coordinates = None

    def apply_style_to_childs(self, style: Style):
        for item in self.items:
            if not hasattr(item,"menu"): item.style = style
            else: item.apply_style_to_childs(style)

    def primary_draw(self):
        super().primary_draw()
        if self.borders and hasattr(self, "border_font_surface"):
            chc = [1,1] if self.layout!=None else self._resize_ratio
            self.surface.blit(self.border_font_surface, [self.coordinates[0]*chc[0], self.coordinates[1]*chc[1]-self.border_font_surface.get_height()])
            pygame.draw.rect(self.surface,(255,255,255),[self.coordinates[0]*chc[0], self.coordinates[1]*chc[1],int(self.size[0]*self._resize_ratio[0]),int(self.size[1]*self._resize_ratio[1])],1)
        for item in self.freedom_items:
            self._draw_widget(item, self._resize_ratio)

    def _read_dirty_rects(self):
        dirty_rects = []
        for item in self.items+self.freedom_items:
            if len(item._dirty_rect) > 0:
                dirty_rects.extend(item._dirty_rect)
                item._dirty_rect = []
        return dirty_rects

    def secondary_update(self, *args):
        super().secondary_update()
        if self.menu:self.surface = self.menu.surface;self.all_layouts_coords = [0,0]
        elif self.layout:self.surface = self.layout.surface;self.all_layouts_coords = [self.layout.all_layouts_coords[0]+self.coordinates[0],self.layout.all_layouts_coords[1]+self.coordinates[1]];self.first_parent_menu = self.layout.first_parent_menu
        for item in self.freedom_items:
            item.master_coordinates = [item.coordinates[0]+self.first_parent_menu.coordinatesMW[0],item.coordinates[1]+self.first_parent_menu.coordinatesMW[1]]
            item.update()
        if type(self) == LayoutType: self._dirty_rect = self._read_dirty_rects()

    def _connect_to_menu(self, menu: Menu):
        self.cached_coordinates = None
        self.menu = menu
        self.surface = self.menu.surface
        self.first_parent_menu = menu
        self.border_name = self._border_name

    def _connect_to_layout(self, layout):
        self.surface = layout.surface
        self.layout = layout
        self.first_parent_menu = layout.first_parent_menu
        self.border_name = self._border_name
        self.cached_coordinates = None

    def get_item_by_id(self, id: str) -> NevuObject|None:
        mass = self.items + self.freedom_items
        if id == None: return None
        for item in mass:
            if item.id == id: return item
        return None

class Grid(LayoutType):
    def __init__(self, size: Vector2|list, x: int = 1, y: int = 1, style: Style = default_style, 
                 floating: bool = False, id: str = None, content: dict[tuple, NevuObject] = None):
        super().__init__(size, style, floating, id)
        self._lazy_kwargs = {'size': size, 'content': content}
        self.grid_x = x
        self.grid_y = y
    def _lazy_init(self, size: Vector2|list, content: dict[tuple, NevuObject] = None):
        super()._lazy_init(size)

        self.cell_height = self.size[1] / self.grid_y
        self.cell_width = self.size[0] / self.grid_x
        if content:
            for coords, item in content.items():
                #print("ADD ITEM", item, coords)
                self.add_item(item, coords[0], coords[1])
    
    def secondary_update(self, *args):
        super().secondary_update()
        if self.cached_coordinates is None:
            self.cached_coordinates = []
            for item in self.items:
                if not self.menu:
                    cw = self.cell_width
                    ch = self.cell_height
                else: 
                    cw = self._rsize[0] / self.grid_x
                    ch = self._rsize[1] / self.grid_y
                    
                coordinates = [self.coordinates[0] + self._rsize_marg[0] + self.relx(item.x * cw + (cw - item.size[0]) / 2  ),
                               self.coordinates[1] + self._rsize_marg[1] + self.rely(item.y * ch + (ch - item.size[1]) / 2)]
                item.coordinates = coordinates
                item.master_coordinates = self._get_item_master_coordinates(item)
                self.cached_coordinates.append(coordinates)
        self._light_update()
        if type(self) == Grid: self._dirty_rect = self._read_dirty_rects()
    def add_item(self, item: NevuObject, x: int, y: int):
        range_error = ValueError("Grid index out of range x: {x}, y: {y} ".format(x=x,y=y)+f"Grid size: {self.grid_x}x{self.grid_y}")
        
        range_overflow = x > self.grid_x or y > self.grid_y or x < 1 or y < 1
        if range_overflow: raise range_error
        
        for _widget in self.items: 
            if _widget.x == x-1 and _widget.y == y-1: raise range_error
        item.x = x-1
        item.y = y-1
        super().add_item(item)
        if self.layout: self.layout._event_on_add_widget()

    def secondary_draw(self):
        super().secondary_draw()
        for item in self.items: self._draw_widget(item)

    def get_row(self, x: int) -> list[Widget]:
        needed = []
        for item in self.items:
            if item.x == x: needed.append(item)
        return needed

    def get_column(self, y: int) -> list[Widget]:
        needed = []
        for item in self.items:
            if item.y == y: needed.append(item)
        return needed

    def get_item(self, x: int, y: int) -> Widget:
        w = None
        for item in self.items:
            if item.x == x-1 and item.y == y-1:
                w = item
                return w

    def overwrite_widget(self, x: int, y: int, item: Widget) -> bool:
        for _widget in self.items:
            if _widget.x == x-1 and _widget.y == y-1:
                self.items.remove(_widget)
                self.add_item(item, x, y)
                return True
        return False

class CheckBoxGrid(Grid):
    def __init__(self, size:list[int,int], x:int=1, y:int=1 ,multiple=False,named=False):
        super().__init__(size, x, y*2 if named else y)
        self._named = named
        self.selected = -1
        self.widgets_last_id = 0
        self.multiple = multiple
        raise ValueError("WARNING: this class is deprecated and will be rebranded in the future, for now this class is uncompatible other code!!")
    def draw(self): 
        super().draw()
        for i in range(0,len(self.items)-1):
            item = self.items[i]
            item._changed = True
            if i == self.selected: item.draw(True)
            if not hasattr(item,"menu"):
                self.surface.blit(item.surface,[int(item.coordinates[0]),int(item.coordinates[1])])
    def apply_style_to_childs(self, style:Style):
        for item in self.items:
            if not hasattr(item,"menu"):
                if isinstance(item,CheckBox):
                    item.style = style
            else: item.apply_style_to_childs(style)
    def add_item(self, item: Widget, x: int, y: int, name: str|None = None):
        if not isinstance(item,CheckBox):
            if name != "SYSTEM_NEEDS":raise Exception("Widget must be CheckBox")
            else:name = None
        if name:
            if self._named:
                self.add_item(Label((self.cell_width*self._resize_ratio[0],300*self._resize_ratio[1]),name,default_style(bgcolor=Color_Type.TRANSPARENT,bordercolor=Color_Type.TRANSPARENT)),x,y*2-1,name="SYSTEM_NEEDS")
                y*=2
        super().add_item(item, x, y)
        if hasattr(item,"connect_to_dot_group"):
            item.connect_to_dot_group(self,self.widgets_last_id)
            self.widgets_last_id += 1
            
    @property
    def active(self):
        m = []
        for dot in self.items:
            if isinstance(dot,CheckBox):
                if dot.is_active: m.append(dot)
        return m
    @active.setter
    def active(self, id: int) -> list[CheckBox]|CheckBox|None:
        if not self.multiple:
            for dot in self.items:
                if isinstance(dot,CheckBox): dot.is_active = False
        for dot in self.items:
            if isinstance(dot,CheckBox):
                if dot._id == id:
                    if self.multiple:
                        if not dot.is_active: dot.is_active = True
                        else: dot.is_active = False
                    else: dot.is_active = True
    @property
    def active_state(self) -> list[object]|object|None:
        m = []
        for dot in self.items:
            if isinstance(dot,CheckBox):
                if dot.is_active: m.append(dot.state)
        if len(m)>1: return m
        elif len(m) == 1: return m[0]
        else: return None
    @active_state.setter
    def active_state(self,value,id:int=None):
        for dot in self.items:
            if isinstance(dot,CheckBox):
                if dot.is_active:
                    if dot._id == id or id == None: dot.state = value
    @property
    def inactive(self) -> list[CheckBox]|CheckBox|None:
        m = []
        for dot in self.items:
            if not dot.is_active:
                if isinstance(dot,CheckBox): m.append(dot)
        if len(m)>1: return m
        elif len(m) == 1: return m[0]
        else: return None
    
    @property
    def inactive_state(self) -> list[object]|object|None:
        m = []
        for dot in self.items:
            if not dot.is_active:
                if isinstance(dot,CheckBox): m.append(dot.state)
        if len(m)>1: return m
        elif len(m) == 1: return m[0]
        else: return None

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
    def __init__(self, size: list|tuple):
        super().__init__(size)
        self.selected_page = None
        self.selected_page_id = 0
    def add_item(self, item: LayoutType):
        if not self.is_layout(item): raise Exception("Widget must be Layout")
        super().add_item(item)
        if self.layout: self.layout._event_on_add_widget()
        if not self.selected_page:
            self.selected_page = item
            self.selected_page_id = 0
    def draw(self):
        super().draw()
        pygame.draw.line(self.surface,(0,0,0),[self.coordinates[0]+self.relx(20),self.coordinates[1]+self.rely(20)],[self.coordinates[0]+self.relx(40),self.coordinates[1]+self.rely(20)],2)
        pygame.draw.line(self.surface,(0,0,0),[self.coordinates[0]+self.relx(20),self.coordinates[1]+self.rely(20)],[self.coordinates[0]+self.relx(20),self.coordinates[1]+self.rely(40)],2)
        
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
    def update(self, *args):
        super().update()
        if mouse.left_fdown:
            rectleft = pygame.Rect(self.coordinates[0]+(self.first_parent_menu.coordinatesMW[0]),self.coordinates[1]+self.first_parent_menu.coordinatesMW[1],self.relx(self.size[0]/10),self.rely(self.size[1]))
            rectright = pygame.Rect(self.coordinates[0]+self.relx(self.size[0]-self.size[0]/10)+self.first_parent_menu.coordinatesMW[0],self.coordinates[1]+self.first_parent_menu.coordinatesMW[1],self.relx(self.size[0]/10),self.rely(self.size[1]))
            if rectleft.collidepoint(mouse.pos): self.move_by_point(-1)
            if rectright.collidepoint(mouse.pos): self.move_by_point(1)

        self.items[self.selected_page_id].coordinates = [self.coordinates[0]+self.relx(self.size[0]/2-self.items[self.selected_page_id].size[0]/2),
                                                           self.coordinates[1]+self.rely(self.size[1]/2-self.items[self.selected_page_id].size[1]/2),]
        self.items[self.selected_page_id].first_parent_menu = self.first_parent_menu
        self.items[self.selected_page_id].update()
    def get_selected(self): return self.items[self.selected_page_id]
class Gallery_Pages(Pages):
    def __init__(self, size: list|tuple):
        super().__init__(size)
        
    def add_item(self, item: Widget):
        if self.is_layout(item): raise Exception("Widget must not be Layout, layout creates automatically")
        if isinstance(item,ImageWidget) or isinstance(item,GifWidget):
            g = Grid(self.size)
            g.add_item(item, 1, 1)
            super().add_item(g)

class Scrollable(LayoutType):
    """
    WARNING: VERY OUTDATED DOKSTING
    Implements an infinite scrolling layout to display items that exceed the visible area.

    This layout allows for displaying a long list or a large number of items
    that do not fit within the given layout size by using scroll bars for navigation.

    It supports both vertical and horizontal scrolling (though horizontal scrolling
    might be less developed at the moment) and allows adding items
    with different alignment options.

    **Nested Class:**

    * `Scroll_Bar`:  The scroll bar item that controls the visibility and position
                      of the scrollable area.

    **Key Features:**

    * **Infinite Scrolling:** Displays content exceeding layout bounds using scrollbars.
    * **Vertical and Horizontal Scrolling:** Supports scrolling in both directions.
    * **Widget Management:** Adding and managing items within the scrollable area.
    * **Widget Alignment:**  Allows aligning items to the left, center, or right.
    * **Interactivity:** Scroll control via mouse interaction.

    **Usage Example:**

    ```python
    # Example requires definitions for LayoutType, Widget, default_style, Align and pygame

    # Creating an infinite scroll layout
    infinite_scroll_layout = Scrollable((300, 200))

    # Adding items
    # ......
    ```
    """
    class Scroll_Bar(Widget):
        def __init__(self, size, style, minval, maxval, scrsizet, scrsizeb, t, master = None):
            super().__init__(size, style)
            self.minval = minval
            self.maxval = maxval
            self.percentage = 0
            self.scroll = False
            self.scroll_sizeT = scrsizet
            self.scroll_sizeB = scrsizeb
            self.type = t
            self.master = master
            if not isinstance(self.master, LayoutType):
                print("WARNING: this class only used in InfiniteScroll and is not compatible with other code")
        def secondary_update(self, *args):
            if self.type == 1:
                rect = pygame.Rect(self.master_coordinates[0], self.scroll_sizeT, self.size[0] * self._resize_ratio[0], self.scroll_sizeB * self._resize_ratio[1])
            elif self.type == 2:
                rect = pygame.Rect(self.scroll_sizeT * self._resize_ratio[0], self.master_coordinates[1], self.scroll_sizeB * self._resize_ratio[0], self.size[1] * self._resize_ratio[1])
            if mouse.left_fdown:
                self.scroll = rect.collidepoint(mouse.pos)
            if mouse.left_up:
                self.scroll = False
            if self.scroll:
                self.coordinates[1] = mouse.pos[1] - self.master_coordinates[1] + self.coordinates[1]
            try:
                self.percentage = self.coordinates[1] / (self.scroll_sizeB * self._resize_ratio[1]) * 100
            except ZeroDivisionError:
                self.percentage = 0

            self.percentage = max(0, min(self.percentage, 100))
            self.coordinates[1] = max(0, min(self.coordinates[1], (self.scroll_sizeT + self.scroll_sizeB - self.size[1]) * self._resize_ratio[1]))
        def set_mv_mx_val(self, minval, maxval, scrsizet, scrsizeb):
            self.scroll_sizeT = scrsizet
            self.scroll_sizeB = scrsizeb
            self.minval = minval
            self.maxval = maxval
    def __init__(self, size: Vector2|list, style: Style = default_style, content: dict[Align, NevuObject] = None, draw_scrool_area: bool = False, id: str = None):
        ### TESTS USE WITH CAUTION!
        self._test_list_instances_compatibility = False # Needed for correct work for now
        self._test_debug_print = False
        self._test_rect_calculation = False
        self._test_always_update = True
        ### TESTS USE WITH CAUTION!
        
        # WARNING!!!!
        #
        # IN THIS LAYOUT FOUND UNKNOWN BUGS THAT AFFECT PERFORMANCE AND SPEED
        # USE WITH CAUTION!!!
        #
        # THANK YOU FOR UNDERSTANDING
        
        super().__init__(size, style, content, False, id)
        self.max_x = 0
        self.max_y = 0
        self.actual_max_y = 1
        self.padding = 30
        self.draw_scrool_area = draw_scrool_area
        self.widgets_alignment = []

    def _lazy_init(self, size: Vector2|list, content: dict[Align, NevuObject] = None):
        super()._lazy_init(size, content)
        self.original_size = self.size.copy()
        self.__init_scroll_bars__()
        if content and type(self) == Scrollable:
            for align, item in content.items():
                self.add_item(item, align)
        self.first_update_fuctions.append(self.__first_update_bars__)
        
    def _event_on_add_widget(self):
        self.cached_coordinates = None
        if self._test_debug_print:
            print("used event on add widget")
        self.__init_scroll_bars__()
        self.__first_update_bars__()
        self.max_y = self.padding
        self.max_x = self.original_size[0] if self.original_size != self.size else self.size[0]
        for item in self.items:
            self.max_y += self.relx(item.size[1] + self.padding)
        self.actual_max_y = self.max_y - self.size[1]
    def __first_update_bars__(self):
        if self._test_debug_print:
            print("used first update bars")
        self.scroll_bar_y.set_mv_mx_val(self._coordinates[1],self.max_y,self._coordinates[1]+self.first_parent_menu.coordinatesMW[1],self.size[1])
        self.scroll_bar_x.set_mv_mx_val(self._coordinates[0]-self.max_x/2,self._coordinates[0]+self.max_x/2,self._coordinates[0]+self.first_parent_menu.coordinatesMW[0],self.size[0])
    def __init_scroll_bars__(self):
        if self._test_debug_print:
            print("used init scroll bars")
        self.scroll_bar_y = self.Scroll_Bar([self.size[0]/40,self.size[1]/20],default_style(bgcolor=(100,100,100)),0,0,0,0,1,self)
        self.scroll_bar_x = self.Scroll_Bar([self.size[0]/20,self.size[1]/40],default_style(bgcolor=(100,100,100)),0,0,0,0,2,self)
    def _connect_to_layout(self, layout: LayoutType):
        if self._test_debug_print:
            print("used connect to layout")
        super()._connect_to_layout(layout)
        #self.__init_scroll_bars__()
    def _connect_to_menu(self, menu: Menu):
        if self._test_debug_print:
            print("used connect to menu")
        super()._connect_to_menu(menu)
        need_resize = False
        if menu.size[0] < self.size[0]:
            self.size[0] = menu.size[0]
            need_resize = True
        if menu.size[1] < self.size[1]:
            self.size[1] = menu.size[1]
            need_resize = True
        if need_resize:
            self.menu._set_layout_coordinates(self)
        #self.__init_scroll_bars__()
    def _is_widget_drawable(self, item: NevuObject):
        if self._test_debug_print:
            print("used is drawable for", item)
        item_rect = item.get_rect()
        self_rect = self.get_rect()
        if item_rect.colliderect(self_rect): return True
        return False
    def _is_widget_drawable_optimized(self, item: NevuObject):
        if self._test_debug_print:
            print("used is drawable optimized(test) for", item)
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
            drawable = self._is_widget_drawable(item) if self._test_rect_calculation else self._is_widget_drawable_optimized(item)
            if drawable: self._draw_widget(item)
        if self.actual_max_y > 0:
            self.scroll_bar_y.draw()
        #    if self.surface: self.surface.blit(self.scroll_bar_y.surface,self.scroll_bar_y.coordinates)
            
    def _set_item_x(self, item: NevuObject, align: Align):
        match align:
            case Align.LEFT:
                item.coordinates[0] = self._coordinates[0] + self.relx(self.padding)
                
            case Align.RIGHT:
                item.coordinates[0] = self._coordinates[0] + self.relx((self.size[0] - item.size[0] - self.padding))
                
            case Align.CENTER:
                item.coordinates[0] = self._coordinates[0] + (self.rel_size[0] / 2 - item.rel_size[0] / 2)
    
    def get_offset(self) -> int | float:
        percentage = self.scroll_bar_y.percentage
        offset = self.actual_max_y / 100 * percentage
        return offset
    
    def secondary_update(self, *args):
        if self._test_debug_print:
            print("used update")
            for name, data in self.__dict__.items():
                print(name+":", data)
        super().secondary_update()
        offset = self.get_offset()
        if self.cached_coordinates is None or self._test_always_update:
            self.cached_coordinates = []
            padding_offset = self.rely(self.padding)
            for i in range(len(self.items)):
                item = self.items[i]
                align = self.widgets_alignment[i]
                ### THIS IS ONLY FOR TESTING PURPOSES!
                if self._test_list_instances_compatibility:
                    try:
                        item.coordinates = item.coordinates.tolist()
                    except: pass   
                ### THIS IS ONLY FOR TESTING PURPOSES!
                
                self._set_item_x(item, align)
                item.coordinates[1] = self._coordinates[1] + padding_offset
                self.cached_coordinates.append(item.coordinates)
                item.master_coordinates = self._get_item_master_coordinates(item)
                current_end = item.coordinates[1] + self.rely(offset)
                padding_offset = current_end + item.rel_size[1] + self.rely(self.padding)
        
        self._light_update(0, -self.rely(offset))    
                
        if self.actual_max_y > 0:
            self.scroll_bar_y.coordinates = [self._coordinates[0] + self.relx(self.size[0] - self.scroll_bar_y.size[0]), self.scroll_bar_y.coordinates[1]]
            self.scroll_bar_y.master_coordinates = self._get_item_master_coordinates(self.scroll_bar_y)
            self.scroll_bar_y.update()
    def resize(self, resize_ratio: list | tuple):
        if self._test_debug_print:
            print("used resize", resize_ratio)
        super().resize(resize_ratio)
        self.scroll_bar_y.resize(resize_ratio)
        self.scroll_bar_y.coordinates[1] = self.scroll_bar_y.size[1] * self._resize_ratio[1]
    def add_item(self, item: NevuObject, alignment: Align = Align.LEFT):
        if self._test_debug_print:
            print("used add widget", item, alignment)
        
        self.max_y = self.padding
        self.max_x = self.original_size[0] if self.original_size != self.size else self.size[0]
        for _item in self.items:
            self.max_y += self.rely(_item.size[1] + self.padding)
        super().add_item(item)
        self.max_y += self.rely(item.size[1] + self.padding)
        self.actual_max_y = self.max_y - self.size[1]
        self.widgets_alignment.append(alignment)
        if self.layout:
            self.layout._event_on_add_widget()
    def clear(self):
        self.items.clear()
        self.widgets_alignment.clear()
        self.max_x = 0
        self.max_y = self.padding
        self.actual_max_y = 0
    def apply_style_to_childs(self, style: Style):
        super().apply_style_to_childs(style)
        self.scroll_bar_y.style = style
        
class Appending_Layout_Type(LayoutType):
    def __init__(self, content: list = [], style: Style = default_style):
        
        ### TESTS USE WITH CAUTION!
        self._test_always_update = True
        ### TESTS USE WITH CAUTION!
        
        self._margin = 20
        super().__init__((self.margin, 0), style)
        self.widgets_alignment = []
        self._can_be_main_layout = True
        if len(content) == 0: return
        for item in content:
            item, align = item
            self.add_widget(item, align)
    def add_widget(self, item: Widget | LayoutType, alignment: Align = Align.CENTER):
        super().add_widget(item)
        self.widgets_alignment.append(alignment)
        self._recalculate_size()
        if self.layout: self.layout._event_on_add_widget()
    def insert_item(self, item: Widget | LayoutType, id: int = -1):
        try:
            self.items.insert(id,item)
            self.widgets_alignment.insert(id,Align.CENTER)
            self._recalculate_size()
            if self.layout: self.layout._event_on_add_widget()
        except Exception as e: raise e #TODO
    def _connect_to_layout(self, layout: LayoutType):
        super()._connect_to_layout(layout)
        self._recalculate_widget_coordinates()
    def _connect_to_menu(self, menu: Menu):
        super()._connect_to_menu(menu)
        self._recalculate_widget_coordinates() 
    def _event_on_add_widget(self):
        self._recalculate_size()
        if self.layout: self.layout._event_on_add_widget()
    def update(self, *args):
        super().update()
        if self.cached_coordinates is None or self._test_always_update:
            self._recalculate_widget_coordinates()
        self._light_update()
    def draw(self):
        super().draw()
        
        for item in self.items:
            self._draw_widget(item)
    @property
    def margin(self): return self._margin
    @margin.setter
    def margin(self, val):
        self._margin = val
        self._recalculate_size()
        
class Appending_Layout_H(Appending_Layout_Type):
    def _recalculate_size(self):
        self.size[0] = sum(item.size[0]+self._margin for item in self.items) if len(self.items) > 0 else 0
        self.size[1] = max(x.size[1] for x in self.items) if len(self.items) > 0 else 0
    def _recalculate_widget_coordinates(self):
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

class Appending_Layout_V(Appending_Layout_Type):
    def _recalculate_size(self):
        self.size[1] = sum(item.size[1]+self._margin for item in self.items) if len(self.items) > 0 else 0
        self.size[0] = max(x.size[0] for x in self.items) if len(self.items) > 0 else 0
    def _recalculate_widget_coordinates(self):
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