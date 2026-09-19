import pyray as rl

import nevu_ui as ui
from nevu_ui.core.size.units import auto

rl.set_trace_log_level(rl.TraceLogLevel.LOG_ERROR)
window = ui.Window((300, 300), backend = ui.Backend.RayLib)

menu = ui.Menu(window, (300, 300),
    main_layout = ui.Grid(
        {
            (1, 1): ui.Label("Hello!", size = auto(), draw_borders = False, draw_content = False, style = ui.Style(font_name = ui.FontLibrary.InterBold))
        }, x=1, y=1, size = ui.fill_all
    )
)

app = ui.Manager(
    window = window,
    menu = [menu],
)
app.run()
