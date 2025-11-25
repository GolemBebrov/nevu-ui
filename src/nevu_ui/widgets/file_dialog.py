from nevu_ui.widgets import Button
from warnings import deprecated
@deprecated("FileDialog is deprecated")
class FileDialog(Button):
    def __init__(self, on_change_function, dialog,text, size, style, active = True, freedom=False, words_indent=False, deprecated_status = True):
        raise NotImplementedError("FileDialog is deprecated")