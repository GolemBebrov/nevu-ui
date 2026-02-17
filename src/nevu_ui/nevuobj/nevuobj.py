from collections.abc import Callable
from warnings import deprecated
import pygame
import copy
import difflib
import weakref
from typing import Unpack, Any
import pyray as rl

from nevu_ui.style import Style
from nevu_ui.fast.nevucobj import NevuCobject
from nevu_ui.color import SubThemeRole
from nevu_ui.core.classes import Events
from nevu_ui.fast.zsystem import ZRequest
from nevu_ui.core.state import nevu_state
from nevu_ui.struct.base import standart_config
from nevu_ui.animations import AnimationType, AnimationManager
from nevu_ui.utils import Cache, NevuEvent, mouse
from nevu_ui.size.rules import Px, SizeRule
from nevu_ui.fast.nvvector2 import NvVector2
from nevu_ui.overlay.tooltip import Tooltip
from nevu_ui.nevuobj.typehints import NevuObjectKwargs, NevuObjectTemplate

from nevu_ui.fast.logic import (
    get_rect_helper_pygame, get_rect_helper
)
from nevu_ui.core.enums import (
    HoverState, EventType, CacheType, ConstantLayer
)

global_counter = 0

def add_obj(self):
    global global_counter
    global_counter += 1
   # print(self.__class__.__name__, "added, counter:", global_counter)

def del_obj(self):
    global global_counter
    global_counter -= 1
    #print(self, "deleted, counter:", global_counter)

class NevuObject(NevuCobject):
    #INIT STRUCTURE: ====================
    #    __init__ >
    #        preinit >
    #            flags
    #            test_flags
    #            constants l1
    #        basic_variables >
    #            booleans/dependent flags
    #            numerical
    #            lists/vectors
    #            constants l2
    #        complicated_variables >
    #            style
    #            objects
    #            constants l3
    #    _lazy_init >
    #        size/master dependent code
    #======================================
    
    def __init__(self, size: NvVector2 | list, style: Style | str, **constant_kwargs: Unpack[NevuObjectKwargs]):
        self.constant_kwargs = constant_kwargs.copy()
        self.cache = Cache()
        self._template = NevuObjectTemplate(size)
        self._first_update_functions = []
        
    #=== Pre Init ===
        #=== Flags ===
        self._init_flags()
        
        #=== Test Flags ===
        self._init_test_flags()
        
        #=== Constants Declaration ===
        self._declare_constants(**constant_kwargs)
        
        #=== Constants L1 ===
        self._init_constant_layer(ConstantLayer.Top, **constant_kwargs)
        
    #=== Basic Variables ===    
        #=== Booleans(Flags) ===
        self._init_booleans()

        #=== Numerical(int, float) ===
        self._init_numerical()

        #=== Lists/Vectors ===
        self._init_lists()
        
        #=== Constants L2 ===
        self._init_constant_layer(ConstantLayer.Basic, **constant_kwargs)
        
    #=== Complicated Variables ===
        #=== Style ===
        self._init_style(style)
    
        #=== Objects ===
        self._init_objects()
        
        #=== Constants L3 ===
        self._init_constant_layer(ConstantLayer.Complicated, **constant_kwargs)
        
        if __debug__:
            add_obj(self)
            weakref.finalize(self, del_obj, self.__class__.__name__)
    
