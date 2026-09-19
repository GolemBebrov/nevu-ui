import pyray as rl

import nevu_ui as ui
from nevu_ui.core.classes import TooltipType
from nevu_ui.core.size.units import *
from nevu_ui.overlay.tooltip import Tooltip
from nevu_ui.rendering.canvas import Canvas


def checkboxgroup_wrapper(checkbox: ui.RectCheckBox | None):
    if checkbox is None: print("You discontinued the selection"); return
    assert checkbox.id
    if "1" in checkbox.id:
        print("selected first checkbox")
    if "2" in checkbox.id:
        print("selected second checkbox")
    if "3" in checkbox.id:
        print("selected third checkbox")

def switch_test(switch, state):
    print("Changed Switch state to", state)
    if state:
        switch.style = ui.Style(colortheme=ui.ColorThemeLibrary.catppuccin_latte, br=999, bw=2)
    else:
        switch.style = ui.Style(colortheme=ui.ColorThemeLibrary.material3_dark, br=999, bw=2)

def create_test_instances():
    ui.apply_config("structure_test.yaml", ui.ConfigLoadType.Yaml)
    rl.set_trace_log_level(rl.TraceLogLevel.LOG_WARNING)

    #test_window = ui.ConfiguredWindow()
    test_window = ui.Window((1600, 900), title = "Test Window", backend = ui.Backend.RayLib)

    widgets_style = ui.Style(
        border_radius = (100, 50, 0, 25),
        border_width = 5,
        colortheme = ui.ColorThemeLibrary.github_dark,
        font_name = ui.FontLibrary.InterRegular,
        font_size = 64
    )
    widgets_style2 = widgets_style(
        colortheme = ui.StateVariable(
            ui.ColorThemeLibrary.catppuccin_mocha,
            ui.ColorThemeLibrary.material3_dark,
            ui.ColorThemeLibrary.github_dark
        )
    )
    widget_style3 = widgets_style(
        gradient = ui.Gradient(
            [
                (ui.Color.with_alpha(ui.Color.White, 240), 1.2),
                (ui.Color.with_alpha(ui.Color.Teal, 150), 1)
            ],
            ui.GradientType.Linear,
            ui.LinearSide.BottomLeft
        ),
        border_radius = 50)

    test_menu = ui.Menu(test_window, (100%vw, 100%vh), widgets_style(border_radius = 10, border_width = 0, bg_image = "tests/test3.jpg"))
    widgets_size = (75%vw, 35%vh)

    widget_kwargs = {"style": widgets_style, "size": widgets_size}

    checkbox_group = ui.CheckBoxGroup(single_selection=True)
    checkbox_group.on_single_toggled = checkboxgroup_wrapper

    #widgets
    widget = ui.Button(
        lambda: None,
        "some button",
        style = widget_style3(align_x = ui.Align.LEFT, align_y = ui.Align.TOP),
        size = (50*ui.vw, 20*ui.vh),
        font_role = ui.PairColorRole.BACKGROUND,
        single_instance = False,
        callbacks = {
            ui.BindType.Click: [lambda *args: print("Click1!!", args), lambda *args: print("Click2!!", args)],
            ui.BindType.Resize: lambda *args: print("Resized!!!", args)
        }
    )
    widget.callbacks.bind(ui.BindType.Click, lambda *args: print("Click3!!", args), add_to_end = False, weak = False)
    widget.subtheme_role = ui.SubThemeRole.ERROR

    switch = ui.Switch(True, on_switch_change = switch_test, size = (10*ui.vw, 35*ui.vh), style = widget_style3(border_radius = 250), font_role = ui.PairColorRole.BACKGROUND)

    canvas = (Canvas()
        .draw_line((0, 0), ui.fill_all, 10)
        .draw_line((100%ui.fill, 0), (0, 100%ui.fill), 10)
        .draw_rect((0, 0), ui.fill_perc(50), style = ui.Style(colortheme=ui.ColorThemeLibrary.material3_green))
    )

    label = ui.Label("Frutiger Aero Label \n(not really)", size=widget_kwargs["size"], canvas = canvas, style=widget_style3(borderradius=250), font_role=ui.PairColorRole.BACKGROUND, clickable=True)
    input_box = ui.Input(**widget_kwargs, placeholder = "Input!", multi_line=True, tooltip = Tooltip(TooltipType.BigCustom(ui.NvVector2(0.2, 0.4),"This is INPUT...", "it can: \n1. - store text! 3. - store text! \n2. - store text! 4. - store text!"), widgets_style(font_size=10, borderradius=(0,35,35,35))))

    #Faputa Approved
    rect_checkbox_row = ui.Row(
        size = (90*fill, 35*fill),
        x = 3,
        single_instance = False,
        content = {
            1: ui.RectCheckBox(id = "check_box1", size = 35, style = widgets_style(borderradius=17), checkbox_group=checkbox_group),
            2.2: ui.RectCheckBox(id = "check_box2", size = 35, style = widgets_style, checkbox_group=checkbox_group),
            3: ui.RectCheckBox(id = "check_box3", size = 35, style = widgets_style, checkbox_group=checkbox_group)
        },
        bg_widget = ui.Widget(ui.fill_all, z = 1, draw_content = False)
    )

    panel = ui.ScrollableRow([label], (90*fill, 35*fill), bg_widget = ui.Widget((1, 1), bg_variant=True))

    btn_list = []
    for i in range(20):
        btn = ui.Button(lambda: print(i), f"Button {i}", (120, 50))
        btn_list.append(btn)

    my_flex = ui.FlexLayout(
        *btn_list,
        direction=ui.FlexDirection.Column,
        wrap=True,
        justify_content=ui.FlexJustify.SpaceEvenly,
        gap=15,
    )

    element_swither = ui.ElementSwitcher(
        **widget_kwargs,
        elements = ["ooo","an apple", "nom nom", "mehhh"],
        clickable = True
    )

    progress_bar = ui.ProgressBar(
        widgets_size,
        widget_style3(border_radius = widgets_style2.border_radius),
        current = 50,
        role = ui.PairColorRole.SURFACE_VARIANT,
        clickable = True
    )

    slider_bar = ui.Slider(
        (300, 300),
        widgets_style2(
            bg_image = "tests/test1.png",
            border_radius = 999,
            bw = 10,
            align_x = ui.StateVariable(ui.Align.CENTER, ui.Align.RIGHT, ui.Align.LEFT),
            font_size = 45
        ),
        start_value = 0,
        end_value = 100,
        step = 1,
        current_value = 50,
        filled_rect_role = ui.PairColorRole.SURFACE_VARIANT,
        tooltip = Tooltip(TooltipType.Small("Это страшная кнопка"*10), widgets_style2(font_size=10)),
        single_instance=True
    )

    showcase_widgets = [widget, switch, label, element_swither, panel, progress_bar, input_box, slider_bar, rect_checkbox_row, my_flex]
    styles = [widgets_style, widgets_style2, widget_style3]
    return test_window, test_menu, showcase_widgets, styles#, showcase_layouts


