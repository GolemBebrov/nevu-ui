import pygame
from basic import NevuTest

import nevu_ui as ui

pygame.init()
class TestGrid(NevuTest):
    def add(self):
        self.grid.add_items({
            (2,2):self.showcase_widgets[0],

        })

    def add_to_layout(self):
        self.label = ui.Label("Geometry",single_instance=True, size=(40*ui.vw,100*ui.gc), style=ui.Style(font_name="tests/vk_font.ttf", gradient=ui.Gradient([ui.Color.RebeccaPurple, ui.Color.Black], type=ui.GradientType.Linear, direction=ui.LinearSide.Left),font_size=50))
        self.label.animation_manager.add_continuous_animation(ui.core.AnimationType.Position, ui.animations.Vector2Animation(ui.NvVector2(-200, 0), ui.NvVector2(200, 0), 1, ui.animations.steps(2)))
        self.fps = 9999
        self.grid = ui.Grid(
            size = (ui.FillH(100), ui.FillH(100)),
            x = 6,
            y = 6,
            content={
                (2,6): self.showcase_widgets[0],
                (1,6): self.showcase_widgets[0],
                (3,6): self.showcase_widgets[0],
                (4,6): self.showcase_widgets[0],
                (5,6): self.showcase_widgets[0],
                (6,6): self.showcase_widgets[0],
                (2,5): self.showcase_widgets[0],
                (2,4): self.showcase_widgets[0],
                (5,5): self.showcase_widgets[0],
                (5,4): self.showcase_widgets[0],
                (3.5,3): self.label,
                }
            )

        return self.grid

ts = TestGrid()
ts.run()
