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
            ui.StackRow(spacing = 40,single_instance=False, content = 
            [(ui.Align.CENTER, self.showcase_widgets[0]),
             (ui.Align.CENTER, self.showcase_widgets[1]),
             (ui.Align.CENTER, self.showcase_widgets[0]),]
            )
        print("STARTED APPENDING", self.appending_layout_h._lazy_kwargs)
        #i OBVIOSLY HATE NIGG...
        #upd: banned
        #upd2: banned ban
        #upd3: cancelled ban of ban
        #upd4: banned
        self.test_menu.layout = \
        ui.Grid([ui.Fill(100), ui.Fill(100)], x=3,y=3,
                content={
                    (2,2): self.appending_layout_h
                    }
                )
        self.grid = self.test_menu.layout
    def on_update(self, events=None):
        super().on_update(events)
        #print(self.test_hard_widget.text)
        #print(self.test_hard_dick.__dict__)
ts = TestAppending()
ts.run()