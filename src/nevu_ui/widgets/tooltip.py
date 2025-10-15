from nevu_ui.style import Style, default_style
from nevu_ui.core_types import TooltipType
class Tooltip():
    def __init__(self, type: TooltipType, text, style: Style = default_style):
        self.text = text
        self.style = style
        self.type = type.lower()
        
        raise NotImplementedError("Tooltip is not implemented yet, wait till 0.6.X")
    def draw(self):
        pass #TODO in version 0.6 
    