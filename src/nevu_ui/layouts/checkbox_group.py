from nevu_ui.widgets import RectCheckBox
from nevu_ui.core_types import EventType
from nevu_ui.utils import NevuEvent

#CHECKBOX_GROUP STRUCTURE: ====================
#    Properties >
#        all property functions
#    Wrappers >
#        wrappers for different modes
#    Hooks >
#        on_checkbox_added
#        on_single_toggled
#        on_multiple_toggled
#    Functions >
#        all other functions

class CheckBoxGroup():
    def __init__(self, checkboxes: list[RectCheckBox] | None = None, single_selection: bool = False):
        self._single_select = single_selection; self._content: list[RectCheckBox] = []; self._events: list[NevuEvent] = []
        for checkbox in checkboxes or []: self.add_checkbox(checkbox)

#=== Properties ===
    @property
    def current_checkboxes(self): return self._content

    @property
    def single_select(self): return self._single_select

#=== Wrappers ===
    def _on_toggle_multiple_wrapper(self, checkbox: RectCheckBox): self.on_multiple_toggled([c for c in self._content if c.toogled])
    
    def _on_toggle_single_wrapper(self, checkbox: RectCheckBox):
        if checkbox.toogled == False: return self.on_single_toggled(None)
        for item in self._content:
            if item is not checkbox: item.toogled = False
        self.on_single_toggled(checkbox)
        
#=== Hooks ===
    def on_checkbox_added(self, checkbox: RectCheckBox): pass #=== hook ===

    def on_multiple_toggled(self, included_checkboxes: list[RectCheckBox]): pass #=== hook ===

    def on_single_toggled(self, checkbox: RectCheckBox | None): pass #=== hook ===

#=== Functions ===
    def add_checkbox(self, checkbox: RectCheckBox):
        checkbox.subscribe(NevuEvent(self, self._on_toggle_single_wrapper if self.single_select else self._on_toggle_multiple_wrapper, EventType.OnKeyDown))
        checkbox.subscribe(NevuEvent(self, self._sub_add, EventType.OnCopy))
        self._sub_add(checkbox)
    
    def _sub_add(self, checkbox: RectCheckBox):
        self._content.append(checkbox)
        self.on_checkbox_added(checkbox)
    
    def get_checkbox_by_id(self, id: str) -> RectCheckBox | None:
        assert id, "Id can not be None."
        return next((item for item in self._content if item.id == id), None)
    
    def add_event(self, event: NevuEvent): self._events.append(event)

    def _event_cycle(self, event_type: EventType, *args, **kwargs):
        for event in self._events:
            if event._type == event_type: event(*args, **kwargs)