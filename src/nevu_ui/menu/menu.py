import pygame
import copy
import pyray as rl
from pygame._sdl2 import Texture
from functools import partial
from typing import Unpack

from nevu_ui.window import Window
from nevu_ui.components.layouts import LayoutType
from nevu_ui.components.widgets import Widget
from nevu_ui.presentation.color import SubThemeRole
from nevu_ui.core.state import nevu_state
from nevu_ui.fast.nvvector2 import NvVector2
from nevu_ui.core.size.rules import SizeRule
from nevu_ui.rendering.pygame.renderer import BackgroundRendererPygame
from nevu_ui.rendering.raylib.renderer import BackgroundRendererRayLib
from nevu_ui.core.enums import HoverState
from nevu_ui.utils import Cache, NevuEvent
from nevu_ui.presentation.style import Style, default_style, StyleKwargs
from nevu_ui.fast.logic.fast_logic import relm_helper, rel_helper, mass_rel_helper, vec_rel_helper

from nevu_ui.core.enums import (
    Quality, CacheType, EventType
)

class MenuRendererProxy:
    def __init__(self, menu):
        self.menu = menu
        self.clickable = False
        self.hoverable = False
        
    @property
    def _draw_borders(self): return True
    @property
    def _csize(self): return self.menu.rel(self.menu.size)
    @property
    def _hover_state(self): return HoverState.UN_HOVERED
    @property
    def subtheme_content(self): return self.menu._subtheme_content()
    @property
    def subtheme_border(self): return self.menu._subtheme_border()
    def __getattr__(self, name): return getattr(self.menu, name)

class MenuLayoutProxy:
    def __init__(self, menu):
        self.menu = menu
        self.first_parent_menu = self.menu
        self.booted = True
    @property
    def original_size(self): return self.menu.size
    def __getattr__(self, name): return getattr(self.menu, name)

