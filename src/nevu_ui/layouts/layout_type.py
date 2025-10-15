import pygame
import copy
from typing import TypeGuard

from nevu_ui.widgets import Widget
from nevu_ui.menu import Menu
from nevu_ui.nevuobj import NevuObject
from nevu_ui.fast.logic import _light_update_helper
from nevu_ui.fast.nvvector2 import NvVector2

from nevu_ui.style import (
    Style, default_style
)
from nevu_ui.core_types import (
    SizeRule, Vh, Vw, Fill
)

class LayoutType(NevuObject):
    items: list[NevuObject]
    floating_items: list[NevuObject]
    
    def _get_item_master_coordinates(self, item: NevuObject):
        assert isinstance(item, NevuObject), f"Can't use _get_item_master_coordinates on {type(item)}"
        return item.coordinates + self.first_parent_menu.coordinatesMW

    def _draw_widget(self, item: NevuObject, multiply: NvVector2 | None = None, add: NvVector2 | None = None):
        assert isinstance(item, NevuObject), f"Cant use _draw_widget on {type(item)}"
        assert isinstance(self.surface, pygame.Surface), "Cant use _draw_widget with uninitialized surface"
        
        if item._wait_mode:
            self.read_item_coords(item)
            self._start_item(item)
            return
        
        item.draw()
        if self.is_layout(item): return
        
        coordinates = item.coordinates.copy()
        if multiply: coordinates *= multiply
        if add: coordinates += add
        self.surface.blit(item.surface, coordinates.to_tuple())

    def _boot_up(self):
        #print("booted layout", self)
        self.booted = True
        for item in self.items + self.floating_items:
            assert isinstance(item, (Widget, LayoutType))
            self.read_item_coords(item)
            self._start_item(item)
            item.booted = True
            
            item._boot_up()
            
    @property
    def _rsize(self) -> NvVector2:
        bw = self.menu.style.borderwidth if self.menu else self.first_parent_menu.style.borderwidth
        return self._csize - NvVector2(bw, bw) if self.menu else self._csize

    @property
    def _rsize_marg(self) -> NvVector2:
        bw = self.menu.style.borderwidth if self.menu else self.first_parent_menu.style.borderwidth
        bw = int(self.relm(bw))
        if self.menu: return (self._csize - (self._csize - NvVector2(bw,bw)))/2
        return NvVector2()
    
    def __init__(self, size: NvVector2 | list, style: Style = default_style, content: list | None  = None, **constant_kwargs):
        super().__init__(size, style, **constant_kwargs)
        self._lazy_kwargs = {'size': size, 'content': content}
        self.border_name = " "
        
    def _init_lists(self):
        super()._init_lists()
        self.floating_items = []
        self.items = []
        self.cached_coordinates = None
        self.all_layouts_coords = NvVector2()
        
    def _init_booleans(self):
        super()._init_booleans()
        self._can_be_main_layout = True
        self._borders = False
        
    def _init_objects(self):
        super()._init_objects()
        self.first_parent_menu = Menu(None, (1,1), default_style)
        self.menu: Menu | None = None
        self.layout: LayoutType | None = None
        self.surface: pygame.Surface | None = None
        
    def _lazy_init(self, size: NvVector2 | list, content: list | None = None):
        super()._lazy_init(size)
        if content and type(self) == LayoutType:
            for i in content:
                self.add_item(i)

    def base_light_update(self, add_x: int | float = 0, add_y: int | float = 0 ):
        _light_update_helper(
            self.items,
            self.cached_coordinates or [],
            self.first_parent_menu,
            add_x,
            add_y,
            self._resize_ratio,
            self.cached_coordinates is None or len(self.items) != len(self.cached_coordinates)
            
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
                self.border_font = pygame.sysfont.SysFont("Arial", self.relx(self.first_parent_menu._style.fontsize))
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
        for item in self.items + self.floating_items:
            assert isinstance(item, (Widget, LayoutType))
            item.resize(self._resize_ratio)
        self.border_name = self._border_name

    @staticmethod
    def is_layout(item: NevuObject) -> TypeGuard['LayoutType']:
        return isinstance(item, LayoutType)
    
    @staticmethod
    def is_widget(item: NevuObject) -> TypeGuard['Widget']:
        return isinstance(item, Widget)
    
    def _event_on_add_item(self): pass

    def add_item(self, item: NevuObject):
        if not item.single_instance: item = item.clone()
        item._master_z_handler = self._master_z_handler
        if self.is_layout(item): 
            assert self.is_layout(item)
            item._connect_to_layout(self)
        elif self.is_widget(item):
            self.read_item_coords(item)
            self._start_item(item)
            if item.floating: self.floating_items.append(item)
            else: self.items.append(item)
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
        if self.borders:
            assert self.surface
            if hasattr(self, "border_font_surface"):
                self.surface.blit(self.border_font_surface, [self.coordinates[0], self.coordinates[1] - self.border_font_surface.get_height()])
                pygame.draw.rect(self.surface,(255,255,255),[self.coordinates[0], self.coordinates[1], self._csize.x, self._csize.y], 1)
        
        for item in self.floating_items:
            self._draw_widget(item, self.rel(item.coordinates))

    def _read_dirty_rects(self):
        dirty_rects = []
        for item in self.items + self.floating_items:
            assert isinstance(item, (Widget, LayoutType))
            if len(item._dirty_rect) > 0:
                dirty_rects.extend(item._dirty_rect)
                item._dirty_rect.clear()
        return dirty_rects

    def secondary_update(self):
        super().secondary_update()
        if self.menu:
            self.surface = self.menu.surface
            self.all_layouts_coords = NvVector2()
            
        elif self.layout: 
            self.surface = self.layout.surface
            self.all_layouts_coords = self.layout.all_layouts_coords + self.coordinates
            self.first_parent_menu = self.layout.first_parent_menu
        
        for item in self.floating_items:
            item.master_coordinates = item.coordinates + self.first_parent_menu.coordinatesMW
            item.update()
            
        if self.cached_coordinates is None and self.booted:
            self._regenerate_coordinates()
            
        if type(self) == LayoutType: self._dirty_rect = self._read_dirty_rects()
        
    def _regenerate_coordinates(self):
        for item in self.items + self.floating_items:
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
        mass = self.items + self.floating_items
        if id is None: return None
        return next((item for item in mass if item.id == id), None)
    
    def clone(self):
        return LayoutType(self._lazy_kwargs['size'], copy.deepcopy(self.style), self._lazy_kwargs['content'], **self.constant_kwargs)
