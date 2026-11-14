from collections.abc import Callable
from typing import Any, Unpack

import nevu_ui.core.modules as md
from nevu_ui.components._typehints import _RectCheckBoxKwargs, nevu_object_defaults
from nevu_ui.components.widgets.widget import Widget
from nevu_ui.core import Annotations
from nevu_ui.core.enums import BindType, RenderReturnType
from nevu_ui.core.size import _SizeRule
from nevu_ui.core.state import nevu_state
from nevu_ui.cython.vector2 import Vector2
from nevu_ui.rendering import DrawBaseCall

class CheckBox(Widget):
    # === Params ===
    on_toggle_function: Callable | None
    toggled: bool
    toggled_rect_scale: int | float
    checkbox_group: Any
    toggled_rect_opacity: int
    # ==============

    def __init__(
        self,
        size: Annotations.nevuobj_size | Annotations.size_item = None,
        style: Annotations.nevuobj_style = None,
        **params: Unpack[_RectCheckBoxKwargs],
    ):
        if size is None:
            size = nevu_object_defaults.library.get("size")
        if isinstance(size, int | float):
            size = Vector2.from_xy(size, size)
        elif isinstance(size, _SizeRule):
            size = (size, size)

        super().__init__(size, style, **params)

    def _system_callback_binds(self):
        super()._system_callback_binds()
        self._system_callbacks.bind(BindType.Click, _checkbox_click, weak=True, add_to_end=False)

    def _lazy_init(self, size: Vector2 | list):
        super()._lazy_init(size)
        if val := self.checkbox_group:
            val.add_checkbox(self)

    def _add_params(self):
        from nevu_ui.components.checkbox_group import CheckBoxGroup
        super()._add_params()
        self._add_param("on_toggle_function", type(None) | Callable, None)
        self._add_param_link("on_toggle", "on_toggle_function")
        self._add_param("toggled", bool, False, setter=self._toggled_setter)
        self._add_param(
            "toggled_rect_scale",
            int | float,
            0.8,
            setter=self._toggled_rect_fill_setter,
        )
        self._add_param_link("toggled_scale", "toggled_rect_scale")
        self._add_param("checkbox_group", type(None) | CheckBoxGroup, None)
        self._add_param_link("group", "checkbox_group")
        self._add_param("toggled_rect_opacity", int, 255)
        self._change_param_default("hoverable", True)

    def _toggled_rect_fill_setter(self, value: float):
        self._changed = True
        return value

    def _toggled_setter(self, value: bool):
        old_value = self.toggled
        if old_value == value:
            return value
        self.get_param_strict("toggled").value = value
        self._changed = True
        self.clear_surfaces()
        if self.on_toggle_function:
            self.on_toggle_function(value)
        return value

    def _draw_main(self):
        if not self.toggled:
            return

        margin = self.current_size * ((1 - self.toggled_rect_scale) / 2)
        margin.round()

        active_size = self.current_size - (margin * 2)

        active_size.x = max(1, int(active_size.x))
        active_size.y = max(1, int(active_size.y))

        inner_radius = self._borders_of_current_size.x * 2
        inner_radius = [inner_radius] * 4

        radius = self.style.border_radius

        for i in range(len(inner_radius)):
            inner_radius[i] += radius[i]
            inner_radius[i] = max(0, int(inner_radius[i]))

        color = self.subtheme_border
        dot_surface = self.renderer.run_base(
            DrawBaseCall(
                style=self.style,
                cache=self.cache,
                color=(color[0], color[1], color[2], self.toggled_rect_opacity),
                size=active_size,
                gradient_support=False,
                return_type=RenderReturnType.CreateNew,
                glassy = self.glassy
            )
        )
        assert dot_surface
        self.surface.blit(dot_surface, margin.get_int_tuple())
        if nevu_state.window.renderer_type.raylib:
            md.rl.set_texture_filter(
                dot_surface.native.texture, md.rl.TextureFilter.TEXTURE_FILTER_BILINEAR
            )

def _checkbox_click(self: CheckBox):
    self.toggled = not self.toggled
