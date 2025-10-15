from typing import Any, TypedDict, NotRequired
from collections.abc import Callable
from warnings import deprecated
import pygame
import copy
import contextlib

from nevu_ui.style import Style
from nevu_ui.color import SubThemeRole
from nevu_ui.fast.zsystem import ZRequest
from typing import Unpack

from nevu_ui.animations import (
    AnimationType, AnimationManager
)
from nevu_ui.utils import (
    Cache, mouse, NevuEvent
)
from nevu_ui.fast.logic import (
    relm_helper, rel_helper, mass_rel_helper, get_rect_helper_pygame, get_rect_helper
)
from nevu_ui.core_types import (
    SizeRule, Px, Vh, Vw, Fill, HoverState, Events, EventType, ZRequestType, CacheType
)
from nevu_ui.fast.nvvector2 import (
    NvVector2 as Vector2, NvVector2
)

class ZSystemPlaceholder:
    def add(self, *args, **kwargs):
        pass
    def mark_dirty(self, *args, **kwargs):
        pass
        

class ConstantStorage:
    __slots__ = ('supported_classes', 'defaults', 'links', 'properties', 'is_set', 'excluded', 'external')
    def __init__(self):
        self.supported_classes = {}
        self.defaults = {}
        self.links = {}
        self.properties = {}
        self.is_set = {}
        self.external = {}
        self.excluded = []

class NevuObjectKwargs(TypedDict):
    actual_clone: NotRequired[bool] 
    id: NotRequired[str | None]
    floating: NotRequired[bool]
    single_instance: NotRequired[bool]
    events: NotRequired[Events]
    z: NotRequired[int]
    depth: NotRequired[int]
    z_request_optimization: NotRequired[bool]

