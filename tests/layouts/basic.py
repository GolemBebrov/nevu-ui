import nevu_ui as ui
import pygame
from nevu_ui.size.units import *
from nevu_ui.overlay.tooltip import _SmallTooltip, Tooltip
from nevu_ui.core.classes import TooltipType
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
    ui.default_style = ui.default_style(colortheme=ui.StateVariable(ui.ColorThemeLibrary.pastel_rose_light, ui.ColorThemeLibrary.material3_dark, ui.ColorThemeLibrary.pastel_rose_light))
    ui.apply_config("structure_test.json")
    #test_window = ui.ConfiguredWindow()
    test_window = ui.Window((1600,900), title="Test Window", resize_type=ui.ResizeType.CropToRatio, ratio=ui.NvVector2(16,9), backend=ui.Backend.RayLib)
    widgets_style = ui.default_style(borderradius=(100,50,0,25), borderwidth=5, colortheme=ui.ColorThemeLibrary.github_dark, fontname="tests/vk_font.ttf")
    widgets_style2 = widgets_style(colortheme=ui.StateVariable(ui.ColorThemeLibrary.pastel_rose_light, ui.ColorThemeLibrary.material3_dark, ui.ColorThemeLibrary.pastel_rose_light))
    test_menu = ui.Menu(test_window,[100*vw, 100*vh],widgets_style(borderradius=10,borderwidth=0))
    test_menu.set_coordinates_relative(50, 50)
    widgets_size = [75*vw, 35*vh]
    widgets_size_small = [75*vw, 15*vh]
    widgets_size_fixed = [300, 100]
    
    widget_kwargs = {"style": widgets_style, "size": widgets_size}
    
    checkbox_group = ui.CheckBoxGroup(single_selection=True)
    checkbox_group.on_single_toggled = checkboxgroup_wrapper
    
    #widgets
    widget = ui.Widget(style=widgets_style, clickable=True, size=widgets_size, )#single_instance=True)
    #widget.animation_manager.add_continuous_animation(ui.animations.EaseInSine(6, [0,0], [0,100], ui.animations.AnimationType.POSITION))
    widget.subtheme_role = ui.SubThemeRole.ERROR
    
    label = ui.Label(lorem_ipsum, size=widget_kwargs["size"], style=ui.Style(fontname="tests/vk_font.ttf"))
    input_box = ui.Input(**widget_kwargs, placeholder = "Input!", multiple=True, tooltip = Tooltip(TooltipType.Medium("Выбор персонажа...", "Выберите персонажа \n1. - Фапута 3. - Наначи \n2. - Бондрюд 4. - Декстер морган"), widgets_style(text_align_x=ui.Align.LEFT)))
    
    #composable | checkboxgroup example
    rect_checkbox_row = ui.Row([90*fill, 35*fill], x = 3, single_instance=True, borders=True, border_name="RectCheckBox Row", border_color=(255,0,0),
                            content = {
                                1: ui.RectCheckBox(id = "check_box1", size = 35, style = widgets_style(borderradius=17)), 
                                2.2: ui.RectCheckBox(id = "check_box2", size = 35, style = widgets_style),
                                3: ui.RectCheckBox(id = "check_box3", size = 35, style = widgets_style),
                            })
    #rect_checkbox_row.borders = True
    #rect_checkbox_row.border_name = "RectCheckBox Row"
    
    for item in rect_checkbox_row._template["content"].values():
        assert isinstance(item, ui.RectCheckBox)
        checkbox_group.add_checkbox(item)
    
    
    element_swither = ui.ElementSwitcher(**widget_kwargs, elements = ["ooo","an apple", "nom nom", "mehhh"])
    progress_bar = ui.ProgressBar(**widget_kwargs, value = 50)
    
    
    slider_bar = ui.Slider(widgets_size, widgets_style2(text_align_x = ui.StateVariable(ui.Align.CENTER, ui.Align.RIGHT, ui.Align.LEFT), fontsize=45), start = 0, end = 100, step = 1, current_value = 50, tuple_role = ui.TupleColorRole.INVERSE_PRIMARY, bar_pair_role=ui.PairColorRole.SURFACE_VARIANT, tooltip=Tooltip(TooltipType.Small("Это страшная кнопка"*10), widgets_style2), single_instance=True)# alt = True)
    #element = element_swither.find("fruit_1")
    showcase_widgets = [widget, label, progress_bar, slider_bar]
    
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
    def on_draw(self):
        super().on_draw()
        self.test_menu.draw()
    def on_update(self, events = None):
        self.test_menu.update()
        if self.do_fps_test:
            #print(f"Debug: FPS-{ui.time.fps}")
            pass
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
        super().on_update(events)
    def _after_draw(self):
        super()._after_draw()
        #if self.draw_cursor:
            #surf = pygame.Surface((10,10))
            #pygame.draw.circle(surf, (255,0,0), (0,0), 5)
           # self.window._display.blit(surf, pygame.rect.Rect(*pygame.mouse.get_pos(), 10, 10))

#to create test:
#   1. Override add_to_layout
#   2. Run it via manager.run()