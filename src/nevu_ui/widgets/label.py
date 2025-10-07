import copy

from nevu_ui.fast.nvvector2 import NvVector2
from nevu_ui.widgets import Widget, WidgetKwargs
from nevu_ui.color import PairColorRole

from typing import Any, TypedDict, NotRequired, Unpack

from nevu_ui.style import (
    Style, default_style
)

class LabelKwargs(WidgetKwargs):
    words_indent: NotRequired[bool]

class Label(Widget):
    words_indent: bool
    def __init__(self, text: str, size: NvVector2 | list, style: Style = default_style, **constant_kwargs: Unpack[LabelKwargs]):
        super().__init__(size, style, **constant_kwargs)
        self._lazy_kwargs = {'size': size, 'text': text}
        self._changed = True

    def _add_constants(self):
        super()._add_constants()
        self._add_constant("words_indent", bool, False)

    def _init_booleans(self):
        super()._init_booleans()
        self.hoverable = False
    
    def _lazy_init(self, size: NvVector2 | list, text: str): # type: ignore
        super()._lazy_init(size)
        assert isinstance(text, str)
        self._text = "" 
        self.text = text 
        
    @property
    def text(self):
        return self._text
    
    def _fast_bake_text(self):
        self.bake_text(self._text, False, self.words_indent, self.style.text_align_x, self.style.text_align_y, color = self._subtheme_font)
    
    def _on_style_change(self):
        super()._on_style_change()
        #print(f"{self} style changed")
        
    @text.setter
    def text(self, text: str):
        self._changed = True
        self._text = text

    def resize(self, resize_ratio: NvVector2):
        super().resize(resize_ratio)
        self._changed = True

    @property
    def style(self):
        return self._style()
    @style.setter
    def style(self,style: Style):
        self._changed = True
        self._style = copy.deepcopy(style)
        self._update_image()

    def secondary_draw_content(self):
        super().secondary_draw_content()
        if not self.visible: return
        if self._changed:
            self._fast_bake_text()
            assert self._text_surface is not None and self._text_rect is not None
            self.surface.blit(self._text_surface, self._text_rect)
        
    def secondary_draw_end(self):
        super().secondary_draw_end()
        if not type(self).__subclasses__():
            self._changed = False

    def clone(self):
        return Label(self._lazy_kwargs['text'], self._lazy_kwargs['size'], copy.deepcopy(self.style), **self.constant_kwargs)