class NevuObject:
    id: str | None
    floating: bool
    single_instance: bool
    _events: Events
    actual_clone: bool
    z: int
    z_request_optimization: bool
    
    #INIT STRUCTURE: ====================
    #    __init__ >
    #        preinit >
    #            constants 
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
    
    def __init__(self, size: Vector2 | list, style: Style, **constant_kwargs: Unpack[NevuObjectKwargs]):
        self.constant_kwargs = constant_kwargs.copy() 
        self._lazy_kwargs = {'size': size}
        
    #=== Pre Init ===
    
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
    
    def _add_constant(self, name, supported_classes: tuple | Any, default: Any, 
                      getter: Callable | None = None, setter: Callable | None = None, deleter: Callable | None = None):
        self.constants.supported_classes[name] = supported_classes
        self.constants.defaults[name] = default
        self.constants.is_set[name] = False
        if getter or setter or deleter:
            self.constants.properties[name] = [getter, setter, deleter]
    
    def _add_free_constant(self, name, default: Any):
        self.constants.supported_classes[name] = Any
        self.constants.defaults[name] = default
        self.constants.is_set[name] = None
        self.constants.external[name] = True
    
    def _block_constant(self, name: str):
        self.constants.excluded.append(name)
    
    def _init_constants_base(self):
        self.constants = ConstantStorage()

    def __getattribute__(self, name):
        get = super().__getattribute__
        with contextlib.suppress(AttributeError):
            constants: ConstantStorage = get('constants')
            constant_properties = constants.properties
            if name in constant_properties:
                return constant_properties[name][0]()
        return get(name)

    def __setattr__(self, name, value):
        try:
            if name in self.constants.supported_classes:
                if name in self.constants.external:
                    super().__setattr__(name, value)
                elif name in self.constants.properties:
                    self.constants.properties[name][1](value)
                elif not self._is_valid_type(value, self.constants.supported_classes[name]):
                        raise TypeError(
                            f"Invalid type for constant '{name}'. ",
                            f"Expected {self.constants.supported_classes[name]}, but got {type(value).__name__}.")
                else: super().__setattr__(name, value)
            else:
                super().__setattr__(name, value)
        except AttributeError:
            super().__setattr__(name, value)
            
    def _get_events(self):
        return self._events

    def _set_events(self, value):
        self._events = value
        self._events.on_add = self._on_event_add
        if self.actual_clone:
            self.constant_kwargs['events'] = value
    
    def _on_event_add(self):
        self.constant_kwargs['events'] = self._events
    
    def _add_constants(self):
        self._add_constant("actual_clone", bool, False)
        self._add_constant("id", (str, type(None)), None)
        self._add_constant("floating", bool, False)
        self._add_constant("single_instance", bool, False)
        self._add_constant("events", Events, Events(), getter=self._get_events, setter=self._set_events)
        self._add_constant("z", int, 0)
        self._add_constant_link("depth", "z")
        self._add_constant("z_request_optimization", bool, False)

    def _add_constant_link(self, name: str, link_name: str):
        self.constants.links[name] = link_name

    def _preinit_constants(self):
        for name, value in self.constants.defaults.items():
            if not hasattr(self, name) or self.constants.external.get(name, False):
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
        if name in self.constants.supported_classes.keys():
            constant_name = name
            needed_types = self.constants.supported_classes[name]
        elif name in self.constants.links.keys():
            constant_name = self.constants.links[name]
            if constant_name in self.constants.supported_classes.keys():
                needed_types = self.constants.supported_classes[constant_name]
            else:
                raise ValueError(f"Invalid constant link {name} -> {self.constants.links[name]}. Constant not found.")
        else:
            raise ValueError(f"Constant {name} not found")
        return constant_name, needed_types
    
    def _is_valid_type(self, value, needed_types):
        if not isinstance(needed_types, tuple):
            needed_types = (needed_types,)
        for needed_type in needed_types:
            if needed_type == Callable and callable(value):
                return True
            if needed_type == Any:
                return True
            if isinstance(value, needed_type):
                return True
        return False

    def _process_constant(self, name, constant_name, needed_types, value):
        assert needed_types
        if constant_name not in self.constants.external.keys():
            if constant_name in self.constants.excluded:
                raise ValueError(f"Constant {name} is unconfigurable")
            
            if not isinstance(needed_types, tuple):
                needed_types = (needed_types,)
        
            if not(is_valid := self._is_valid_type(value, needed_types)):
                raise TypeError(f"Invalid type for constant '{constant_name}'. ",
                                f"Expected {needed_types}, but got {type(value).__name__}.")
        
        setattr(self, constant_name, value)
        self.constants.is_set[constant_name] = True

    def _init_test_flags(self):
        pass
    
    def _init_numerical(self):
        self._z_request_optimization_timer = 5
        self._z_request_optimization_max = 5
    
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
        
        self._master_z_handler = None
        self._master_z_handler_placeholder = ZSystemPlaceholder()

    def _init_booleans(self):
        self._sended_z_link = False
        self._dragging = False
        self._kup_kostil = False
        self._kup_abandoned = False
        self._universal_state_kostil = False
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
        #self._events: list[NevuEvent] = []
        self._dirty_rect = []
        
    def _init_start(self):
        if self.booted: return
        self._wait_mode = False
        for i, item in enumerate(self._lazy_kwargs["size"]): #type: ignore
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
        self._events.add(event)
        
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
        #print(self._events.content)
        for event in self._events.content:
            if event._type == type:
                #print(event)
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
    
    def on_click(self):
        """Override this function to run code when the object is clicked"""
    def on_hover(self):
        """Override this function to run code when the object is hovered"""
    def on_keyup(self):
        """Override this function to run code when a key is released"""
    def on_keyup_abandon(self):
        """Override this function to run code when a key is released outside of the object"""
    def on_unhover(self):
        """Override this function to run code when the object is unhovered"""
    def on_scroll(self, side: bool):
        """Override this function to run code when the object is scrolled"""
        
    def _on_click_system(self):
        self._event_cycle(EventType.OnKeyDown, self)
    def _on_hover_system(self):
        self._event_cycle(EventType.OnHover, self)
    def _on_keyup_system(self):
        self._event_cycle(EventType.OnKeyUp, self)
    def _on_keyup_abandon_system(self):
        self._event_cycle(EventType.OnKeyUpAbandon, self)
    def _on_unhover_system(self):
        self._event_cycle(EventType.OnUnhover, self)
    def _on_scroll_system(self, side: bool):
        self._event_cycle(EventType.OnMouseScroll, self, side)
    
    def _group_on_click(self):
        self._on_click_system()
        self.on_click()
    def _group_on_hover(self):
        self._on_hover_system()
        self.on_hover()
    def _group_on_keyup(self):
        self._on_keyup_system()
        self.on_keyup()
    def _group_on_keyup_abandon(self):
        self._on_keyup_abandon_system()
        self.on_keyup_abandon()
    def _group_on_unhover(self):
        self._on_unhover_system()
        self.on_unhover()
    def _group_on_scroll(self, side: bool):
        self._on_scroll_system(side)
        self.on_scroll(side)
    
    def _click(self):
        self._universal_state_kostil = True
        self.hover_state = HoverState.CLICKED

    def _unhover(self):
        self.hover_state = HoverState.UN_HOVERED
    def _hover(self):
        self.hover_state = HoverState.HOVERED
    def _kup(self):
        self._kup_kostil = True
        self._universal_state_kostil = True
        self.hover_state = HoverState.HOVERED
    def _kup_abandon(self):
        self._kup_abandoned = True
        self._universal_state_kostil = True
        self.hover_state = HoverState.UN_HOVERED
        
    @property
    def hover_state(self):
        return self._hover_state
    @hover_state.setter
    def hover_state(self, value: HoverState):
        #if hasattr(self, "_hover_state"):
            #print(f"hover change setter called in {self}, curr_state:{self._hover_state}, new_state:{value}")
        if self._hover_state == value and not self._universal_state_kostil: print("Same state. Exiting"); return
        if self._universal_state_kostil: self._universal_state_kostil = False
        self._hover_state = value
        match self._hover_state:
            case HoverState.CLICKED:
                self._group_on_click()
            case HoverState.HOVERED:
                if self._kup_kostil:
                    self._group_on_keyup()
                    self._kup_kostil = False
                else:
                    self._group_on_hover()
            case HoverState.UN_HOVERED:
                if self._kup_abandoned:
                    self._group_on_keyup_abandon()
                    self._kup_abandoned = False
                else:
                    self._group_on_unhover()
            
    def get_rect_opt(self, without_animation: bool = False):
        if not without_animation:
            return self.get_rect()
        anim_coords = self.animation_manager.get_animation_value(AnimationType.POSITION)
        anim_coords = anim_coords or [0,0]
        return pygame.Rect(
            self.master_coordinates.x - self.relx(anim_coords[0]), # type: ignore
            self.master_coordinates.y - self.rely(anim_coords[1]), # type: ignore
            *self.rel(self.size)
        )
        
    def get_rect(self):
        return get_rect_helper_pygame(self.master_coordinates, self._resize_ratio, self.size)
    
    def get_rect_tuple(self):
        return get_rect_helper(self.master_coordinates, self._resize_ratio, self.size)

    def get_rect_static(self):
        return get_rect_helper(self.coordinates, self._resize_ratio, self.size)

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
        if not self._active or not self._visible:
            return

        if not self._sended_z_link and self._master_z_handler:
            self._sended_z_link = True
            self._z_request = ZRequest(
                link=self,
                on_hover_func=self._hover,
                on_unhover_func=self._unhover,
                on_scroll_func=self._group_on_scroll,
                on_keyup_func=self._kup,
                on_keyup_abandon_func=self._kup_abandon,
                on_click_func=self._click
            )
            self._master_z_handler.add(self._z_request)
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
        if self._changed:
            self._changed = False
    
    def relx(self, num: int | float, min: int | None = None, max: int| None = None) -> int | float:
        return rel_helper(num, self._resize_ratio.x, min, max)

    def rely(self, num: int | float, min: int | None = None, max: int| None = None) -> int | float:
        return rel_helper(num, self._resize_ratio.y, min, max)

    def relm(self, num: int | float, min: int | None = None, max: int | None = None) -> int | float:
        return relm_helper(num, self._resize_ratio.x, self._resize_ratio.y, min, max)
    
    def rel(self, mass: NvVector2, vector: bool = True) -> NvVector2:  
        return mass_rel_helper(mass, self._resize_ratio.x, self._resize_ratio.y, vector) # type: ignore