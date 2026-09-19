import gc
import nevu_ui as ui
import pyray as rl

rl.set_trace_log_level(rl.TraceLogLevel.LOG_ERROR)

# Made partially with ai

layouts = [
    (ui.LayoutType, (1, 1)),
    (ui.Grid, (1, 1)),
    (ui.ScrollableColumn, (1, 1)),
    (ui.ScrollableRow, (1, 1)),
    (ui.StackColumn, (1, 1)),
    (ui.StackRow, (1, 1)),
]

widgets = [
    (ui.Widget, None),
    (ui.Slider, None),
    (ui.ProgressBar, None),
    (ui.Label, ("test",)),
    (ui.Button, (lambda: None, "test",)),
    (ui.Input, None),
    (ui.RectCheckBox, None),
    
]
def check_for_leaks(class_type):
    gc.collect()
    leftover_objects = [obj for obj in gc.get_objects() if isinstance(obj, class_type)]
    
    assert len(leftover_objects) == 0, (
        f"Утечка памяти! Найдено {len(leftover_objects)} уцелевших "
        f"объектов класса {class_type.__name__} после kill()."
    )

def main_layout(layout_type, size):
    menu = ui.Menu(window, (1, 1))
    if layout_type in (ui.StackColumn, ui.StackRow):
        layout = layout_type()
    else:
        layout = layout_type(size)
    menu.layout = layout

    for _ in range(50):
        menu.update()
        menu.draw()

    layout.kill()
    del layout
    
    check_for_leaks(layout_type)

def main_widget(widget_type, args):
    menu = ui.Menu(window, (1, 1))
    layout = ui.StackColumn()
    widget = widget_type(*args)
    layout.add_item(widget)
    
    for _ in range(50):
        menu.update()
        menu.draw()
    
    widget.kill()
    del widget
    layout.kill()
    del layout
    
    check_for_leaks(widget_type)
    check_for_leaks(ui.StackColumn)

if __name__ == "__main__":
    window = ui.Window((1, 1), backend=ui.Backend.RayLib)
    print("\n=== Starting automated test... ===")
    
    try:
        for layout_type, args in layouts:
            print(f"Testing layout: {layout_type.__name__}...", end=" ", flush=True)
            main_layout(layout_type, args)
            print("OK")
            
        ui.nevu_object_globals.modify(size=(1, 1), single_instance=True)
        
        for widget_type, args in widgets:
            if args is None:
                args = tuple()
            print(f"Testing widget: {widget_type.__name__}...", end=" ", flush=True)
            main_widget(widget_type, args)
            print("OK")
            
        print("\n==== All tests passed successfully! No leaks detected. ====\n")
        
    except AssertionError as e:
        print("\n\n!!!! TEST FAILED !!!!")
        print(e)