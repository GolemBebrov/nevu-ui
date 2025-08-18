import pygame
from .style import *
from .utils import *
from .utils import Event
from .animations import AnimationType, AnimationManager
from enum import Enum, auto
from .utils import NvVector2 as Vector2
import copy
from .color import *

class HoverState(Enum):
    UN_HOVERED = auto()
    HOVERED = auto()
    CLICKED = auto()

class NevuObject:
    def __init__(self, size: Vector2 | list, style: Style, floating: bool = False, id: str | None = None):
        self._lazy_kwargs = {'size': size}
        self.id = id
    
        #Objects
        self._init_objects(style)

        #Booleans
        self._init_booleans(floating)

        #Lists
        self._init_lists()

    def _init_objects(self, style: Style):
        self.cache = Cache()
        self._subtheme_role = SubThemeRole.TERTIARY
        self._hover_state = HoverState.UN_HOVERED
        self.animation_manager = AnimationManager()
        self.style = style
        
    def _init_booleans(self, floating: bool):
        self._visible = True
        self._active = True
        self._changed = True
        self._first_update = True
        self.booted = False
        self._wait_mode = False
        self._floating = floating
        
    def _init_lists(self):
        self._resize_ratio = Vector2(1, 1)
        self.coordinates = Vector2()
        self.master_coordinates = Vector2()
        self.first_update_functions = []
        self._events = []
        self._dirty_rect = []
        
    def _init_start(self):
        self._wait_mode = False
        for i, item in enumerate(self._lazy_kwargs["size"]):
            self._lazy_kwargs["size"][i] = self.num_handler(item) #type: ignore
        if not self._wait_mode:
            self._lazy_init(**self._lazy_kwargs)

    def _lazy_init(self, size):
        self.size = size if isinstance(size, Vector2) else Vector2(size)

    def num_handler(self, number: SizeRule | int | float) -> SizeRule | int | float:
        if isinstance(number, SizeRule):
            if type(number) == Px:
                return number.value
            elif type(number) in [Vh, Vw, Fill]:
                self._wait_mode = True
        return number

    def add_event(self, event: Event):
        self._events.append(event)

    @property
    def wait_mode(self):
        return self._wait_mode
    @wait_mode.setter
    def wait_mode(self, value: bool):
        if self._wait_mode == True and not value:
            self._lazy_init(**self._lazy_kwargs)
            #print("WAIT MODE DISABLED")
        self._wait_mode = value

    @property
    def _csize(self):
        return self.cache.get_or_exec(CacheType.RelSize,self._update_size) or self.size

    def add_first_update_action(self, function):
        self.first_update_functions.append(function)

    def show(self):
        self._visible = True
    def hide(self):
        self._visible = False

    @property
    def visible(self):
        return self._visible
    @visible.setter
    def visible(self, value: bool):
        self._visible = value

    def activate(self):
        self._active = True
    def disactivate(self):
        self._active = False

    @property
    def active(self):
        return self._active
    @active.setter
    def active(self, value: bool):
        self._active = value

    def _event_cycle(self, type: int, *args, **kwargs):
        for event in self._events:
            if event.type == type:
                event(*args, **kwargs)

    def resize(self, resize_ratio: Vector2):
        self._changed = True
        self._resize_ratio = resize_ratio

    @property
    def style(self):
        return self._style
    @style.setter
    def style(self, style: Style):
        self._changed = True
        self._style = copy.copy(style)
    
    def get_animation_value(self, animation_type: AnimationType):
        return self.animation_manager.get_current_value(animation_type)

    def _update_hover_state(self):
        if self._hover_state == HoverState.UN_HOVERED:
            self._handle_unhovered()
        elif self._hover_state == HoverState.HOVERED:
            self._handle_hovered()
        elif self._hover_state == HoverState.CLICKED:
            self._handle_clicked()

    def _handle_unhovered(self):
        if self.get_rect().collidepoint(mouse.pos):
            self._hover_state = HoverState.HOVERED
            self.on_hover()
            self._on_hover_system()

    def _handle_hovered(self):
        if not self.get_rect().collidepoint(mouse.pos):
            self._hover_state = HoverState.UN_HOVERED
            self.on_unhover()
            self._on_unhover_system()
        elif mouse.left_fdown:
            self._hover_state = HoverState.CLICKED
            self.on_click()
            self._on_click_system()

    def _handle_clicked(self):
        if mouse.left_up:
            self._hover_state = HoverState.HOVERED 
            self.on_keyup()
            self._on_keyup_system()

    def on_click(self):
        """Override this function to run code when the object is clicked"""
    def on_hover(self):
        """Override this function to run code when the object is hovered"""
    def on_keyup(self):
        """Override this function to run code when a key is released"""
    def on_unhover(self):
        """Override this function to run code when the object is unhovered"""

    def _on_click_system(self):
        pass #realizes in the subclasses
    def _on_hover_system(self):
        pass #realizes in the subclasses
    def _on_keyup_system(self):
        pass #realizes in the subclasses
    def _on_unhover_system(self):
        pass #realizes in the subclasses

    def get_rect_opt(self, without_animation: bool = False):
        if not without_animation:
            return self.get_rect()
        anim_coords = self.animation_manager.get_animation_value(AnimationType.POSITION)
        anim_coords = anim_coords or [0,0]
        return pygame.Rect(
            self.master_coordinates[0] - self.relx(anim_coords[0]),
            self.master_coordinates[1] - self.rely(anim_coords[1]),
            *self.rel(self.size)
        )
    def get_rect(self):
        anim_coordinates = self.animation_manager.get_animation_value(AnimationType.POSITION)
        anim_coordinates = [0,0] if anim_coordinates is None else anim_coordinates
        return pygame.Rect(
            self.master_coordinates[0],
            self.master_coordinates[1],
            *self.rel(self.size)
        )

    def _update_coords(self):
        return self.coordinates

    def _update_size(self):
        return self.rel(self.size)

    def get_font(self):
        avg_resize_ratio = (self._resize_ratio[0] + self._resize_ratio[1]) / 2
        font_size = int(self.style.fontsize * avg_resize_ratio)
        return (pygame.font.SysFont(self.style.fontname, font_size) if self.style.fontname == "Arial" 
                else pygame.font.Font(self.style.fontname, font_size))
    @property
    def subtheme_role(self):
        return self._subtheme_role
    @subtheme_role.setter
    def subtheme_role(self, value: SubThemeRole):
        self._subtheme_role = value
        self.cache.clear()
        self._on_subtheme_role_change()
    def _on_subtheme_role_change(self):
        pass
    @property
    def _subtheme(self):
        return self.style.colortheme.get_subtheme(self._subtheme_role)

    #UPDATE STRUCTURE: -------------------
    #    update >
    #        primary_update >
    #            logic_update
    #            animation_update
    #            event_update
    #        secondary_update >
    #            widget/layout update code
    #--------------------------------------

    def update(self, events: list | None = None):
        events = events or []
        self.primary_update(events)
        self.secondary_update()
        self._event_cycle(Event.UPDATE)
    def primary_update(self, events: list | None = None):
        events = events or []
        self.logic_update()
        self.animation_update()
        self.event_update(events)
    def logic_update(self):
        pass #TODO
    def animation_update(self):
        self.animation_manager.update()
    def event_update(self, events: list):
        pass
    def secondary_update(self):
        pass

    #DRAW STRUCTURE: ----------------------
    #    draw >
    #        primary_draw >
    #            basic draw code
    #        secondary_draw >
    #            widget/layout draw code
    #--------------------------------------

    def draw(self):
        self.primary_draw()
        self._event_cycle(Event.DRAW)
        self.secondary_draw()
        self._event_cycle(Event.RENDER)
        
    def primary_draw(self):
        pass
    def secondary_draw(self):
        pass
    
    def _rel_corner(self, result: int | float, min: int | None, max: int | None) -> int | float:
        if min is not None and result < min: return min
        return max if max is not None and result > max else result
    
    def relx(self, num: int | float, min: int | None = None, max: int| None = None, function = None) -> int | float:
        if not function: function = round
        result = function(num*self._resize_ratio.x)
        return self._rel_corner(result, min, max)
    def rely(self, num: int | float, min: int | None = None, max: int | None = None, function = None) -> int | float:
        if not function: function = round
        result = function(num*self._resize_ratio.y)
        return self._rel_corner(result, min, max)
    def relm(self, num: int | float, min: int | None = None, max: int | None = None, function = None) -> int | float:
        if not function: function = round
        result = function(num*((self._resize_ratio.x+self._resize_ratio.y)/2))
        return self._rel_corner(result, min, max)
    
    def rel(self, mass: list | tuple | Vector2, vector: bool = False) -> list | Vector2:  
        if not (hasattr(mass, '__getitem__') and len(mass) >= 2):
            raise ValueError("mass must be a sequence with two elements")
        return (Vector2(mass[0] * self._resize_ratio.x, mass[1] * self._resize_ratio.y) if vector 
                else [mass[0] * self._resize_ratio.x, mass[1] * self._resize_ratio.y] )
    