#=== ConstantEngine functions ===
#INFO: ConstantEngine Version V4C

    def _add_param(self, name, supported_classes: tuple | Any, default: Any, 
                      getter: Callable | None = None, setter: Callable | None = None, layer = 1):
        super()._add_param(name, supported_classes, default, getter, setter, layer)

            
    def _change_param_name(self, name: str, new_name: str):
        if name == new_name: return
        param_names = self._get_param_names()
        if name not in param_names: raise KeyError(f"Constant '{name}' does not exist and cannot be renamed.")
        if new_name in param_names: raise ValueError(f"Constant '{new_name}' already exists.")
        param = self._find_param(name)
        assert param
        param.name = new_name
    
    def _change_param_default(self, name: str, default: Any):
        if name not in self._get_param_names(): raise KeyError(f"Constant '{name}' does not exist and cannot be changed.")
        self.get_param_strict(name).default = default
    
    def _add_free_param(self, name, default: Any, layer = 1):
        pass
    
    def _block_param(self, name: str):
        param_names = self._get_param_names()
        if name not in param_names: raise KeyError(f"Constant '{name}' does not exist and cannot be renamed.")
        self._blacklisted_params.append(name)
    
    def __getattr__(self, name: str):
        return self.get_param_value(name)
    
    def _add_params(self):
        self._add_param("id", (str, type(None)), None)
        self._add_param("floating", bool, False)
        self._add_param("single_instance", bool, False)
        self._add_param("events", Events, Events(), getter=self._get_events, setter=self._set_events, layer=ConstantLayer.Basic)
        #print(self._find_param("events").setter)
        self._add_param("z", int, 0)
        self._add_param_link("depth", "z")
        self._add_param("tooltip", Tooltip | type(None), None, getter=self._tooltip_getter, layer=ConstantLayer.Lazy)
        self._add_param("subtheme_role", SubThemeRole, SubThemeRole.TERTIARY, getter=self._subtheme_role_getter, setter=self._subtheme_role_setter, layer=ConstantLayer.Complicated)
        
    def _add_param_link(self, link_name: str, name: str): 
        self._param_links[link_name] = name

    def _preinit_params(self, layer):
        for param in self.params:
            if param.layer != layer: continue
            if param.name in list(self.constant_kwargs.keys()): continue
            param.value = param.default

    def _apply_params(self, current_layer, **kwargs):
        constant_name = None
        needed_types = None
        processed = set()
        for name, value in kwargs.items():
            name = name.lower()
            constant_name, needed_types, layer = self._extract_param_data(name)
            if current_layer != layer: continue
            if constant_name in processed: 
                raise ValueError(f"Constant {name}({constant_name}) is already set.")
            self._process_constant(name, constant_name, needed_types, value)
            processed.add(constant_name)
    
    def _extract_param_data(self, name):
        if name in self._get_param_names():
            param = self._find_param(name)
        elif name in self._param_links.keys():
            param = self._find_param(self._param_links[name])
        else: raise ValueError(f"Paramether {name} not found")
        assert param
        return param.name, param.type, param.layer
    
    def _is_valid_type(self, value, needed_types):
        needed_types = (needed_types,)
        for needed_type in needed_types:
            if needed_type == Callable and callable(value): return True
            if needed_type == Any: return True
            if type(needed_type) == tuple:
                if needed_type[0] == Any: return True
            #print(value, needed_type)
            if isinstance(value, needed_type): return True
        return False

    def _process_constant(self, name, param_name, needed_types, value):
        assert needed_types
        if param_name not in self._get_param_names():
            if param_name in self._blacklisted_params:
                raise ValueError(f"Param {name} is unconfigurable")
            if not self._is_valid_type(value, needed_types):
                raise TypeError(f"Invalid type for param '{param_name}' in {self.__class__.__name__} instance. ",
                                f"Expected {needed_types}, but got {type(value).__name__}.")
        param = self.get_param_strict(param_name)
        assert param
        param.set(value)

#=== Initialization ===

    def _create_template(self, size: NvVector2 | list):
        return NevuObjectTemplate(size)
    
    def _init_flags(self): 
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
        self._dead = False
        
    def _init_test_flags(self): pass
    
    def _init_numerical(self): pass
    
    def _declare_constants(self, **kwargs):
        self._add_params()
        
    def _init_constant_layer(self, layer, **kwargs):
        self._preinit_params(layer)
        self._apply_params(layer, **kwargs)
            
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
        self._hover_state: HoverState = HoverState.UN_HOVERED
        self.animation_manager = AnimationManager()
        self.z_request: ZRequest | None = None

    def _init_booleans(self): pass
        
    def _init_lists(self):
        self._resize_ratio = NvVector2(1, 1)
        self.coordinates = NvVector2()
        self.absolute_coordinates = NvVector2()
        self._next_frame_functions = []
        
    def _init_start(self):
        if self.booted: return
        self._wait_mode = False
        for i, item in enumerate(self._template.size): #type: ignore
            self._template.size[i] = self._handle_size_rules(item) #type: ignore
        if not self._wait_mode: self._lazy_init(**self._template.__dict__)
    
    def _lazy_init_wrapper(self, *args, **kwargs):
        self._lazy_init(*args, **kwargs)
        self._init_constant_layer(ConstantLayer.Lazy, **self.constant_kwargs)
        
    def _lazy_init(self, size):
        self.size = size if isinstance(size, NvVector2) else NvVector2(size)
        self.original_size = self.size.copy()

    def _handle_size_rules(self, number: SizeRule | int | float) -> SizeRule | int | float:
        if isinstance(number, SizeRule):
            if type(number) == Px: return number.value
            else: self._wait_mode = True
        return number

