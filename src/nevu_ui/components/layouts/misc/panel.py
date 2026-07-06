import copy
from typing import Unpack

from nevu_ui.components.layouts.grid.base import Grid, GridKwargs_uni
from nevu_ui.components.nevuobj import NevuObject
from nevu_ui.components.widgets.widget import Widget
from nevu_ui.core import Annotations
from nevu_ui.core.state import nevu_state
from nevu_ui.fast.nvvector2 import NvVector2
from nevu_ui.presentation.style import Style
from nevu_ui.presentation.style.style import StyleKwargs


class Panel(Grid):
    _is_panel = True

    def __init__(
        self,
        size: Annotations.nevuobj_size,
        style: Annotations.nevuobj_style = None,
        slot: NevuObject | None = None,
        bg_widget: Widget | None = None,
        **constant_kwargs: Unpack[GridKwargs_uni],
    ):
        super().__init__(size, style, slot, **constant_kwargs)  # type: ignore
        self.bg_widget = bg_widget
        self._custom_primary_draw = True

    def _add_params(self):
        super()._add_params()
        self._block_param("column")
        self._block_param("row")

    def _rl_predraw_widgets(self):
        super()._rl_predraw_widgets()
        if self.bg_widget:
            self.bg_widget.draw()

    def _lazy_init(self, size: NvVector2 | list, content=None):
        super()._lazy_init(size, None)
        if slot := content:
            self.add_item(slot, 1, 1)

        if self.bg_widget is None:
            self._create_bg_widget()

        if not self.is_widget(self.bg_widget):
            raise ValueError(
                Annotations.format_nverror(
                    "bg_widget must be a Widget object",
                    f"current bg_widget object is: {self.bg_widget} with class name: {self.bg_widget.__class__.__name__}",
                    "check all your Panel objects constructor arguments and if the bg_widget argument is not a Widget object, remove or correct it",
                )
            )
        self.bg_widget._template.size = self.size.xy
        self.bg_widget._init_start()
        self.bg_widget.booted = True
        self.bg_widget._boot_up()

    def _create_bg_widget(self):
        dummy = Widget(self.size, self.style)
        valid_keys = set(dummy._get_param_names()) | set(dummy._param_links.keys())
        dummy._kill_base()
        widget_kwargs = {
            k: v for k, v in self.constant_kwargs.items() if k.lower() in valid_keys
        }

        self.bg_widget = Widget(
            self.size, self.style, z=-99999999999, bg_variant=True, **widget_kwargs
        )
        self.bg_widget.coordinates = self.coordinates.copy()

        self.bg_widget.set_param_value("clickable", False)
        self.bg_widget.set_param_value("hoverable", False)
        self.bg_widget._sended_z_link = True

    def apply_style_patch_to_childs(self, **patch: Unpack[StyleKwargs]):
        super().apply_style_patch_to_childs(**patch)
        self.bg_widget.style = self.bg_widget.style(**patch)

    def apply_style_to_childs(self, style: Style):
        super().apply_style_to_childs(style)
        self.bg_widget.style = style

    def _coordinates_setter(self, coordinates: NvVector2) -> bool:  # type: ignore
        result = super()._coordinates_setter(coordinates)
        if self.bg_widget:
            self.bg_widget.coordinates = coordinates.copy()
        if slot := self.get_item(1, 1):
            if self.is_layout(slot):
                slot.cached_coordinates = None
        return result

    def _resize_content(self, resize_ratio: NvVector2):
        super()._resize_content(resize_ratio)
        if self.bg_widget:
            self.bg_widget._resize(resize_ratio)
            self.bg_widget._changed = True

    def secondary_update(self, *args):
        if self.bg_widget:
            self.bg_widget.update()
        super().secondary_update(*args)

    def _primary_draw(self):
        if not self.bg_widget or not self.surface:
            return
        self.bg_widget.draw()
        if nevu_state.window.renderer_type.raylib:
            self.surface.fast_blit(
                self.bg_widget.surface, self.coordinates.get_int_tuple()
            )
        else:
            self.surface.blit(self.bg_widget.surface, self.coordinates.get_int_tuple())
        super()._primary_draw()

    @property
    def style(self) -> Style:
        return self._style

    @style.setter
    def style(self, style: Style):
        self._style = style
        self._changed = True
        if hasattr(self, "bg_widget") and self.bg_widget:
            self.bg_widget.style = style
            self.bg_widget.cache.clear()

    def _create_clone(self):
        cloned_bg = self.bg_widget.clone() if self.bg_widget else None

        kwargs = self.constant_kwargs.copy()
        return Panel(
            size=self._template["size"],
            style=copy.deepcopy(self.style),
            slot=copy.deepcopy(self._template["content"]),
            bg_widget=cloned_bg,
            **kwargs,
        )
