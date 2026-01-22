import copy
import contextlib

from nevu_ui.fast.nvvector2 import NvVector2
from nevu_ui.utils import keyboard
from nevu_ui.style import Style, default_style
from nevu_ui.core.enums import CacheType, HoverState

from nevu_ui.widgets import (
    Widget, Button, WidgetKwargs
)
from typing import (
    Callable, Any, NotRequired, Unpack
)

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
            raise ValueError("Some objects cannot be converted into str", e) from e
        
        element_list.extend(Element(pair[0], pair[1]) for pair in final_list)
        return element_list

class ElementSwitcher(Widget):
    on_content_change: Callable | None
    _сurrent_index: int
    button_padding: int
    arrow_width: int
    left_text: str
    right_text: str
    left_key: Any
    right_key: Any
    offset_perc: NvVector2
    def __init__(self, size: NvVector2 | list, elements: list[Element | Any | list] | None = None, style: Style = default_style, **constant_kwargs: Unpack[ElementSwitcherKwargs]):
        super().__init__(size, style, **constant_kwargs)
        self._lazy_kwargs = {'size': size, 'elements': elements}

    def _add_constants(self):
        super()._add_constants()
        self._add_constant("on_content_change", (type(None), Callable), None)
        self._add_constant("current_index", int, 0)
        self._add_constant("button_padding", int, 10)
        self._add_constant("arrow_width", int, 30)
        self._add_constant("left_text", (str), "<")
        self._add_constant("left_key", Any, None)
        self._add_constant("right_text", (str), ">")
        self._add_constant("right_key", Any, None)
        self._add_constant("offset_perc", NvVector2, NvVector2(2,2))

    def _init_booleans(self):
        super()._init_booleans()
        self._delayed_button_update = False
        self.hoverable = False
        self._easy_mode = False
        
    def _lazy_init(self, size: NvVector2 | list, elements: list[Element] | None = None):
        super()._lazy_init(size)
        elements = elements or []
        self.elements = Elements.create(*elements)
        self.renderer.bake_text(self.current_element_text)
        self._create_buttons()
    
    def _init_numerical(self):
        super()._init_numerical()
        self._additional_y_marg = 1
    
    @property
    def _global_hovered(self): return self.hover_state in [HoverState.HOVERED, HoverState.CLICKED] or self._button_hovered
    @property
    def _button_hovered(self): return self.button_left.hover_state in [HoverState.HOVERED, HoverState.CLICKED] or self.button_right.hover_state in [HoverState.HOVERED, HoverState.CLICKED]
    
    def logic_update(self):
        super().logic_update()
        with contextlib.suppress(Exception):
            if not self._global_hovered: return
            if keyboard.is_fdown(self.left_key):
                self.previous()
            elif keyboard.is_fdown(self.right_key):
                self.next()
    
    def _change_style_rad(self, style: Style, norad_idx: tuple[int, int], rad_idx: tuple[int, int], offset: int):
        if isinstance(style.borderradius, tuple):
            br = list(style.borderradius)
            br[norad_idx[0]], br[norad_idx[1]] = 0, 0
            br[rad_idx[0]], br[rad_idx[1]] = br[rad_idx[0]] - offset, br[rad_idx[1]] - offset
        else:
            br = [0]*4
            br[rad_idx[0]], br[rad_idx[1]] = style.borderradius - offset, style.borderradius - offset
        style.borderradius = tuple(br) # type: ignore
    
    def _shape_buttons_radius(self, offset: int | float):
        button_style = self.style(borderwidth=0)
        button_style_left = button_style()
        button_style_right = button_style()
        border_offset = self.relm(self.style.borderwidth) 
        idx1, idx2 = (2, 1), (0, 3)
        self._change_style_rad(button_style_left, idx1, idx2, -offset + border_offset) # type: ignore
        self._change_style_rad(button_style_right, idx2, idx1, -offset + border_offset) # type: ignore
        self.button_left.style = button_style_left
        self.button_right.style = button_style_right
    
    def _create_buttons(self):
        button_size = (NvVector2(self._get_arrow_width(), self._rsize.y) / 100 * (NvVector2(100,100) - self.offset_perc)).to_round()
        self.button_offset = NvVector2(self._get_arrow_width(), self._rsize.y) - button_size
        self.button_left = Button(self.previous, self.left_text, button_size, self.style, z = self.z + 1, inline = True, fancy_click_style = False, alt = self.alt) #type: ignore
        self.button_right = Button(self.next, self.right_text, button_size, self.style, z = self.z + 1, inline = True, fancy_click_style = False, alt = self.alt)
        self._shape_buttons_radius(self.relm(0.5))
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
        self._check_mode()
        offset = self._rsize_marg / 2 + self.rel(self.button_offset) / 2 
        self.button_left.coordinates = offset
        right_offset_x = self._rsize.x + self._rsize_marg.x / 2 - self.relx(self.button_offset.x) / 2 - self.button_right._csize.x
        self.button_right.coordinates = NvVector2(right_offset_x, offset.y)
    
    def _get_arrow_width(self):
        return round(self.relx((self.size.x - self.style.borderwidth*2) / 100 * self.arrow_width))
    
    def _resize_buttons(self):
        self._shape_buttons_radius(self.rely(0.5))
        self.button_left.resize(self._resize_ratio)
        self.button_right.resize(self._resize_ratio)

    def resize(self, resize_ratio: NvVector2):
        super().resize(resize_ratio)
        self._position_buttons()
        self._resize_buttons()
        self._delayed_button_update = True
        
    @property
    def current_index(self): return self._current_index
    @current_index.setter
    def current_index(self, index: int):
        self._current_index = index
        self._changed = True
        self._delayed_button_update = True
        if self.on_content_change: 
            self.on_content_change(self.current_element_text)
        
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
    
    def count(self): return len(self.elements)
    
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
    
    def next(self): self.step(1)
    def previous(self): self.step(-1)
        
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
        self._set_master_coordinates(button)
        button.update()
    
    def _set_master_coordinates(self, button: Button):
        button.absolute_coordinates = self.absolute_coordinates + button.coordinates
    
    def primary_draw(self):
        super().primary_draw()
        if self._changed:
            self.button_left.surface = self.surface
            self.button_right.surface = self.surface 
    
    def secondary_draw_content(self):
        super().secondary_draw_content()
        if not self.visible: return
        
        if self._changed:
            assert self.surface
            self.bake_text(self.current_element_text, size_x = self._csize.x - self.button_left._csize.x * 2)
            self._draw_buttons()
            assert self._text_surface is not None and self._text_rect is not None, "Text surface or rect is None"
            self.surface.blit(self._text_surface, self._text_rect)
            
    def _mark_dirty(self):
        self._changed = True
        self.button_left._changed = True
        self.button_right._changed = True
        self._delayed_button_update = True
        self.clear_texture()
    
    def _check_mode(self):
        self._easy_mode = self._csize.y <= 250
    
    def _draw_buttons(self):
        self._check_mode()
        self.button_left.draw()
        self.button_right.draw()

    def clone(self): return ElementSwitcher(self._lazy_kwargs['size'], copy.deepcopy(self._lazy_kwargs['elements']), copy.deepcopy(self.style), **self.constant_kwargs)