#=== Utils ===

    def _coordinates_setter(self, coordinates: NvVector2) -> bool:
        return True

    @property
    def wait_mode(self): return self._wait_mode
    @wait_mode.setter
    def wait_mode(self, value: bool):
        if self._wait_mode == True and not value: self._lazy_init_wrapper(**self._template.__dict__)
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
        self._first_update_functions.append(function)
    
    def add_next_frame_action(self, function):
        self._next_frame_functions.append(function)

    def _get_animation_value(self, animation_type: AnimationType):
        return self.animation_manager.get_current_value(animation_type)

    def get_pygame_font(self, override_size = None):
        font_size = int(self.relm(override_size or self.style.fontsize))
        return (pygame.font.SysFont(self.style.fontname, font_size) if self.style.fontname == "Arial" 
            else pygame.font.Font(self.style.fontname, font_size))
    
    def get_raylib_font(self, override_size=None) -> rl.Font:
        font_size = self.relm(override_size or self.style.fontsize)
        
        def _load_font_with_cyrillic():
            codepoints = list(range(32, 127)) + list(range(1024, 1104)) + [1025, 1105]
            glyph_count = len(codepoints)
            c_array = rl.ffi.new("int[]", codepoints)
            c_ptr = rl.ffi.cast("int *", c_array)
            return rl.load_font_ex(self.style.fontname, round(font_size), c_ptr, glyph_count)

        return self.cache.get_or_exec(CacheType.RlFont, _load_font_with_cyrillic) #type: ignore
    
    @property
    def max_borderradius(self): return min(self._rsize.x, self._rsize.y) / 2

    @property
    def _rsize(self) -> NvVector2:
        bw = self.relm(self.style.borderwidth)
        return self._csize - (NvVector2(bw, bw)) * 2

    @property
    def _rsize_marg(self) -> NvVector2: return self._csize - self._rsize 

    def _subtheme_role_getter(self): return self._subtheme_role
    
    def _subtheme_role_setter(self, value: SubThemeRole):
        self._subtheme_role = value
        self.cache.clear()
        self._on_subtheme_role_change()
        
    def _on_subtheme_role_change(self): pass
    
    @property
    def _subtheme(self): return self.style.colortheme.get_subtheme(self.get_param_strict("subtheme_role").value)
    
    @property
    def tooltip(self): return self.get_param_strict("tooltip").value
    @tooltip.setter
    def tooltip(self, value: Tooltip | None): 
        self.get_param_strict("tooltip").value = value
        if self.get_param_strict("tooltip").value: 
            self.get_param_strict("tooltip").value.connect_to_master(self)

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
        for event in self.get_param_strict("events").value.content:
            if event._type == type:
                event(*args, **kwargs)

    def subscribe(self, event: NevuEvent):
        """Adds a new event listener to the object.
        Args:
            event (NevuEvent): The event to subscribe
        Returns:
            None
        """
        self.get_param_value("events").add(event)
        
    @deprecated("use .subscribe() instead. This method will be removed in a future version.")
    def add_event(self, event: NevuEvent):
        """**Deprecated**: use .subscribe instead."""
        return self.subscribe(event)

    def _set_events(self, value: Events):
        value.on_add = self._on_event_add #type: ignore
        return self.get_param_value("events")
    
    def _on_event_add(self): self.constant_kwargs['events'] = self.get_param_value("events")
        
    def _resize(self, resize_ratio: NvVector2):
        self._changed = True
        self._resize_ratio = resize_ratio
        self.cache.clear_selected(whitelist=[CacheType.RelSize])
        if self.tooltip: self.tooltip.resize(resize_ratio)

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
    def on_change(self): """Override this function to run code when the object is changed"""
    
    #=== System hooks ===
    def _on_click_system(self): self._event_cycle(EventType.OnKeyDown, self)
    def _on_hover_system(self): self._event_cycle(EventType.OnHover, self)
    def _on_keyup_system(self): self._event_cycle(EventType.OnKeyUp, self)
    def _on_keyup_abandon_system(self): self._event_cycle(EventType.OnKeyUpAbandon, self)
    def _on_unhover_system(self): self._event_cycle(EventType.OnUnhover, self)
    def _on_scroll_system(self, side: bool): self._event_cycle(EventType.OnMouseScroll, self, side)
    def _on_change_system(self): self._event_cycle(EventType.OnChange, self)
    
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
        self._primary_update(events)
        self.secondary_update()
        self._event_cycle(EventType.Update)
        
    def _primary_update(self, events: list | None = None):
        events = events or []
        self._logic_update()
        self._animation_update()
        self._event_update(events)
        
    def _logic_update(self):
        if not self._active or not self._visible: return
        if not self._sended_z_link and nevu_state.window != None:
            self._sended_z_link = True
            self._z_request = ZRequest(
                link=self,
                on_hover_func=self._hover,
                on_unhover_func=self._unhover,
                on_scroll_func=self._group_on_scroll,
                on_keyup_func=self._kup,
                on_keyup_abandon_func=self._kup_abandon,
                on_click_func=self._click)
            nevu_state.window.add_request(self._z_request)
        if self._next_frame_functions:
            for func in self._next_frame_functions: func()
            self._next_frame_functions.clear()
            
    def _animation_update(self):
        self.animation_manager.update()
        
    def _event_update(self, events: list): pass
    
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
        if self._changed and self._active and self._visible and not self.wait_mode:
            self.on_change()
            self._on_change_system()
        self._primary_draw()
        self._event_cycle(EventType.Draw)
        self._secondary_draw()
        self._event_cycle(EventType.Render)
        
    def _primary_draw(self): pass
    
    def _secondary_draw(self):
        self.secondary_draw_content()
        self._secondary_draw_end()
        
    def secondary_draw_content(self): pass
    
    def _secondary_draw_end(self):
        if self._changed: self._changed = False

#=== Relative functions ===
    #Empty... :3
    #Realized in NevuCobject

#=== Clone functions ===
    def _create_clone(self):
        cls = self.__class__
        return cls(self._template['size'], copy.deepcopy(self.style), **self.constant_kwargs)
    
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
        clone._dead = self._dead
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
        self._dead = True
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