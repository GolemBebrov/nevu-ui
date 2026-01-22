import pygame
import copy
from pygame._sdl2 import Texture
from functools import partial
from nevu_ui.nevuobj import NevuObject
from nevu_ui.window import Window
from nevu_ui.layouts import LayoutType
from nevu_ui.widgets import Widget
from nevu_ui.color import SubThemeRole
from nevu_ui.core.state import nevu_state
from nevu_ui.rendering.shader import convert_surface_to_gl_texture
from nevu_ui.fast.nvvector2 import NvVector2
from nevu_ui.size.rules import SizeRule
from nevu_ui.rendering.background_renderer import BackgroundRenderer
from nevu_ui.core.enums import HoverState
from nevu_ui.utils import Cache, NevuEvent
from nevu_ui.style import Style, default_style

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
    def subtheme_content(self): return self.menu._subtheme_content
    @property
    def subtheme_border(self): return self.menu._subtheme_border
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
        self._init_primary(window, style)
        if not self.window: return
        self._renderer_proxy = MenuRendererProxy(self)
        self._renderer = BackgroundRenderer(self._renderer_proxy) 
        self._borrow_from_nevuobj()
        self._borrow_from_widget()
        self._borrow_from_layout()
        self._init_size(size)
        self._init_secondary()
        self._init_tertiary(size)
        self._init_subtheme(alt)
        self._init_dirty_rects()
        if layout: self.layout = layout
    
    def _borrow_from_nevuobj(self):
        self.rel = partial(NevuObject.rel, self)
        self.relm = partial(NevuObject.relm, self) 
        self.relx = partial(NevuObject.relm, self)
        self.rely = partial(NevuObject.relm, self) 
    def _borrow_from_widget(self):
        self.clear_surfaces = partial(Widget.clear_surfaces, self) #type: ignore
        self.clear_all = partial(Widget.clear_all, self) #type: ignore
    def _borrow_from_layout(self):
        self._layout_proxy = MenuLayoutProxy(self)
        self._convert_item_coord = partial(LayoutType._convert_item_coord, self._layout_proxy)
        self._parse_fillx = partial(LayoutType._parse_fillx, self._layout_proxy)
        self._parse_gcx = partial(LayoutType._parse_gcx, self._layout_proxy)
        self._parse_vx =  partial(LayoutType._parse_vx, self._layout_proxy)
        self._percent_helper = partial(LayoutType._percent_helper) #
        self.read_item_coords = partial(LayoutType.read_item_coords, self._layout_proxy)
    def _borrow_func(self, func, master = None):
        master = master or self
        return partial(func, master)
    
    @property
    def _texture(self): return self.cache.get_or_exec(CacheType.Texture, self.convert_texture)
    
    def convert_texture(self, surf = None):
        if nevu_state.renderer is None: raise ValueError("Window not initialized!")
        surface = surf or self.surface
        assert self.window, "Window not initialized!"
        if self.window._gpu_mode and not self.window._open_gl_mode:
            texture = Texture(nevu_state.renderer, (self.size*self._resize_ratio).to_tuple(), target=True) #type: ignore
            nevu_state.renderer.target = texture
            ntext = Texture.from_surface(nevu_state.renderer, surface) #type: ignore
            nevu_state.renderer.blit(ntext, pygame.Rect(0,0, *(self.size*self._resize_ratio).to_tuple()))
            nevu_state.renderer.target = None
        elif self.window._open_gl_mode:
            texture = convert_surface_to_gl_texture(self.window._display.renderer, surface) #type: ignore
            raise ValueError("OpenGL is not supported for now Sowwy >W<")
        return texture #type: ignore
    
    def _update_size(self): return (self.size * self._resize_ratio).to_pygame()

    @property
    def _pygame_size(self) -> list:
        result = self.cache.get_or_exec(CacheType.RelSize, self._update_size)
        return result or [0, 0]
    
    def _init_primary(self, window: Window | None, style: Style):
        self.window = window
        self.window_surface = None
        self.cache = Cache()
        self.quality = Quality.Decent
        self.style = style
        if self.window: self.window.add_event(NevuEvent(self, self.resize, EventType.Resize))

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
        self._layout = None

    def _init_secondary(self):
        self._changed = True
        self._update_surface()
        self.isrelativeplaced = False
        self.relative_percent_x = None
        self.relative_percent_y = None
        self._enabled = True
        self.will_resize = False

    def _init_tertiary(self, size):
        self.first_window_size = self.window.size if self.window else NvVector2(0, 0)
        self.first_size = size
        self.first_coordinates = NvVector2(0, 0)
        self._opened_sub_menu = None
        self._subtheme_role = SubThemeRole.PRIMARY

    def _init_subtheme(self, alt):
        if not alt:
            self._subtheme_border = self._main_subtheme_border
            self._subtheme_content = self._main_subtheme_content
        else:
            self._subtheme_border = self._alt_subtheme_border
            self._subtheme_content = self._alt_subtheme_content

    def _init_dirty_rects(self):
        self._dirty_rects = []
        if self.window:
            self.window._next_update_dirty_rects.append(pygame.Rect(0, 0, *self.size))
    
    def read_item_coords(self, item: NevuObject):
        w_size = item._lazy_kwargs['size']
        x, y = w_size
        x, is_x_rule = self._convert_item_coord(x, 0)
        y, is_y_rule = self._convert_item_coord(y, 1)
        item._lazy_kwargs['size'] = [x,y]
        
    def _proper_load_layout(self):
        if not self._layout: return
        self._layout._boot_up()
        
    @property
    def _main_subtheme_content(self): return self._subtheme.color
    @property
    def _main_subtheme_border(self): return self._subtheme.oncolor
    @property
    def _alt_subtheme_content(self): return self._subtheme.container
    @property
    def _alt_subtheme_border(self): return self._subtheme.oncontainer
    
    @property
    def _background(self):
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
        if self.window is None: raise ValueError("Window is not initialized!")
        self._absolute_coordinates = self.rel(coordinates) + self.window._offset
    def abs_coordinates_update(self): self.absolute_coordinates = self.coordinates
        
    def open_submenu(self, menu, style: Style|None = None, *args):
        assert isinstance(menu, Menu)
        self._opened_sub_menu = menu
        self._args_menus_to_draw = []
        for item in args: self._args_menus_to_draw.extend(item)
        if style: self._opened_sub_menu.apply_style_to_layout(style)
        self._opened_sub_menu._resize_with_ratio(self._resize_ratio)
    def close_submenu(self): self._opened_sub_menu = None
        
    def _update_surface(self):
        if self.style.borderradius>0:self.surface = pygame.Surface(self._pygame_size, pygame.SRCALPHA)
        else: self.surface = pygame.Surface(self._pygame_size)
        if self.style.transparency: self.surface.set_alpha(self.style.transparency)

    def resize(self, size: NvVector2):
        self.clear_surfaces()
        self._changed = True
        self._resize_ratio = NvVector2([size[0] / self.first_window_size[0], size[1] / self.first_window_size[1]])
        if self.window is None: raise ValueError("Window is not initialized!")
        if self.isrelativeplaced:
            assert self.relative_percent_x and self.relative_percent_y
            self.coordinates = NvVector2(
                (self.window.size[0] - self.window._crop_width_offset) / 100 * self.relative_percent_x - self.size[0] / 2,
                (self.window.size[1] - self.window._crop_height_offset) / 100 * self.relative_percent_y - self.size[1] / 2)

        self.abs_coordinates_update()
        self._update_surface()
        
        if self._layout:
            self._layout.resize(self._resize_ratio)
            self._layout.coordinates = NvVector2(self.rel(self.size, vector=True) / 2 - self.rel(self._layout.size,vector=True) / 2)
            self._layout.update()
            self._layout.draw()
        if self.style.transparency: self.surface.set_alpha(self.style.transparency)

    def _resize_with_ratio(self, ratio: NvVector2):
        self.clear_surfaces()
        self._changed = True
        self._resize_ratio = ratio
        self.abs_coordinates_update()
        if self.style.transparency: self.surface.set_alpha(self.style.transparency)
        if self._layout: self._layout.resize(self._resize_ratio)
        
    @property
    def style(self) -> Style: return self._style
    @style.setter
    def style(self, style: Style): self._style = copy.copy(style)

    def apply_style_to_layout(self, style: Style):
        self._changed = True
        self.style = style
        if self._layout: self._layout.apply_style_to_childs(style)
        
    @property
    def layout(self): return self._layout
    @layout.setter
    def layout(self, layout):
        assert self.window, "Window is not set!"
        if layout._can_be_main_layout:
            self.read_item_coords(layout)
            layout._master_z_handler = self.window.z_system
            layout._init_start()
            layout._connect_to_menu(self)
            layout.first_parent_menu = self
            layout._boot_up()
            layout.coordinates = NvVector2(self.size[0]/2 - layout.size[0]/2, self.size[1]/2 - layout.size[1]/2)
            self._layout = layout
        else: raise ValueError(f"Layout {type(layout).__name__} can't be main")
        
    def _set_layout_coordinates(self, layout):
        layout.coordinates = NvVector2(self.size[0]/2 - layout.size[0]/2, self.size[1]/2 - layout.size[1]/2)
        
    def set_coordinates(self, x: int, y: int):
        self.coordinates = NvVector2(x, y)
        self.abs_coordinates_update()
        
        self.isrelativeplaced = False
        self.relative_percent_x = None
        self.relative_percent_y = None
        self.first_coordinates = self.coordinates
        
    def set_coordinates_relative(self, percent_x: int, percent_y: int):
        if self.window is None: raise ValueError("Window is not initialized!")
        self.coordinates = NvVector2([(self.window.size[0]-self.window._crop_width_offset)/100*percent_x-self.size[0]/2,
                                    (self.window.size[1]-self.window._crop_height_offset)/100*percent_y-self.size[1]/2])
        self.abs_coordinates_update()
        self.isrelativeplaced = True
        self.relative_percent_x = percent_x
        self.relative_percent_y = percent_y
        self.first_coordinates = self.coordinates

    def draw(self):
        if not self.enabled or not self.window: return
        scaled_bg = self.cache.get_or_exec(CacheType.Scaled_Background, self._background)
        if nevu_state.renderer:
            if self.window._gpu_mode:
                assert isinstance(scaled_bg, Texture)
                if self._layout is not None:
                    nevu_state.renderer.target = self._texture
                    nevu_state.renderer.blit(scaled_bg, self.get_rect())
                    self._layout.draw()
                    nevu_state.renderer.target = None
                self.window._display.blit(self._texture, self.absolute_coordinates.to_int().to_tuple())
                if self._opened_sub_menu:
                    for item in self._args_menus_to_draw: item.draw()
                    self._opened_sub_menu.draw()
                return 
            
            elif self.window._open_gl_mode:
                if self._layout is not None:
                    self.window._display.set_target(self._texture)
                    self.window._display.blit(scaled_bg, self.get_rect())
                    self._layout.draw()
                    self.window._display.set_target(None)
                self.window._display.blit(self._texture, self.absolute_coordinates.to_int().to_tuple())
                if self._opened_sub_menu:
                    for item in self._args_menus_to_draw: item.draw()
                    self._opened_sub_menu.draw()
                return
            
        if scaled_bg:
            self.surface.blit(scaled_bg, (0, 0))
        
        if self._layout is not None:
            self._layout.draw() 
        self.window._display.blit(self.surface, self.absolute_coordinates.to_int().to_tuple())
        
        if self._opened_sub_menu:
            for item in self._args_menus_to_draw: item.draw()
            self._opened_sub_menu.draw()

    def update(self):
        if not self.enabled: return
        if self.window is None: return
        assert isinstance(self.window, Window)
        
        if len(self._dirty_rects) > 0:
            self.window._next_update_dirty_rects.extend(self._dirty_rects)
            self._dirty_rects = []
            
        assert isinstance(self._opened_sub_menu, (Menu, type(None)))
        if self._opened_sub_menu:
            self._opened_sub_menu.update()
            return
        if self._layout: 
            self._layout.master_coordinates = self._layout.coordinates + self.window.offset
            self._layout.update(nevu_state.current_events)
        
    def get_rect(self) -> pygame.Rect: return pygame.Rect((0,0), self.size * self._resize_ratio)
    
    def kill(self):
        self._enabled = False
        
        if self._layout:
            self._layout.kill()
            for item in self._layout._all_items:
                item.kill()
            self._layout = None
            
        if self._opened_sub_menu:
            self._opened_sub_menu.kill()
            self._opened_sub_menu = None

        for item in self._args_menus_to_draw: item.kill()
        
        self._args_menus_to_draw.clear()
        self.cache.clear()
        self.surface = None
        self.window = None
        
        if nevu_state.window: nevu_state.window.z_system.mark_dirty()