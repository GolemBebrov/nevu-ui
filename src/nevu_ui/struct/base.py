from nevu_ui.core.classes import ConfigType

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
        self.styles = {}
        self.colors = {}
        self.colorthemes = {}
        self.animations = NotCreatedError
        
standart_config = Config()

def get_color(name: str, default = None):
    return standart_config.colors.get(name, default)

def get_style(name: str, default = None):
    return standart_config.styles.get(name, default)

def get_colortheme(name: str, default = None):
    return standart_config.colorthemes.get(name, default)