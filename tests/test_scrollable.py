import nevu_ui as ui
import pygame
from test_basic import NevuTest
pygame.init()
class TestScrollable(NevuTest):
    def add_to_layout(self):
        self.do_fps_test = True
        self.test_menu.layout = \
        ui.Scrollable([100*ui.vw, 100*ui.vh],
                content=[
                    (ui.Align.CENTER, self.test_widget),
                    (ui.Align.CENTER, self.test_hard_widget),
                    (ui.Align.CENTER, self.test_inner_layout),
                    (ui.Align.CENTER, self.test_widget),
                    (ui.Align.CENTER, self.test_widget),
                    (ui.Align.CENTER, self.test_widget),
                ]
                )
        self.scrollable = self.test_menu.layout
        #self.scrollable._test_always_update = True
        print(self.scrollable.get_rect())
        assert isinstance(self.scrollable, ui.Scrollable)
    def draw_loop(self):
        super().draw_loop()
        print(self.scrollable.items[0].get_rect())
        print(self.scrollable._hover_state)
        
        
ts = TestScrollable()
ts.run()