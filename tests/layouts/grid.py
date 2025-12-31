import nevu_ui as ui
import pygame
from basic import NevuTest
import sys
pygame.init()
class TestGrid(NevuTest):
    def add(self):
        self.grid.add_items({
            (2,2):self.showcase_widgets[2], 
            
        })
        #self.grid.items[-1].primary_draw = lambda: None
        #self.grid.items[-1].secondary_draw = lambda: None
        #self.grid.items[-1].primary_update = lambda *args, **kwargs: None
        
    def add_to_layout(self):
        self.a = 0
        self.b = 0
        #self.do_fps_test = True
        #self.draw_cursor = False
        #self.print_debug_fps = True
        self.fps = 99999999999
        self.test_menu.layout = \
        ui.Grid([ui.Fill(100), ui.Fill(100)], x=3,y=3,
                content={
                    (2,1): self.showcase_widgets[0],
                    #(1,2): self.showcase_widgets[1],
                    (2,3): ui.Button(self.add, "add", [50*ui.fill,33*ui.fill]),
                    }
                )
        self.grid = self.test_menu.layout
        self.grid.skip_add_check = True
    def on_update(self, events=None):
        super().on_update(events)
        
        self.a += 1
        if self.a > 2:
            self.add()
            self.a = 0
            print(f"fps: {ui.time.fps}")
            print(len(self.test_menu.layout.items))
            self.b += 1
        if self.b > 300:
            sys.exit(0)
        #print(self.test_hard_widget.text)
ts = TestGrid()
ts.run()