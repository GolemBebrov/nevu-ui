from __future__ import annotations
import copy
from itertools import chain

from typing import (
    TypeGuard, Iterator, Unpack, NotRequired, Any, TYPE_CHECKING
)

if TYPE_CHECKING: 
    from nevu_ui.menu import Menu
import nevu_ui.core.modules as md
from nevu_ui.core import Annotations
from nevu_ui.components.widgets import Widget
from nevu_ui.overlay import overlay
from nevu_ui.fast.logic.fast_logic import _light_update_helper, rl_predraw_widgets
from nevu_ui.fast.nvvector2 import NvVector2
from nevu_ui.core.state import nevu_state
from nevu_ui.core.enums import ConstantLayer
from nevu_ui.core.classes import BorderConfig
from nevu_ui.components.nevuobj import NevuObject, NevuObjectKwargs
from nevu_ui.components.layouts.typehints import LayoutTemplate

from nevu_ui.core.size.rules import (
    SizeRule, _all_fillx, _all_vx, _all_gcx, Fill, FillW, FillH, CFill, CFillW, CFillH, Vh, Vw, Cvh, Cvw
)

from nevu_ui.presentation.style import (
    Style, default_style, StyleKwargs
)

class LayoutTypeKwargs(NevuObjectKwargs):
    borders: NotRequired[BorderConfig]
    
