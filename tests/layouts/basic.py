import nevu_ui as ui
import pygame
import pyray as rl
from nevu_ui.core.size.units import *
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

def switch_test(switch, state):
    print("SWitched:", state)
    if state:
        switch.style = ui.Style(colortheme=ui.ColorThemeLibrary.catppuccin_latte, br=999, bw=2)
    else:
        switch.style = ui.Style(colortheme=ui.ColorThemeLibrary.material3_dark, br=999, bw=2)

def create_test_instances():
    
    ui.default_style = ui.default_style(colortheme=ui.StateVariable(ui.ColorThemeLibrary.pastel_rose_light, ui.ColorThemeLibrary.material3_dark, ui.ColorThemeLibrary.pastel_rose_light))
    ui.apply_config("structure_test.yaml", ui.ConfigLoadType.Yaml)
    rl.set_trace_log_level(rl.TraceLogLevel.LOG_WARNING)
    test_window = ui.ConfiguredWindow()
    print(ui.ColorThemeLibrary._names)
    print(ui.get_colortheme("base_theme"))
    print("-"*10)
    print(ui.ColorThemeLibrary.synthwave_dark)
    #print(ui.get_style("zov").colortheme.name)
    #test_window = ui.Window((1600,900), title="Test Window", resize_type=ui.ResizeType.CropToRatio, ratio=ui.NvVector2(16,9), backend=ui.Backend.Pygame)
    widgets_style = ui.default_style(borderradius=(100,50,0,25), borderwidth=5, colortheme=ui.ColorThemeLibrary.github_dark, font_name="tests/vk_font.ttf", font_size=64)
    widgets_style2 = widgets_style(colortheme=ui.StateVariable(ui.ColorThemeLibrary.pastel_rose_light, ui.ColorThemeLibrary.material3_dark, ui.ColorThemeLibrary.pastel_rose_light))
    wstyle3 = widgets_style(gradient=ui.Gradient([(ui.Color.with_alpha(ui.Color.White, 240), 1.2), (ui.Color.with_alpha(ui.Color.Teal, 150), 1)], ui.GradientType.Linear, ui.LinearSide.BottomLeft), borderradius=50)
    test_menu = ui.Menu(test_window,[100*vw, 100*vh],)#widgets_style(borderradius=10,borderwidth=0, bgimage="tests/test3.jpg"))
    test_menu.set_coordinates_relative(50, 50)
    widgets_size = [75*vw, 35*vh]
    widgets_size_small = [75*vw, 15*vh]
    widgets_size_fixed = [300, 100]
    
    widget_kwargs = {"style": widgets_style, "size": widgets_size}
    
    checkbox_group = ui.CheckBoxGroup(single_selection=True)
    checkbox_group.on_single_toggled = checkboxgroup_wrapper
    
    #widgets
    #print(ui.gradient_queue((ui.Color.White, 70), (ui.Color.Red, 30)))
    widget = ui.Button(lambda: None, "some button",style=wstyle3, clickable=True, hoverable=True, size=(50*ui.vw, 20*ui.vh), font_role=ui.PairColorRole.BACKGROUND, single_instance=False)
    switch = ui.components.widgets.Switch(True, on_switch_change=switch_test, size=(10*ui.vw, 35*ui.vh), style=wstyle3(borderradius=250), font_role=ui.PairColorRole.BACKGROUND)
    #widget.animation_manager.add_continuous_animation(ui.animations.EaseInSine(6, [0,0], [0,100], ui.animations.AnimationType.POSITION))
    widget.subtheme_role = ui.SubThemeRole.ERROR
    
    label = ui.Label("Frutiger Aero Label \n(not really)", size=widget_kwargs["size"], style=wstyle3(borderradius=250), font_role=ui.PairColorRole.BACKGROUND, clickable=True)
    input_box = ui.Input(**widget_kwargs, placeholder = "Input!", multiple=True, tooltip = Tooltip(TooltipType.Large("This is INPUT...", "it can: \n1. - store text! 3. - store text! \n2. - store text! 4. - store text!"), widgets_style(font_size=10, borderradius=5)),)
    
    #composable | checkboxgroup example фапута одаброяет
    rect_checkbox_row = ui.Row([90*fill, 35*fill], x = 3, single_instance=False, borders=ui.BorderConfig(name="CheckBoxRow", color=(255,0,0), font=ui.load_font("tests/vk_font.ttf", 20)),
                            content = {
                                1: ui.RectCheckBox(id = "check_box1", size = 35, style = widgets_style(borderradius=17), checkbox_group=checkbox_group), 
                                2.2: ui.RectCheckBox(id = "check_box2", size = 35, style = widgets_style, checkbox_group=checkbox_group),
                                3: ui.RectCheckBox(id = "check_box3", size = 35, style = widgets_style, checkbox_group=checkbox_group)
                            },)
    panel = ui.components.layouts.misc.panel.Panel([90*fill, 35*fill],
        slot = label)
    #rect_checkbox_row.borders = True
    #rect_checkbox_row.border_name = "RectCheckBox Row"
    
    #for item in rect_checkbox_row._template["content"].values():
    #    assert isinstance(item, ui.RectCheckBox)
    #    checkbox_group.add_checkbox(item)
    
    
    element_swither = ui.ElementSwitcher(**widget_kwargs, elements = ["ooo","an apple", "nom nom", "mehhh"], clickable=True)
    progress_bar = ui.ProgressBar(widgets_size, wstyle3(borderradius=widgets_style2.border_radius), value = 50, color_pair_role=ui.PairColorRole.SURFACE_VARIANT, clickable=True)
    
    
    slider_bar = ui.Slider(widgets_size, widgets_style2(align_x = ui.StateVariable(ui.Align.CENTER, ui.Align.RIGHT, ui.Align.LEFT), fontsize=45), start = 0, end = 100, step = 1, current_value = 50, tuple_role = ui.TupleColorRole.INVERSE_PRIMARY, bar_pair_role=ui.PairColorRole.SURFACE_VARIANT, tooltip=Tooltip(TooltipType.Small("Это страшная кнопка"*10), widgets_style2(font_size=10)), single_instance=True)# alt = True)
    #element = element_swither.find("fruit_1")
    showcase_widgets = [widget, switch, label, element_swither, panel, progress_bar, input_box, slider_bar, rect_checkbox_row]
    styles = [widgets_style, widgets_style2, wstyle3]
    return test_window, test_menu, showcase_widgets, styles#, showcase_layouts


class NevuTest(ui.Manager):
    def __init__(self):
        self.window, self.test_menu, self.showcase_widgets, self.styles = create_test_instances()
        
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
        #if self.draw_cursor:
            #surf = pygame.Surface((10,10))
            #pygame.draw.circle(surf, (255,0,0), (0,0), 5)
           # self.window._display.blit(surf, pygame.rect.Rect(*pygame.mouse.get_pos(), 10, 10))

#to create test:
#   1. Override add_to_layout
#   2. Run it via manager.run()
#   3. Enjoy :)

