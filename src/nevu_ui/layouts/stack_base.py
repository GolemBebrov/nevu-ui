from abc import ABC, abstractmethod
from typing import Unpack, NotRequired, TypedDict
import copy

from nevu_ui.size.base import SizeRule
from nevu_ui.widgets import Widget
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from nevu_ui.menu import Menu
from nevu_ui.nevuobj import NevuObject
from nevu_ui.fast.nvvector2 import NvVector2
from nevu_ui.core.enums import Align
from nevu_ui.layouts import LayoutType, LayoutTypeKwargs
from nevu_ui.style import Style, default_style

class _StackKwargs(TypedDict):
    spacing: NotRequired[int | float]

class StackKwargs(_StackKwargs, LayoutTypeKwargs): pass

#Nnna nanachi approved!
class StackBase(LayoutType, ABC):
    content_type = list[tuple[Align, NevuObject]]
    def __init__(self, style: Style = default_style, content: content_type | None = None, **constant_kwargs: Unpack[StackKwargs]):
        super().__init__(NvVector2(), style, content, **constant_kwargs)
        
    def _lazy_init(self, size: NvVector2 | list, content: content_type | None = None):
        super()._lazy_init(size, content)
        self.add_items(content)

    def add_items(self, content: content_type | None): # type: ignore
        if content is None: return
        for inner_tuple in content:
            align, item = inner_tuple
            self.add_item(item, align)
            
    def _init_lists(self):
        super()._init_lists()
        self.widgets_alignment = []
        
    def _add_params(self):
        super()._add_params()
        self._add_param("spacing",(int, float), 10)
    
    def _init_numerical(self):
        super()._init_numerical()
        self._bugfix1 = 2
    
    def _clear_cached_coordinates(self):
        super()._clear_cached_coordinates()
    
    def _init_test_flags(self):
        super()._init_test_flags()
        self._test_always_update = False
    
    def add_item(self, item: NevuObject, alignment: Align = Align.CENTER): # type: ignore
        super().add_item(item)
        self.widgets_alignment.append(alignment)
        self.cached_coordinates = None

    def _parse_fillx(self, coord: SizeRule, pos: int) -> tuple[float, bool] | None:
        raise ValueError(f"Handling for SizeRule '{type(coord).__name__}' is not supported in {type(self).__name__}")
    
    def insert_item(self, item: Widget | LayoutType, id: int = -1):
        try:
            self.items.insert(id, item)
            self.widgets_alignment.insert(id, Align.CENTER)
            self._recalculate_size()
            if self.layout: self.layout._on_item_add(item)
        except Exception as e: raise e #TODO: FUCK i forgor 
        
    def _connect_to_layout(self, layout: LayoutType):
        super()._connect_to_layout(layout)
        self._recalculate_widget_coordinates()
        
    def _connect_to_menu(self, menu: Menu):
        super()._connect_to_menu(menu)
        self._recalculate_widget_coordinates() 
    
    def _on_item_add(self, item: NevuObject):
        #print(self, item)
        if not self.booted:
            self.cached_coordinates = None
            if self.layout: self.layout.cached_coordinates = None 
            return
        self._recalculate_size()
        if self.layout: self.layout._on_item_add(item)
        
    def secondary_update(self, *args):
        super().secondary_update()
        self._base_light_update()
    
    def _secondary_draw(self):
        super()._secondary_draw()
        for item in self.items:
            assert isinstance(item, (Widget, LayoutType))
            if not item.booted:
                item.booted = True
                item._boot_up()
                self._start_item(item)
            self._draw_widget(item)
            
    @property
    def spacing(self): return self.get_param_strict("spacing").value
    @spacing.setter
    def spacing(self, val): self.set_param_value("spacing", val)
        
    def _regenerate_coordinates(self):
        super()._regenerate_coordinates()
        self._recalculate_size()
        self._recalculate_widget_coordinates()
    
    def _create_clone(self):
        return self.__class__(copy.deepcopy(self.style), copy.deepcopy(self._template['content']), **self.constant_kwargs)

#=== Placeholders ===
    @abstractmethod
    def _set_align_coords(self, item: NevuObject, alignment: Align): pass
    @abstractmethod
    def _recalculate_size(self): pass
    @abstractmethod
    def _recalculate_widget_coordinates(self): pass