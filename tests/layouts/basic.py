import nevu_ui as ui
import pygame

def checkboxgroup_wrapper(checkbox: ui.RectCheckBox | None):
    if checkbox is None: print("Вы прекратили выбор"); return
    assert checkbox.id
    if "1" in checkbox.id:
        print("Выбран первый чекбокс")
    if "2" in checkbox.id:
        print("Выбран второй чекбокс")
    if "3" in checkbox.id:
        print("Выбран третий чекбокс")

lorem_ipsum = "Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat. Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur. Excepteur sint occaecat cupidatat non proident, sunt in culpa qui officia deserunt mollit anim id est laborum."

def create_test_instances():
    ui.default_style = ui.default_style(colortheme=ui.ColorThemeLibrary.material3_dark_color_theme)
    test_window = ui.Window((300,300), "Test Window", resize_type=ui.ResizeType.CropToRatio, ratio=ui.NvVector2(1,1))
    test_menu = ui.Menu(test_window,[100*ui.vw, 100*ui.vh],ui.default_style(borderradius=10))
    
    widgets_style = ui.default_style(borderradius=10)
    
    widgets_size = [75*ui.vw, 35*ui.vh]
    
    widget_kwargs = {"style": widgets_style, "size": widgets_size}
    
    checkbox_group = ui.CheckBoxGroup(single_select=True)
    checkbox_group.on_checkbox_toggled_single = checkboxgroup_wrapper
    
    #widgets
    widget = ui.Widget(**widget_kwargs)
    label = ui.Label(lorem_ipsum, **widget_kwargs)
    input_box = ui.Input(**widget_kwargs, placeholder = "Input!")
    
    #composable | checkboxgroup example
    rect_checkbox_row = ui.Row([90*ui.fill, 35*ui.fill], x = 3, content = 
                               {
                                   1: ui.RectCheckBox(id = "check_box1", size = 35, style = widgets_style), #type: ignore
                                   2: ui.RectCheckBox(id = "check_box2", size = 35, style = widgets_style), #type: ignore
                                   3: ui.RectCheckBox(id = "check_box3", size = 35, style = widgets_style), #type: ignore
                               })
    
    for item in rect_checkbox_row._lazy_kwargs["content"].values():
        assert isinstance(item, ui.RectCheckBox)
        checkbox_group.add_checkbox(item)
    
    
    element_swither = ui.ElementSwitcher(**widget_kwargs, elements = ["Apple", "Banana", "Cherry", "Date", "Banana"])
    
    showcase_widgets = [widget, label, input_box, rect_checkbox_row, element_swither]
    
    return test_window, test_menu, showcase_widgets#, showcase_layouts

class NevuTest(ui.Manager):
    def __init__(self):
        self.window, self.test_menu, self.showcase_widgets = create_test_instances()
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