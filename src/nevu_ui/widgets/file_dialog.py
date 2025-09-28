from nevu_ui.widgets import Button

from nevu_ui.style import default_style

class FileDialog(Button):
    def __init__(self, on_change_function, dialog,text, size, style = default_style, active = True, freedom=False, words_indent=False):
        super().__init__(None, text, size, style, active, False, freedom, words_indent)
        self.on_change_function = on_change_function
        self.dialog = dialog
        self.filepath = None
    def _open_filedialog(self):
        self.filepath = self.dialog()
        
        if self.on_change_function:
            self.on_change_function(self.filepath)
            
    def update(self,*args):
        super().update(*args)
        if not self.active: return
        if self.hovered and mouse.left_up:
                try: self._open_filedialog()
                except Exception as e:
                    print(e)
                    
