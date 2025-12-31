import nevu_ui as ui
from nevu_ui.size.units import *
import pygame
from basic import NevuTest
pygame.init()
class TestScrollable(NevuTest):
    def add(self): 
        self.scrollable.add_items([
            (ui.Align.LEFT, self.showcase_widgets[0]),
        ])
    def add_to_layout(self):
        #self.do_fps_test = True
        self._dirty_mode = False
        #self.print_debug_fps = True
        self.draw_cursor = False
        self.fps = 9999999991
        a = zip([ui.Align.CENTER] * len(self.showcase_widgets), self.showcase_widgets)
        a = list(a)
        a.append((ui.Align.CENTER, ui.Button(self.add, "add", [50*vw,33*vh])))
        #a.append((ui.Align.CENTER, ui.ScrollableRow([100*ui.fill, 100*ui.vh], content = a.copy())))
        self.test_menu.layout = \
        ui.ScrollableColumn([100*fill, 100*vh], wheel_scroll_power=1,
                z = -1,
                content = a
                )
        self.scrollable = self.test_menu.layout
        #self.scrollable._test_debug_print = True
        self.test_widget = ui.Widget([0,0],)
        #gradient_shader = ui.rendering.Shader(ui.nevu_state.window.display.renderer, None, open("tests/shaders/gradient_dark.frag", "r").read())
    def first_update(self):
        super().first_update()
        
    def on_draw(self):
        super().on_draw()
        for i in self.scrollable.items:
            if isinstance(i, ui.ElementSwitcher):
                #print(i.get_rect())
                pass

    #self.test_widget.surface = self.window.surface
    #a = self.test_widget.renderer._create_surf_base((500,500), radius = 20)
        #self.window.surface.fill(ui.default_style.colortheme.get_subtheme(ui.SubThemeRole.SECONDARY).color)
        #self.window.surface.blit(a, (10,10))

ts = TestScrollable()

ts.run() 