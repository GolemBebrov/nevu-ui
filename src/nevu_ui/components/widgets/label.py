import copy
from typing import Callable, Unpack

import nevu_ui.core.modules as md
from nevu_ui.components.widgets.typehints import LabelKwargs, LabelTemplate
from nevu_ui.components.widgets.widget import Widget
from nevu_ui.core import Annotations, nevu_state
from nevu_ui.core.enums import CacheType, RenderConfig, RenderReturnType
from nevu_ui.fast.nvrendertex import NvRenderTexture
from nevu_ui.fast.nvvector2 import NvVector2
from nevu_ui.fast.raylib.nevu_raylib import begin_blend_mode, end_blend_mode
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
        **constant_kwargs: Unpack[LabelKwargs],
    ):
        super().__init__(size, style, **constant_kwargs)
        self._template = LabelTemplate(self._template.size, text)

    def _add_params(self):
        super()._add_params()
        self._add_param("words_indent", bool, False)
        self._add_param("on_text_change", (type(None), Callable), None)

    def _lazy_init(self, size: NvVector2 | list, text: str):  # type: ignore
        super()._lazy_init(size)
        assert isinstance(text, str)
        self.text = text

    @property
    def text(self):
        return self._text

    @text.setter
    def text(self, text: str):
        self._changed = True
        self.clear_surfaces()
        self.clear_texture()
        self._text = text
        if self.on_text_change:
            self.on_text_change(self, text)

    def _fast_bake_text(self):
        result = self.cache.get_or_exec(
            CacheType.TextArgs,
            lambda: self.renderer.run_text(
                DrawTextCall(
                    text=self.text or "",
                    words_indent=self.words_indent,
                    return_type=RenderReturnType.CreateNew,
                    continuous=False,
                )
            ),
        )
        assert result

        self._text_rect, self._text_surface = result
        if nevu_state.window.renderer_type.raylib:
            texture = self._text_surface.texture
            rl = md.rl
            md.rl.set_texture_filter(
                texture, rl.TextureFilter.TEXTURE_FILTER_ANISOTROPIC_16X
            )
            md.rl.set_texture_wrap(texture, rl.TextureWrap.TEXTURE_WRAP_CLAMP)

    def secondary_draw_content(self):
        self._fast_bake_text()

        if self.inline:
            coordinates = NvVector2(self._text_rect)
            coordinates += self.coordinates
            coordinates = coordinates.get_int_tuple()
        else:
            coordinates = (self._text_rect[0], self._text_rect[1])

        text_surface = self._text_surface
        if not text_surface:
            return
        rtype = nevu_state.window.renderer_type
        surf = self.surface

        if rtype.pygame_like:
            surf.blit(text_surface, coordinates)

        elif rtype.raylib:
            assert isinstance(surf, NvRenderTexture)
            with surf:
                begin_blend_mode(self._correct_blend)
                surf.fast_blit(text_surface, coordinates)
                end_blend_mode()

    def _create_clone(self):
        return self.__class__(
            self._template["text"],
            self._template["size"],
            copy.deepcopy(self.style),
            **self.constant_kwargs,
        )
