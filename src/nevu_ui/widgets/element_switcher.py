import copy
import pygame
import numpy as np
import contextlib
from typing import Callable, AnyStr, Any

from nevu_ui.fast.nvvector2 import NvVector2
from nevu_ui.widgets import Widget, Button, WidgetKwargs
from nevu_ui.utils import mouse, keyboard

from typing import Any, TypedDict, NotRequired, Unpack

from nevu_ui.style import (
    Style, default_style
)

from nevu_ui.core_types import CacheType, HoverState

class ElementSwitcherKwargs(WidgetKwargs):
    on_change: NotRequired[Callable | None]
    current_index: NotRequired[int]
    button_padding: NotRequired[int]
    arrow_width: NotRequired[int]
    left_text: NotRequired[str]
    left_key: NotRequired[Any]
    right_text: NotRequired[str]
    right_key: NotRequired[Any]

class Element:
    __slots__ = ["text", "id"]
    def __init__(self, text, id: str | None = None):
        self.text = text
        self.id = id

class Elements:
    @staticmethod
    def create(*items):
        final_list = []
        element_list = []
        element_pair = []
        try:
            for item in items:
                if isinstance(item, Element):
                    element_list.append(item)
                    continue
                elif not isinstance(item, str):
                    if isinstance(item, (list, tuple)) and len(item) == 2:
                        element_pair = [str(item[0]), str(item[1]) if item[1] else None]
                    else:
                        element_pair = [str(item), None]
                else:
                    element_pair = [item, None]
                final_list.append(element_pair)
        except Exception as e:
            raise ValueError("Some objects cannot be converted into str", e)
        
        element_list.extend(Element(pair[0], pair[1]) for pair in final_list)
        return element_list

