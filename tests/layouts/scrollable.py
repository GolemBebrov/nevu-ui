
import random

import pygame
import pyray as rl
from basic import NevuTest

import nevu_ui as ui
from nevu_ui.core.size.units import *

pygame.init()
curi = 0

class TestScrollable(NevuTest):
    def add(self):
        global curi
        curi += 1
        w: ui.Button = self.showcase_widgets[0]
        w._template.text = f"Button: {curi}"
        self.scrollable.add_items([
            (ui.Align.LEFT, w),
        ])
        print(len(self.scrollable.items))

    def create_layout(self):
        self.center = (random.random(), random.random())
        self.show_tooltip = False
        self.fps = 9999
        self.timer = 1000
        self.font = pygame.font.Font("tests/vk_font.ttf", 20)
        self.max_timer = 100
        self.anim_manager = ui.presentation.animations.AnimationManager()
        a = zip([ui.Align.CENTER] * len(self.showcase_widgets), self.showcase_widgets)
        a = list(a)
        a.append((ui.Align.CENTER, ui.Button(self.add, "add", (50*vw, 33*vh), style = ui.Style(font_name="tests/vk_font.ttf", font_size=64, colortheme=ui.StateVariable(ui.ColorThemeLibrary.github_light, ui.ColorThemeLibrary.material3_dark, ui.ColorThemeLibrary.material3_blue)), hoverable=True, clickable=True)))
        a.append((ui.Align.CENTER, ui.Label("add", [50*vw,33*vh], hoverable=True, clickable=True)))
        self.scrollable = ui.ScrollableColumn(
            size = (100*fill, 100*fill),
            wheel_scroll_power = 1,
            scrollbar_perc = ui.NvVector2(2,5),
            style = self.styles[-1](border_width = 1),
            z = -1,
            content = a,
            single_instance = True,
        )
        for _ in range(100):
            self.add()

        return self.scrollable

    def on_draw(self):
        super().on_draw()
        self.anim_manager.update()
        draw_fps = True
        if draw_fps:
            if ui.nevu_state.window.renderer_type.raylib:
                rl.draw_fps(0,0)
            else:
                self.window.renderer.blit(self.font.render(f"FPS: {ui.time.fps!s}", True, (255, 255, 255)), (10,10))
        self.window.draw_overlay()

ts = TestScrollable()

ts.run()
