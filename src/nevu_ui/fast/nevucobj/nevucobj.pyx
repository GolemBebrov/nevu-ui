# distutils: language = c++
# cython: language_level=3
# cython: boundscheck=False
# cython: wraparound=False
# cython: cdivision=True
# cython: nonecheck=False
# cython: initializedcheck=False
from __future__ import annotations
import weakref
from nevu_ui.fast.nvvector2.nvvector2 cimport NvVector2
from nevu_ui.fast.nvparam.nvparam cimport NvParam
from cpython.dict cimport PyDict_GetItem
from cpython.object cimport PyObject, PyObject_GenericSetAttr, PyObject_GenericGetAttr
from cpython.list cimport PyList_GET_SIZE, PyList_GET_ITEM
from nevu_ui.fast.nevucache.nevucache cimport Cache
from nevu_ui.core.state import nevu_state
from nevu_ui.core.enums import CacheType
from nevu_ui.core.classes import _strategy_type, Strategy
from nevu_ui.fast.zsystem.fast_zsystem cimport ZSystem, ZRequest
from nevu_ui.core.enums import (
    HoverState, EventType, CacheType, ParamLayer, AnimationType
)

cimport cython
cdef extern from "Python.h":
    object PyObject_CallNoArgs(object func)

call_noarg = PyObject_CallNoArgs

