import nevu_ui as ui
import pygame
from basic import NevuTest
import sys
pygame.init()
class TestGrid(NevuTest):
    def add(self):
        self.grid.add_items({
            (2,2):self.showcase_widgets[0], 
            
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
        ui.Grid([ui.FillH(100), ui.FillH(100)], x=6,y=6,
                content={
                    (2,6): self.showcase_widgets[0],
                    (1,6): self.showcase_widgets[0],
                    (3,6): self.showcase_widgets[0],
                    (4,6): self.showcase_widgets[0],
                    (5,6): self.showcase_widgets[0],
                    (6,6): self.showcase_widgets[0],
                    
                    (2,5): self.showcase_widgets[0],
                    (2,4): self.showcase_widgets[0],
                    
                    (5,5): self.showcase_widgets[0],
                    (5,4): self.showcase_widgets[0],
                    (3.5,3): ui.Label("GEOMETRIA", size=[40*ui.vw,100*ui.gc], style=ui.Style(fontname="tests/vk_font.ttf", gradient=ui.Gradient([ui.Color.REBECCAPURPLE, ui.Color.BLACK], type=ui.GradientType.Linear, direction=ui.LinearSide.Left),fontsize=50)),
                    #(1,2): self.showcase_widgets[1],
                    }
                )
        self.grid = self.test_menu.layout
    def on_update(self, events=None):
        super().on_update(events)
        #print(self.test_hard_widget.text)
ts = TestGrid()
ts.run()