import nevu_ui as ui
import pygame
from basic import NevuTest
pygame.init()
class TestGrid(NevuTest):
    def add_to_layout(self):
        self.do_fps_test = True
        #self.draw_cursor = False
        #self.print_debug_fps = True
        self.fps = 99999999
        self.test_menu.layout = \
        ui.Grid([ui.Fill(100), ui.Fill(100)], x=3,y=3,
                content={
                    (2,1): self.showcase_widgets[0],
                    (1,2): self.showcase_widgets[1],
                    (2,3): self.showcase_widgets[2],
                    }
                )
        self.grid = self.test_menu.layout
    def update_loop(self, events=None):
        super().update_loop(events)
        #print(self.test_hard_widget.text)
ts = TestGrid()
ts.run()