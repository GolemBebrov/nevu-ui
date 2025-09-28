#Deprecated

class IntPickerGrid:
    def __init__(self, deprecated = "so TRUE"):
        raise DeprecationWarning("IntPickerGrid is deprecated")

"""
class IntPickerGrid(Grid):
    def __init__(self, amount_of_colors: int = 3, item_size: int = 50, y_size: int = 50, margin:int = 0, title: str = "", 
                 color_widget_style: Style = default_style, title_label_style: Style = default_style, on_change_function=None):
        if amount_of_colors <= 0: raise Exception("Amount of colors must be greater than 0")
        if item_size <= 0: raise Exception("Item size must be greater than 0")
        if margin < 0: raise Exception("Margin must be greater or equal to 0")
        self._widget_line = 1
        if title.strip() != "": self._widget_line = 2
        self.size = (amount_of_colors*item_size+margin*(amount_of_colors-1), y_size*self._widget_line+margin*(self._widget_line-1))
        self.on_change_function = on_change_function  
        super().__init__(self.size,amount_of_colors,self._widget_line)
        for i in range(amount_of_colors): 
            self.add_item(Input((item_size,y_size),color_widget_style(text_align_x=Align.CENTER),"","0",None,Input_Type.NUMBERS,on_change_function=self._return_colors,max_characters=3),i+1,self._widget_line)
        if self._widget_line == 2:
            if amount_of_colors % 2 == 0: offset = 0.5
            else: offset = 1
            self.label = Label((self.size[0],y_size),title,title_label_style(text_align_x=Align.CENTER))
            self.add_item(self.label,amount_of_colors//2+offset,1)
    def _return_colors(self, *args):
        c = self.get_color()
        if self.on_change_function: self.on_change_function(c)
    def get_color(self) -> tuple:
        c = []
        for item in self.items: 
            if isinstance(item, Input): c.append(int(item.text))
        return tuple(c)
    def set_color(self, color: tuple|list):
        for i in range(len(color)):
            if i == len(self.items): break
            self.items[i].text = str(color[i])
"""