class LayoutType(NevuObject):
    items: list[NevuObject]
    floating_items: list[NevuObject]
    content_type = list
    borders: BorderConfig | None
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
    
    def _rl_border_draw_call(self):
        if not self.get_nvrect().collide_rect(nevu_state.window.get_nvrect()): return
        norm_size = self._csize.to_round().get_int_tuple()
        abs_coords = self.absolute_coordinates.to_round()
        borders: BorderConfig = self.get_param_strict("borders").value
        if len(borders.color) == 3: borders.color = (*borders.color, 255)
        md.rl.draw_rectangle_lines_ex([*abs_coords, *norm_size], self.relm(borders.width), borders.color)
        if borders.name:
            if borders.font: md.rl.draw_text_ex(borders.font, borders.name or "", abs_coords.get_int_tuple(), borders.font.baseSize, 0, borders.color)
            else: md.rl.draw_text(borders.name or "", *abs_coords.get_int_tuple(), 20, borders.color)

    def _rl_predraw_widgets(self):
        if self.get_param_strict("borders").value and self._need_update_overlay:
            self._need_update_overlay = False
            abs_coords = self.absolute_coordinates.to_round()
            overlay.add_draw_call(self, self._rl_border_draw_call, abs_coords, -1)
        rl_predraw_widgets(self.items, LayoutType, Widget)
    
    def _draw_item_pygame(self, item: NevuObject, coordinates: NvVector2):
        assert isinstance(self.surface, md.pygame.Surface), "Cant use _draw_widget with uninitialized surface"
        self.surface.blit(item.surface, coordinates.to_tuple()) #type: ignore
    
    def _draw_item_sdl(self, item: NevuObject, coordinates: NvVector2):
        if not hasattr(item, '_sdl2_texture'): return
        if not item._sdl2_texture: return
        assert item._sdl2_texture
        nevu_state.window.display.blit(item._sdl2_texture, (coordinates.to_tuple(), item._csize.to_tuple())) #type: ignore
    
    def _draw_item_raylib(self, item: NevuObject, coordinates: NvVector2):
        display = nevu_state.window.display
        assert nevu_state.window.is_raylib(display)
        display.fast_blit_pro(item.surface.texture, coordinates.get_int_tuple(), flip = True)
    
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
        elif self.is_layout(item): 
            item.draw()
            return
        
        if not isinstance(item, Widget): return
        
        coordinates = item.coordinates.xy
        if multiply: coordinates *= multiply
        if add: coordinates += add
        
        self._draw_item(item, coordinates)
    
    def _draw_widget_optimized(self, item: NevuObject):
        assert isinstance(item, NevuObject), f"Cant use _draw_widget on {type(item)}"
        assert nevu_state.window, "Window not initialized!"
        if not nevu_state.window.is_dtype.raylib:
            item.draw()
            if self.is_layout(item): return
        elif self.is_layout(item): 
            item.draw()
            return
        if not isinstance(item, Widget): return
        self._draw_item(item, item.coordinates)
    
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

    def __init__(self, size: Annotations.nevuobj_size, style: Style = default_style, content: list | None  = None, **constant_kwargs: Unpack[LayoutTypeKwargs]):
        super().__init__(size, style, **constant_kwargs)
        self._template = self._create_template(size, content)
    
    def _create_template(self, size: Annotations.nevuobj_size, content: list | None): # type: ignore
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
        self._need_update_overlay = True
        
    def _init_objects(self):
        super()._init_objects()
        self.first_parent_menu = None
        self.menu = None
        self.layout = None
        self._last_border_name = None
        self._draw_item = lambda *args, **kwargs: None
        if nevu_state.window.is_dtype.raylib:
            self._draw_item = self._draw_item_raylib
        elif nevu_state.window.is_dtype.pygame:
            self._draw_item = self._draw_item_pygame
        elif nevu_state.window.is_dtype.sdl:
            self._draw_item = self._draw_item_sdl 
    
    def _add_params(self):
        super()._add_params()
        #self._add_param("border_name", str, "", layer = ConstantLayer.Complicated)# setter = self._border_name_setter)
        #self._add_param("borders", bool, False, layer = ConstantLayer.Basic)
        self._add_param("borders", BorderConfig | type(None), None, layer = ConstantLayer.Complicated, setter=self._borders_setter)
    
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
            self.first_parent_menu.absolute_coordinates if self.first_parent_menu else NvVector2.from_xy(0,0),
            NvVector2.from_xy(add_x, add_y))

    def _coordinates_setter(self, coordinates: NvVector2):
        self._clear_cached_coordinates_noregen()
        return True
    
    def _borders_setter(self, value: BorderConfig):
        if not value.font: return
        if nevu_state.window.is_dtype.raylib:
            rlfont = value.font
            if not hasattr(rlfont, "glyphCount"):
                raise ValueError("font must be a raylib font")
        else:
            pgfont = value.font
            if not isinstance(pgfont, md.pygame.font.Font):
                raise ValueError("font must be a md.pygame font")
    
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
       # print(w_size, type(item).__name__)
        x, y = w_size
        x, is_x_rule = self._convert_item_coord(x, 0)
        y, is_y_rule = self._convert_item_coord(y, 1)

        item._template['size'] = [x,y]

    def _start_item(self, item: NevuObject):
        if isinstance(item, LayoutType):
            item._connect_to_layout(self)
        if self.booted == False:  return
        item._wait_mode = False
        item._init_start()

    def _resize(self, resize_ratio: NvVector2):
        super()._resize(resize_ratio)
        self.cached_coordinates = None
        self._border_font_surface = None
        self._need_update_overlay = True
        for item in self._all_items():
            assert isinstance(item, (Widget, LayoutType))
            item._resize(self._resize_ratio)

    def _clear_cached_coordinates_noregen(self):
        self.cached_coordinates = None
    
    def _clear_cached_coordinates(self):
        pass

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
        if  self._need_update_overlay and not nevu_state.window.is_dtype.raylib and self.borders:
            assert self.surface
            assert nevu_state.window
            if not self.borders.font:
                self.border_font = md.pygame.sysfont.SysFont("Arial", int(self.relx(self.first_parent_menu._style.font_size))) #type: ignore
            else:
                self.border_font = self.borders.font
            self._border_font_surface = self.border_font.render(self.borders.name, True, self.borders.color)
            #self.surface.blit(self._border_font_surface, [self.coordinates[0], self.coordinates[1] - self._border_font_surface.get_height()])
            #md.pygame.draw.rect(self.surface, self.borders.color, [self.coordinates[0], self.coordinates[1], self._csize.x, self._csize.y], 1)
            #elif nevu_state.window.is_dtype.sdl:
            surf = md.pygame.Surface(self._csize.to_tuple(), flags = md.pygame.SRCALPHA)
            surf.fill((0,0,0,0))
            if hasattr(self, "border_font_surface"):
                surf.blit(self._border_font_surface, [0, 0])
                md.pygame.draw.rect(surf, self.borders.color, [0, 0, self._csize.x, self._csize.y], 1)
            overlay.add_element(self, surf, self.absolute_coordinates.to_round(), -1)
                
        for item in self.floating_items:
            self._draw_widget(item, self.rel(item.coordinates))

    def _logic_update(self):
        super()._logic_update()
        if overlay.has_element(self):
            abs_coordinates = self.absolute_coordinates
            if overlay.get_element_strict(self)[1] != abs_coordinates.to_round():
                overlay.change_coordinates(self, abs_coordinates)
                
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
    
    def _connect_to_parent(self, attr: tuple[str, Any], surface: Any, first_parent_menu: Menu | None):
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
    
    def kill(self):
        super().kill()
        for item in self._all_items():
            item.kill()
        if self._template.content:
            content = self._template.content
            if isinstance(content, dict):
                for item in content.values(): item.kill()
            elif isinstance(content, list):
                for item in content:
                    if isinstance(item, tuple): item[-1].kill()
        self.items.clear()