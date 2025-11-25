from nevu_ui.widgets import Widget
from warnings import deprecated
@deprecated("Gif is deprecated")
class Gif(Widget):
    def __init__(self,size,gif_path, style, frame_duration=100, deprecated_status = True):
        raise NotImplementedError("Gif is deprecated")