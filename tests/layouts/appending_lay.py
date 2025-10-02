import nevu_ui as ui
import pygame
from basic import NevuTest
pygame.init()
class TestAppending(NevuTest):
    def add_to_layout(self):
        self.do_fps_test = True
        #self.print_debug_fps = True
        self.fps = 99999999
        self.appending_layout_h = \
            ui.StackRow(spacing = 40,content = 
                                  [(ui.Align.CENTER, self.test_widget),
                                   (ui.Align.CENTER, self.test_hard_widget),
                                   (ui.Align.CENTER, self.test_inner_layout),]
                                  )
        print("STARTED APPENDING", self.appending_layout_h._lazy_kwargs)
        self.test_menu.layout = \
        ui.Grid([ui.Fill(100), ui.Fill(100)], x=3,y=3,
                content={
                    (2,2): self.appending_layout_h
                    }
                )
        self.grid = self.test_menu.layout
    def update_loop(self, events=None):
        super().update_loop(events)
        #print(self.test_hard_widget.text)
ts = TestAppending()
ts.run()