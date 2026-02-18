from __future__ import annotations
import copy
import pygame
from itertools import chain

from typing import (
    TypeGuard, Iterator, Unpack, NotRequired, Any, TYPE_CHECKING
)

if TYPE_CHECKING: from nevu_ui.menu import Menu
from nevu_ui.components.widgets import Widget
from nevu_ui.overlay import overlay
from nevu_ui.fast.logic import _light_update_helper
from nevu_ui.fast.nvvector2 import NvVector2
from nevu_ui.core.state import nevu_state
from nevu_ui.core.enums import ConstantLayer
from nevu_ui.components.nevuobj import NevuObject, NevuObjectKwargs
from nevu_ui.components.layouts.typehints import LayoutTemplate

from nevu_ui.core.size.rules import (
    SizeRule, _all_fillx, _all_vx, _all_gcx, Fill, FillW, FillH, CFill, CFillW, CFillH, Vh, Vw, Cvh, Cvw
)

from nevu_ui.presentation.style import (
    Style, default_style, StyleKwargs
)

class LayoutTypeKwargs(NevuObjectKwargs):
    border_color: NotRequired[tuple]
    borders: NotRequired[bool]
    border_name: NotRequired[str]
    
class LayoutType(NevuObject):
    items: list[NevuObject]
    floating_items: list[NevuObject]
    content_type = list
    border_color: tuple
    layout: LayoutType | None
    menu: Menu | None
    

    def _all_items(self) -> Iterator[NevuObject]:
        return chain(self.items, self.floating_items)

    def _unconnected_layout_error(self, item):
        return ValueError(f"Cant use {item} in unconnected layout {self}")

    def _uninitialized_layout_error(self, item):
        return ValueError(f"Cant use {item} in uninitialized layout {self}")
    
    def _get_item_abs_coords(self, item: NevuObject):
        assert isinstance(item, NevuObject), f"Can't use _get_item_master_coordinates on {type(item)}"
        assert self.first_parent_menu, self._unconnected_layout_error(item)
        return item.coordinates + self.first_parent_menu.absolute_coordinates #+ NvVector2(self.first_parent_menu._window._crop_width_offset, self.first_parent_menu._window._crop_height_offset)

    def _rl_predraw_widgets(self):
        for item in self._all_items():
            if self.is_layout(item):
                item._rl_predraw_widgets()
            elif self.is_widget(item):
                if item._changed:
                    item.draw()
    
    def _draw_widget(self, item: NevuObject, multiply: NvVector2 | None = None, add: NvVector2 | None = None):
        assert isinstance(item, NevuObject), f"Cant use _draw_widget on {type(item)}"
        assert nevu_state.window, "Window not initialized!"
        if item._wait_mode:
            self.read_item_coords(item)
            self._start_item(item)
            return
        
        if not nevu_state.window.is_dtype.raylib:
            item.draw()
            if self.is_layout(item): return
        
        coordinates = item.coordinates.xy
        if multiply: coordinates *= multiply
        if add: coordinates += add
        
        if not isinstance(item, Widget): return
        
        if nevu_state.window.is_dtype.sdl: 
            if not hasattr(item, 'texture'): return
            assert item.texture
            nevu_state.renderer.blit(item.texture, pygame.Rect((coordinates).to_tuple(), item._csize.to_tuple())) #type: ignore
        elif nevu_state.window.is_dtype.pygame:
            assert isinstance(self.surface, pygame.Surface), "Cant use _draw_widget with uninitialized surface"
            self.surface.blit(item.surface, coordinates.to_tuple()) #type: ignore
        elif nevu_state.window.is_dtype.raylib:
            display = nevu_state.window.display
            assert nevu_state.window.is_raylib(display)
            display.blit_rect_vec(item.surface.texture, coordinates.get_int_tuple()) #type: ignore

    def _boot_up(self):
        self.booted = True
        for item in self._all_items():
            assert isinstance(item, (Widget, LayoutType))
            self.read_item_coords(item)
            self._start_item(item)
            item.booted = True
            item._boot_up()

    def __getitem__(self, id: str) -> NevuObject:
        return self.get_item_by_id_strict(id)

    def __init__(self, size: NvVector2 | list, style: Style = default_style, content: list | None  = None, **constant_kwargs: Unpack[LayoutTypeKwargs]):
        super().__init__(size, style, **constant_kwargs)
        self._template = self._create_template(size, content)
    
    def _create_template(self, size: NvVector2 | list, content: list | None): # type: ignore
        return LayoutTemplate(size, content)
    
    def _init_lists(self):
        super()._init_lists()
        self.floating_items = []
        self.items = []
        self.cached_coordinates = None
        self.all_layouts_coords = NvVector2()
        
    def _init_booleans(self):
        super()._init_booleans()
        self._can_be_main_layout = True
        
    def _init_objects(self):
        super()._init_objects()
        self.first_parent_menu = None
        self.menu = None
        self.layout = None
        self.surface: pygame.Surface | None = None
    
    def _add_params(self):
        super()._add_params()
        self._add_param("border_name", str, "", layer=ConstantLayer.Complicated)
        self._add_param("borders", bool, False, layer=ConstantLayer.Complicated)
        self._add_param("border_color", tuple, (255, 255, 255))
    
    def _lazy_init(self, size: NvVector2 | list, content: content_type | None = None):
        super()._lazy_init(size)
        if content and type(self) == LayoutType:
            for i in content:
                self.add_item(i)

    def add_items(self, content: content_type):
        raise NotImplementedError("Subclasses of LayoutType may implement add_items()")
    
    def _base_light_update(self, add_x: int | float = 0, add_y: int | float = 0 ):
        if self.cached_coordinates is None or len(self.items) != len(self.cached_coordinates): return
        _light_update_helper(
            self.items,
            self.cached_coordinates or [],
            self.first_parent_menu.absolute_coordinates if self.first_parent_menu else NvVector2(),
            NvVector2(add_x, add_y))


    def _coordinates_setter(self, coordinates: NvVector2):
        self.add_next_frame_action(self._clear_cached_coordinates_noregen)
        return True

    @property
    def borders(self): return self.get_param_strict("borders").value
    @borders.setter
    def borders(self, value: bool): self.set_param_value("borders", value)
    @property
    def border_name(self) -> str: return self.get_param_strict("border_name").value
    @border_name.setter
    def border_name(self, name: str):
        self.set_param_value("border_name", name)
        if self.first_parent_menu:
            try:
                self.border_font = pygame.sysfont.SysFont("Arial", int(self.relx(self.first_parent_menu._style.fontsize)))
                self.border_font_surface = self.border_font.render(self.get_param_strict("border_name").value, True, self.border_color)
            except Exception as e: print(f"Error with border_name: {e}")
    
    @staticmethod
    def _percent_helper(size, value): return size / 100 * value
    
    def _parse_vx(self, coord: SizeRule) -> tuple[float, bool] | None:
        if self.first_parent_menu is None: raise self._unconnected_layout_error("Vx like coords")
        if self.first_parent_menu._window is None: raise self._uninitialized_layout_error("Vx like coords")
        if type(coord) == Cvw: return self._percent_helper(self.first_parent_menu._window.size.x, coord.value), True
        elif type(coord) == Cvh: return self._percent_helper(self.first_parent_menu._window.size.y, coord.value), True
        elif type(coord) == Vw: return self._percent_helper(self.first_parent_menu._window.original_size.x, coord.value), True
        elif type(coord) == Vh: return self._percent_helper(self.first_parent_menu._window.original_size.y, coord.value), True
    
    def _parse_fillx(self, coord: SizeRule, pos: int) -> tuple[float, bool] | None:
        if self.first_parent_menu is None: raise self._unconnected_layout_error("FillX coords")
        if self.first_parent_menu._window is None: raise self._uninitialized_layout_error("FillX coords")
        if  type(coord) == Fill: return self._percent_helper(self.original_size[pos], coord.value), True
        elif type(coord) == FillW: return self._percent_helper(self.original_size.x, coord.value), True
        elif type(coord) == FillH: return self._percent_helper(self.original_size.y, coord.value), True
        elif type(coord) == CFill: return self._percent_helper(self._rsize[pos], coord.value), True
        elif type(coord) == CFillW: return self._percent_helper(self._rsize.x, coord.value), True
        elif type(coord) == CFillH: return self._percent_helper(self._rsize.y, coord.value), True
    
    def _parse_gcx(self, coord, pos: int):
        raise ValueError(f"Handling for SizeRule '{type(coord).__name__}' is only Grid feature")
    
    def _convert_item_coord(self, coord, pos: int = 0) -> tuple[float, bool]:
        if not isinstance(coord, SizeRule): return coord, False
        result = None
        if type(coord) in _all_vx:
            result = self._parse_vx(coord)
        elif type(coord) in _all_fillx: 
            result = self._parse_fillx(coord, pos)
        elif type(coord) in _all_gcx:
            result = self._parse_gcx(coord, pos)
        
        if result is None: raise ValueError(f"Handling for SizeRule '{type(coord).__name__}' is not implemented")
        
        return result

    def read_item_coords(self, item: NevuObject):
        if self.booted == False: return
        w_size = item._template['size']
        x, y = w_size
        x, is_x_rule = self._convert_item_coord(x, 0)
        y, is_y_rule = self._convert_item_coord(y, 1)

        item._template['size'] = [x,y]

    def _start_item(self, item: NevuObject):
        if isinstance(item, LayoutType):
            item._connect_to_layout(self)
        if self.booted == False:  return
        item._wait_mode = False; item._init_start()

    def _resize(self, resize_ratio: NvVector2):
        super()._resize(resize_ratio)
        self.cached_coordinates = None
        for item in self._all_items():
            assert isinstance(item, (Widget, LayoutType))
            item._resize(self._resize_ratio)
        self.border_name = self.border_name

    def _clear_cached_coordinates_noregen(self):
        self.cached_coordinates = None
    
    def _clear_cached_coordinates(self):
        self._regenerate_coordinates()
        if self.layout is None: return
        self.layout._regenerate_coordinates()

    @staticmethod
    def is_layout(item: NevuObject) -> TypeGuard[LayoutType]: return isinstance(item, LayoutType)
    @staticmethod
    def is_widget(item: NevuObject) -> TypeGuard[Widget]: return isinstance(item, Widget)

    def _on_item_add(self, item: NevuObject): pass

    def _item_add(self, item: NevuObject):
        if not item.get_param_strict("single_instance").value: item = item.clone()
        if self.is_layout(item): 
            item._connect_to_layout(self)
        self.read_item_coords(item)
        self._start_item(item)
        if self.booted:
            item.booted = True
            item._boot_up()
            item._resize(self._resize_ratio)
        return item
    
    def _after_item_add(self, item: NevuObject):
        if self.layout: self.layout._on_item_add(item)
            
    def add_item(self, item: NevuObject):
        item = self._item_add(item)
        self.items.append(item)
        self.cached_coordinates = None
        self._after_item_add(item)
        self._on_item_add(item)
        return item
    
    def add_floating_item(self, item: NevuObject):
        item = self._item_add(item)
        self.floating_items.append(item)
        self.cached_coordinates = None
        self._after_item_add(item)
        self._on_item_add(item)
        return item
    
    @property
    def _global_coordinates(self):
        assert self.first_parent_menu
        if not self.layout:
            return self.absolute_coordinates + self.first_parent_menu.absolute_coordinates
        return self.absolute_coordinates
    
    def apply_style_to_childs(self, style: Style):
        for item in self._all_items():
            assert isinstance(item, (Widget, LayoutType))
            if self.is_widget(item): 
                item.style = style
                item.cache.clear()
            elif self.is_layout(item): 
                item.apply_style_to_childs(style)
                
    def apply_style_patch_to_childs(self, **patch: Unpack[StyleKwargs]):
        for item in self._all_items():
            assert isinstance(item, (Widget, LayoutType))
            if self.is_widget(item): 
                item.style = item.style(**patch)
                item.cache.clear()
            elif self.is_layout(item): 
                item.apply_style_patch_to_childs(**patch)

    def _primary_draw(self):
        super()._primary_draw()
        if self.borders and not nevu_state.window.is_dtype.raylib:
            assert self.surface
            assert nevu_state.window
           
            if nevu_state.window.is_legacy(nevu_state.window.display):
                if hasattr(self, "border_font_surface") and self.border_font_surface:
                    #print(self.border_font_surface.size)
                    self.surface.blit(self.border_font_surface, [self.coordinates[0], self.coordinates[1] - self.border_font_surface.get_height()])
                    pygame.draw.rect(self.surface, self.border_color, [self.coordinates[0], self.coordinates[1], self._csize.x, self._csize.y], 1)
            else:
                surf = pygame.Surface(self._csize.to_tuple(), flags = pygame.SRCALPHA)
                surf.fill((0,0,0,0))
                if hasattr(self, "border_font_surface"):
                    surf.blit(self.border_font_surface, [0, 0])
                    pygame.draw.rect(surf, self.border_color, [0, 0, self._csize.x, self._csize.y], 1)
                overlay.change_element(self, surf, self._global_coordinates, -1)
        for item in self.floating_items:
            self._draw_widget(item, self.rel(item.coordinates))

    def _logic_update(self):
        super()._logic_update()
        if overlay.has_element(self):
            overlay.change_coordinates(self, self.absolute_coordinates)
        if self.menu:
            self.surface = self.menu._surface #type: ignore
        elif self.layout: 
            self.surface = self.layout.surface
            self.first_parent_menu = self.layout.first_parent_menu
        
        for item in self.floating_items:
            assert self.first_parent_menu, self._unconnected_layout_error(item)
            item.absolute_coordinates = item.coordinates + self.first_parent_menu.absolute_coordinates
            item.update()
            
        if self.cached_coordinates is None and self.booted:
            self._regenerate_coordinates()
        
    def _regenerate_coordinates(self):
        for item in self._all_items():
            if not item._wait_mode: continue
            self.read_item_coords(item)
            self._start_item(item)
    
    def _connect_to_parent(self, attr: tuple[str, Any], surface: pygame.Surface | None, first_parent_menu: Menu | None):
        setattr(self, *attr)
        self.surface = surface
        self.first_parent_menu = first_parent_menu
        self.cached_coordinates = None
        self.add_next_frame_action(self._clear_cached_coordinates)
    
    def _connect_to_menu(self, menu: Menu): self._connect_to_parent(("menu", menu), menu._surface, menu) #type: ignore
    def _connect_to_layout(self, layout: LayoutType):  self._connect_to_parent(("layout", layout), layout.surface, layout.first_parent_menu)
        
        
    def get_item_by_id(self, id: str) -> NevuObject | None:
        if id is None: return None
        return next((item for item in self._all_items() if item.id == id), None)
    
    def get_item_by_id_strict(self, id: str) -> NevuObject:
        if id is None: raise ValueError("ID cannot be None")
        if result := next((item for item in self._all_items() if item.id == id), None):
            return result
        else: raise ValueError(f"Item with id {id} not found")
    
    def _create_clone(self):
        return self.__class__(self._template['size'], copy.deepcopy(self.style), copy.deepcopy(self._template['content']), **self.constant_kwargs)