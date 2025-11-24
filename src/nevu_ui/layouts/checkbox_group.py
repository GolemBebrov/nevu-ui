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
#        on_checkbox_toggled_multiple
#        on_checkbox_toggled_single
#    Functions >
#        all other functions

class CheckBoxGroup():
    def __init__(self, checkboxes: list[RectCheckBox] | None = None, single_select: bool = False):
        self._single_select = single_select
        self._content: list[RectCheckBox] = []
        self._events: list[NevuEvent] = []
        if checkboxes is None: checkboxes = []
        for checkbox in checkboxes:
            self.add_checkbox(checkbox)

#=== Properties ===
    @property
    def current_checkboxes(self): return self._content

    @property
    def single_select(self): return self._single_select

#=== Wrappers ===
    def _on_toggle_multiple_wrapper(self, checkbox: RectCheckBox):
        toogled_checkboxes = []
        toogled_checkboxes.extend(checkbox for checkbox in self._content if checkbox.toogled)
        self.on_checkbox_toggled_multiple(toogled_checkboxes)
    
    def _on_toggle_single_wrapper(self, checkbox: RectCheckBox):
        if checkbox.toogled == False: return self.on_checkbox_toggled_single(None)
        for item in self._content:
            if item is not checkbox: item.toogled = False
        self.on_checkbox_toggled_single(checkbox)
        
#=== Hooks ===
    def on_checkbox_added(self, checkbox: RectCheckBox):
    #=== hook ===
        pass

    def on_checkbox_toggled_multiple(self, included_checkboxes: list[RectCheckBox]):
    #=== hook ===
        pass

    def on_checkbox_toggled_single(self, checkbox: RectCheckBox | None):
    #=== hook ===
        pass 

#=== Methods ===
    def _add_copy(self, checkbox: RectCheckBox):
        self._content.append(checkbox)
        self.on_checkbox_added(checkbox)
    
    def add_checkbox(self, checkbox: RectCheckBox):
        function = self._on_toggle_single_wrapper if self.single_select else self._on_toggle_multiple_wrapper
        checkbox.subscribe(NevuEvent(self, function, EventType.OnKeyDown))
        checkbox.subscribe(NevuEvent(self, self._add_copy, EventType.OnCopy))
        self._content.append(checkbox)
        self.on_checkbox_added(checkbox)
        
    def get_checkbox_by_id(self, id: str) -> RectCheckBox | None:
        assert id, "Id can not be None."
        return next((item for item in self._content if item.id == id), None)

    def add_event(self, event: NevuEvent):
        self._events.append(event)

    def _event_cycle(self, type: EventType, *args, **kwargs):
        for event in self._events:
            if event._type == type:
                event(*args, **kwargs)