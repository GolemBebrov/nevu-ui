import pygame
import copy

from nevu_ui.nevuobj import NevuObject
from nevu_ui.window import Window
from nevu_ui.color import SubThemeRole

from nevu_ui.style import (
    Style, default_style
)
from nevu_ui.core_types import (
    _QUALITY_TO_RESOLUTION, SizeRule, Vh, Vw, Fill, Quality, CacheType, EventType
)
from nevu_ui.rendering import (
    OutlinedRoundedRect, RoundedRect, AlphaBlit, Gradient
)
from nevu_ui.utils import (
    Cache, mouse, NevuEvent
)
from nevu_ui.fast.logic import (
    rel_helper, relm_helper, mass_rel_helper
)
from nevu_ui.fast.nvvector2 import (
    NvVector2 as Vector2, NvVector2
)

class Menu:
    def __init__(self, window: Window | None, size: list | tuple | Vector2, style: Style = default_style, alt: bool = False, layout = None): 
        self._coordinatesWindow = Vector2(0,0)
        self._init_primary(window, style)
        if not self.window:
            #print("Created empty menu!")
            return
        self._init_size(size)
        self._init_secondary()
        self._init_tertiary(size)
        self._init_subtheme(alt)
        self._init_dirty_rects()
        if layout:
            self.layout = layout

    def _update_size(self):
        return (self.size * self._resize_ratio).to_pygame()

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
        initial_size = list(size)
        for i in range(len(initial_size)):
            item = initial_size[i]
            if isinstance(item, SizeRule):
                #print("Ruled", item)
                converted, is_ruled = self._convert_item_coord(item, i)
                initial_size[i] = float(converted)
            else:
                initial_size[i] = float(item)
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
    def _main_subtheme_content(self):
        return self._subtheme.color
    @property
    def _main_subtheme_border(self):
        return self._subtheme.oncolor
    @property
    def _alt_subtheme_content(self):
        return self._subtheme.container
    @property
    def _alt_subtheme_border(self):
        return self._subtheme.oncontainer
    
    def relx(self, num: int | float, min: int | None = None, max: int| None = None) -> int | float:
        return rel_helper(num, self._resize_ratio.x, min, max)

    def rely(self, num: int | float, min: int | None = None, max: int| None = None) -> int | float:
        return rel_helper(num, self._resize_ratio.y, min, max)

    def relm(self, num: int | float, min: int | None = None, max: int | None = None) -> int | float:
        return relm_helper(num, self._resize_ratio.x, self._resize_ratio.y, min, max)
    
    def rel(self, mass: NvVector2, vector: bool = True) -> NvVector2:  
        return mass_rel_helper(mass, self._resize_ratio.x, self._resize_ratio.y, vector)
    
    def _draw_gradient(self, _set = False):
        if not self.style.gradient: return
        cached_gradient = pygame.Surface(self.size*_QUALITY_TO_RESOLUTION[self.quality], flags = pygame.SRCALPHA)
        if self.style.transparency: cached_gradient = self.style.gradient.with_transparency(self.style.transparency).apply_gradient(cached_gradient)
        else: cached_gradient =  self.style.gradient.apply_gradient(cached_gradient)
        if _set:
            self.cache.set(CacheType.Gradient, cached_gradient)
        else:
            return cached_gradient
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
        if self.will_resize:
            return lambda: self._scale_background(self.size*self._resize_ratio)
        else:
            return lambda: self._generate_background()
        #return lambda: self._scale_background(self.size*_QUALITY_TO_RESOLUTION[self.quality]) if self.will_resize else self._generate_background

    def _generate_background(self):
        resize_factor = _QUALITY_TO_RESOLUTION[self.quality] if self.will_resize else self._resize_ratio
        bgsurface = pygame.Surface(self.size * resize_factor, flags = pygame.SRCALPHA)
        if isinstance(self.style.gradient,Gradient):
            content_surf = self.cache.get_or_exec(CacheType.Scaled_Gradient, lambda: self._scale_gradient(self.size * resize_factor))
            if self.style.transparency: bgsurface.set_alpha(self.style.transparency)
        else: content_surf = self.cache.get(CacheType.Scaled_Gradient)
        if content_surf:
            bgsurface.blit(content_surf,(0,0))
        else: bgsurface.fill(self._subtheme.container)
        
        if self._style.borderwidth > 0:
            border = self.cache.get_or_exec(CacheType.Borders, lambda: self._create_outlined_rect(self.size * resize_factor))
            if border:
                bgsurface.blit(border,(0,0))
        if self._style.borderradius > 0:
            mask_surf = self.cache.get_or_exec(CacheType.Surface, lambda: self._create_surf_base(self.size * resize_factor))
            if mask_surf:
                AlphaBlit.blit(bgsurface, mask_surf,(0,0))
        return bgsurface
    
    def _scale_background(self, size = None):
        size = size if size else self.size*self._resize_ratio
        surf = self.cache.get_or_exec(CacheType.Background, self._generate_background)
        if surf is None: return
        surf = pygame.transform.smoothscale(surf, (max(1, int(size.x)), max(1, int(size.y))))
        return surf
    
    @property
    def _subtheme(self):
        return self.style.colortheme.get_subtheme(self._subtheme_role)
    
    @property
    def enabled(self) -> bool:
        return self._enabled
    
    @enabled.setter
    def enabled(self, value: bool):
        self._enabled = value
        
    def clear_all(self):
        self.cache.clear()
        
    def clear_surfaces(self):
        self.cache.clear_selected(whitelist = [CacheType.Image, CacheType.Scaled_Gradient, CacheType.Surface, CacheType.Borders, CacheType.Scaled_Background, CacheType.RelSize])
    
    @property
    def coordinatesMW(self) -> Vector2:
        return self._coordinatesWindow
    
    @coordinatesMW.setter
    def coordinatesMW(self, coordinates: Vector2):
        if self.window is None: raise ValueError("Window is not initialized!")
        self._coordinatesWindow = Vector2(self.relx(coordinates.x) + self.window._offset[0], 
                                        self.rely(coordinates.y) + self.window._offset[1])
        
    def coordinatesMW_update(self):
        """Applies offset to coordinates"""
        self.coordinatesMW = self.coordinates
        
    def open_submenu(self, menu, style: Style|None = None,*args):
        assert isinstance(menu, Menu)
        self._opened_sub_menu = menu
        self._args_menus_to_draw = []
        for item in args: self._args_menus_to_draw.extend(item)
        if style: self._opened_sub_menu.apply_style_to_layout(style)
        self._opened_sub_menu._resize_with_ratio(self._resize_ratio)
        
    def close_submenu(self):
        self._opened_sub_menu = None
        
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
            self.coordinates = Vector2(
                (self.window.size[0] - self.window._crop_width_offset) / 100 * self.relative_percent_x - self.size[0] / 2,
                (self.window.size[1] - self.window._crop_height_offset) / 100 * self.relative_percent_y - self.size[1] / 2
            )

        self.coordinatesMW_update()
        self._update_surface()
        
        if self._layout:
            self._layout.resize(self._resize_ratio)
            self._layout.coordinates = Vector2(self.rel(self.size, vector=True) / 2 - self.rel(self._layout.size,vector=True) / 2)
            self._layout.update()
            self._layout.draw()
        if self.style.transparency:
            self.surface.set_alpha(self.style.transparency)
        #print(self._resize_ratio)
        
    def _resize_with_ratio(self, ratio: NvVector2):
        self.clear_surfaces()
        self._changed = True
        self._resize_ratio = ratio
        self.coordinatesMW_update()
        if self.style.transparency: self.surface.set_alpha(self.style.transparency)
        if self._layout: self._layout.resize(self._resize_ratio)
        
    @property
    def style(self) -> Style:
        return self._style
    @style.setter
    def style(self, style: Style):
        self._style = copy.copy(style)
        
    def apply_style_to_layout(self, style: Style):
        self._changed = True
        self.style = style
        if self._layout: self._layout.apply_style_to_childs(style)
        
    @property
    def layout(self):
        return self._layout

    @layout.setter
    def layout(self, layout):
        if layout._can_be_main_layout:
            self.read_item_coords(layout)
            layout._master_z_handler = self.window.z_system
            layout._init_start()
            layout._connect_to_menu(self)
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
        if not self.enabled: return
        if self.window is None: return
        assert isinstance(self.window, Window)
        scaled_bg = self.cache.get_or_exec(CacheType.Scaled_Background, self._background)
        if scaled_bg:
            self.surface.blit(scaled_bg,(0,0))
        if self._layout is not None:
            if len(self._layout._dirty_rect)>0:
                self._dirty_rects.extend(self._layout._dirty_rect)
            self._layout.draw()
        self.window.surface.blit(self.surface, self.coordinatesMW)
        
        assert isinstance(self._opened_sub_menu, (Menu, type(None)))
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
            self._layout.update(self.window.last_events)
        
    def get_rect(self) -> pygame.Rect:
        return pygame.Rect(self.coordinatesMW, self.size * self._resize_ratio)


