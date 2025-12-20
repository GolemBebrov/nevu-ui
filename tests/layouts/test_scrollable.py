import nevu_ui as ui
import pygame
from test_basic import NevuTest
pygame.init()

class TestScrollable(NevuTest):
    def _some_func(self, checkbox):
        id = checkbox.id
        if id is None: print("НЕТУ ID")
        if id == "Zov": print("ЗОВ БРАТИК")
        if id == "GOIDA": print("GOIDA ZOV ZOV ZOV")
    def add_to_layout(self):
        self.do_fps_test = True
        self._dirty_mode = False
        tetete_progressbar = ui.Slider([35*ui.vw, 35*ui.vw], ui.default_style(borderradius=500, borderwidth=3))
        nyachechevitsya = ui.ElementSwitcher([80*ui.fill, 15*ui.fill], ["Goida", ["Тромб", "x_01"], "Маг 1", "Мечник 2", "Маг 3"],ui.default_style(borderradius=30), single_instance = False)
        self.fps = 999999999
        self.test_menu.layout = \
        ui.ScrollableColumn([100*ui.fill, 100*ui.vh],
            z = -1,
            content=[
                (ui.Align.CENTER, ui.Row([100*ui.vw, 20*ui.fill], x=3,
                                        content = {1 :self.test_widget,
                                                    2 :self.test_widget,
                                                    3 :self.test_widget,})),
                (ui.Align.CENTER, self.test_widget),
                (ui.Align.CENTER, self.test_hard_widget),
                (ui.Align.CENTER, self.test_inner_layout),
                (ui.Align.CENTER, self.test_widget),
                (ui.Align.CENTER, self.test_widget),
                (ui.Align.CENTER, tetete_progressbar),
                (ui.Align.CENTER, nyachechevitsya),
                
            ]
            )
        #self.tooglegroup.on_checkbox_toggled_single = lambda checkbox: self._some_func(checkbox)
        self.scrollable = self.test_menu.layout
        self.scrollable.items[0].on_click = lambda: print("asd")
        self.scrollable.items[0].items[0].on_click = lambda: print("goida")
        self.test_menu.layout.items[-1].id = "GOIDA"
        self.test_menu.layout.items[-2].id = "Zov"
        #self.scrollable._test_always_update = True
        print(self.scrollable.get_rect())
        
        #assert isinstance(self.scrollable, ui.ScrollableRow)
    def first_update(self):
        super().first_update()
    def on_draw(self):
        super().on_draw()
        #print(ui.time.fps)
        #self.scrollable.update(self.window.last_events)
        #print(self.scrollable.items[0].get_rect())
        #print(self.scrollable._hover_state)
        #pygame.draw.rect(self.window.surface, (0,0,0), self.scrollable.scroll_bar_y.get_rect(), 5)
        #print(self.scrollable._csize)
        #print(self.window._crop_height_offset)
        
        #self.scrollable._regenerate_coordinates()

ts = TestScrollable()

ts.run()

