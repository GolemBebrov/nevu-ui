from nevu_ui.widgets.widget import Widget
from nevu_ui.style import Style, default_style

class Tooltip(Widget):
    def __init__(self, text, style: Style = default_style):
        self.text = text
        self.style = style
        self.size = (200,400)
        self.bake_text(self.text,False,True,self.style.text_align_x,self.style.text_align_y)
        raise NotImplementedError("Tooltip is not implemented yet, wait till 0.05")
    def draw(self):
        pass #TODO in version 0.6 :)
    