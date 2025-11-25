import pygame
import copy
from pygame._sdl2 import Texture

from nevu_ui.nevuobj import NevuObject
from nevu_ui.window import Window
from nevu_ui.color import SubThemeRole
from nevu_ui.state import nevu_state
from nevu_ui.rendering.shader import convert_surface_to_gl_texture
from nevu_ui.style import Style, default_style
from nevu_ui.fast.nvvector2 import NvVector2 as Vector2, NvVector2
from nevu_ui.utils import Cache, NevuEvent

from nevu_ui.core_types import (
    _QUALITY_TO_RESOLUTION, SizeRule, Vh, Vw, Fill, Quality, CacheType, EventType
)
from nevu_ui.rendering import (
    OutlinedRoundedRect, RoundedRect, AlphaBlit, Gradient
)
from nevu_ui.fast.logic import (
    rel_helper, relm_helper, mass_rel_helper
)

class Menu:
    def __init__(self, window: Window | None, size: list | tuple | Vector2, style: Style = default_style, alt: bool = False, layout = None): 
        self._coordinatesWindow = Vector2(0,0)
        self._init_primary(window, style)
        if not self.window: return
        self._init_size(size)
        self._init_secondary()
        self._init_tertiary(size)
        self._init_subtheme(alt)
        self._init_dirty_rects()
        if layout: self.layout = layout
    
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
        if self.window:
            self.window.add_event(NevuEvent(self, self.resize, EventType.Resize))

    def _init_size(self, size: list | tuple | Vector2):
        initial_size = list(size) #type: ignore
        for i in range(len(initial_size)):
            item = initial_size[i]
            if isinstance(item, SizeRule):
                converted, is_ruled = self._convert_item_coord(item, i)
                initial_size[i] = float(converted)
            else: initial_size[i] = float(item)
        self.size = Vector2(initial_size)
        self.coordinates = Vector2(0, 0)
        self._resize_ratio = Vector2(1, 1)
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
        self.first_window_size = self.window.size if self.window else Vector2(0, 0)
        self.first_size = size
        self.first_coordinates = Vector2(0, 0)
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
        
    def _convert_item_coord(self, coord: int | float | SizeRule, i: int = 0) -> tuple[float, bool]:
        if not self.window: raise ValueError("Window is not initialized!")
        if isinstance(coord, (int, float)): return coord, False
        elif isinstance(coord, SizeRule):
            if type(coord) == Vh: return self.window.size[1]/100 * coord.value, True
            elif type(coord) == Vw: return self.window.size[0]/100 * coord.value, True
            elif type(coord) == Fill: return self.size[i]*self._resize_ratio[i]/ 100 * coord.value, True
            raise NotImplementedError(f"Handling for SizeRule type '{type(coord).__name__}' is not implemented!")
        raise TypeError(f"Unsupported coordinate type: {type(coord).__name__}")
    
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
    
    def relx(self, num: int | float, min: int | None = None, max: int| None = None) -> int | float:
        return rel_helper(num, self._resize_ratio.x, min, max)

    def rely(self, num: int | float, min: int | None = None, max: int| None = None) -> int | float:
        return rel_helper(num, self._resize_ratio.y, min, max)

    def relm(self, num: int | float, min: int | None = None, max: int | None = None) -> int | float:
        return relm_helper(num, self._resize_ratio.x, self._resize_ratio.y, min, max)
    
    def rel(self, mass: NvVector2, vector: bool = True) -> NvVector2:  
        return mass_rel_helper(mass, self._resize_ratio.x, self._resize_ratio.y, vector) # type: ignore
    
    def _draw_gradient(self, _set = False):
        if not self.style.gradient: return
        cached_gradient = pygame.Surface(self.size*_QUALITY_TO_RESOLUTION[self.quality], flags = pygame.SRCALPHA)
        if self.style.transparency: cached_gradient = self.style.gradient.with_transparency(self.style.transparency).apply_gradient(cached_gradient)
        else: cached_gradient =  self.style.gradient.apply_gradient(cached_gradient)
        if _set:
            self.cache.set(CacheType.Gradient, cached_gradient)
        else: return cached_gradient
        
    def _scale_gradient(self, size = None):
        if not self.style.gradient: return
        size = size or self.size * self._resize_ratio
        cached_gradient = self.cache.get_or_exec(CacheType.Gradient, self._draw_gradient)
        if cached_gradient is None: return
        target_size_vector = size
        target_size_tuple = (
            max(1, int(target_size_vector.x)), 
            max(1, int(target_size_vector.y))
        )
        cached_gradient = pygame.transform.smoothscale(cached_gradient, target_size_tuple)
        return cached_gradient
    
    @property
    def _background(self):
        if self.will_resize: result1 =  lambda: self._scale_background(self.size*self._resize_ratio)
        else: result1 = lambda: self._generate_background()
        if nevu_state.renderer: result = lambda: self.convert_texture(result1())
        else: result = result1
        return result

    def _scale_image(self, size = None):
        size = size or self.size * self._resize_ratio
        return self.cache.get_or_exec(CacheType.Image, lambda: self._load_image(size))
    def _load_image(self, size = None):
        size = size or self.size * self._resize_ratio
        surf = pygame.image.load(self.style.bgimage).convert_alpha()
        surf = pygame.transform.smoothscale(surf, (max(1, int(size.x)), max(1, int(size.y))))
        return surf
    
    def _generate_background(self):
        resize_factor = _QUALITY_TO_RESOLUTION[self.quality] if self.will_resize else self._resize_ratio
        bgsurface = pygame.Surface(self.size * resize_factor, flags = pygame.SRCALPHA)
        if isinstance(self.style.gradient,Gradient):
            content_surf = self.cache.get_or_exec(CacheType.Scaled_Gradient, lambda: self._scale_gradient(self.size * resize_factor))
            if self.style.transparency: bgsurface.set_alpha(self.style.transparency)
        else: content_surf = self.cache.get(CacheType.Scaled_Gradient)
        if isinstance(self.style.bgimage, str):
            content_surf = self.cache.get_or_exec(CacheType.Scaled_Image, lambda: self._scale_image(self.size * resize_factor))
        else: content_surf = self.cache.get(CacheType.Scaled_Image)
        if content_surf: bgsurface.blit(content_surf,(0,0))
        else: bgsurface.fill(self._subtheme.container)
        
        if self._style.borderwidth > 0:
            border = self.cache.get_or_exec(CacheType.Borders, lambda: self._create_outlined_rect(self.size * resize_factor))
            if border: bgsurface.blit(border,(0,0))
        if self._style.borderradius > 0:
            mask_surf = self.cache.get_or_exec(CacheType.Surface, lambda: self._create_surf_base(self.size * resize_factor))
            if mask_surf: AlphaBlit.blit(bgsurface, mask_surf,(0,0))
        return bgsurface
    
    def _scale_background(self, size = None):
        size = size if size else self.size*self._resize_ratio
        surf = self.cache.get_or_exec(CacheType.Background, self._generate_background)
        if surf is None: return
        surf = pygame.transform.smoothscale(surf, (max(1, int(size.x)), max(1, int(size.y))))
        return surf
    
    @property
    def _subtheme(self): return self.style.colortheme.get_subtheme(self._subtheme_role)
    @property
    def enabled(self) -> bool: return self._enabled
    
    @enabled.setter
    def enabled(self, value: bool): self._enabled = value
        
    def clear_all(self): self.cache.clear()
        
    def clear_surfaces(self):
        self.cache.clear_selected(whitelist = [CacheType.Image, CacheType.Scaled_Gradient, CacheType.Surface, CacheType.Borders, CacheType.Scaled_Background, CacheType.RelSize, CacheType.Texture])
    
    @property
    def coordinatesMW(self) -> Vector2: return self._coordinatesWindow
    
    @coordinatesMW.setter
    def coordinatesMW(self, coordinates: Vector2):
        if self.window is None: raise ValueError("Window is not initialized!")
        self._coordinatesWindow = Vector2(self.relx(coordinates.x) + self.window._offset[0], 
                                        self.rely(coordinates.y) + self.window._offset[1])
        
    def coordinatesMW_update(self): self.coordinatesMW = self.coordinates
        
    def open_submenu(self, menu, style: Style|None = None,*args):
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
        self._resize_ratio = Vector2([size[0] / self.first_window_size[0], size[1] / self.first_window_size[1]])
        if self.window is None: raise ValueError("Window is not initialized!")
        if self.isrelativeplaced:
            assert self.relative_percent_x and self.relative_percent_y
            self.coordinates = Vector2(
                (self.window.size[0] - self.window._crop_width_offset) / 100 * self.relative_percent_x - self.size[0] / 2,
                (self.window.size[1] - self.window._crop_height_offset) / 100 * self.relative_percent_y - self.size[1] / 2)

        self.coordinatesMW_update()
        self._update_surface()
        
        if self._layout:
            self._layout.resize(self._resize_ratio)
            self._layout.coordinates = Vector2(self.rel(self.size, vector=True) / 2 - self.rel(self._layout.size,vector=True) / 2)
            self._layout.update()
            self._layout.draw()
        if self.style.transparency: self.surface.set_alpha(self.style.transparency)

    def _resize_with_ratio(self, ratio: NvVector2):
        self.clear_surfaces()
        self._changed = True
        self._resize_ratio = ratio
        self.coordinatesMW_update()
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
        layout.coordinates = Vector2(self.size[0]/2 - layout.size[0]/2, self.size[1]/2 - layout.size[1]/2)
        
    def set_coordinates(self, x: int, y: int):
        self.coordinates = Vector2(x, y)
        self.coordinatesMW_update()
        
        self.isrelativeplaced = False
        self.relative_percent_x = None
        self.relative_percent_y = None
        self.first_coordinates = self.coordinates
        
    def set_coordinates_relative(self, percent_x: int, percent_y: int):
        if self.window is None: raise ValueError("Window is not initialized!")
        self.coordinates = Vector2([(self.window.size[0]-self.window._crop_width_offset)/100*percent_x-self.size[0]/2,
                                    (self.window.size[1]-self.window._crop_height_offset)/100*percent_y-self.size[1]/2])
        self.coordinatesMW_update()
        self.isrelativeplaced = True
        self.relative_percent_x = percent_x
        self.relative_percent_y = percent_y
        self.first_coordinates = self.coordinates
        
    def _create_surf_base(self, size = None):
        ss = (self.size*self._resize_ratio).xy if size is None else size
        surf = pygame.Surface((int(ss[0]), int(ss[1])), pygame.SRCALPHA)
        surf.fill((0,0,0,0))
        if self.will_resize:
            avg_scale_factor = _QUALITY_TO_RESOLUTION[self.quality]
        else:
            avg_scale_factor = (self._resize_ratio[0] + self._resize_ratio[1]) / 2
        radius = self._style.borderradius * avg_scale_factor
        surf.blit(RoundedRect.create_sdf([int(ss[0]), int(ss[1])], int(radius), self._subtheme_content), (0, 0))
        return surf
    
    def _create_outlined_rect(self, size = None):
        ss = (self.size*self._resize_ratio).xy if size is None else size
        if self.will_resize:
            avg_scale_factor = _QUALITY_TO_RESOLUTION[self.quality]
        else:
            avg_scale_factor = (self._resize_ratio[0] + self._resize_ratio[1]) / 2
        radius = self._style.borderradius * avg_scale_factor
        width = self._style.borderwidth * avg_scale_factor
        return OutlinedRoundedRect.create_sdf([int(ss[0]), int(ss[1])], int(radius), int(width), self._subtheme_border)
    
    def draw(self):
        if not self.enabled or not self.window:
            return
        scaled_bg = self.cache.get_or_exec(CacheType.Scaled_Background, self._background)
        if nevu_state.renderer:
            if self.window._gpu_mode:
                assert isinstance(scaled_bg, Texture)
                if self._layout is not None:
                    nevu_state.renderer.target = self._texture
                    nevu_state.renderer.blit(scaled_bg, self.get_rect())
                    self._layout.draw()
                    nevu_state.renderer.target = None
                if self._opened_sub_menu:
                    for item in self._args_menus_to_draw: item.draw()
                    self._opened_sub_menu.draw()
                self.window._display.blit(self._texture, self.coordinatesMW.to_int().to_tuple())
                return 
            elif self.window._open_gl_mode:
                if self._layout is not None:
                    self.window._display.set_target(self._texture)
                    self.window._display.blit(scaled_bg, self.get_rect())
                    self._layout.draw()
                    self.window._display.set_target(None)
                self.window._display.blit(self._texture, self.coordinatesMW.to_int().to_tuple())
                if self._opened_sub_menu:
                    for item in self._args_menus_to_draw: item.draw()
                    self._opened_sub_menu.draw()
                return
        if scaled_bg:
            self.surface.blit(scaled_bg, (0, 0))
        
        if self._layout is not None:
            self._layout.draw() 
        self.window._display.blit(self.surface, self.coordinatesMW.to_int().to_tuple())
        
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
            self._layout.update(nevu_state.current_events)#self.window.last_events)
        
    def get_rect(self) -> pygame.Rect: return pygame.Rect((0,0), self.size * self._resize_ratio)
    
    def kill(self):
        self._enabled = False
        
        if self._layout:
            if hasattr(self._layout, 'kill'):
                self._layout.kill()
            elif hasattr(self._layout, 'items'):
                for item in list(self._layout.items):
                    if hasattr(item, 'kill'):
                        item.kill()
            self._layout = None
            
        if self._opened_sub_menu:
            if hasattr(self._opened_sub_menu, 'kill'):
                self._opened_sub_menu.kill()
            self._opened_sub_menu = None

        if hasattr(self, '_args_menus_to_draw'):
            for item in self._args_menus_to_draw:
                if hasattr(item, 'kill'):
                    item.kill()
            self._args_menus_to_draw.clear()
            
        self.cache.clear()
        self.surface = None
        self.window = None
        
        if nevu_state.window:
            nevu_state.window.z_system.mark_dirty()

    def __del__(self):
        self.kill()