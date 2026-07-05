import copy
from collections.abc import Callable
from typing import Any, Unpack

import nevu_ui.core.modules as md
from nevu_ui.components.nevuobj.nevuobj import NevuObject
from nevu_ui.components.nevuobj.typehints import nevu_object_globals
from nevu_ui.components.widgets import RectCheckBoxKwargs, Widget
from nevu_ui.core import Annotations
from nevu_ui.core.enums import EventType, RenderConfig, RenderReturnType
from nevu_ui.core.size.units import SizeRule
from nevu_ui.core.state import nevu_state
from nevu_ui.fast.nvvector2 import NvVector2
from nevu_ui.rendering import DrawBaseCall


class RectCheckBox(Widget):
    # === Params ===
    on_toggle_function: Callable | None
    toggled: bool
    toggled_rect_scale: int | float
    checkbox_group: Any

    # ==============
    def __init__(
        self,
        size: Annotations.nevuobj_size | Annotations.size_item = None,
        style: Annotations.nevuobj_style = None,
        **constant_kwargs: Unpack[RectCheckBoxKwargs],
    ):
        if size is None:
            size = nevu_object_globals.library.get("size")
        if isinstance(size, int | float):
            size = NvVector2([size, size])
        elif isinstance(size, SizeRule):
            size = (size, size)
        elif isinstance(size, list | tuple):
            size = size
        super().__init__(size, style, **constant_kwargs)

    def _init_booleans(self):
        super()._init_booleans()
        self._supports_tuple_borderradius = False

    def _lazy_init(self, size: NvVector2 | list):
        super()._lazy_init(size)
        if val := self.get_param_value("checkbox_group"):
            val.add_checkbox(self)  # type: ignore

    def _add_params(self):
        from nevu_ui.components.layouts.misc.checkbox_group import CheckBoxGroup

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
        self._change_param_default("hoverable", True)

    def _toggled_rect_fill_setter(self, value: int | float):
        self._changed = True
        return value

    def _toggled_setter(self, value: bool):
        old_value = self.toggled
        if old_value == value:
            return value
        self._changed = True
        self.clear_surfaces()
        if self.on_toggle_function:
            self.on_toggle_function(value)
        if hasattr(self, "cache"):
            self.clear_texture()
        return value

    def secondary_draw_content(self):
        if not (self._changed and self.toggled):
            return

        margin = self._csize * (1 - self.toggled_rect_scale)
        margin.to_round()

        self.clear_texture()
        active_size = self._csize - (margin * 2)

        active_size.x = max(1, int(active_size.x))
        active_size.y = max(1, int(active_size.y))

        inner_radius = self._borders_marg_size.x * 2
        inner_radius = [inner_radius] * 4

        br = self.style.border_radius

        if isinstance(br, int | float):
            br = [br] * 4

        for i in range(len(inner_radius)):
            inner_radius[i] += br[i]
            inner_radius[i] = max(0, int(inner_radius[i]))

        inner_surf = self.renderer.core.create_clear(active_size)
        color = self.subtheme_border
        self.renderer.run_base(
            DrawBaseCall(
                radius=inner_radius,
                color=color,
                size=active_size,
                modify_object=inner_surf,
                standstill=True,
                gradient_support=False,
                return_type=RenderReturnType.Modify,
            )
        )
        self.surface.blit(inner_surf, margin.get_int_tuple())
        if nevu_state.window.renderer_type.raylib:
            md.rl.set_texture_filter(
                inner_surf.texture, md.rl.TextureFilter.TEXTURE_FILTER_BILINEAR
            )  # type: ignore

    def _on_click_system(self):
        self.toggled = not self.toggled
        super()._on_click_system()

    def _create_clone(self):
        self.constant_kwargs["events"] = self.get_param_strict("events").value.copy()
        return self.__class__(
            self._template["size"], copy.deepcopy(self.style), **self.constant_kwargs
        )  # type: ignore

    def _on_copy_system(self, clone: NevuObject):  # type: ignore
        super()._on_copy_system(clone, no_cache=True)
        self._event_cycle(EventType.OnCopy, clone)
