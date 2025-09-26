import nevu_ui as ui
import pygame
from test_basic import NevuTest
pygame.init()

def printHui():
    print("Hui")
def printHui2():
    print("Hui2")
class TestScrollable(NevuTest):
    def add_to_layout(self):
        self.do_fps_test = True
        self._dirty_mode = False
        self.print_debug_fps = True
        self.fps = 9999999

        a = self.test_inner_layout
        self.test_menu.layout = \
        ui.Scrollable([100*ui.fill, 100*ui.vh],
                content=[
                    (ui.Align.CENTER, ui.Row([100*ui.vw, 20*ui.fill], x=3,
                                             content = {1 :self.test_widget,
                                                        2 :self.test_widget,
                                                        3 :self.test_widget,})),
                    (ui.Align.CENTER, self.test_widget),
                    (ui.Align.CENTER, self.test_hard_widget),
                    (ui.Align.CENTER, self.test_inner_layout),
                    (ui.Align.CENTER, self.test_widget),
                    (ui.Align.CENTER, self.test_widget),
                    (ui.Align.CENTER, self.test_widget),
                    
                ]
                )
        self.scrollable = self.test_menu.layout
        self.scrollable.on_click = printHui
        self.scrollable.items[0].on_click = printHui
        self.scrollable.items[1].on_click = printHui2
        #self.scrollable._test_always_update = True
        print(self.scrollable.get_rect())
        
        assert isinstance(self.scrollable, ui.Scrollable)
    def first_update(self):
        super().first_update()
    def draw_loop(self):
        super().draw_loop()

        #print(self.tooglegroup._content)
        #self.tooglegroup.on_checkbox_toggled_single(self.test_widget)
        #print(self.test_widget.events.content[0])
        #self.scrollable.update(self.window.last_events)
        #print(self.scrollable.items[0].get_rect())
        #print(self.scrollable._hover_state)
        #pygame.draw.rect(self.window.surface, (0,0,0), self.scrollable.scroll_bar_y.get_rect(), 5)
        #print(self.scrollable._csize)
        #print(self.window._crop_height_offset)
        
        #self.scrollable._regenerate_coordinates()

ts = TestScrollable()

ts.run()
