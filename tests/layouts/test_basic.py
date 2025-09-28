import nevu_ui as ui
import pygame

def create_test_instances():
    ui.default_style = ui.default_style(colortheme=ui.ColorThemeLibrary.gruvbox_light_color_theme)
    test_window = ui.window.Window((300,300), "Test Window", resize_type=ui.ResizeType.CropToRatio, ratio=ui.NvVector2(1,1))
    test_widget = ui.RectCheckBox(50 ,ui.default_style(borderradius=999, borderwidth=0 ),single_instance=False, active_rect_factor=0.9, alt=True)#ui.Button(lambda: print("pressed"), "Nevu UI!", (100, 100), ui.default_style(borderwidth=10, borderradius = 15),single_instance=False)
    tooglegroup = ui.CheckBoxGroup([test_widget], True)
    tooglegroup.on_checkbox_toggled_single = lambda checkbox: print(checkbox.toogled or checkbox is None)
    tooglegroup.on_checkbox_toggled = lambda checkbox: print(checkbox)
    
    test_widget.active_rect_factor = 0.1
    test_widget.subtheme_role = ui.SubThemeRole.ERROR
    super_duper_test_button = lambda print_text, text: ui.Button(lambda: print(print_text), text, [50*ui.fill,30*ui.fill], style = ui.default_style(borderradius=5, colortheme=ui.ColorThemeLibrary.synthwave_dark_color_theme), alt = False)
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
        self.do_fps_test = False
        self._dirty_mode = False
        self.print_debug_fps = False
        self.draw_cursor = True
        self.max_fps = -1
        self.min_fps = 999999
        self.frame = 0
        self.start_of_check = 200
        self.middle_list = []
        self.middle_items = 5
        self.add_to_layout()
    def add_to_layout(self):
        pass
        #Override in test
    def draw_loop(self):
        super().draw_loop()
        self.test_menu.draw()
    def update_loop(self, events = None):
        super().update_loop(events)
        self.test_menu.update()
        if self.do_fps_test:
            print(f"Debug: FPS-{ui.time.fps}")
        if self.print_debug_fps:
            if self.frame > self.start_of_check:
                if self.frame < self.start_of_check + self.middle_items:
                    self.middle_list.append(ui.time.fps)
                else:
                    self.middle_list.pop(0)
                    self.middle_list.append(ui.time.fps)
                if ui.time.fps > self.max_fps: self.max_fps = ui.time.fps
                if ui.time.fps < self.min_fps: self.min_fps = ui.time.fps
            print(f'frame: {self.frame} max fps:{self.max_fps}')
            print(f'frame: {self.frame} min fps:{self.min_fps}')
            if len(self.middle_list) != 0: 
                print(f'frame: {self.frame} avg fps:{int(sum(self.middle_list)/len(self.middle_list))}')
            self.frame += 1
    def _after_draw_loop(self):
        super()._after_draw_loop()
        if self.draw_cursor:
            pygame.draw.circle(self.window.surface, (255,0,0), ui.mouse.pos, 5)

#to create test:
#   1. Override add_to_layout
#   2. Run it via manager.run()