class ElementSwitcher(Widget):
    on_change: Callable | None
    _сurrent_index: int
    button_padding: int
    arrow_width: int
    left_text: str
    right_text: str
    left_key: Any
    right_key: Any
    def __init__(self, size: NvVector2 | list, elements: list[Element | Any | list] | None = None, style: Style = default_style, **constant_kwargs: Unpack[ElementSwitcherKwargs]):
        super().__init__(size, style, **constant_kwargs)
        self._lazy_kwargs = {'size': size, 'elements': elements}

    def _add_constants(self):
        super()._add_constants()
        self._add_constant("on_change", (type(None), Callable), None)
        self._add_constant("current_index", int, 0)
        self._add_constant("button_padding", int, 10)
        self._add_constant("arrow_width", int, 10)
        self._add_constant("left_text", (str), "<")
        self._add_constant("left_key", Any, None)
        self._add_constant("right_text", (str), ">")
        self._add_constant("right_key", Any, None)

    def _init_booleans(self):
        super()._init_booleans()
        self.hoverable = False
        self._delayed_button_update = False
        
    def _lazy_init(self, size: NvVector2 | list, elements: list[Element] | None = None):
        super()._lazy_init(size)
        elements = elements or []
        self.elements = Elements.create(*elements)
        self.bake_text(self.current_element_text)
        self.add_first_update_action(self._create_buttons)
    
    def _init_numerical(self):
        super()._init_numerical()
        self._additional_y_marg = 1
    
    @property
    def _global_hovered(self):
        return self.hover_state in [HoverState.HOVERED, HoverState.CLICKED] or self._button_hovered
    
    @property
    def _button_hovered(self):
        return self.button_left.hover_state in [HoverState.HOVERED, HoverState.CLICKED] or self.button_right.hover_state in [HoverState.HOVERED, HoverState.CLICKED]
    
    def logic_update(self):
        super().logic_update()
        with contextlib.suppress(Exception):
            if not self._global_hovered: return
            if keyboard.is_fdown(self.left_key):
                self.previous()
            elif keyboard.is_fdown(self.right_key):
                self.next()
    
    def _create_buttons(self):
        self.button_left = Button(self.previous, self.left_text, NvVector2(self._get_arrow_width(), self._rsize.y).to_round(), self.style(borderwidth = 0, borderradius = self.style.borderradius - self._rsize_marg.x / 2), z = self.z + 1, inline = True, fancy_click_style = False, alt = self.alt)
        self.button_right = Button(self.next, self.right_text, NvVector2(self._get_arrow_width(), self._rsize.y).to_round(), self.style(borderwidth = 0), z = self.z + 1, inline = True, fancy_click_style = False, alt = self.alt)
        self._start_button(self.button_left)
        self._start_button(self.button_right)
        self._delayed_button_update = True
    
    def _start_button(self, button: Button):
        button.surface = self.surface
        button._init_start()
        button.booted = True
        button._boot_up()
        button._on_style_change_additional = self._mark_dirty
        button._on_style_change()
    
    def _style_update_buttons(self):
        self.button_left._on_style_change()
        self.button_right._on_style_change()
        
    def _position_buttons(self):
        self.button_left.coordinates = NvVector2(self._rsize_marg.x / 2, self._rsize_marg.y / 2)
        self.button_right.coordinates = NvVector2(self._rsize.x + self._rsize_marg.x / 2 - self.button_right._csize.x, self._rsize_marg.y / 2)
    
    def _get_arrow_width(self):
        return round(self.relx(self.size.x / 100 * self.arrow_width))
    
    def _resize_buttons(self):
        self.button_left.resize(self._resize_ratio)
        self.button_right.resize(self._resize_ratio)

    def resize(self, resize_ratio: NvVector2):
        super().resize(resize_ratio)
        self._position_buttons()
        self._resize_buttons()
        self._delayed_button_update = True
        
    @property
    def current_index(self):
        return self._current_index
    
    @current_index.setter
    def current_index(self, index: int):
        self._current_index = index
        self._changed = True
        self._delayed_button_update = True
        if self.on_change: 
            self.on_change(self.current_element_text)
        
    @property
    def current_element(self):
        return self.elements[self.current_index] if self.elements else None
    @property
    def current_element_text(self):
        return self.current_element.text if self.current_element else "Not selected"
    
    def step(self, step: int = 1):
        self.current_index = (self.current_index + step) % len(self.elements)
    
    def move_to(self, id: str):
        assert id, "id cannot be None"
        try:
            index = next(i for i, el in enumerate(self.elements) if el.id == id)
            self.current_index = index
        except StopIteration as e:
            raise ValueError(f"Element with id {id} not found") from e
    
    def find(self, id: str):
        assert id, "id cannot be None"
        return next((item for item in self.elements if item.id == id), None)
    
    def rfind(self, id: str):
        assert id, "id cannot be None"
        return next((item for item in reversed(self.elements) if item.id == id), None)
    
    def count(self):
        return len(self.elements)
    
    def remove(self, id: str):
        assert id, "id cannot be None"
        try:
            index = self.find(id)
            self.elements.remove(index)
        except ValueError as e:
            raise ValueError(f"Element with id {id} not found") from e
    
    def add_element(self, element: Element):
        self.elements.append(element)
        self._changed = True
    
    def next(self):
        self.step(1)
        
    def previous(self):
        self.step(-1)
        
    def secondary_update(self):
        super().secondary_update()
        if not self.active: return
        
        self._light_update_button(self.button_left)
        self._light_update_button(self.button_right)
        
        if self._delayed_button_update:
            self._position_buttons()
            self._style_update_buttons()
            self._delayed_button_update = False
    
    def _light_update_button(self, button: Button):
        button._master_z_handler = self._master_z_handler
        self._set_master_coordinates(button)
        button.update()
    
    def _set_master_coordinates(self, button: Button):
        button.master_coordinates = self.master_coordinates + button.coordinates
    
    def primary_draw(self):
        super().primary_draw()
        if self._changed:
            self.button_left.surface = self.surface
            self.button_right.surface = self.surface 
    
    def secondary_draw_content(self):
        super().secondary_draw_content()
        if not self.visible: return
        
        if self._changed:
            self.renderer.bake_text(self.current_element_text, size_x = self._csize.x - self.button_left._csize.x * 2)
            self._draw_buttons()
            assert self._text_surface is not None and self._text_rect is not None, "Text surface or rect is None"
            self.surface.blit(self._text_surface, self._text_rect)
            
    def _mark_dirty(self):
        self._changed = True
        self.button_left._changed = True
        self.button_right._changed = True
        self._delayed_button_update = True
        
    def _draw_buttons(self):
        self.button_left._master_mask = self.renderer._get_correct_mask()
        self.button_left.draw()
        
        self.button_right._master_mask = self.renderer._get_correct_mask()
        self.button_right.draw()

        if self.style.borderwidth > 0:
            if borders := self.cache.get_or_exec(CacheType.Borders, lambda: self.renderer._create_outlined_rect(self._csize, self.relm(self.style.borderradius),self.relm(self.style.borderwidth))):
                self.surface.blit(borders, (0, 0))

    def clone(self):
        return ElementSwitcher(self._lazy_kwargs['size'], copy.deepcopy(self._lazy_kwargs['elements']), copy.deepcopy(self.style), **self.constant_kwargs)