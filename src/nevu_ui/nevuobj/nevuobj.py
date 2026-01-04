from typing import Any, TypedDict, NotRequired
from collections.abc import Callable
from warnings import deprecated
import pygame
import copy
import contextlib
import difflib
import weakref
from typing import Unpack

from nevu_ui.style import Style
from nevu_ui.color import SubThemeRole
from nevu_ui.core.classes import Events
from nevu_ui.fast.zsystem import ZRequest
from nevu_ui.core.state import nevu_state
from nevu_ui.struct.base import standart_config
from nevu_ui.animations import AnimationType, AnimationManager
from nevu_ui.utils import Cache, NevuEvent
from nevu_ui.size.rules import Px, SizeRule
from nevu_ui.fast.nvvector2 import NvVector2

from nevu_ui.fast.logic import (
    relm_helper, rel_helper, mass_rel_helper, vec_rel_helper, get_rect_helper_pygame, get_rect_helper
)
from nevu_ui.core.enums import (
    HoverState, EventType, CacheType
)

global_counter = 0

def add_obj(self):
    global global_counter
    global_counter += 1
    #print(self.__class__.__name__, "added, counter:", global_counter)

def del_obj(self):
    global global_counter
    global_counter -= 1
    #print(self, "deleted, counter:", global_counter)

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
    id: NotRequired[str | None]
    floating: NotRequired[bool]
    single_instance: NotRequired[bool]
    events: NotRequired[Events]
    z: NotRequired[int]
    depth: NotRequired[int]

class NevuObject:
    id: str | None
    floating: bool
    single_instance: bool
    _events: Events
    z: int
    
    
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
    
    def __init__(self, size: NvVector2 | list, style: Style | str, **constant_kwargs: Unpack[NevuObjectKwargs]):
        self.constants: ConstantStorage = None #type: ignore
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
        
        if __debug__:
            add_obj(self)
            weakref.finalize(self, del_obj, self.__class__.__name__)
    
#=== ConstantEngine functions ===
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

    def __getattribute__(self, name):
        get = _get_attr
        constants: ConstantStorage = get(self,'constants')
        if constants is None: return get(self,name)
        constant_properties = constants.properties
        if name in constant_properties: return constant_properties[name][0]()
        return get(self,name)

    def __setattr__(self, name, value):
        try:
            if name in self.constants.supported_classes:
                if name in self.constants.external: super().__setattr__(name, value)
                elif name in self.constants.properties: self.constants.properties[name][1](value)
                elif not self._is_valid_type(value, self.constants.supported_classes[name]):
                    raise TypeError(
                        f"Invalid type for constant '{name}'. ",
                        f"Expected {self.constants.supported_classes[name]}, but got {type(value).__name__}.")
                else: super().__setattr__(name, value)
            else: super().__setattr__(name, value)
        except AttributeError: super().__setattr__(name, value)
    
    def _add_constants(self):
        self._add_constant("id", (str, type(None)), None)
        self._add_constant("floating", bool, False)
        self._add_constant("single_instance", bool, False)
        self._add_constant("events", Events, Events(), getter=self._get_events, setter=self._set_events)
        self._add_constant("z", int, 0)
        self._add_constant_link("depth", "z")

    def _add_constant_link(self, name: str, link_name: str): self.constants.links[name] = link_name

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
            if constant_name not in self.constants.supported_classes.keys():
                raise ValueError(f"Invalid constant link {name} -> {self.constants.links[name]}. Constant not found.")
            needed_types = self.constants.supported_classes[constant_name]
        else:
            raise ValueError(f"Constant {name} not found")
        return constant_name, needed_types
    
    def _is_valid_type(self, value, needed_types):
        needed_types = (needed_types,)
        for needed_type in needed_types:
            if needed_type == Callable and callable(value): return True
            if needed_type == Any: return True
            if isinstance(value, needed_type): return True
        return False

    def _process_constant(self, name, constant_name, needed_types, value):
        assert needed_types
        if constant_name not in self.constants.external.keys():
            if constant_name in self.constants.excluded:
                raise ValueError(f"Constant {name} is unconfigurable")
            
            if not isinstance(needed_types, tuple): needed_types = (needed_types,)
        
            if not(is_valid := self._is_valid_type(value, needed_types)):
                raise TypeError(f"Invalid type for constant '{constant_name}' in {self.__class__.__name__} instance. ",
                                f"Expected {needed_types}, but got {type(value).__name__}.")
        
        setattr(self, constant_name, value)
        self.constants.is_set[constant_name] = True

