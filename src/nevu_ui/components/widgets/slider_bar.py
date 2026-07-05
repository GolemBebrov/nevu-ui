from typing import Unpack, overload

import nevu_ui.core.modules as md
from nevu_ui.components.widgets import Widget
from nevu_ui.components.widgets.progress_bar import ProgressBar
from nevu_ui.components.widgets.typehints import (
    SliderKwargs,
    SliderKwargsLong,
    SliderKwargsShort,
)
from nevu_ui.core import Annotations
from nevu_ui.core.enums import (
    Align,
    CacheType,
    ParamLayer,
    RenderConfig,
    RenderReturnType,
)
from nevu_ui.core.state import nevu_state
from nevu_ui.fast import NvRect, NvRenderTexture, NvVector2
from nevu_ui.fast.raylib import begin_blend_mode, end_blend_mode
from nevu_ui.presentation.color import Color, PairColorRole, TupleColorRole
from nevu_ui.presentation.style import Style
from nevu_ui.rendering import DrawTextCall
from nevu_ui.utils import mouse


class Slider(Widget):
    # === Params ===
    bar_style: Style
    padding_x: int
    padding_y: int
    filled_rect_role: PairColorRole
    start_value: int | float
    end_value: int | float
    step: int | float
    bar_font_role: TupleColorRole
    current_value: int | float

    # ==============
    @overload
    def __init__(
        self,
        size: Annotations.nevuobj_size = None,
        style: Annotations.nevuobj_style = None,
        **constant_kwargs: Unpack[SliderKwargsShort],
    ): ...
    @overload
    def __init__(
        self,
        size: Annotations.nevuobj_size = None,
        style: Annotations.nevuobj_style = None,
        **constant_kwargs: Unpack[SliderKwargsLong],
    ): ...
    def __init__(
        self,
        size: Annotations.nevuobj_size = None,
        style: Annotations.nevuobj_style = None,
        **constant_kwargs: Unpack[SliderKwargs],
    ):
        self.booted = False
        self._constant_current_val = None
        super().__init__(size, style, **constant_kwargs)

    def _init_booleans(self):
        self._custom_secondary_draw_content = True
        self._custom_secondary_update = True

    def _lazy_init(self, size: NvVector2 | list):
        super()._lazy_init(size)
        self.create_progress_bar()
        self.add_first_update_action(self._first_progressbar_update)

    def _first_progressbar_update(self):
        self._on_progress_bar_change()
        self._create_font()

    def _on_progress_bar_change(self, *args, **kwargs):
        rtype = nevu_state.window.renderer_type
        progress_bar_surf = self.progress_bar.surface
        if rtype.raylib:
            assert isinstance(progress_bar_surf, NvRenderTexture)
            with progress_bar_surf:
                progress_bar_surf.clear(Color.Blank)
        elif rtype.pygame_like:
            progress_bar_surf.fill(Color.Blank)
            self._create_surf()

    def create_progress_bar(self):
        assert self.surface

        progress_style = self.bar_style or self.style
        self.progress_bar = ProgressBar(
            self.size,
            progress_style,
            on_value_change=self._on_progress_bar_change,
            start=self.start_value,
            end=self.end_value,
            current=self.current_value,
            alt=self.inverted,
            role=self.filled_rect_role,
            z=-999,
        )

        self.progress_bar._on_change_system = self._on_progress_bar_change
        self.progress_bar._init_start()
        self.progress_bar.booted = True
        self.progress_bar._boot_up()

    def _init_flags(self):
        super()._init_flags()
        self.dragging = False
        self._font_changed = False

    def _init_objects(self):
        super()._init_objects()
        self.progress_bar_surf = None

    def _on_hover_system(self):
        super()._on_hover_system()
        self.progress_bar._hover()
        self.add_next_frame_action(self._create_surf)

    def _on_unhover_system(self):
        super()._on_unhover_system()
        self.progress_bar._unhover()
        self.add_next_frame_action(self._create_surf)

    def _on_click_system(self):
        super()._on_click_system()
        self.dragging = True
        self.progress_bar._click()
        self.add_next_frame_action(self._create_surf)

    def _on_keyup_system(self):
        super()._on_keyup_system()
        self.dragging = False
        self.progress_bar._kup()
        self.add_next_frame_action(self._create_surf)

    def _on_keyup_abandon_system(self):
        super()._on_keyup_abandon_system()
        self.dragging = False
        self.progress_bar._kup_abandon()

    def _add_params(self):
        super()._add_params()
        self._add_param("start_value", int | float, 0)
        self._add_param_link("start", "start_value")
        self._add_param("end_value", int | float, 100)
        self._add_param_link("end", "end_value")
        self._add_param(
            "current_value",
            int | float,
            0,
            layer=ParamLayer.Complicated,
            getter=self._current_value_getter,
            setter=self._current_value_setter,
        )
        self._add_param_link("current", "current_value")

        self._add_param("step", int | float, 1)
        self._add_param("bar_style", Style | type(None), None)

        self._add_param("padding_x", int, 10)
        self._add_param_link("pad_x", "padding_x")
        self._add_param("padding_y", int, 10)
        self._add_param_link("pad_y", "padding_y")
        self._add_param("bar_font_role", TupleColorRole, TupleColorRole.INVERSE_PRIMARY)

        self._add_param("filled_rect_role", PairColorRole, PairColorRole.BACKGROUND)
        self._add_param_link("role", "filled_rect_role")

    def _on_style_change_additional(self):
        super()._on_style_change_additional()
        if hasattr(self, "progress_bar") and self.progress_bar:
            self.progress_bar._changed = True

    def _current_value_getter(self, value):
        return (
            self.progress_bar.current_value
            if hasattr(self, "progress_bar") and self.progress_bar
            else 0
        )

    def _current_value_setter(self, new_value: float | int):
        if hasattr(self, "progress_bar") and self.progress_bar:
            self.progress_bar.set_progress_by_value(new_value)
            self._changed = True
        else:
            self._constant_current_val = new_value
        return new_value

    def _logic_update(self):
        super()._logic_update()
        if self._constant_current_val and hasattr(self, "progress_bar"):
            self.current_value = self._constant_current_val
            self.cache.clear_selected(whitelist=[CacheType.TextArgs])
            self.clear_texture()
            self._create_font()
            self._changed = True
            self._constant_current_val = None

    def secondary_update(self):
        super().secondary_update()
        self.progress_bar.update()
        if self.dragging:
            self._on_drag()

    def _on_drag(self):
        relative_x = mouse.pos.x - self.absolute_coordinates.x

        slider_pos = max(
            self._borders_marg_size.x / 2, min(self._no_borders_size.x, relative_x)
        )
        slider_perc = (slider_pos - self._borders_marg_size.x / 2) / (
            self._no_borders_size.x - self._borders_marg_size.x / 2
        )

        value = slider_perc * (self.end_value - self.start_value) + self.start_value
        if value % self.step != 0:
            value = round(value / self.step) * self.step
        value = max(self.start_value, min(self.end_value, value))

        if abs(value - self.current_value) > 1e-9:
            self.current_value = value
            self.cache.clear_selected(whitelist=[CacheType.TextArgs])
            self._create_font()

    def _primary_draw(self):
        pass

    def _create_surf(self):
        assert self.surface and self.progress_bar.surface
        self.clear_texture()
        self._create_font()
        self.adjust_text_rect()

        rtype = nevu_state.window.renderer_type
        surf = self.surface
        progressbar_surf = self.progress_bar.surface
        text_surf = self._text_surface

        if rtype.raylib:
            assert isinstance(surf, NvRenderTexture)
            assert isinstance(progressbar_surf, NvRenderTexture)
            assert isinstance(text_surf, NvRenderTexture)
            with surf:
                surf.fast_clear(Color.Blank)
                fast_blit = surf.fast_blit
                begin_blend_mode(md.rl.BlendMode.BLEND_ALPHA_PREMULTIPLY)
                fast_blit(progressbar_surf, (0, 0))
                fast_blit(text_surf, self._text_rect)  # type: ignore
                end_blend_mode()

        elif rtype.pygame_like:
            assert isinstance(surf, md.pygame.Surface)
            assert isinstance(progressbar_surf, md.pygame.Surface)
            if not text_surf:
                return
            surf_blit = surf.blit
            surf.fill(Color.Blank)
            surf_blit(progressbar_surf, (0, 0))
            if self._text_surface:
                surf_blit(text_surf, self._text_rect)  # type: ignore

    def _create_font(self):
        result = self.cache.get_or_exec(
            CacheType.TextArgs,
            lambda: self.renderer.run_text(
                DrawTextCall(
                    text=str(round(self.current_value)),
                    color=self.style.colortheme.get_tuple(self.bar_font_role),
                    return_type=RenderReturnType.CreateNew,
                )
            ),
        )
        assert result
        self._text_rect, self._text_surface = result

    def _after_state_change_system(self):
        super()._after_state_change_system()
        self.cache.clear_selected(whitelist=[CacheType.TextArgs])
        self._create_font()
        self.adjust_text_rect()
        self._create_surf()

    def secondary_draw_content(self):
        super().secondary_draw_content()
        self.progress_bar.coordinates = NvVector2()
        self.progress_bar.draw()
        assert self.surface
        self._create_font()
        self.adjust_text_rect()
        self._create_surf()

    def adjust_text_rect(self, rect=None):
        result_rect = rect or self._text_rect
        result_rect = NvRect(result_rect or NvRect(0, 0, 0, 0))
        if self.style.align_x == Align.CENTER and self.style.align_y == Align.CENTER:
            return rect

        padx = 0
        pady = 0

        border_size = self._borders_marg_size / 2

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
        if rect is None:
            self._text_rect = result_rect
        else:
            return result_rect

    def _resize_content(self, resize_ratio: NvVector2):
        super()._resize_content(resize_ratio)
        assert self.surface
        self._create_font()
        self.progress_bar._resize(resize_ratio)