class Menu:
    def __init__(self, window: Window | None, size: list | tuple | NvVector2, style: Style = default_style, alt: bool = False, layout = None): 
        self._absolute_coordinates = NvVector2(0,0)
        self.alt = alt
        self._init_primary(window, style)
        if not self._window: return
        self._renderer_proxy = MenuRendererProxy(self)
        if self._window.is_dtype.raylib: self._renderer = BackgroundRendererRayLib(self._renderer_proxy) #type: ignore
        else: self._renderer = BackgroundRendererPygame(self._renderer_proxy) #type: ignore
        self._borrow_from_nevuobj()
        self._borrow_from_widget()
        self._borrow_from_layout()
        self._init_size(size)
        self._init_secondary()
        self._init_tertiary(size)
        self._init_subtheme(alt)
        self._init_dirty_rects()
        if layout: self.layout = layout
    
    def relx(self, num: int | float, min: int | None = None, max: int| None = None) -> int | float:
        return rel_helper(num, self._resize_ratio.x, min, max)

    def rely(self, num: int | float, min: int | None = None, max: int| None = None) -> int | float:
        return rel_helper(num, self._resize_ratio.y, min, max)

    def relm(self, num: int | float, min: int | None = None, max: int | None = None) -> int | float:
        return relm_helper(num, self._resize_ratio.x, self._resize_ratio.y, -1.0, -1.0)
    
    def rel(self, mass: NvVector2, vector: bool = True) -> NvVector2:  
        return vec_rel_helper(mass, self._resize_ratio.x, self._resize_ratio.y) # type: ignore
    
    def _borrow_from_nevuobj(self):
        pass
    def _borrow_from_widget(self):
        self._clear_surfaces = partial(Widget.clear_surfaces, self) #type: ignore
        self._clear_all = partial(Widget.clear_all, self) #type: ignore
    def _borrow_from_layout(self):
        self._layout_proxy = MenuLayoutProxy(self)
        self._convert_item_coord = partial(LayoutType._convert_item_coord, self._layout_proxy) #type: ignore
        self._parse_fillx = partial(LayoutType._parse_fillx, self._layout_proxy) #type: ignore
        self._parse_gcx = partial(LayoutType._parse_gcx, self._layout_proxy) #type: ignore
        self._parse_vx =  partial(LayoutType._parse_vx, self._layout_proxy) #type: ignore
        self._percent_helper = partial(LayoutType._percent_helper)
        self._read_item_coords = partial(LayoutType.read_item_coords, self._layout_proxy) #type: ignore
    def _borrow_func(self, func, master = None):
        return partial(func, master or self)
    
    @property
    def _texture(self): return self.cache.get_or_exec(CacheType.Texture, self.convert_texture)
    
    def convert_texture(self, surf = None):
        if nevu_state.renderer is None: raise ValueError("Window not initialized!")
        surface = surf or self._surface
        assert self._window, "Window not initialized!"
        if self._window.is_dtype.sdl:
            texture = Texture(nevu_state.renderer, (self.size*self._resize_ratio).to_tuple(), target=True) #type: ignore
            nevu_state.renderer.target = texture
            ntext = Texture.from_surface(nevu_state.renderer, surface) #type: ignore
            nevu_state.renderer.blit(ntext, pygame.Rect(0,0, *(self.size*self._resize_ratio).to_tuple()))
            nevu_state.renderer.target = None
        elif self._window.is_dtype.raylib:
            #texture = convert_surface_to_gl_texture(self._window._display.renderer, surface) #type: ignore
            raise ValueError("Raylib texture conversion is not supported for now Sowwy >W<")
        return texture #type: ignore
    
    def _update_size(self): return (self.size * self._resize_ratio).to_pygame()

    @property
    def _pygame_size(self) -> list:
        result = self.cache.get_or_exec(CacheType.RelSize, self._update_size)
        return result or [0, 0]
    
    def _clear_rl_specific(self):
        if self._window.is_dtype.raylib and self.cache.get(CacheType.Scaled_Background):
            rl.unload_render_texture(self.cache.get(CacheType.Scaled_Background)) #type: ignore
        Widget._clear_rl_specific(self) #type: ignore
    
    def _init_primary(self, window: Window | None, style: Style):
        self._window = window
        self.window_surface = None
        self.cache = Cache()
        self.quality = Quality.Decent
        self.style = style
        self._subtheme_role = self.style.subtheme_role or SubThemeRole.PRIMARY
        if self._window: self._window.add_event(NevuEvent(self, self._resize, EventType.Resize))

    def _init_size(self, size: list | tuple | NvVector2):
        initial_size = list(size) #type: ignore
        for i in range(len(initial_size)):
            item = initial_size[i]
            if isinstance(item, SizeRule):
                converted, is_ruled = self._convert_item_coord(item, i)
                initial_size[i] = float(converted)
            else: initial_size[i] = float(item)
        self.size = NvVector2(initial_size)
        self.coordinates = NvVector2()
        self._resize_ratio = NvVector2(1, 1)
        self._layout: LayoutType | None = None

    def _init_secondary(self):
        self._changed = True
        self._update_surface()
        self.isrelativeplaced = False
        self.relative_percent_x = None
        self.relative_percent_y = None
        self._enabled = True
        self.will_resize = False

    def _init_tertiary(self, size):
        self.first_window_size = self._window.size if self._window else NvVector2(0, 0)
        self.first_size = size
        self.first_coordinates = NvVector2(0, 0)
        self._opened_sub_menu = None


    def _init_subtheme(self, alt):
        if not alt:
            self._subtheme_border = self._main_subtheme_border
            self._subtheme_content = self._main_subtheme_content
        else:
            self._subtheme_border = self._alt_subtheme_border
            self._subtheme_content = self._alt_subtheme_content

    def _init_dirty_rects(self):
        self._dirty_rects = []
        if self._window:
            self._window._next_update_dirty_rects.append(pygame.Rect(0, 0, *self.size))
        
    def _proper_load_layout(self):
        if not self._layout: return
        self._layout._boot_up()
        
    def _main_subtheme_content(self): return self._subtheme.oncolor
    def _main_subtheme_border(self): return self._subtheme.color
    def _alt_subtheme_content(self): return self._subtheme.oncontainer
    def _alt_subtheme_border(self): return self._subtheme.container
    
    @property
    def _background(self):
        # sourcery skip: assign-if-exp, inline-immediately-returned-variable, lift-return-into-if
        result1 = lambda: self._renderer._generate_background(sdf=True, only_content=True)
        if nevu_state.renderer: result = lambda: self.convert_texture(result1())
        else: result = result1
        return result

    @property
    def _subtheme(self): return self.style.colortheme.get_subtheme(self._subtheme_role)
    
    @property
    def enabled(self) -> bool: return self._enabled
    @enabled.setter
    def enabled(self, value: bool): self._enabled = value
        
    @property
    def absolute_coordinates(self) -> NvVector2: return self._absolute_coordinates
    @absolute_coordinates.setter
    def absolute_coordinates(self, coordinates: NvVector2):
        if self._window is None: raise ValueError("Window is not initialized!")
        #print(coordinates, self._window._offset)
        self._absolute_coordinates = coordinates + self._window._offset
    def _abs_coordinates_update(self): self.absolute_coordinates = self.coordinates
        
    def open_submenu(self, menu, style: Style|None = None, *args):
        assert isinstance(menu, Menu)
        self._opened_sub_menu = menu
        self._args_menus_to_draw = []
        for item in args: self._args_menus_to_draw.extend(item)
        if style: self._opened_sub_menu.apply_style_to_layout(style)
        self._opened_sub_menu._resize_with_ratio(self._resize_ratio)
    def close_submenu(self): self._opened_sub_menu = None
        
    def _update_surface(self):
        if self._window.is_dtype.raylib:
            if hasattr(self, '_surface'): 
                rl.unload_render_texture(self._surface)
            self._surface = rl.load_render_texture(*(self.size*self._resize_ratio).get_int_tuple())
            return
        if self.style.borderradius>0:self._surface = pygame.Surface(self._pygame_size, pygame.SRCALPHA)
        else: self._surface = pygame.Surface(self._pygame_size)
        if self.style.transparency: self._surface.set_alpha(self.style.transparency)

    def _resize(self, size: NvVector2):
        self._clear_surfaces()
        self._changed = True
        self.cache.clear_selected(whitelist = [CacheType.RelSize])
        self._resize_ratio = NvVector2([size[0] / self.first_window_size[0], size[1] / self.first_window_size[1]])
        if self._window is None: raise ValueError("Window is not initialized!")
        if self.isrelativeplaced:
            window_size = self._window.size - NvVector2(self._window._crop_width_offset, self._window._crop_height_offset)
            target_pos = window_size * (NvVector2(self.relative_percent_x, self.relative_percent_y) / 100) #type: ignore
            widget_center_offset = self.rel(self.size) / 2

            self.coordinates = target_pos - widget_center_offset
        self._abs_coordinates_update()
        self._update_surface()
        
        if self._layout:
            self._layout._resize(self._resize_ratio)
            self._layout.coordinates = NvVector2(self.rel(self.size - self._layout.size) / 2)
            self._layout.update()
            self._layout.draw()
            
        if self.style.transparency: self._surface.set_alpha(self.style.transparency) #type: ignore

    def _resize_with_ratio(self, ratio: NvVector2):
        self._clear_surfaces()
        self._changed = True
        self._resize_ratio = ratio
        self._abs_coordinates_update()
        if self.style.transparency: self._surface.set_alpha(self.style.transparency) #type: ignore
        if self._layout: self._layout._resize(self._resize_ratio)
        
    @property
    def style(self) -> Style: return self._style
    @style.setter
    def style(self, style: Style): self._style = copy.copy(style)

    def apply_style_to_layout(self, style: Style):
        self._changed = True
        self.style = style
        self.cache.clear()
        self._init_subtheme(self.alt)
        if self._layout: self._layout.apply_style_to_childs(style)
    
    def apply_style_patch_to_layout(self, **patch: Unpack[StyleKwargs]):
        self._changed = True
        self.style = self.style(**patch)
        self.cache.clear()
        self._init_subtheme(self.alt)
        if self._layout: self._layout.apply_style_patch_to_childs(**patch)
    
    @property
    def layout(self): return self._layout
    @layout.setter
    def layout(self, layout):
        assert self._window, "Window is not set!"
        if layout._can_be_main_layout:
            if self._layout: self._layout.kill()
            self._read_item_coords(layout)
            layout._master_z_handler = self._window.z_system
            layout._init_start()
            layout._connect_to_menu(self)
            layout.first_parent_menu = self
            layout.coordinates = NvVector2(self.size[0]/2 - layout.size[0]/2, self.size[1]/2 - layout.size[1]/2)
            layout.absolute_coordinates = layout.coordinates + self.absolute_coordinates
            layout._boot_up()
            
            layout._resize(self._resize_ratio)
            self._layout = layout
        else: raise ValueError(f"Layout {type(layout).__name__} can't be main")
        
    def _set_layout_coordinates(self, layout):
        layout.coordinates = NvVector2(self.size[0]/2 - layout.size[0]/2, self.size[1]/2 - layout.size[1]/2)
        
    def set_coordinates(self, x: int, y: int):
        self.coordinates = NvVector2(x, y)
        self._on_set_coordinates(False, None, None)
        
    def set_coordinates_relative(self, percent_x: int, percent_y: int):
        if self._window is None: raise ValueError("Window is not initialized!")
        self.coordinates = NvVector2([(self._window.size[0]-self._window._crop_width_offset)/100*percent_x-self.size[0]/2,
                                    (self._window.size[1]-self._window._crop_height_offset)/100*percent_y-self.size[1]/2])
        self._on_set_coordinates(True, percent_x, percent_y)

    def _on_set_coordinates(self, arg0, arg1, arg2):
        self._abs_coordinates_update()
        self.isrelativeplaced = arg0
        self.relative_percent_x = arg1
        self.relative_percent_y = arg2
        self.first_coordinates = self.coordinates

    def draw(self):
        if not self.enabled or not self._window: return
        assert self._surface
        scaled_bg = self.cache.get_or_exec(CacheType.Scaled_Background, self._background)
        if nevu_state.renderer:
            if self._window.is_dtype.sdl:
                assert isinstance(scaled_bg, Texture)
                if self._layout is not None:
                    nevu_state.renderer.target = self._texture
                    nevu_state.renderer.blit(scaled_bg, self.get_rect())
                    self._layout.draw()
                    nevu_state.renderer.target = None
                self._window._display.blit(self._texture, self.absolute_coordinates.to_int().to_tuple()) #type: ignore
                if self._opened_sub_menu:
                    for item in self._args_menus_to_draw: item.draw()
                    self._opened_sub_menu.draw()
                return 
            
        elif self._window.is_dtype.raylib:
            if self._layout is not None:
                self._layout._rl_predraw_widgets()
                rl.begin_texture_mode(self._surface) #type: ignore
                #rl.begin_blend_mode(rl.BlendMode.BLEND_ALPHA_PREMULTIPLY)
                rl.clear_background(rl.BLANK)
                self._window.display.blit(scaled_bg.texture, (0, 0))
                self._layout.draw()
                #rl.end_blend_mode()
                rl.end_texture_mode()
            self._window._display.blit(self._surface.texture, self.absolute_coordinates.get_int_tuple()) #type: ignore
            if self._opened_sub_menu:
                for item in self._args_menus_to_draw: item.draw()
                self._opened_sub_menu.draw()
            return
            
        if scaled_bg:
            self._surface.blit(scaled_bg, (0, 0))
        
        if self._layout is not None:
            self._layout.draw() 
        self._window._display.blit(self._surface, self.absolute_coordinates.get_int_tuple()) #type: ignore
        
        if self._opened_sub_menu:
            for item in self._args_menus_to_draw: item.draw()
            self._opened_sub_menu.draw()

    def update(self):
        if not self.enabled: return
        if self._window is None: return
        assert isinstance(self._window, Window)
        
        if len(self._dirty_rects) > 0:
            self._window._next_update_dirty_rects.extend(self._dirty_rects)
            self._dirty_rects = []
            
        assert isinstance(self._opened_sub_menu, (Menu, type(None)))
        if self._opened_sub_menu:
            self._opened_sub_menu.update()
            return
        if self._layout: 
            #print(self._layout.get_param_strict("id").value)
           # if self._layout.get_param_strict("id").value == "scr":
                
              #  print(self._layout.coordinates + self.absolute_coordinates)
            self._layout.absolute_coordinates = self._layout.coordinates + self.absolute_coordinates
            self._layout.update(nevu_state.current_events)
           # print("updata")
        
    def get_rect(self) -> pygame.Rect: return pygame.Rect((0,0), self.size * self._resize_ratio)
    
    def kill(self):
        self._enabled = False
        
        if self._layout:
            self._layout.kill()
            for item in self._layout._all_items():
                item.kill()
            self._layout = None
        
        if hasattr(self, '_opened_sub_menu') and self._opened_sub_menu:
            self._opened_sub_menu.kill()
            self._opened_sub_menu = None

        if hasattr(self, '_args_menus_to_draw'):
            for item in self._args_menus_to_draw: item.kill()
            self._args_menus_to_draw.clear()
            
        self.cache.clear()
        self._surface = None
        self._window = None
        
        if nevu_state.window: nevu_state.window.z_system.mark_dirty()