#=== Initialization ===
    def _init_test_flags(self): pass
    
    def _init_numerical(self):
        self._z_request_optimization_timer = 5
        self._z_request_optimization_max = 5
    
    def _init_constants(self, **kwargs):
        self.constants = ConstantStorage()
        self._add_constants()
        self._preinit_constants()
        self._change_constants_kwargs(**kwargs)
            
    def _init_style(self, style: Style | str):
        if isinstance(style, str):
            if result := standart_config.styles.get(style, None):
                self.style = result
            else:
                if not standart_config.styles:
                    raise ValueError("No config styles found")
                suggestions = difflib.get_close_matches(style, standart_config.styles.keys())
                err_msg = f"Style {style} not found."
                if suggestions:
                    err_msg += f" Did you mean {', '.join(suggestions)}?"
                raise ValueError(err_msg)
        else: self.style = style
        
    def _init_objects(self):
        self.cache = Cache()
        self._subtheme_role = SubThemeRole.TERTIARY
        self._hover_state = HoverState.UN_HOVERED
        self.animation_manager = AnimationManager()
        self.z_request = None

    def _init_booleans(self):
        self._sended_z_link = False
        self._dragging = False
        self._is_kup = False
        self._kup_abandoned = False
        self._force_state_set_continue = False
        self._visible = True
        self._active = True
        self._changed = True
        self._first_update = True
        self.booted = False
        self._wait_mode = False
        self.dead = False
        
    def _init_lists(self):
        self._resize_ratio = NvVector2(1, 1)
        self.coordinates = NvVector2()
        self.absolute_coordinates = NvVector2()
        self.first_update_functions = []
        self._dirty_rect = []
        
    def _init_start(self):
        if self.booted: return
        self._wait_mode = False
        for i, item in enumerate(self._lazy_kwargs["size"]): #type: ignore
            self._lazy_kwargs["size"][i] = self.num_handler(item) #type: ignore
        if not self._wait_mode: self._lazy_init(**self._lazy_kwargs)

    def _lazy_init(self, size):
        self.size = size if isinstance(size, NvVector2) else NvVector2(size)
        self.original_size = self.size.copy()

    def num_handler(self, number: SizeRule | int | float) -> SizeRule | int | float:
        if isinstance(number, SizeRule):
            if type(number) == Px: return number.value
            else: self._wait_mode = True
        return number

#=== Utils ===
    @property
    def wait_mode(self): return self._wait_mode
    @wait_mode.setter
    def wait_mode(self, value: bool):
        if self._wait_mode == True and not value: self._lazy_init(**self._lazy_kwargs)
        self._wait_mode = value

    @property
    @deprecated("Use absolute_coordinates instead")
    def master_coordinates(self):
        return self.absolute_coordinates
    
    @master_coordinates.setter
    @deprecated("Use absolute_coordinates instead")
    def master_coordinates(self, value):
        self.absolute_coordinates = value

    @property
    def _csize(self):
        return self.cache.get_or_exec(CacheType.RelSize,self._update_size) or self.size

    def add_first_update_action(self, function):
        self.first_update_functions.append(function)

    def get_animation_value(self, animation_type: AnimationType):
        return self.animation_manager.get_current_value(animation_type)

    def get_font(self):
        avg_resize_ratio = (self._resize_ratio[0] + self._resize_ratio[1]) / 2
        font_size = int(self.style.fontsize * avg_resize_ratio)
        return (pygame.font.SysFont(self.style.fontname, font_size) if self.style.fontname == "Arial" 
                else pygame.font.Font(self.style.fontname, font_size))
    
    @property
    def max_borderradius(self): return min(self._rsize.x, self._rsize.y) / 2

    @property
    def _rsize(self) -> NvVector2:
        bw = self.relm(self.style.borderwidth)
        return self._csize - (NvVector2(bw, bw)) * 2

    @property
    def _rsize_marg(self) -> NvVector2: return self._csize - self._rsize 

    @property
    def subtheme_role(self): return self._subtheme_role
    
    @subtheme_role.setter
    def subtheme_role(self, value: SubThemeRole):
        self._subtheme_role = value
        self.cache.clear()
        self._on_subtheme_role_change()
        
    def _on_subtheme_role_change(self): pass
    
    @property
    def _subtheme(self): return self.style.colortheme.get_subtheme(self._subtheme_role)

#=== Action functions ===
    def show(self): self._visible = True
    def hide(self): self._visible = False

    @property
    def visible(self): return self._visible
    @visible.setter
    def visible(self, value: bool): self._visible = value

    def activate(self): self._active = True
    def disactivate(self): self._active = False

    @property
    def active(self): return self._active
    @active.setter
    def active(self, value: bool): self._active = value

