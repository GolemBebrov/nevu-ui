import copy
from typing import Unpack

from nevu_ui.fast.nvvector2 import NvVector2
from nevu_ui.core import nevu_state
from nevu_ui.presentation.style import Style, default_style
from nevu_ui.components.widgets import Widget, LabelKwargs, LabelTemplate

class Label(Widget):
    words_indent: bool
    def __init__(self, text: str, size: NvVector2 | list, style: Style = default_style, **constant_kwargs: Unpack[LabelKwargs]):
        super().__init__(size, style, **constant_kwargs)
        self._template = LabelTemplate(size, text)
        self._changed = True

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
        if not nevu_state.window.is_dtype.raylib: 
            self.bake_text(self._text, False, self.words_indent, self.style.text_align_x, self.style.text_align_y, color = self.subtheme_font)
        else: self.renderer.bake_text(self._text, False, self.words_indent, self.style, color = self.subtheme_font, modify=self.surface)
    def _resize(self, resize_ratio: NvVector2):
        super()._resize(resize_ratio)
        self._changed = True
    
    def secondary_draw_content(self):
        super().secondary_draw_content()
        if not self.visible: return
        if self._changed_text or self._changed:
            self._changed_text = False
            self._fast_bake_text()
            if self._text_surface and self._text_rect and not nevu_state.window.is_dtype.raylib:
                self.surface.blit(self._text_surface, self._text_rect)
            #elif self._text_surface and self._text_rect and nevu_state.window.is_dtype.raylib:
                #rl.begin_texture_mode(self.surface)
                #nevu_state.window.display.blit(self._text_surface.texture, (self._text_rect.x, self._text_rect.y))
                #№rl.end_texture_mode()

    def _create_clone(self):
        return self.__class__(self._template['text'], self._template['size'], copy.deepcopy(self.style), **self.constant_kwargs)