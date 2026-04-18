import copy
from typing import Unpack

import nevu_ui.core.modules as md
from nevu_ui.core import Annotations
from nevu_ui.fast.nvvector2 import NvVector2
from nevu_ui.core import nevu_state
from nevu_ui.presentation.style import Style, default_style
from nevu_ui.components.widgets import Widget, LabelKwargs, LabelTemplate
from nevu_ui.core.enums import RenderConfig, RenderReturnType, CacheType

class Label(Widget):
    def __init__(self, text: str, size: Annotations.nevuobj_size = None, style: Annotations.nevuobj_style = None, **constant_kwargs: Unpack[LabelKwargs]):
        super().__init__(size, style, **constant_kwargs)
        self._template = LabelTemplate(self._template.size, text)
        self._changed = True

    @property
    def words_indent(self) -> bool: return self.get_param_strict("words_indent").value
    
    def _add_params(self):
        super()._add_params()
        self._add_param("words_indent", bool, False)

    def _init_booleans(self):
        super()._init_booleans()
        self._changed_text = True
    
    def _lazy_init(self, size: NvVector2 | list, text: str): # type: ignore
        super()._lazy_init(size)
        assert isinstance(text, str)
        self._text = "" 
        self.text = text 
        
    @property
    def text(self): return self._text
    @text.setter
    def text(self, text: str):
        self._changed = True
        self._text = text

    def _fast_bake_text(self):
        #if not nevu_state.window.is_dtype.raylib: 
        #    self.bake_text(self._text, False, self.words_indent, self.style.align_x, self.style.align_y, color = self.subtheme_font)
        #else: self.renderer.bake_text(self._text, False, self.words_indent, self.style, color = self.subtheme_font)
        cached_args = self.cache.get_or_exec(CacheType.TextArgs, lambda: self.renderer.run_text(RenderConfig.DrawL3, text=self._text, 
                                                                                                words_indent=self.words_indent, return_type=RenderReturnType.CreateNew))
        self._text_rect, self._text_surface = cached_args
        if nevu_state.window.is_dtype.raylib:
            md.rl.set_texture_filter(self._text_surface.texture, md.rl.TextureFilter.TEXTURE_FILTER_BILINEAR)
            md.rl.set_texture_wrap(self._text_surface.texture, md.rl.TextureWrap.TEXTURE_WRAP_CLAMP)
        
    def secondary_draw_content(self):
        super().secondary_draw_content()
        if not self.visible: return
        if self._changed_text or self._changed:
            self._changed_text = False
            self._fast_bake_text()
            coordinates = NvVector2(self._text_rect)
            if self.inline: coordinates += self.coordinates
            if self._text_surface and not nevu_state.window.is_dtype.raylib:
                
                self.surface.blit(self._text_surface, coordinates.get_int_tuple()) 
            elif self._text_surface and self._text_rect:
                with self.surface: #type: ignore
                    md.rl.begin_blend_mode(md.rl.BlendMode.BLEND_ALPHA_PREMULTIPLY)
                    self.surface.fast_blit(self._text_surface, coordinates.get_int_tuple())
                    md.rl.end_blend_mode()
                    #nevu_state.window.display.blit_rect_vec(self._text_surface.texture, (0, 0), mode = md.rl.BlendMode.BLEND_ALPHA_PREMULTIPLY) #type: ignore

    def _create_clone(self):
        return self.__class__(self._template['text'], self._template['size'], copy.deepcopy(self.style), **self.constant_kwargs)