#=== Event functions ===
    def _event_cycle(self, type: EventType, *args, **kwargs):
        for event in self._events.content:
            if event._type == type:
                event(*args, **kwargs)

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

    def _get_events(self): return self._events

    def _set_events(self, value):
        self._events = value
        self._events.on_add = self._on_event_add #type: ignore
        if self.actual_clone: self.constant_kwargs['events'] = value
    
    def _on_event_add(self): self.constant_kwargs['events'] = self._events
        
    def resize(self, resize_ratio: NvVector2):
        self._changed = True
        self._resize_ratio = resize_ratio
        self.cache.clear_selected(whitelist=[CacheType.RelSize])

    @property
    def style(self) -> Style: return self._style
    @style.setter
    def style(self, style: Style):
        self._changed = True
        self._style = copy.copy(style)

#=== Zsystem functions ===

    #=== User hooks ===
    def on_click(self): """Override this function to run code when the object is clicked"""
    def on_hover(self): """Override this function to run code when the object is hovered"""
    def on_keyup(self): """Override this function to run code when a key is released"""
    def on_keyup_abandon(self): """Override this function to run code when a key is released outside of the object"""
    def on_unhover(self): """Override this function to run code when the object is unhovered"""
    def on_scroll(self, side: bool): """Override this function to run code when the object is scrolled"""
    
    #=== System hooks ===
    def _on_click_system(self): self._event_cycle(EventType.OnKeyDown, self)
    def _on_hover_system(self): self._event_cycle(EventType.OnHover, self)
    def _on_keyup_system(self): self._event_cycle(EventType.OnKeyUp, self)
    def _on_keyup_abandon_system(self): self._event_cycle(EventType.OnKeyUpAbandon, self)
    def _on_unhover_system(self): self._event_cycle(EventType.OnUnhover, self)
    def _on_scroll_system(self, side: bool): self._event_cycle(EventType.OnMouseScroll, self, side)
    
    #=== Group functions ===
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
    
    #=== Selection functions ===
    def _click(self):
        self._force_state_set_continue = True
        self.hover_state = HoverState.CLICKED
    def _unhover(self):
        self.hover_state = HoverState.UN_HOVERED
    def _hover(self):
        self.hover_state = HoverState.HOVERED
    def _kup(self):
        self._is_kup = True
        self._force_state_set_continue = True
        self.hover_state = HoverState.HOVERED
    def _kup_abandon(self):
        self._kup_abandoned = True
        self._force_state_set_continue = True
        self.hover_state = HoverState.UN_HOVERED

#=== Hover state ===
    @property
    def hover_state(self):
        return self._hover_state
    
    @hover_state.setter
    def hover_state(self, value: HoverState):
        if self._hover_state == value and not self._force_state_set_continue: return
        self.on_state_change(value)
        self._on_state_change_system(value)
        
        if self._force_state_set_continue: self._force_state_set_continue = False
        self._hover_state = value
        
        self.style.mark_state(value)
        
        match self._hover_state:
            case HoverState.CLICKED:
                self._group_on_click()
            case HoverState.HOVERED:
                if self._is_kup:
                    self._group_on_keyup()
                    self._is_kup = False
                else: self._group_on_hover()
            case HoverState.UN_HOVERED:
                if self._kup_abandoned:
                    self._group_on_keyup_abandon()
                    self._kup_abandoned = False
                else: self._group_on_unhover()
                
        self.after_state_change()
        self._after_state_change_system()
        
    def on_state_change(self, state: HoverState): pass
    def _on_state_change_system(self, state: HoverState): pass
    def after_state_change(self): pass
    def _after_state_change_system(self): pass

#=== Rect functions ===
    def get_rect_opt(self, without_animation: bool = False):
        if not without_animation:
            return self.get_rect()
        anim_coords = self.animation_manager.get_animation_value(AnimationType.POSITION)
        anim_coords = anim_coords or [0,0]
        return pygame.Rect(
            self.absolute_coordinates.x - self.relx(anim_coords[0]), # type: ignore
            self.absolute_coordinates.y - self.rely(anim_coords[1]), # type: ignore
            *self.rel(self.size)
        )
        
    def get_rect(self):
        return get_rect_helper_pygame(self.absolute_coordinates, self._resize_ratio, self.size)
    def get_rect_static(self):
        return get_rect_helper(self.coordinates, self._resize_ratio, self.size)

#=== Cache update functions ===
    def _update_coords(self): return self.coordinates
    def _update_size(self): return NvVector2(self.rel(self.size))