from nevu_ui.fast.logic.fast_logic cimport relm_helper, rel_helper, mass_rel_helper, vec_rel_helper, get_nvrect_helper
from nevu_ui.fast.nvrect.nvrect cimport NvRect
@cython.freelist(32)
cdef class NevuCobject:
    def __cinit__(self, *args, **kwargs):
        self.coordinates = NvVector2.new(0, 0)
        self.absolute_coordinates = NvVector2.new(0, 0)
        self.size = NvVector2.new(0, 0)
        self._resize_ratio = NvVector2.new(1, 1)
        self.params = list()
        self._blacklisted_params = list()
        self._param_links = dict()
        self._params_map = dict()
        self.cache = Cache.new()
        self._sended_z_link = False
        self._dragging = False
        self._is_kup = False
        self._kup_abandoned = False
        self._force_state_set_continue = False
        self._visible = True
        self._active = True
        self._custom_secondary_update = False
        self._custom_animation_update = False
        self._custom_logic_update = False
        self._custom_event_update = False
        self._custom_primary_draw = False
        self._custom_secondary_draw = False
        self._custom_secondary_draw_content = False
        self._custom_secondary_draw_end = False
        self._changed = True
        self._first_update = True
        self.booted = False
        self._wait_mode = False
        self._dead = False
        self._has_position_anim = False
        self.node_type = 0
        self.specific_cache_whitelist = [CacheType.Scaled_Image, CacheType.Image, CacheType.Scaled_Gradient, CacheType.Surface,  CacheType.Borders, CacheType.Scaled_Borders, CacheType.Scaled_Background, CacheType.Background, CacheType.Texture, CacheType.RlFont, CacheType.TextArgs, CacheType.ClickTexture]

    cpdef _set_node_type(self, short node_type):
        self.node_type = node_type

    cpdef list _get_param_names(self):
        return list(self._params_map.keys())

    cpdef object _find_param(self, str name):
        return self._params_map.get(name)

    cpdef void _add_param(self, str name, supported_classes, default, getter, setter, int layer):
        param = NvParam.new(name, layer, None, default, supported_classes, getter, setter)
        self.params.append(param)
        self._params_map[name] = param

    cpdef NvParam get_param_strict(self, str name):
        cdef PyObject* p_ptr = PyDict_GetItem(self._params_map, name)
        return <NvParam>p_ptr

    cpdef NvParam get_param(self, str name):
        cdef PyObject* p_ptr = PyDict_GetItem(self._params_map, name)

        if p_ptr == NULL:
            return None

        return <NvParam><object>p_ptr

    cpdef object get_param_value(self, str name):
        cdef PyObject* p_ptr = PyDict_GetItem(self._params_map, name)
        if p_ptr == NULL: return None
        cdef NvParam param = <NvParam>p_ptr
        return param.get()

    cpdef void set_param_value(self, str name, object new_value):
        cdef PyObject* p_ptr = PyDict_GetItem(self._params_map, name)
        if p_ptr == NULL:
            raise KeyError(f"Parameter '{name}' not found")
        cdef NvParam param = <NvParam>p_ptr
        param.set(new_value)

    cpdef double relx_custom(self, double num, double min, double max):
        return rel_helper(num, self._resize_ratio.x, min, max)

    cpdef double rely_custom(self, double num, double min, double max):
        return rel_helper(num, self._resize_ratio.y, min, max)

    cpdef double relm_custom(self, double num, double min, double max):
        return relm_helper(num, self._resize_ratio.x, self._resize_ratio.y, min, max)

    cpdef double relx(self, double num):
        return rel_helper(num, self._resize_ratio.x, -1.0, -1.0)

    cpdef double rely(self, double num):
        return rel_helper(num, self._resize_ratio.y, -1.0, -1.0)

    cpdef double relm(self, double num):
        return relm_helper(num, self._resize_ratio.x, self._resize_ratio.y, -1.0, -1.0)

    cpdef NvVector2 rel(self, NvVector2 vec):
        return vec_rel_helper(vec, self._resize_ratio.x, self._resize_ratio.y)

    cpdef NvRect get_nvrect(self):
        return get_nvrect_helper(self.absolute_coordinates, self._resize_ratio, self.size)

    cpdef set_coordinates(self, NvVector2 coordinates):
        if self.coordinates == coordinates:
            return
        cdef bint need_to_set = self._coordinates_setter(coordinates) #type: ignore
        if not need_to_set: return
        self.coordinates = coordinates

    cdef inline void c_set_coords_xy(self, double x, double y) noexcept:
        if self.coordinates.x == x and self.coordinates.y == y:
            return
        cdef NvVector2 new_coords = NvVector2.new(x, y)
        cdef bint need_to_set = self._coordinates_setter(new_coords) #type: ignore
        if not need_to_set: return
        self.coordinates = new_coords

    cpdef void clear_all(self):
        if nevu_state.window.renderer_type.raylib:
            self._clear_rl_specific()
        self.cache.c_clear()

    cpdef void clear_surfaces(self):
        if nevu_state.window.renderer_type.raylib:
            call_noarg(self._clear_rl_specific)
        self.cache.c_clear_selected(whitelist = self.specific_cache_whitelist, blacklist = [])

    cdef inline NvVector2 c_get_actual_size(self):
        if self.get_param_value("strategy") == Strategy.Relative:
            return self.size * self._resize_ratio
        return self.size

    def get_actual_size(self):
        return self.c_get_actual_size()

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

    def _event_cycle(self, type, *args, **kwargs):
        cdef NvParam events = self.get_param_strict("events")
        cdef list content = events.value.content
        self._core_event_cycle(type, content, args, kwargs)

    cdef inline void _core_event_cycle(self, object type, list content, tuple args, dict kwargs):
        cdef Py_ssize_t n = PyList_GET_SIZE(content)
        cdef Py_ssize_t i = 0

        while i < n:
            event = <object>PyList_GET_ITEM(content, i)
            if event._type == type:
                event(*args, **kwargs)
            i += 1

    cdef inline void _core_event_cycle_clear(self, object type):
        cdef NvParam events = self.get_param_strict("events")
        cdef list content = events.value.content
        cdef Py_ssize_t n = PyList_GET_SIZE(content)
        cdef Py_ssize_t i = 0
        while i < n:
            event = <object>PyList_GET_ITEM(content, i)
            if event._type == type:
                call_noarg(event)
            i += 1

    cpdef update(self):
        if not self._active or self._dead: return
        events = nevu_state.current_events
        self._primary_update(events)
        if self._custom_secondary_update:
            call_noarg(self.secondary_update)
        self._core_event_cycle_clear(EventType.Update)

    cdef inline void _primary_update(self, events):
        events = events or []
        self._base_logic_update()
        if self._custom_logic_update:
            call_noarg(self._logic_update)
        self._base_animation_update()
        if self._custom_animation_update:
            call_noarg(self._animation_update)
        if self._custom_event_update:
            self._event_update(events)

    cdef inline void _base_animation_update(self):
        if not self.animation_manager: return
        self.animation_manager.update()

    @staticmethod
    def _ensure_func_safety(function):
        if function is None: return None

        if hasattr(function, '__self__') and function.__self__ is not None:
            # tis shit is bound method
            return weakref.WeakMethod(function)

        return weakref.ref(function)

    cdef inline void _base_logic_update(self):
        if not self._sended_z_link and nevu_state.window != None:
            self._sended_z_link = True
            self._z_request = ZRequest.new(
                self,
                self._ensure_func_safety(self._hover),
                self._ensure_func_safety(self._unhover),
                self._ensure_func_safety(self._click),
                self._ensure_func_safety(self._kup),
                self._ensure_func_safety(self._kup_abandon),
                self._ensure_func_safety(self._group_on_scroll),
            )
            nevu_state.window.add_request(self._z_request) # type: ignore
        cdef list next_frame_functions = self._next_frame_functions
        cdef Py_ssize_t n = PyList_GET_SIZE(next_frame_functions)
        if n == 0: return
        cdef Py_ssize_t i = 0
        while i < n:
            func = <object>PyList_GET_ITEM(next_frame_functions, i)
            if isinstance(func, (weakref.ref, weakref.WeakMethod)):
                func = func()
            if func:
                call_noarg(func)
            i+=1
        next_frame_functions.clear()


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

    cpdef draw(self):
        if not self._visible or self._wait_mode or self._dead: return
        if self._changed:
            call_noarg(self.on_change)
            self._on_change_system()
        if self._custom_primary_draw:
            call_noarg(self._primary_draw)
        ce = self._core_event_cycle_clear
        ce(EventType.Draw)
        self._base_secondary_draw()
        if self._custom_secondary_draw:
            call_noarg(self.secondary_draw)
        ce(EventType.Render)

    cdef inline void _base_secondary_draw(self):
        if self._custom_secondary_draw_content:
            call_noarg(self.secondary_draw_content)
        if self._custom_secondary_draw_end:
            call_noarg(self._secondary_draw_end)
        self._base_secondary_draw_end()

    cdef inline void _base_secondary_draw_end(self):
        if self._changed: self._changed = False

    def on_state_change(self, state: HoverState): pass
    def _on_state_change_system(self, state: HoverState): pass

    #=== System hooks ===
    cpdef _on_click_system(self): self._event_cycle(EventType.OnKeyDown, self)
    cpdef _on_hover_system(self): self._event_cycle(EventType.OnHover, self)
    cpdef _on_keyup_system(self): self._event_cycle(EventType.OnKeyUp, self)
    cpdef _on_keyup_abandon_system(self): self._event_cycle(EventType.OnKeyUpAbandon, self)
    cpdef _on_unhover_system(self): self._event_cycle(EventType.OnUnhover, self)
    cpdef _on_scroll_system(self, bint side): self._event_cycle(EventType.OnMouseScroll, self, side)
    cpdef _on_change_system(self): self._event_cycle(EventType.OnChange, self)

    #=== Group functions ===
    cpdef _group_on_click(self):
        self._on_click_system()
        call_noarg(self.on_click)
    cpdef _group_on_hover(self):
        self._on_hover_system()
        call_noarg(self.on_hover)
    cpdef _group_on_keyup(self):
        self._on_keyup_system()
        call_noarg(self.on_keyup)
    cpdef _group_on_keyup_abandon(self):
        self._on_keyup_abandon_system()
        call_noarg(self.on_keyup_abandon)
    cpdef _group_on_unhover(self):
        self._on_unhover_system()
        call_noarg(self.on_unhover)
    cpdef _group_on_scroll(self, bint side):
        self._on_scroll_system(side)
        self.on_scroll(side)

    #=== Selection functions ===
    cpdef _click(self):
        self._force_state_set_continue = True
        self.set_hover_state(HoverState.Clicked)
    cpdef _unhover(self): self.set_hover_state(HoverState.NotHovered)
    cpdef _hover(self): self.set_hover_state(HoverState.Hovered)
    cpdef _kup(self):
        self._is_kup = True
        self._force_state_set_continue = True
        self.set_hover_state(HoverState.Hovered)
    cpdef _kup_abandon(self):
        self._kup_abandoned = True
        self._force_state_set_continue = True
        self.set_hover_state(HoverState.NotHovered)

    cdef inline set_hover_state(self, value):
        if self._hover_state == value and not self._force_state_set_continue: return
        self.on_state_change(value)
        self._on_state_change_system(value)

        if self._force_state_set_continue: self._force_state_set_continue = False
        self._hover_state = value

        self.style.mark_state(value)


        if value == HoverState.Clicked:
            self._group_on_click()
        elif value == HoverState.Hovered:
            if self._is_kup:
                self._group_on_keyup()
                self._is_kup = False
            else: self._group_on_hover()
        elif value == HoverState.NotHovered:
            if self._kup_abandoned:
                self._group_on_keyup_abandon()
                self._kup_abandoned = False
            else: self._group_on_unhover()

        self.after_state_change()
        self._after_state_change_system()

    def __getattribute__(self, name):
        cdef dict params_map
        cdef PyObject* param
        cdef NvParam c_param

        params_map = self._params_map
        if params_map is not None:
            param = PyDict_GetItem(params_map, name)
            if param != NULL:
                c_param = <NvParam>param
                return c_param.get()

        return PyObject_GenericGetAttr(self, name)

    def __setattr__(self, name, value):
        cdef dict params_map
        cdef object prop
        cdef PyObject* param
        cdef NvParam c_param

        if len(name) >= 1 and name[0] == '_':
            if PyObject_GenericSetAttr(self, name, value) < 0:
                raise
            return

        prop = getattr(self.__class__, name, None)
        if prop is not None and hasattr(prop, "__set__"):
            prop.__set__(self, value)
            return

        params_map = self._params_map
        if params_map is not None:
            param = PyDict_GetItem(params_map, name)
            if param != NULL:
                c_param = <NvParam><object>param
                c_param.set(value)
                return

        if PyObject_GenericSetAttr(self, name, value) < 0:
            raise
