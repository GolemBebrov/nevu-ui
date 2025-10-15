from nevu_ui.widgets import Widget
from nevu_ui.menu import Menu
from nevu_ui.nevuobj import NevuObject
from nevu_ui.fast.nvvector2 import NvVector2
from nevu_ui.core_types import Align
from nevu_ui.layouts import LayoutType

from nevu_ui.style import (
    Style, default_style
)

class StackBase(LayoutType):
    _margin: int | float
    def __init__(self, style: Style = default_style, content: list[tuple[Align, NevuObject]] | None = None, **constant_kwargs):
        super().__init__(NvVector2(), style, None, **constant_kwargs)
        self._lazy_kwargs = {'size': NvVector2(), 'content': content}
        
    def _lazy_init(self, size: NvVector2 | list, content: list[tuple[Align, NevuObject]] | None = None):
        super()._lazy_init(size, content)
        if content is None: return
        if len(content) == 0: return
        for inner_tuple in content:
            align, item = inner_tuple
            self.add_item(item, align)
            
    def _init_lists(self):
        super()._init_lists()
        self.widgets_alignment = []
        
    def _add_constants(self):
        super()._add_constants()
        self._add_constant("spacing",(int, float), 10)
        
    def _init_test_flags(self):
        super()._init_test_flags()
        self._test_always_update = True
    
    def _recalculate_size(self):
        pass
    
    def _recalculate_widget_coordinates(self):
        pass
    
    def add_item(self, item: NevuObject, alignment: Align = Align.CENTER):
        super().add_item(item)
        self.widgets_alignment.append(alignment)
        self.cached_coordinates = None
        if self.layout: self.layout._event_on_add_item()
        
    def insert_item(self, item: Widget | LayoutType, id: int = -1):
        try:
            self.items.insert(id,item)
            self.widgets_alignment.insert(id,Align.CENTER)
            self._recalculate_size()
            if self.layout: self.layout._event_on_add_item()
        except Exception as e: raise e #TODO
        
    def _connect_to_layout(self, layout: LayoutType):
        super()._connect_to_layout(layout)
        self._recalculate_widget_coordinates()
        
    def _connect_to_menu(self, menu: Menu):
        super()._connect_to_menu(menu)
        self._recalculate_widget_coordinates() 
        
    def _event_on_add_item(self):
        if not self.booted:
            self.cached_coordinates = None
            if self.layout:
                self.layout.cached_coordinates = None 
            return

        self._recalculate_size()
        
        if self.layout:
            self.layout._event_on_add_item()
        
    def secondary_update(self, *args):
        super().secondary_update()
        self.base_light_update()
        
    def secondary_draw(self):
        super().secondary_draw()
        for item in self.items:
            assert isinstance(item, (Widget, LayoutType))
            if not item.booted:
                item.booted = True
                item._boot_up()
                self._start_item(item)
            self._draw_widget(item)
            
    @property
    def spacing(self): return self._spacing
    @spacing.setter
    def spacing(self, val):
        self._spacing = val
        
    def _regenerate_coordinates(self):
        super()._regenerate_coordinates()
        self._recalculate_size()
        self._recalculate_widget_coordinates()
    
    def _set_align_coords(self, item, alignment):
        pass