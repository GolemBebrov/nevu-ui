from nevu_ui.widgets import Widget
import copy

class EmptyWidget(Widget):
    def draw(self):
        pass
    def clone(self):
        return EmptyWidget(self._lazy_kwargs['size'], copy.deepcopy(self.style), **self.constant_kwargs)