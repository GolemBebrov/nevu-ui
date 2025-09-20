import nevu_ui as ui
import pygame

def create_test_instances():
    ui.default_style = ui.default_style(colortheme=ui.gruvbox_light_color_theme)
    test_window = ui.window.Window((300,300), "Test Window", resize_type=ui.ResizeType.CropToRatio, ratio=ui.Vector2(1,1))
    test_widget = ui.RectCheckBox(50 ,ui.default_style(borderradius=999, borderwidth=0 ),single_instance=False, active_rect_factor=0.9, alt=True)#ui.Button(lambda: print("pressed"), "Nevu UI!", (100, 100), ui.default_style(borderwidth=10, borderradius = 15),single_instance=False)
    tooglegroup = ui.CheckBoxGroup([test_widget], True)
    tooglegroup.on_checkbox_toggled_single = lambda checkbox: print(checkbox.toogled or checkbox is None)
    tooglegroup.on_checkbox_toggled = lambda checkbox: print(checkbox)
    
    test_widget.active_rect_factor = 0.1
    test_widget.subtheme_role = ui.SubThemeRole.ERROR
    super_duper_test_button = lambda print_text, text: ui.Button(lambda: print(print_text), text, [50*ui.fill,30*ui.fill], style = ui.default_style(borderradius=5, colortheme=ui.synthwave_dark_color_theme), alt = False)
    test_hard_widget = ui.Input([70*ui.vw, 20*ui.vh],ui.default_style(borderradius=30),"InputTest",multiple=True,single_instance=True, alt=True)

    test_inner_layout = ui.Grid([50*ui.vw, 35*ui.vh], x=3,y=3, single_instance=True, 
                                    content={
                                        (1,1): super_duper_test_button("Button Topleft", "Test Chamber"),
                                        (2,2): super_duper_test_button("Button Center", "Test Chamber"),
                                        (3,3): super_duper_test_button("Button BottomRight", "Test Chamber"),
                                        (1,3): super_duper_test_button("Button BottomLeft", "Test Chamber"),
                                        (3,1): super_duper_test_button("Button TopRight", "Test Chamber"),
                                    }
                            )
    test_inner_layout.border_name = "Inner Layout"
    test_inner_layout.borders = True
    test_menu = ui.Menu(test_window,[100*ui.vw, 100*ui.vh],ui.default_style(borderradius=10))
    return test_window, test_widget, test_hard_widget, test_inner_layout, test_menu, tooglegroup

class NevuTest(ui.Manager):
    def __init__(self):
        self.window, self.test_widget, self.test_hard_widget, self.test_inner_layout, self.test_menu, self.tooglegroup = create_test_instances()
        super().__init__(self.window)
        self.add_to_layout()
        self.do_fps_test = False
        self._dirty_mode = False
    def add_to_layout(self):
        pass
        #Override in test
    def draw_loop(self):
        super().draw_loop()
        self.test_menu.draw()
    def _a_system_draw_loop(self):
        super()._a_system_draw_loop()
        #if hasattr(self.test_hard_widget, "size"):
            #pygame.draw.rect(self.window.surface, (0,0,0), self.test_hard_widget.get_rect(), 2)
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