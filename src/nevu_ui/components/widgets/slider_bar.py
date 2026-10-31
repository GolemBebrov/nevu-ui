from typing import Any, Unpack, overload

import nevu_ui.core.modules as md
from nevu_ui.components._typehints import (
    _SliderKwargs,
    _SliderKwargsLongFull,
    _SliderKwargsShortFull,
)
from nevu_ui.components.widgets.progress_bar import ProgressBar
from nevu_ui.core import Annotations
from nevu_ui.core.enums import (
    Align,
    BindType,
    CacheType,
    CustomFunctions,
    RenderReturnType,
)
from nevu_ui.core.state import nevu_state
from nevu_ui.fast import NvRect, NvVector2
from nevu_ui.fast.raylib import begin_blend_mode, end_blend_mode
from nevu_ui.presentation.color import TupleColorRole
from nevu_ui.presentation.style import Style
from nevu_ui.rendering import DrawTextCall
from nevu_ui.utils import mouse


class Slider(ProgressBar):
    bar_style: Style | None
    padding_x: int
    padding_y: int
    step: int | float
    bar_font_role: TupleColorRole

    @overload
    def __init__(
        self,
        size: Annotations.nevuobj_size = None,
        style: Annotations.nevuobj_style = None,
        **params: Unpack[_SliderKwargsShortFull],
    ): ...

    @overload
    def __init__(
        self,
        size: Annotations.nevuobj_size = None,
        style: Annotations.nevuobj_style = None,
        **params: Unpack[_SliderKwargsLongFull],
    ): ...

    def __init__(
        self,
        size: Annotations.nevuobj_size = None,
        style: Annotations.nevuobj_style = None,
        **params: Unpack[_SliderKwargs] | Any,
    ):
        super().__init__(size, style, **params)

    def _init_booleans(self):
        super()._init_booleans()
        self.hoverable = True
        self._add_custom_flags(
            CustomFunctions.draw_main | CustomFunctions.update_main
        )

    def _init_flags(self):
        super()._init_flags()
        self.dragging = False

    def _init_objects(self):
        super()._init_objects()
        self._text_rect = None
        self._text_surface = None

    def _add_params(self):
        super()._add_params()
        self._add_param("step", int | float, 1)
        self._add_param("bar_style", Style | type(None), None)
        self._add_param("padding_x", int, 10)
        self._add_param_link("pad_x", "padding_x")
        self._add_param("padding_y", int, 10)
        self._add_param_link("pad_y", "padding_y")
        self._add_param("bar_font_role", TupleColorRole, TupleColorRole.INVERSE_PRIMARY)

    def _system_callback_binds(self):
        super()._system_callback_binds()
        self._system_callbacks.bind(BindType.Click, slider_on_click)
        self._system_callbacks.bind(BindType.KeyUp, slider_on_keyup)
        self._system_callbacks.bind(BindType.KeyUpAbandon, slider_on_keyup_abandon)
        self._system_callbacks.bind(BindType.AfterStateChange, _slider_after_state_change)
        self._system_callbacks.bind(BindType.StyleChange, _slider_on_style_change)

    def _current_value_setter(self, value):
        val = super()._current_value_setter(value)
        if hasattr(self, "cache"):
            self.cache.clear_selected(whitelist=[CacheType.TextArgs])
        return val

    def _update_main(self):
        super()._update_main()
        if self.dragging:
            self._on_drag()

    def _on_drag(self):
        relative_x = mouse.pos.x - self.absolute_coordinates.x

        slider_pos = max(
            self._borders_of_current_size.x,
            min(
                self._no_borders_current_size.x + self._borders_of_current_size.x,
                relative_x,
            ),
        )

        if self._no_borders_current_size.x == 0:
            slider_perc = 0.0
        else:
            slider_perc = (slider_pos - self._borders_of_current_size.x) / (
                self._no_borders_current_size.x
            )

        value = slider_perc * (self.end_value - self.start_value) + self.start_value
        if self.step != 0 and value % self.step != 0:
            value = round(value / self.step) * self.step
        value = max(self.start_value, min(self.end_value, value))

        if abs(value - self.current_value) > 1e-9:
            self.current_value = value

    def _create_text(self):
        result = self.renderer.run_text(
            DrawTextCall(
                size=self.current_size,
                text=str(round(self.current_value)),
                color=self.style.colortheme.get_tuple(self.bar_font_role),
                return_type=RenderReturnType.CreateNew,
            )
        )
        return result

    def adjust_text_rect(self, rect):
        result_rect = NvRect(rect)
        if self.style.align_x == Align.CENTER and self.style.align_y == Align.CENTER:
            return rect

        padx = 0
        pady = 0

        border_size = self._borders_of_current_size / 2

        match self.style.align_x:
            case Align.LEFT:
                padx = self.padding_x + border_size.x
            case Align.RIGHT:
                padx = -self.padding_x - border_size.x

        match self.style.align_y:
            case Align.TOP:
                pady = self.padding_y + border_size.y
            case Align.BOTTOM:
                pady = -self.padding_y - border_size.y

        if isinstance(result_rect, tuple):
            result_rect = NvRect(*result_rect)
        result_rect.move_ip(padx, pady)
        result_rect = result_rect.get_int_tuple()
        return result_rect

    def _draw_text(self):
        surface = self.surface
        text_rect, text_surface = self.cache.get_or_exec(CacheType.TextArgs, self._create_text)
        coords = (text_rect[0], text_rect[1])

        is_raylib = nevu_state.window.renderer_type.raylib
        with surface:
            if is_raylib:
                begin_blend_mode(md.rl.BlendMode.BLEND_ALPHA_PREMULTIPLY)
            surface.blit(text_surface, coords)
            if is_raylib:
                end_blend_mode()

    def _draw_main(self):
        super()._draw_main()
        if not self.surface:
            return
        text_rect, text_surface = self.cache.get_or_exec(CacheType.TextArgs, self._create_text)
        self.cache.set(CacheType.TextArgs, (self.adjust_text_rect(text_rect), text_surface))
        self._draw_text()

    def _resize_content(self, resize_ratio: NvVector2):
        super()._resize_content(resize_ratio)
        self.cache.clear_selected(whitelist=[CacheType.TextArgs])


def slider_on_click(self, *args, **kwargs):
    self.dragging = True
    self._on_drag()


def slider_on_keyup(self, *args, **kwargs):
    self.dragging = False


def slider_on_keyup_abandon(self, *args, **kwargs):
    self.dragging = False


def _slider_after_state_change(self, *args, **kwargs):
    self.cache.clear_selected(whitelist=[CacheType.TextArgs])
    self._changed = True


def _slider_on_style_change(self, *args, **kwargs):
    self.cache.clear_selected(whitelist=[CacheType.TextArgs])
    self._changed = True
