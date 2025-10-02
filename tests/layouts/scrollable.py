import nevu_ui as ui
import pygame
from basic import NevuTest
pygame.init()

class TestScrollable(NevuTest):
    def add_to_layout(self):
        self.do_fps_test = True
        self._dirty_mode = False
        self.fps = 999999999
        self.test_menu.layout = \
        ui.Scrollable([100*ui.fill, 100*ui.vh],
                z = -1,
                content = zip([ui.Align.CENTER] * len(self.showcase_widgets), self.showcase_widgets)
                )
        self.scrollable = self.test_menu.layout
        self.element: ui.ElementSwitcher = self.scrollable.items[-1]#.button_right
        
        assert isinstance(self.scrollable, ui.Scrollable)
        self.test_widget = ui.Widget([0,0], inline = True)
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
