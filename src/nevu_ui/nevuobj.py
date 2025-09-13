import pygame
from .style import Style
from .utils import *
from .utils import Event
from .animations import AnimationType, AnimationManager
from enum import Enum, auto
from .utils import NvVector2 as Vector2
import copy
from typing import Any
from .color import *
from warnings import deprecated
from .fast_logic import (
    relx_helper, rely_helper, relm_helper, rel_helper
)
from .core_types import (
    SizeRule, Px, Vh, Vw, Fill, HoverState
)
from collections.abc import Callable
class NevuObject:
    id: str | None
    floating: bool
    single_instance: bool
    
    #INIT STRUCTURE: ====================
    #    __init__ >
    #        constants 
    #        basic_variables >
    #            test_flags
    #            booleans
    #            numerical
    #            lists
    #        complicated_variables >
    #            objects
    #            style
    #    postinit(lazy_init) >
    #        size dependent code
    #======================================
    
    def __init__(self, size: Vector2 | list, style: Style, **constant_kwargs):
        self.constant_kwargs = copy.deepcopy(constant_kwargs)
        self._lazy_kwargs = {'size': size}

        #=== Constants ===
        self._init_constants(**constant_kwargs)
        
    #=== Basic Variables ===    

        #=== Test Flags ===
        self._init_test_flags()
        
        #=== Booleans(Flags) ===
        self._init_booleans()
        
        #=== Numerical(int, float) ===
        self._init_numerical()

        #=== Lists/Vectors ===
        self._init_lists()
        
    #=== Complicated Variables ===
        #=== Objects ===
        self._init_objects()
        
        #=== Style ===
        self._init_style(style)
        
    def clone(self):
        return NevuObject(self._lazy_kwargs['size'], copy.deepcopy(self.style), **self.constant_kwargs)
    
    def __deepcopy__(self, *args, **kwargs):
        return self.clone()
    
    def _add_constant(self, name, supported_classes: tuple | Any, default: Any):
        self.constant_supported_classes[name] = supported_classes
        self.constant_defaults[name] = default
        self.is_constant_set[name] = False
    
    def _block_constant(self, name: str):
        self.excluded_constants.append(name)
    
    def _init_constants_base(self):
        self.constant_supported_classes = {}
        self.constant_defaults = {}
        self.constant_links = {}
        self.is_constant_set = {}
        self.excluded_constants = []
        
    def _add_constants(self):
        self._add_constant("id", (str, type(None)), None)
        self._add_constant("floating", bool, False)
        self._add_constant("single_instance", bool, False)
        
    def _add_constant_link(self, name: str, link_name: str):
        self.constant_links[name] = link_name
        
    def _preinit_constants(self):
        for name, value in self.constant_defaults.items():
            if not hasattr(self, name):
                setattr(self, name, value)
                
    def _change_constants_kwargs(self, **kwargs):
        constant_name = None
        needed_types = None
        for name, value in kwargs.items():
            name = name.lower()
            
            constant_name, needed_types = self._extract_constant_data(name)
                
            self._process_constant(name, constant_name, needed_types, value)
            constant_name = None
            needed_types = None
    
    def _extract_constant_data(self, name):
        if name in self.constant_supported_classes.keys():
            constant_name = name
            needed_types = self.constant_supported_classes[name]
        elif name in self.constant_links.keys():
            constant_name = self.constant_links[name]
            if constant_name in self.constant_supported_classes.keys():
                needed_types = self.constant_supported_classes[constant_name]
            else:
                raise ValueError(f"Invalid constant link {name} -> {self.constant_links[name]}. Constant not found.")
        else:
            raise ValueError(f"Constant {name} not found")
        return constant_name, needed_types
    
    def _process_constant(self, name, constant_name, needed_types, value):
        assert needed_types
        if constant_name in self.excluded_constants:
            raise ValueError(f"Constant {name} is unconfigurable")
        if not isinstance(needed_types, tuple):
            needed_types = (needed_types,)
        is_valid = False
        for needed_type in needed_types:
            if needed_type == Callable:
                is_valid = callable(value) if is_valid == False else is_valid
            elif needed_type == Any:
                is_valid = True
            else:
                is_valid = isinstance(value, needed_type) if is_valid == False else is_valid
        if is_valid and not self.is_constant_set[constant_name]:
            print(f"Debug: Set constant {name}({constant_name}) to {value} in {self}({type(self).__name__})")
            setattr(self, constant_name, value)
            self.is_constant_set[constant_name] = True
            
        elif self.is_constant_set[constant_name]:
            raise ValueError(f"Constant {name}({constant_name}) is already set")
        
        else:
            raise TypeError(
                f"Invalid type for constant '{constant_name}'. "
                f"Expected {needed_types}, but got {type(value).__name__}."
            )
    def _init_test_flags(self):
        pass
    
    def _init_numerical(self):
        pass
    
    def _init_constants(self, **kwargs):
        self._init_constants_base()
        self._add_constants()
        self._preinit_constants()
        self._change_constants_kwargs(**kwargs)
            
    def _init_style(self, style: Style):
        self.style = style
        
    def _init_objects(self):
        self.cache = Cache()
        self._subtheme_role = SubThemeRole.TERTIARY
        self._hover_state = HoverState.UN_HOVERED
        self.animation_manager = AnimationManager()
        
    def _init_booleans(self):
        self._visible = True
        self._active = True
        self._changed = True
        self._first_update = True
        self.booted = False
        self._wait_mode = False
        
    def _init_lists(self):
        self._resize_ratio = Vector2(1, 1)
        self.coordinates = Vector2()
        self.master_coordinates = Vector2()
        self.first_update_functions = []
        self._events: list[NevuEvent] = []
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

    def subscribe(self, event: NevuEvent):
        """Adds a new event listener to the object.

        Args:
            event (NevuEvent): The event to subscribe

        Returns:
            None
        """
        self._events.append(event)
        
    @deprecated("use .subscribe() instead. This method will be removed in a future version.")
    def add_event(self, event: NevuEvent):
        """**Deprecated**: use .subscribe instead."""
        return self.subscribe(event)

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

    def _event_cycle(self, type: EventType, *args, **kwargs):
        for event in self._events:
            if event._type == type:
                event(*args, **kwargs)

    def resize(self, resize_ratio: Vector2):
        self._changed = True
        self._resize_ratio = resize_ratio
        self.cache.clear_selected(whitelist=[CacheType.RelSize])

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
    def on_scroll(self, side: bool):
        """Override this function to run code when the object is scrolled"""
        
    def _on_click_system(self):
        self._event_cycle(EventType.OnKeyDown)
    def _on_hover_system(self):
        self._event_cycle(EventType.OnHover)
    def _on_keyup_system(self):
        self._event_cycle(EventType.OnKeyUp)
    def _on_unhover_system(self):
        self._event_cycle(EventType.OnUnhover)
    def _on_scroll_system(self, side: bool):
        self._event_cycle(EventType.OnMouseScroll, side)

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
        return Vector2(self.rel(self.size))

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

    #UPDATE STRUCTURE: ====================
    #    update >
    #        primary_update >
    #            logic_update
    #            animation_update
    #            event_update
    #        secondary_update >
    #            widget/layout update code
    #======================================

    def update(self, events: list | None = None):
        events = events or []
        self.primary_update(events)
        self.secondary_update()
        self._event_cycle(EventType.Update)
    def primary_update(self, events: list | None = None):
        events = events or []
        self.logic_update()
        self.animation_update()
        self.event_update(events)
    def logic_update(self):
        self._update_hover_state()
    def _update_scroll(self):
        if mouse.wheel_still: return
        self.on_scroll(mouse.wheel_up)
        self._on_scroll_system(mouse.wheel_up)
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
    #            secondary_draw_content
    #            secondary_draw_end
    #--------------------------------------

    def draw(self):
        self.primary_draw()
        self._event_cycle(EventType.Draw)
        self.secondary_draw()
        self._event_cycle(EventType.Render)
        
    def primary_draw(self):
        pass
    def secondary_draw(self):
        self.secondary_draw_content()
        self.secondary_draw_end()
        
    def secondary_draw_content(self):
        pass
    def secondary_draw_end(self):
        pass
    
    def relx(self, num: int | float, min: int | None = None, max: int| None = None) -> int | float:
        return relx_helper(num, self._resize_ratio.x, min, max)

    def rely(self, num: int | float, min: int | None = None, max: int| None = None) -> int | float:
        return rely_helper(num, self._resize_ratio.y, min, max)

    def relm(self, num: int | float, min: int | None = None, max: int | None = None) -> int | float:
        return relm_helper(num, self._resize_ratio.x, self._resize_ratio.y, min, max)
    
    def rel(self, mass: list | tuple | Vector2, vector: bool = False) -> list | Vector2:  
        return rel_helper(mass, self._resize_ratio.x, self._resize_ratio.y, vector)
    