#=== Update functions ===
    #========= UPDATE STRUCTURE: ==========
    #    update >
    #
    #        primary_update >
    #            logic_update >
    #                all math and logic code
    #            animation_update >
    #                system animation code
    #            event_update >
    #                all pygame.event dependent code
    #
    #        secondary_update >
    #            widget/layout update code
    #
    #        Update event cycle
    #======================================

    def update(self, events: list | None = None):
        events = events or nevu_state.current_events
        self.primary_update(events)
        self.secondary_update()
        self._event_cycle(EventType.Update)
        
    def primary_update(self, events: list | None = None):
        events = events or []
        self.logic_update()
        self.animation_update()
        self.event_update(events)
        
    def logic_update(self):
        if not self._active or not self._visible: return
        if not self._sended_z_link and nevu_state.window != None:
            self._sended_z_link = True
            #print("SENDED {}".format(self))
            self._z_request = ZRequest(
                link=self,
                on_hover_func=self._hover,
                on_unhover_func=self._unhover,
                on_scroll_func=self._group_on_scroll,
                on_keyup_func=self._kup,
                on_keyup_abandon_func=self._kup_abandon,
                on_click_func=self._click)
            nevu_state.window.add_request(self._z_request)
            
    def animation_update(self):
        self.animation_manager.update()
        
    def event_update(self, events: list): pass
    
    def secondary_update(self): pass

#=== Draw functions ===
    #========== DRAW STRUCTURE: ===========
    #    draw >
    #        primary_draw >
    #            basic draw code
    #
    #        Draw event cycle
    #
    #        secondary_draw >
    #            secondary_draw_content >
    #                all additional draw | on change code
    #            secondary_draw_end >
    #                all after change code
    #
    #        Render event cycle
    #======================================

    def draw(self):
        self.primary_draw()
        self._event_cycle(EventType.Draw)
        self.secondary_draw()
        self._event_cycle(EventType.Render)
        
    def primary_draw(self): pass
    
    def secondary_draw(self):
        self.secondary_draw_content()
        self.secondary_draw_end()
        
    def secondary_draw_content(self): pass
    
    def secondary_draw_end(self):
        if self._changed: self._changed = False

#=== Relative functions ===
    def relx(self, num: int | float, min: int | float = -1.0, max: int | float = -1.0) -> int | float:
        return rel_helper(num, self._resize_ratio.x, min, max)

    def rely(self, num: int | float, min: int | float = -1.0, max: int | float = -1.0) -> int | float:
        return rel_helper(num, self._resize_ratio.y, min, max)

    def relm(self, num: int | float, min: int | float = -1.0, max: int | float = -1.0) -> int | float:
        return relm_helper(num, self._resize_ratio.x, self._resize_ratio.y, min, max)
    
    def rel(self, mass: NvVector2, vector: bool = True) -> NvVector2:  
        return vec_rel_helper(mass, self._resize_ratio.x, self._resize_ratio.y) # type: ignore

#=== Clone functions ===
    def _create_clone(self):
        cls = self.__class__
        return cls(self._lazy_kwargs['size'], copy.deepcopy(self.style), **self.constant_kwargs)
    
    def clone(self): 
        new_self = self._create_clone()
        self._on_copy_system(new_self)
        self.on_copy(new_self)
        new_self._on_copy_system_after()
        new_self.on_copy_after()
        return new_self
    
    def _on_copy_system(self, clone: "NevuObject", no_cache: bool = False): 
        clone._active = self._active
        clone._visible = self._visible
        clone.dead = self.dead
        if not no_cache:
            clone.cache = self.cache.copy()
    def _on_copy_system_after(self): pass
    def on_copy(self, clone): pass
    def on_copy_after(self): pass
    def __deepcopy__(self, *args, **kwargs): return self.clone()

#=== Kill functions ===
    def _clear_z_request(self):
        if hasattr(self, 'z_request') and self.z_request:
            self.z_request.on_click_func = None
            self.z_request.on_hover_func = None
            self.z_request.on_scroll_func = None
            self.z_request.on_unhover_func = None
            self.z_request.on_keyup_func = None
            self.z_request.on_keyup_abandon_func = None
            self.z_request = None
            
    def kill(self):
        self.dead = True
        self.visible = False
        self.is_active = False

        self._clear_z_request()

        if hasattr(self, 'renderer'): self.renderer = None

        if hasattr(self, 'items') and isinstance(self.items, list):
            for item in list(self.items):
                if hasattr(item, 'kill'): item.kill()
            self.items.clear()

        if hasattr(self, '_sended_z_link') and self._sended_z_link and nevu_state.window:
            nevu_state.window.z_system.mark_dirty()

_get_attr = object.__getattribute__