# ------ ALL OF CODE AFTER THIS LINE IS DEPRECATED! ------ #
#
#  * DO NOT USE THIS CODE IN YOUR PROJECTS!
#  * ITS WILL BE RECREATED IN THE FUTURE!
#  * USE AT YOUR OWN RISK!
#
# -------------------------------------------------------- #

"""
class DropDownMenu(Menu):
    def __init__(self, window:Window, size:list[int,int], style:Style=default_style,side:Align=Align.TOP,opened:bool=False,button_size:list[int,int]=None):
        super().__init__(window, size, style)
        self.side = side
        if not button_size:
            sz =[self.size[0]/3,self.size[0]/3]
        else:
            sz = button_size
        self.button = Button(self.toogle_self,"",sz,self.style)
        self.button.add_event(Event(Event.RENDER,lambda:self.draw_arrow(self.button.surface,self.style.bordercolor)))
        self.opened = opened
        self.transitioning = False
        self.animation_manager = AnimationManager()
        if self.side == Align.TOP:
            end = [self.coordinates[0],self.coordinates[1]-self.size[1]]
        elif self.side == Align.BOTTOM:
            end = [self.coordinates[0],self.coordinates[1]+self.size[1]]
        elif self.side == Align.LEFT:
            end = [self.coordinates[0]-self.size[0],self.coordinates[1]]
        elif self.side == Align.RIGHT:
            end = [self.coordinates[0]+self.size[0],self.coordinates[1]]
        self.end = end
        self.animation_speed = 1
    def draw_arrow(self, surface:pygame.Surface, color:list[int,int,int]|list[int,int,int,int], padding:int=1.1):
        bw = surface.get_width() / padding
        bh = surface.get_height() / padding

        mw = (surface.get_width() - bw) / 2
        mh = (surface.get_height() - bh) / 2
        
        if self.side == Align.TOP or self.side == Align.BOTTOM and self.opened and not self.transitioning:
            points = [(mw, mh), (bw // 2 + mw, bh + mh), (bw + mw, mh)]
        if self.side == Align.BOTTOM or self.side == Align.TOP and self.opened and not self.transitioning:
            points = [(mw, bh + mh), (bw // 2 + mw, mh), (bw + mw, bh + mh)]
        if self.side == Align.LEFT or self.side == Align.RIGHT and self.opened and not self.transitioning:
            points = [(mw, mh), (bw + mw, bh // 2 + mh), (mw, bh + mh)]
        if self.side == Align.RIGHT or self.side == Align.LEFT and self.opened and not self.transitioning:
            points = [(bw + mw, mh), (mw, bh // 2 + mh), (bw + mw, bh + mh)]
        pygame.draw.polygon(surface, color, points)
    def toogle_self(self):
        print("toogled")
        if self.transitioning: return
        self.animation_manager = AnimationManager()
        if self.opened:
            self.opened = False
            if self.side == Align.TOP:
                end = [self.coordinatesMW[0],self.coordinatesMW[1]-self.size[1]]
            elif self.side == Align.BOTTOM:
                end = [self.coordinatesMW[0],self.coordinatesMW[1]+self.size[1]]
            elif self.side == Align.LEFT:
                end = [self.coordinatesMW[0]-self.size[0],self.coordinatesMW[1]]
            elif self.side == Align.RIGHT:
                end = [self.coordinatesMW[0]+self.size[0],self.coordinatesMW[1]]
            self.end = end
            anim_transitioning = AnimationEaseInOut(0.5*self.animation_speed,self.coordinatesMW,end,AnimationType.POSITION)
            anim_opac = AnimationLinear(0.25*self.animation_speed,255,0,AnimationType.OPACITY)
            self.animation_manager.add_start_animation(anim_transitioning)
            self.animation_manager.add_start_animation(anim_opac)
            self.transitioning = True
        else:
            self.opened = True
            if self.side == Align.TOP:
                start = [self.coordinatesMW[0],self.coordinatesMW[1]-self.size[1]]
            elif self.side == Align.BOTTOM:
                start = [self.coordinatesMW[0],self.coordinatesMW[1]+self.size[1]]
            elif self.side == Align.LEFT:
                start = [self.coordinatesMW[0]-self.size[0],self.coordinatesMW[1]]
            elif self.side == Align.RIGHT:
                start = [self.coordinatesMW[0]+self.size[0],self.coordinatesMW[1]]
            anim_transitioning = AnimationEaseInOut(0.5*self.animation_speed,start,self.coordinatesMW,AnimationType.POSITION)
            anim_opac = AnimationLinear(0.5*self.animation_speed,0,255,AnimationType.OPACITY)
            self.animation_manager.add_start_animation(anim_transitioning)
            self.animation_manager.add_start_animation(anim_opac)
            self.transitioning = True
        self.animation_manager.update()
    def draw(self):
        customval = [0,0]
        if self.animation_manager.anim_opacity:
            self.surface.set_alpha(self.animation_manager.anim_opacity)
        if self.transitioning:
            customval = self.animation_manager.anim_position
            rect_val = [customval,self.size[0]*self._resize_ratio[0],self.size[1]*self._resize_ratio[1]]
        elif self.opened:
            rect_val = [self.coordinatesMW,self.size[0]*self._resize_ratio[0],self.size[1]*self._resize_ratio[1]]
        else:
            rect_val = [self.end,self.size[0]*self._resize_ratio[0],self.size[1]*self._resize_ratio[1]]
            self.button.draw()
            self.window.surface.blit(self.button.surface,self.button.coordinates)
            return
        self.surface.fill(self._style.bgcolor)
        self._layout.draw()
        if self._style.borderwidth > 0:
            pygame.draw.rect(self.surface,self._style.bordercolor,[0,0,rect_val[1],rect_val[2]],int(self._style.borderwidth*(self._resize_ratio[0]+self._resize_ratio[1])/2) if int(self._style.borderwidth*(self._resize_ratio[0]+self._resize_ratio[1])/2)>0 else 1,border_radius=int(self._style.borderradius*(self._resize_ratio[0]+self._resize_ratio[1])/2))
        if self._style.borderradius > 0:
            self.surface = RoundedSurface.create(self.surface,int(self._style.borderradius*(self._resize_ratio[0]+self._resize_ratio[1])/2))
        if rect_val[0]:
            self.window.surface.blit(self.surface,[int(rect_val[0][0]),int(rect_val[0][1])])
        self.button.draw()

        self.window.surface.blit(self.button.surface,self.button.coordinates)
    def update(self):
        self.animation_manager.update()
        if not self.animation_manager.start and self.transitioning:
            self.transitioning = False
        if self.transitioning:
            if self.animation_manager.anim_position:
                bcoords = self.animation_manager.anim_position
            else:
                bcoords = [-999,-999]
        elif self.opened:
            bcoords = self.coordinatesMW
        else:
            bcoords = self.end
        if self.side == Align.TOP:
            coords = [bcoords[0] + self.size[0] / 2-self.button.size[0]/2, bcoords[1] + self.size[1]]
        elif self.side == Align.BOTTOM:
            coords = [bcoords[0] + self.size[0] / 2-self.button.size[0]/2, bcoords[1]-self.button.size[1]]
        elif self.side == Align.LEFT:
            coords = [bcoords[0] + self.size[0], bcoords[1] + self.size[1] / 2-self.button.size[1]/2]
        elif self.side == Align.RIGHT:
            coords = [bcoords[0]-self.button.size[0], bcoords[1] + self.size[1] / 2-self.button.size[1]/2]
        self.button.coordinates = coords
        self.button.master_coordinates = self.button.coordinates
        self.button.update()
        if self.opened:
            super().update()
        
class ContextMenu(Menu):
    _opened_context = False
    def __init__(self, window, size, style = default_style):
        super().__init__(window, size, style)
        self._close_context()
    def _open_context(self,coordinates):
        self.set_coordinates(coordinates[0]-self.window._crop_width_offset,coordinates[1]-self.window._crop_width_offset)
        self._opened_context = True
    def apply(self):
        self.window._selected_context_menu = self
    def _close_context(self):
        self._opened_context = False
        self.set_coordinates(-self.size[0],-self.size[1])
    def draw(self):
        if self._opened_context: super().draw()
    def update(self):
        if self._opened_context: super().update()
class Group():
    def __init__(self,items=[]):
        self.items = items
        self._enabled = True
        self._opened_menu = None
        self._args_menus_to_draw = []
    def update(self):
        if not self._enabled:
            return
        if self._opened_menu:
            self._opened_menu.update()
            return
        for item in self.items:
            item.update()
    def draw(self):
        if not self._enabled:
            return
        for item in self.items:
            item.draw()
        if self._opened_menu:
            for item2 in self._args_menus_to_draw:
                item2.draw()
            self._opened_menu.draw()
    def step(self):
        if not self._enabled:
            return
        for item in self.items:
            item.update()
            item.draw()
    def enable(self):
        self._enabled = True
    def disable(self):
        self._enabled = False
    def toogle(self):
        self._enabled = not self._enabled
    def open(self,menu,style:Style=None,*args):
        self._opened_menu = menu
        self._args_menus_to_draw = []
        for item in args:
            self._args_menus_to_draw.append(item)
        if style:
            self._opened_menu.apply_style_to_all(style)
        self._opened_menu._resize_with_ratio(self._resize_ratio)
    def close(self):
        self._opened_menu = None

"""