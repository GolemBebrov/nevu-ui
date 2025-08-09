import pygame
import copy
from .style import *
from .style import _QUALITY_TO_RESOLUTION
from .utils import *
from .utils import NvVector2 as Vector2

from .window import Window
from .animations import *
from .widgets import *
class Menu:
    def __init__(self, window: Window, size: tuple | Vector2, style: Style = default_style, alt: bool = False, layout = None): 
        #PRIMARY VARIABLES
        self.window = window
        self.window_surface = None
        self.cache = Cache()
        self.quality = Quality.Decent
        self.style = style
        if self.window:
            self.window.add_event(Event(Event.RESIZE,self.resize))
        else:
            print("Created empty menu!")
            return
        self.size = size if not isinstance(size, (tuple, Vector2)) else list(size) 
        #self.size =size
        #convert_size
        for i in range(len(self.size)):
            item = self.size[i]
            if isinstance(item, SizeRule):
                print("Ruled", item)
                self.size[i], is_ruled = self._convert_item_coord(item)
        print(self.size)
        if not isinstance(size,Vector2):
            self.size = Vector2(self.size)
        else: self.size = size

        self._coordinatesWindow = Vector2(0,0)
        self.coordinates = Vector2(0,0)
        self._resize_ratio = Vector2(1,1)
        
        self._layout = None

        #SECONDARY VARIABLES
        self._changed = True
        print(self.size, self._resize_ratio)
        print(self.size*self._resize_ratio)
        self._update_surface()
        self.isrelativeplaced = False
        self.relx = None
        self.rely = None
        self._enabled = True
        
        #TERTIARY VARIABLES
        self.first_window_size = self.window.size
        self.first_size = size
        self.first_coordinates = Vector2(0,0)
        self._opened_sub_menu = None
        self._subtheme_role = SubThemeRole.PRIMARY

        if not alt:
            self._subtheme_border = self._main_subtheme_border
            self._subtheme_content = self._main_subtheme_content
        else:
            self._subtheme_border = self._alt_subtheme_border
            self._subtheme_content = self._alt_subtheme_content
        
        self._dirty_rects = []
        self.window._next_update_dirty_rects.append(pygame.Rect(0,0,*self.size))

        if layout:
            self.layout = layout
        #DEPRECATED!
        #self._global_changed = True
        #if not self.window:
        #    self.window_surface = self.window
        #    self.window = None
        #    return
    def _convert_item_coord(self, coord, i: int = 0):
        if isinstance(coord, SizeRule):
            if isinstance(coord, (Vh, Vw)):
                if type(coord) == Vh: return self.window.size[1]/100 * coord.value, True
                elif type(coord) == Vw: return self.window.size[0]/100 * coord.value, True
            elif type(coord) == Fill: return self.size[i]*self._resize_ratio[i]/ 100 * coord.value, True
            return coord, False
        return coord, False
    def read_item_coords(self, item: NevuObject):
        w_size = item._lazy_kwargs['size']
        x, y = w_size
        x, is_x_rule = self._convert_item_coord(x, 0)
        y, is_y_rule = self._convert_item_coord(y, 1)

        item._lazy_kwargs['size'] = [x,y]
        #is_ruled = is_x_rule or is_y_rule
        #if is_ruled: item.wait_mode = False; item._init_start(); print("Ruled", item, item._lazy_kwargs['size'])
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
    def relx(self, num: int | float, min: int = None, max: int = None, type: int|float = round) -> int | float:
        result = type(num*self._resize_ratio.x)
        if min is not None and result < min: return min
        if max is not None and result > max: return max
        return result
    def rely(self, num: int | float, min: int = None, max: int = None, type: int|float = round) -> int | float:
        result = type(num*self._resize_ratio.y)
        if min is not None and result < min: return min
        if max is not None and result > max: return max
        return result
    def relm(self, num: int | float, min: int = None, max: int = None, type: int|float = round) -> int | float:
        result = type(num*((self._resize_ratio.x + self._resize_ratio.y)/2))
        if min is not None and result < min: return min
        if max is not None and result > max: return max
        return result
    def rel(self, mass: list | tuple, vector: bool = False, type: int|float = round) -> list | Vector2:
        return [type(mass[0] * self._resize_ratio.x), type(mass[1] * self._resize_ratio.y)] \
                if not vector else Vector2(type(mass[0] * self._resize_ratio.x), type(mass[1] * self._resize_ratio.y))
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
        size = size if size else self.size*self._resize_ratio
        cached_gradient = self.cache.get_or_exec(CacheType.Gradient, self._draw_gradient)
        target_size_vector = size
        target_size_tuple = (
            max(1, int(target_size_vector.x)), 
            max(1, int(target_size_vector.y))
        )
        cached_gradient = pygame.transform.smoothscale(cached_gradient, target_size_tuple)
        return cached_gradient
    def _generate_background(self):
        bgsurface = pygame.Surface(self.size*_QUALITY_TO_RESOLUTION[self.quality], flags = pygame.SRCALPHA)
        if True:
            if isinstance(self.style.gradient,Gradient):
                content_surf = self.cache.get_or_exec(CacheType.Scaled_Gradient, lambda: self._scale_gradient(self.size*_QUALITY_TO_RESOLUTION[self.quality]))
                if self.style.transparency: bgsurface.set_alpha(self.style.transparency)
            else:
                content_surf = self.cache.get(CacheType.Scaled_Gradient)
            if content_surf:
                bgsurface.blit(content_surf,(0,0))
            else: bgsurface.fill(self._subtheme.container)
        
        if self._style.borderwidth > 0:
            bgsurface.blit(self.cache.get_or_exec(CacheType.Borders, lambda: self._create_outlined_rect(self.size*_QUALITY_TO_RESOLUTION[self.quality])),(0,0))
        if self._style.borderradius > 0:
            mask_surf = self.cache.get_or_exec(CacheType.Surface, lambda: self._create_surf_base(self.size*_QUALITY_TO_RESOLUTION[self.quality]))
            AlphaBlit.blit(bgsurface,mask_surf,(0,0))
        return bgsurface
    def _scale_background(self, size = None):
        size = size if size else self.size*self._resize_ratio
        surf = self.cache.get_or_exec(CacheType.Background, self._generate_background)
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
        self.cache.clear_selected(whitelist = [CacheType.Image, CacheType.Scaled_Gradient, CacheType.Surface, CacheType.Borders, CacheType.Scaled_Background])
    @property
    def coordinatesMW(self) -> Vector2:
        return self._coordinatesWindow
    @coordinatesMW.setter
    def coordinatesMW(self, coordinates: Vector2):
        self._coordinatesWindow = [coordinates.x * self._resize_ratio.x + self.window._offset[0], 
                               coordinates.y * self._resize_ratio.y + self.window._offset[1]]
    def coordinatesMW_update(self):
        self.coordinatesMW = self.coordinates #WARAHELL IS DIS SHIT
    def open_submenu(self, menu, style: Style|None = None,*args):
        self._opened_sub_menu = menu
        self._args_menus_to_draw = []
        for item in args: self._args_menus_to_draw.append(item)
        if style: self._opened_sub_menu.apply_style_to_all(style)
        self._opened_sub_menu._resize_with_ratio(self._resize_ratio)
    def close_submenu(self):
        self._opened_sub_menu = None
    def _update_surface(self):
        if self.style.borderradius>0:self.surface = pygame.Surface(self.size*self._resize_ratio, pygame.SRCALPHA)
        else: self.surface = pygame.Surface(self.size*self._resize_ratio)
        if self.style.transparency: self.surface.set_alpha(self.style.transparency)

    def resize(self, size: Vector2):
        self.clear_surfaces()
        self._changed = True
        self._resize_ratio = Vector2([size[0] / self.first_window_size[0], size[1] / self.first_window_size[1]])

        if self.isrelativeplaced:
            self.coordinates = Vector2([
                (self.window.size[0] - self.window._crop_width_offset) / 100 * self.relx - self.size[0] / 2,
                (self.window.size[1] - self.window._crop_height_offset) / 100 * self.rely - self.size[1] / 2
            ])

        self.coordinatesMW_update()
        self._update_surface()
        
        if self._layout:
            self._layout.resize(self._resize_ratio)
            self._layout.coordinates = (self.rel(self.size, vector=True)/2 - self.rel(self._layout.size, vector=True)/2)
            self._layout.update()
            self._layout.draw()
        if self.style.transparency:
            self.surface.set_alpha(self.style.transparency)
        print(self._resize_ratio)
    def _resize_with_ratio(self, ratio: Vector2):
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
            layout.booted = True
            layout._boot_up()
            self.read_item_coords(layout)
            layout._init_start()
            layout.coordinates = (self.size[0]/2 - layout.size[0]/2, self.size[1]/2 - layout.size[1]/2)
            layout._connect_to_menu(self)

            
            self._layout = layout
        else: raise Exception("this Layout can't be main")
    def _set_layout_coordinates(self, layout):
        layout.coordinates = [self.size[0]/2 - layout.size[0]/2, self.size[1]/2 - layout.size[1]/2]
    def set_coordinates(self, x: int, y: int):
        self.coordinates = Vector2(x, y)
        self.coordinatesMW_update()
        
        self.isrelativeplaced = False
        self.relx = None
        self.rely = None
        
        self.first_coordinates = self.coordinates
    def set_coordinates_relative(self, relx: int, rely: int):
        self.coordinates = Vector2([(self.window.size[0]-self.window._crop_width_offset)/100*relx-self.size[0]/2,(self.window.size[1]-self.window._crop_height_offset)/100*rely-self.size[1]/2])
        self.coordinatesMW_update()
        self.isrelativeplaced = True
        self.relx = relx
        self.rely = rely
        self.first_coordinates = self.coordinates
    def _create_surf_base(self, size = None):
        ss = (self.size*self._resize_ratio).xy if size is None else size
        surf = pygame.Surface((int(ss[0]), int(ss[1])), pygame.SRCALPHA)
        surf.fill((0,0,0,0))
        resize_ratio = self._resize_ratio*_QUALITY_TO_RESOLUTION[self.quality]
        surf.blit( RoundedRect.create_sdf( [int(ss[0]), int(ss[1])], int(self._style.borderradius*(resize_ratio[0]+resize_ratio[1])/2)
        ,self._subtheme_content),(0,0))
        return surf
    def _create_outlined_rect(self, size = None):
        ss = (self.size*self._resize_ratio).xy if size is None else size
        resize_ratio = self._resize_ratio*_QUALITY_TO_RESOLUTION[self.quality]
        a =OutlinedRoundedRect.create_sdf([int(ss[0]), int(ss[1])], int(self._style.borderradius*(resize_ratio[0]+resize_ratio[1])/2), int(self._style.borderwidth*(resize_ratio[0]+resize_ratio[1])/2), self._subtheme_border)
        return a
    def draw(self):
        if not self.enabled: return
        self.surface.blit(self.cache.get_or_exec(CacheType.Scaled_Background, self._scale_background),(0,0))
        if len(self.layout._dirty_rect)>0:
            self._dirty_rects.extend(self.layout._dirty_rect)
            self._layout.draw()
        self.window.surface.blit(self.surface, self.coordinatesMW)
        
        if self._opened_sub_menu:
            for item in self._args_menus_to_draw: item.draw()
            self._opened_sub_menu.draw()
    def update(self):
        if not self.enabled: return
        if len(self._dirty_rects) > 0:
            self.window._next_update_dirty_rects.extend(self._dirty_rects)
            self._dirty_rects = []
        if self._opened_sub_menu:
            self._opened_sub_menu.update()
            return
        if self._layout: self._layout.update()
        #DEPRECATED!
        #self._global_changed = self.layout._is_changed
    def get_rect(self) -> pygame.Rect:
        return pygame.Rect(self.coordinatesMW, self.size * self._resize_ratio)

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