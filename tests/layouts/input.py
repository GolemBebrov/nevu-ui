import nevu_ui as ui
import pygame
from basic import NevuTest
pygame.init()
class InputGrid(NevuTest):
    def add_to_layout(self):
        self.do_fps_test = True
        #self.draw_cursor = False
        #self.print_debug_fps = True
        self.fps = 99999999
        input_box: ui.Input = self.showcase_widgets[2]
        input_box._lazy_kwargs['size'] = [ui.Fill(100), ui.Fill(100)]
        input_box.style = ui.default_style(borderradius=15, borderwidth=3, fontsize=12)
        self.test_menu.layout = \
        ui.Grid([ui.Fill(100), ui.Fill(100)], x=3,y=3,
                content={
                    (2,2): input_box,
                    }
                )
        self.grid = self.test_menu.layout
    def on_update(self, events=None):
        super().on_update(events)
        #print(self.test_hard_widget.text)
ts = InputGrid()
ts.run()