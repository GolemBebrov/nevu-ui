from nevu_ui.widgets import Widget
from warnings import deprecated
@deprecated("Image is deprecated")
class Image(Widget):
    def __init__(self, size, image_path: str, stylee, deprecated_status = True):
        raise NotImplementedError("Image is deprecated")