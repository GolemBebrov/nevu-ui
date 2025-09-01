import nevu_ui as ui
import pygame

def create_test_instances():
    test_window = ui.window.Window((300,300), "Test Window")
    test_widget = ui.Button(lambda: print("pressed"), "Press me", (100, 100), ui.default_style(),single_instance=False)
    test_hard_widget = ui.Input([70*ui.fill,20*ui.fill],ui.default_style(borderradius=30),"InputTest",multiple=True,single_instance=True)
    test_inner_layout = ui.Grid([50*ui.fill, 35*ui.fill], x=3,y=3, single_instance=True, 
                                    content={
                                            (1,1): ui.Button(lambda: print("Button Topleft"), "Test Chamber", [50*ui.fill,30*ui.fill],words_indent=True, ),
                                            (2,2): ui.Button(lambda: print("Button Center"), "Test Chamber", [50*ui.fill,30*ui.fill],words_indent=True, ),
                                            (3,3): ui.Button(lambda: print("Button BottomRight"), "Test Chamber", [50*ui.fill,30*ui.fill],words_indent=True, ),
                                            (1,3): ui.Button(lambda: print("Button BottomLeft"), "Test Chamber", [50*ui.fill,30*ui.fill],words_indent=True, ),
                                            (3,1): ui.Button(lambda: print("Button TopRight"), "Test Chamber", [50*ui.fill,30*ui.fill],words_indent=True, ),
                                        }
                            )
    test_inner_layout.border_name = "Inner Layout"
    test_inner_layout.borders = True
    test_menu = ui.Menu(test_window,[100*ui.vw, 100*ui.vh],ui.default_style)
    return test_window, test_widget, test_hard_widget, test_inner_layout, test_menu

class NevuTest(ui.Manager):
    def __init__(self):
        self.window, self.test_widget, self.test_hard_widget, self.test_inner_layout, self.test_menu = create_test_instances()
        super().__init__(self.window)
        self.add_to_layout()
        self.do_fps_test = False
    def add_to_layout(self):
        pass
        #Override in test
    def draw_loop(self):
        super().draw_loop()
        self.test_menu.draw()
    def _a_system_draw_loop(self):
        super()._a_system_draw_loop()
        if hasattr(self.test_hard_widget, "size"):
            pygame.draw.rect(self.window.surface, (0,0,0), self.test_hard_widget.get_rect(), 2)
        if hasattr(self.test_widget, "size"):
            pygame.draw.rect(self.window.surface, (0,0,0), self.test_widget.get_rect(), 2)
    def update_loop(self, events = None):
        super().update_loop(events)
        self.test_menu.update()
        if self.do_fps_test:
            print(f"Debug: FPS-{ui.time.fps}")

#to create test:
#   1. Override add_to_layout
#   2. Run it via manager.run()