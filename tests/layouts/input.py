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
        input_box: ui.Input = self.showcase_widgets[4]
        input_box._template.size = [ui.Fill(100), ui.Fill(100)]
        input_box.style = input_box.style(border_radius=15, border_width=3, font_size=44)
        self.test_menu.layout = \
        ui.Grid([ui.Fill(100), ui.Fill(100)], x=3,y=3,
                content={
                    (2,2): input_box,
                    }
                )
        self.grid = self.test_menu.layout
    def on_update(self, events=None):
        super().on_update()

ts = InputGrid()
ts.run()