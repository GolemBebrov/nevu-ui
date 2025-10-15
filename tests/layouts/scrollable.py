import nevu_ui as ui
import pygame
from basic import NevuTest
pygame.init()

class TestScrollable(NevuTest):
    def add_to_layout(self):
        self.do_fps_test = True
        self._dirty_mode = False
        self.fps = 999999999
        a = zip([ui.Align.CENTER] * len(self.showcase_widgets), self.showcase_widgets)
        a = list(a)
        a.append((ui.Align.CENTER, ui.ScrollableColumn([100*ui.fill, 100*ui.vh], content = a.copy())))
        self.test_menu.layout = \
        ui.ScrollableRow([100*ui.fill, 100*ui.vh],
                z = -1,
                content = a
                )
        self.scrollable = self.test_menu.layout
        #self.scrollable._test_debug_print = True
        self.test_widget = ui.Widget([0,0],)
    def first_update(self):
        super().first_update()
    def draw_loop(self):
        super().draw_loop()

    #self.test_widget.surface = self.window.surface
    #a = self.test_widget.renderer._create_surf_base((500,500), radius = 20)
        #self.window.surface.fill(ui.default_style.colortheme.get_subtheme(ui.SubThemeRole.SECONDARY).color)
        #self.window.surface.blit(a, (10,10))

ts = TestScrollable()

ts.run() 
