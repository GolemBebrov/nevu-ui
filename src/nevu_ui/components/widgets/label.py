import copy
from collections.abc import Callable
from typing import Unpack

import nevu_ui.core.modules as md
from nevu_ui.components._typehints import _LabelKwargs, _LabelTemplate
from nevu_ui.components.widgets.widget import Widget
from nevu_ui.core import Annotations, nevu_state
from nevu_ui.core.enums import CacheType, RenderReturnType
from nevu_ui.core.size.rules import Auto
from nevu_ui.cython.nvvector2 import NvVector2
from nevu_ui.cython.raylib.raylib import begin_blend_mode, end_blend_mode
from nevu_ui.rendering import DrawTextCall


class Label(Widget):
    # === Params ===
    words_indent: bool
    on_text_change: Callable
    # ==============

    def __init__(
        self,
        text: str,
        size: Annotations.nevuobj_size = None,
        style: Annotations.nevuobj_style = None,
        **params: Unpack[_LabelKwargs],
    ):
        if isinstance(size, Auto):
            size = (size, size)
        super().__init__(size, style, **params)
        self._template = _LabelTemplate(self._template.size, text)

    def _add_params(self):
        super()._add_params()
        self._add_param("words_indent", bool, False)
        self._add_param("on_text_change", (type(None), Callable), None)

    def _lazy_init(self, size: NvVector2 | list, text: str):  # type: ignore
        super()._lazy_init(size)
        assert isinstance(text, str)
        self.text = text
        if self._auto_sized:
            _, text_surface = self.cache.get_or_exec(CacheType.TextArgs, self._create_text_surf)
            self.size = NvVector2.from_xy(text_surface.width, text_surface.height)
            self._changed = True
            self.clear_surfaces()

    @property
    def text(self):
        return self._text

    @text.setter
    def text(self, text: str):
        self._changed = True
        self.clear_surfaces()
        self._text = text
        if self.on_text_change:
            self.on_text_change(self, text)

    def _create_text_surf(self):
        result = self.renderer.run_text(
            DrawTextCall(
                size=self.current_size,
                text=self.text or "",
                color=self.subtheme_font,
                words_indent=self.words_indent,
                return_type=RenderReturnType.CreateNew,
                unlimited_x=self._auto_sized,
                style=self.style,
                cache = self.cache,
                relm = self.relm(1)
            )
        )

        if nevu_state.window.renderer_type.raylib:
            texture = result[1].native.texture
            rl = md.rl
            rl.set_texture_filter(
                texture, rl.TextureFilter.TEXTURE_FILTER_BILINEAR
            )
            rl.set_texture_wrap(texture, rl.TextureWrap.TEXTURE_WRAP_CLAMP)

        return result

    def _resize_content(self, resize_ratio: NvVector2):
        super()._resize_content(resize_ratio)
        if self._auto_sized:
            self.cache.clear_selected(whitelist=[CacheType.RelSize])
            anti_rel = NvVector2(1, 1) / self._resize_ratio
            _, text_surface = self.cache.get_or_exec(CacheType.TextArgs, self._create_text_surf)
            self.size = NvVector2.from_xy(
                text_surface.width * anti_rel.x + self._auto_sized_padding[0] * 2,
                text_surface.height * anti_rel.y + self._auto_sized_padding[1] * 2)

    def _draw_main(self):
        text_rect, text_surface = self.cache.get_or_exec(CacheType.TextArgs, self._create_text_surf)
        coordinates = (text_rect[0], text_rect[1])
        if self._auto_sized:
            coordinates = (self.relx(self._auto_sized_padding[0]), self.rely(self._auto_sized_padding[1]))

        if not text_surface:
            return

        surf = self.surface

        is_raylib = nevu_state.window.renderer_type.raylib

        with surf:
            if is_raylib:
                begin_blend_mode(self._correct_blend)
            surf.blit(text_surface, coordinates)
            if is_raylib:
                end_blend_mode()

    def _create_clone(self):
        return self.__class__(
            self._template["text"],
            self._template["size"],
            copy.deepcopy(self.style),
            **self.kwargs,
        )
