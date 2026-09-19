import gc
import inspect
from time import perf_counter

import pygame
import pyray as rl

import nevu_ui as ui

pygame.init()

rl.set_trace_log_level(rl.TraceLogLevel.LOG_ERROR)

deep_research = True
include_startup_time = False
cache = False
time = 50
size = (10, 10)
backend = ui.Backend.RayLib

layouts = [
    (ui.LayoutType, size),
    (ui.Grid, size),
    (ui.Row, size),
    (ui.Column, size),
    (ui.ScrollableColumn, size),
    (ui.ScrollableRow, size),
    (ui.StackColumn, size),
    (ui.StackRow, size),
    (ui.FlexLayout, size)
]

widgets = [
    (ui.Widget, None),
    (ui.Slider, None),
    (ui.ProgressBar, None),
    (ui.Label, ("test",)),
    (ui.Button, (lambda: None, "test",)),
    (ui.Input, None),
    (ui.RectCheckBox, None),
    (ui.Switch, None),
]

def dump_referrers(target, name="target"):
    print(f"\n[LEAK CHECK] {type(target).__name__}, id={id(target)}:")
    print("-"*50)

    referrers = gc.get_referrers(target)
    if len(referrers) == 0:
        print("[V] No leaks")
    for i, ref in enumerate(referrers):
        if ref is locals():
            continue
        if inspect.isframe(ref):
            print(f"  [{i}] Frame: {ref.f_code.co_name} в {ref.f_code.co_filename}:{ref.f_lineno}")
            continue

        if isinstance(ref, dict):
            owners = [o for o in gc.get_referrers(ref) if getattr(o, "__dict__", None) is ref]
            if owners:
                owner = owners[0]
                key_name = [k for k, v in ref.items() if v is target]
                print(f"  [{i}] Attr {key_name} inside: {owner} ({type(owner).__name__})")
                continue
            else:
                print(f"  [{i}] Dict: keys = {list(ref.keys())[:5]}")
                continue

        if isinstance(ref, (list, tuple, set)):
            owners = [o for o in gc.get_referrers(ref) if not inspect.isframe(o)]
            print(f"  [{i}] Collection {type(ref).__name__} (len={len(ref)}). Owners: {owners[:2]}")
            continue

        if inspect.ismethod(ref):
            print(f"  [{i}] Bound Method: {ref.__name__} of object {ref.__self__}")
            continue

        print(f"  [{i}] Object {type(ref).__name__}: {repr(ref)[:100]}")
    print("-"*50 + "\n")

def main_layout(layout_type, size, custom_menu = None):
    menu = custom_menu or ui.Menu(window, size)
    if layout_type is ui.StackColumn or layout_type is ui.StackRow or layout_type is ui.FlexLayout:
        layout = layout_type()
    else:
        layout = layout_type(size = size)
    menu.layout = layout

    for _ in range(time):
        menu.update()
        menu.draw()

    if not custom_menu:
        menu.kill()
    else:
        layout.kill()

    menu._layout = None

    if deep_research:
        dump_referrers(layout, name=f"layout ({layout_type.__name__})")
        dump_referrers(menu, name="menu")

def main_widget(widget_type, args, custom_menu = None):
    menu = custom_menu or ui.Menu(window, size)
    layout = ui.StackColumn()
    widget = widget_type(*args)
    layout.add_item(widget)
    menu.layout = layout

    for _ in range(time):
        menu.update()
        menu.draw()

    if not custom_menu:
        menu.kill()
    else:
        layout.kill()

    menu._layout = None

    if deep_research:
        dump_referrers(layout, name="StackColumn in main_widget")
        dump_referrers(widget, name=f"widget ({widget_type.__name__})")

if __name__ == "__main__":
    if include_startup_time:
        t1 = perf_counter()
    window = ui.Window(size, backend=backend)
    if not include_startup_time:
        t1 = perf_counter()

    ui.nevu_object_globals.modify(size = size, single_instance=True)
    if cache:
        cached_menu = ui.Menu(window, size)
    else:
        cached_menu = None
    print("\n=== Starting test... ===")
    for layout_type, args in layouts:
        print(f"\n--> V test {layout_type.__name__}")
        main_layout(layout_type, args, cached_menu)
        print(f"--> X ended {layout_type.__name__}")



    for widget_type, args in widgets:
        if args is None:
            args = tuple()
        print(f"\n--> V test {widget_type.__name__}")
        main_widget(widget_type, args, cached_menu)
        print(f"--> X ended {widget_type.__name__}")

    t2 = perf_counter()
    result = (t2 - t1) * 1000
    print(f"\n[Time]: {result:.3f}ms")
    print("==== Test ended, if there are no text below, everything is fine ====\n")
