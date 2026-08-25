import copy
from collections.abc import Callable
from typing import Any, Unpack

import nevu_ui.core.modules as md
from nevu_ui.components.widgets.button import Button
from nevu_ui.components.widgets.typehints import (
    ElementSwitcherKwargs,
    ElementSwitcherTemplate,
)
from nevu_ui.components.widgets.widget import Widget
from nevu_ui.core import Annotations
from nevu_ui.core.enums import (
    BindType,
    CacheType,
    CustomFunctions,
    HoverState,
    RenderReturnType,
)
from nevu_ui.core.state import nevu_state
from nevu_ui.fast.nvrendertex import NvRenderTexture
from nevu_ui.fast.nvvector2 import NvVector2
from nevu_ui.presentation.style import Style
from nevu_ui.rendering import DrawTextCall
from nevu_ui.utils import keyboard


class Element:
    __slots__ = ["id", "text"]

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
                        element_pair = [str(item[0]), item[1] if item[1] else None]
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
    # === Params ===
    on_content_change: Callable | None
    _сurrent_index: int
    button_padding: int
    arrow_width: int
    left_text: str
    right_text: str
    left_key: Any
    right_key: Any
    offset_perc: NvVector2
    words_indent: bool

    # ==============
    def __init__(
        self,
        size: Annotations.nevuobj_size = None,
        elements: list[Element | Any | list] | None = None,
        style: Annotations.nevuobj_style = None,
        **constant_kwargs: Unpack[ElementSwitcherKwargs],
    ):
        super().__init__(size, style, **constant_kwargs)
        self._template = ElementSwitcherTemplate(self._template.size, elements)

    def _add_params(self):
        super()._add_params()
        self._add_param("on_content_change", (type(None), Callable), None)
        self._add_param("current_index", int, 0)
        self._add_param("button_padding", int, 2)
        self._add_param("arrow_width", int, 30)
        self._add_param("left_text", (str), "<")
        self._add_param("words_indent", bool, False)
        self._add_param("left_key", Any, None)
        self._add_param("right_text", (str), ">")
        self._add_param("right_key", Any, None)

    def _system_callback_binds(self):
        super()._system_callback_binds()
        self._system_callbacks.bind(
            BindType.StyleChange, _element_switcher_on_style_change, add_to_end=False
        )

    def _init_booleans(self):
        super()._init_booleans()
        self._delayed_button_update = False
        self.hoverable = False
        self._add_custom_flags(
            CustomFunctions.secondary_update
        )

    def _lazy_init(self, size: NvVector2 | list, elements: list[Element] | None = None):  # type: ignore
        super()._lazy_init(size)
        elements: list[Element] = elements or []
        self.elements = Elements.create(*elements)
        cached_args = self.cache.get_or_exec(
            CacheType.TextArgs,
            lambda: self.renderer.run_text(
                DrawTextCall(
                    continuous=False,
                    text=self.current_element_text,
                    words_indent=self.words_indent,
                    return_type=RenderReturnType.CreateNew,
                ),
            ),
        )
        self._text_rect, self._text_surface = cached_args
        self._create_buttons()

    def _init_numerical(self):
        super()._init_numerical()
        self._additional_y_marg = 1

    @property
    def _global_hovered(self):
        return (
            self.hover_state in [HoverState.Hovered, HoverState.Clicked]
            or self._button_hovered
        )

    @property
    def _button_hovered(self):
        assert self.button_left and self.button_right, "Buttons not initialized"
        return self.button_left.hover_state in [
            HoverState.Hovered,
            HoverState.Clicked,
        ] or self.button_right.hover_state in [HoverState.Hovered, HoverState.Clicked]

    def _logic_update(self):
        super()._logic_update()
        if self._dead:
            return
        if not self._global_hovered:
            return
        lkey = self.left_key
        rkey = self.right_key
        fdown = keyboard.is_fdown
        if lkey and fdown(lkey):
            self.previous()
        elif rkey and fdown(rkey):
            self.next()

    def _change_style_rad(
        self,
        style: Style,
        norad_idxs: tuple[int, int],
        rad_idxs: tuple[int, int],
        offset: float,
    ):
        changed_br: list[float]

        r1, r2 = rad_idxs

        if isinstance(style.border_radius, tuple | list):
            nr1, nr2 = norad_idxs
            changed_br = list(style.border_radius)
            changed_br[nr1], changed_br[nr2] = 0, 0
            changed_br[r1], changed_br[r2] = (
                changed_br[r1] - offset,
                changed_br[r2] - offset,
            )
        else:
            changed_br = [0] * 4
            changed_br[r1], changed_br[r2] = (
                style.border_radius - offset,
                style.border_radius - offset,
            )

        style.border_radius = tuple(changed_br)

    def _correct_style_rad(
        self,
        style: Style,
        size: NvVector2,
        rad_idxs: tuple[int, int],
        norad_idxs: tuple[int, int],
    ):
        assert isinstance(style.border_radius, tuple | list), "Style must have tuple or list border radius"
        norad = list(norad_idxs)
        correct_br: list[float] = list(style.border_radius)
        hsize_x = size.x / 2
        hsize_y = size.y / 2

        for i in range(2):
            curr_radius = correct_br[rad_idxs[i]]
            if curr_radius > hsize_x or curr_radius > hsize_y:
                correct_br[norad[i]] = curr_radius
        style.border_radius = tuple(correct_br)

    def _shape_buttons_radius(self, offset: float):
        assert self.button_left and self.button_right, "Buttons not initialized"
        button_style = self.style(border_width = 0)
        button_style_left = button_style()
        button_style_right = button_style()
        idx_left = (0, 3)
        idx_right = (1, 2)

        button_size = self.button_left.size

        self._change_style_rad(button_style_left, idx_right, idx_left, offset)
        self._correct_style_rad(button_style_left, button_size, idx_left, idx_right)
        self._change_style_rad(button_style_right, idx_left, idx_right, offset)
        self._correct_style_rad(button_style_right, button_size, idx_right, idx_left)

        self.button_left.style = button_style_left
        self.button_right.style = button_style_right

    def _create_buttons(self):
        bw = self.relm(self.style.border_width)

        button_width = self._get_arrow_width()
        button_height = self.current_size.y - (bw * 2) - self.button_padding * 2
        button_size = NvVector2(button_width, button_height)

        subtheme_role = self.get_param_strict("subtheme_role").value
        self.button_left = Button(
            self.previous,
            self.left_text,
            button_size,
            self.style,
            z=self.z + 1,
            inline=True,
            throw_errors=True,
            invert_on_click=False,
            inverted=self.inverted,
            subtheme_role=subtheme_role,
        )
        self.button_right = Button(
            self.next,
            self.right_text,
            button_size,
            self.style,
            z=self.z + 1,
            inline=True,
            invert_on_click=False,
            inverted=self.inverted,
            subtheme_role=subtheme_role,
        )

        self._start_button(self.button_left)
        self._start_button(self.button_right)

        self._shape_buttons_radius(self.button_padding + self.style.border_width)
        self._delayed_button_update = True

    def _start_button(self, button: Button):
        button.surface = self.surface
        button._init_start()
        button.booted = True
        button._boot_up()
        button._system_callbacks.bind(BindType.StyleChange, self._mark_dirty, weak=True)
        button._run_callbacks(BindType.StyleChange)

    def _style_update_buttons(self):
        assert self.button_left is not None
        assert self.button_right is not None
        self.button_left._run_callbacks(BindType.StyleChange)
        self.button_right._run_callbacks(BindType.StyleChange)

    def _position_buttons(self):
        assert self.button_left and self.button_right, "Buttons not initialized"
        edge_offset = self.relm(self.style.border_width) + self.button_padding
        b_right = self.button_right
        b_left = self.button_left
        current_size = self.current_size
        y_pos = (current_size.y - b_left.current_size.y) / 2
        b_left.coordinates = NvVector2.from_xy(edge_offset, y_pos)
        right_x = current_size.x - b_right.current_size.x - edge_offset
        b_right.coordinates = NvVector2.from_xy(right_x, y_pos)

    def _get_arrow_width(self):
        return round(
            self.relx(
                (self.size.x - self.style.border_width * 2) / 100 * self.arrow_width
            )
        )

    def _resize_buttons(self):
        assert self.button_left and self.button_right, "Buttons not initialized"
        self._shape_buttons_radius(self.button_padding + self.style.border_width)
        self.button_left._resize(self._resize_ratio)
        self.button_right._resize(self._resize_ratio)

    def _resize_content(self, resize_ratio: NvVector2):
        super()._resize_content(resize_ratio)
        self._position_buttons()
        self._resize_buttons()
        self._delayed_button_update = True

    @property
    def current_index(self):
        return self.get_param_strict("current_index").value

    @current_index.setter
    def current_index(self, index: int):
        self.set_param_value("current_index", index)
        self._changed = True
        self._delayed_button_update = True
        self.cache.clear_selected(whitelist=[CacheType.TextArgs])
        if self.on_content_change:
            self.on_content_change(self.current_element_text, self.current_element.id)  # type: ignore

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

        update_button = self._update_button

        assert self.button_left and self.button_right, "Buttons not initialized"

        update_button(self.button_left)
        update_button(self.button_right)

        if not self._delayed_button_update:
            return

        self._position_buttons()
        self._style_update_buttons()
        self._delayed_button_update = False

    def _update_button(self, button: Button):
        button.absolute_coordinates.sadd(self.absolute_coordinates, button.coordinates)
        button.update()

    def _primary_draw(self):
        assert self.button_left and self.button_right, "Buttons not initialized"
        super()._primary_draw()
        if self._changed:
            self.button_left.surface = self.surface
            self.button_right.surface = self.surface

    def secondary_draw_content(self):
        assert self.button_left and self.button_right, "Buttons not initialized"
        super().secondary_draw_content()
        if not self._changed:
            return
        assert self.surface

        button_left = self.button_left
        button_right = self.button_right

        button_left._changed = True
        button_right._changed = True

        cropped_size = self.current_size.xy
        text_area_offset = button_left.coordinates.x + button_left.current_size.x
        cropped_size.x -= text_area_offset * 2
        cached_args = self.cache.get_or_exec(
            CacheType.TextArgs,
            lambda: self.renderer.run_text(
                DrawTextCall(
                    text=self.current_element_text,
                    words_indent=self.words_indent,
                    max_size=cropped_size,
                    return_type=RenderReturnType.CreateNew,
                )
            ),
        )
        self._text_rect, self._text_surface = cached_args
        text_rect = self._text_rect
        text_surface = self._text_surface

        coordinates = tuple(text_rect)
        self._draw_buttons()

        assert text_surface is not None, "Text surface or rect is None"

        dtype = nevu_state.window.renderer_type
        surface = self.surface

        if dtype.raylib:
            assert isinstance(surface, NvRenderTexture)
            rl = md.rl
            texture = text_surface.texture
            rl.set_texture_filter(
                texture, rl.TextureFilter.TEXTURE_FILTER_ANISOTROPIC_16X
            )
            rl.set_texture_wrap(texture, rl.TextureWrap.TEXTURE_WRAP_CLAMP)
            surface.blit(text_surface, coordinates, blend_mode=self._correct_blend)

        elif dtype.pygame_like:
            assert isinstance(surface, md.pygame.Surface)
            surface.blit(text_surface, coordinates)

    def _mark_dirty(self, *args):
        assert self.button_left and self.button_right, "Buttons not initialized"
        self._changed = True
        self.button_left._changed = True
        self.button_right._changed = True
        self._delayed_button_update = True
        self.clear_texture()

    def _draw_buttons(self):
        assert self.button_left and self.button_right, "Buttons not initialized"
        self.button_left.draw()
        self.button_right.draw()

    def _create_clone(self):
        return self.__class__(
            self._template["size"],
            copy.deepcopy(self._template["elements"]),
            copy.deepcopy(self.style),
            **self.constant_kwargs,
        )

    def _kill_base(self):
        assert self.button_left and self.button_right, "Buttons not initialized"
        super()._kill_base()
        if hasattr(self, "button_left"):
            self.button_left.kill()
        if hasattr(self, "button_right"):
            self.button_right.kill()
        self.button_left = None
        self.button_right = None
        self._delayed_button_update = False


# === NOT CLASS FUNCTIONS ===


def _element_switcher_on_style_change(self):
    if not self.booted:
        return
    self._shape_buttons_radius(self.button_padding + self.style.border_width)
