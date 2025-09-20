import nevu_ui as ui
import pygame
from test_basic import NevuTest
pygame.init()
class TestGrid(NevuTest):
    def add_to_layout(self):
        self.do_fps_test = True
        self.test_menu.layout = \
        ui.Grid([ui.Fill(100), ui.Fill(100)], x=3,y=3,
                content={
                    (2,1): self.test_widget,
                    (2,1.8): self.test_hard_widget,
                    (2,3): self.test_inner_layout,
                    }
                )
        self.grid = self.test_menu.layout
    def update_loop(self, events=None):
        super().update_loop(events)
        #print(self.test_hard_widget.text)
ts = TestGrid()
ts.run()