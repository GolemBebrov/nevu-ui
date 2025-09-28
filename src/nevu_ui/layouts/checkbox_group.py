from nevu_ui.widgets import RectCheckBox
from nevu_ui.core_types import EventType
from nevu_ui.utils import NevuEvent

class CheckBoxGroup():
    def __init__(self, checkboxes: list[RectCheckBox] | None = None, single_select: bool = False):
        self._single_select = single_select
        self._content: list[RectCheckBox] = []
        self._events: list[NevuEvent] = []
        if checkboxes is None: checkboxes = []
        for checkbox in checkboxes:
            self.add_checkbox(checkbox)
    
    @property
    def single_select(self): return self._single_select
    
    def on_checkbox_added(self, checkbox: RectCheckBox):
        pass #hook
    
    def _on_checkbox_toggled_wrapper(self, checkbox: RectCheckBox):
        toogled_checkboxes = []
        toogled_checkboxes.extend(
            checkbox for checkbox in self._content if checkbox.toogled
        )
        self.on_checkbox_toggled(toogled_checkboxes)
    
    def _on_checkbox_toggled_single_wrapper(self, checkbox: RectCheckBox):
        if checkbox.toogled == False: return self.on_checkbox_toggled_single(None)
        for item in self._content:
            if item is not checkbox: item.toogled = False
        self.on_checkbox_toggled_single(checkbox)
    
    def on_checkbox_toggled(self, included_checkboxes: list[RectCheckBox]):
        pass #hook

    def on_checkbox_toggled_single(self, checkbox: RectCheckBox | None):
        pass #hook
    
    def _add_copy(self, checkbox: RectCheckBox):
        self._content.append(checkbox)
        self.on_checkbox_added(checkbox)
    
    def add_checkbox(self, checkbox: RectCheckBox):
        function = self._on_checkbox_toggled_single_wrapper if self.single_select else self._on_checkbox_toggled_wrapper
        checkbox.subscribe(NevuEvent(self, function, EventType.OnKeyDown))
        checkbox.subscribe(NevuEvent(self, self._add_copy, EventType.OnCopy))
        self._content.append(checkbox)
        self.on_checkbox_added(checkbox)
        
    def get_checkbox(self, id: str) -> RectCheckBox | None:
        assert id, "id cant be None"
        return next((item for item in self._content if item.id == id), None)
    
    def add_event(self, event: NevuEvent):
        self._events.append(event)

    def _event_cycle(self, type: EventType, *args, **kwargs):
        for event in self._events:
            if event._type == type:
                event(*args, **kwargs)