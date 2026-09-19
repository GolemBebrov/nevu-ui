
import nevu_ui as ui
import pyray as rl

rl.set_trace_log_level(rl.TraceLogLevel.LOG_ERROR)

class App(ui.Manager):
    def __init__(self):
        window = ui.Window(
            (1600, 900), backend=ui.Backend.RayLib
        )
        style = ui.Style(
            br=12, bw=1, colortheme=ui.ColorThemeLibrary.material3_orange, font_size=28, font_name = "tests/vk_font.ttf"
        )
        ui.nevu_object_globals.modify(size=(10 % ui.vw, 5 % ui.vh), style=style)
        c = 0
        ov_label = ui.Label(f"Equpped: None", style=style(align_x=ui.Align.LEFT),
            size=(15 % ui.vw, 5 % ui.vh), single_instance=True, draw_borders=False, draw_content = False)
        def set_ov_value(text):
            ov_label.text = f"Equpped: {text}"

        ov_lay = ui.FlexLayout(ov_label, single_instance=True)
        ov_lay.coordinates = ui.NvVector2(30, 50)
        def delete_item(item):
            scrollable.kill_item(item)
        def add_label():
            nonlocal c
            c += 1
            label = ui.Label(f"Item: {c}", (7% ui.vw, 5 % ui.vh), subtheme_role=ui.SubThemeRole.PRIMARY, glassy = True, font_role=ui.PairColorRole.SURFACE)

            row = ui.FlexLayout(single_instance = True)
            b1 = ui.Button(lambda item = row: delete_item(row), "rm -rf /*", subtheme_role=ui.SubThemeRole.ERROR)
            b2 = ui.Button(lambda c = c: set_ov_value(c), "Equip", subtheme_role=ui.SubThemeRole.TERTIARY)
            row.add_items([
                label, b1, b2
            ])
            scrollable.add_item(row)


        scrollable = ui.ScrollableColumn([ui.FlexLayout(ui.Button(add_label, "add"))], (50%ui.vw, 100%ui.fill), basic_alignment=ui.Align.CENTER, single_instance=True)
        menu = ui.Menu(
            window,
            ui.fill_all,
            style=style,
            main_layout=scrollable
        )
        scrollable.add_floating_item(ov_lay)
        super().__init__(window, menu)


if __name__ == "__main__":
    App().run()
