import nevu_ui as ui
from nevu_ui.size.units import *
import pygame
from basic import NevuTest
pygame.init()
class TestGrid(NevuTest):
    def add(self):
        self.grid.add_items({
            (2,2): self.showcase_widgets[2],
            
        })
    def add_to_layout(self):
        self.do_fps_test = True
        #self.draw_cursor = False
        #self.print_debug_fps = True
        self.fps = 99
        self.test_menu.layout = \
        ui.Grid([Fill(100), Fill(100)], x=3,y=3,
                content={
                    (2,1): self.showcase_widgets[0],
                    #(1,2): self.showcase_widgets[1],
                    (2,3): ui.Button(self.add, "add", [50*fill,33*fill]),
                    }
                )
        self.grid = self.test_menu.layout
    def on_update(self, events=None):
        super().on_update(events)
        #print(self.test_hard_widget.text)
ts = TestGrid()
ts.run()