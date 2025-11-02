from nevu_ui.struct import Struct
from nevu_ui.core_types import ConfigType

class NotCreatedError(Exception):
    def __init__(self) -> None:
        super().__init__("This config paramether is not created yet.")

class Config:
    def __init__(self) -> None:
        self.set_original()
    def set_original(self):
        self.win_config = {
            "title": "Nevu UI",
            "size": ConfigType.Window.Size.Medium,
            "display": ConfigType.Window.Display.Classic,
            "utils": ConfigType.Window.Utils.All,
            "fps": 60,
            "resizable": True,
            "ratio": (1,1)
        }
        self.styles = NotCreatedError
        self.colors = {}
        self.colorthemes = NotCreatedError
        self.animations = NotCreatedError
        
standart_config = Config()
