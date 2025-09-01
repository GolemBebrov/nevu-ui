import nevu_ui as ui
import pygame
from test_basic import NevuTest
pygame.init()
class TestGrid(NevuTest):
    def add_to_layout(self):
        self.do_fps_test = True
        self.test_menu.layout = \
        ui.Grid([100*ui.fill, 100*ui.fill], x=3,y=3,
                content={
            
                    (2,1): self.test_widget,
                    (2,2): self.test_hard_widget,
                    (2,3): self.test_inner_layout,
                    }
                )

ts = TestGrid()
ts.run()