class NevuTest(ui.Manager):
    def __init__(self):
        self.window, self.test_menu, self.showcase_widgets, self.styles = create_test_instances()

        super().__init__(self.window, [self.test_menu])
        self.do_fps_test = False
        self._dirty_mode = False
        self.print_debug_fps = False
        self.max_fps = -1
        self.min_fps = 999999
        self.frame = 0
        self.start_of_check = 200
        self.middle_list = []
        self.middle_items = 5
        self.test_menu.main_layout = self.create_layout()

    def create_layout(self): ...
    def on_update(self):
        if self.do_fps_test:
            print(f"Debug: FPS-{ui.time.fps}")
        if self.print_debug_fps:
            if self.frame > self.start_of_check:
                if self.frame < self.start_of_check + self.middle_items:
                    self.middle_list.append(ui.time.fps)
                else:
                    self.middle_list.pop(0)
                    self.middle_list.append(ui.time.fps)
                self.max_fps = max(self.max_fps, ui.time.fps)
                self.min_fps = min(self.min_fps, ui.time.fps)
            print(f'frame: {self.frame} max fps:{self.max_fps}')
            print(f'frame: {self.frame} min fps:{self.min_fps}')
            if len(self.middle_list) != 0:
                print(f'frame: {self.frame} avg fps:{int(sum(self.middle_list)/len(self.middle_list))}')
            self.frame += 1

#to create test:
#   1. Override create_layout
#   2. Run it via manager.run()
#   3. Enjoy :)
