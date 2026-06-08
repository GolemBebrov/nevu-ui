import nevu_ui as ui
from nevu_ui.core.size.units import *
import pygame
import pyray as rl
from basic import NevuTest
from nevu_ui.overlay.tooltip import _SmallTooltip, Tooltip
from nevu_ui.core.classes import TooltipType
import random

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
    def _seset(self):
        self.widget.tooltip.size = self.widget.size * 0.2
    def create_grad(self, value):
        return ui.rendering.uni_gradient.GradientRaylib([(ui.Color.with_alpha(ui.Color.White, 255), value), (ui.Color.with_alpha(ui.Color.Red, 255), 10)],type=ui.GradientType.Radial, center=self.center)
    def add_to_layout(self):
        #self.widget: ui.Widget = self.showcase_widgets[0]
        widget = ui.Widget(ui.NvVector2(300,300))
        #widget._template['size'] = [100*vw, 100*vh]
       # self.widget.tooltip = Tooltip(TooltipType.BigCustom(ui.NvVector2(0.3, 0.4), "Выбор персонажа...", "Выберите персонажа \n1. - Фапута 3. - Наначи \n2. - Бондрюд 4. - Декстер морган"), self.widget.style)
        #self.widget.add_first_update_action(self._seset)
        #self.do_fps_test = True
        self._dirty_mode = False
        self.center = (random.random(), random.random())
        self.show_tooltip = False
       #self.print_debug_fps = True
        self.draw_cursor = False
        self.fps = 9999
        self.timer = 1000
        self.font = pygame.font.Font("tests/vk_font.ttf", 20)
        self.max_timer = 100
        self.anim_manager = ui.presentation.animations.AnimationManager()
        a = zip([ui.Align.CENTER] * len(self.showcase_widgets), self.showcase_widgets)
        a = list(a)
        a.append((ui.Align.CENTER, ui.Button(self.add, "add", [50*vw,33*vh], style=ui.Style(font_name="tests/vk_font.ttf", font_size=64, colortheme=ui.StateVariable(ui.ColorThemeLibrary.pastel_rose_light, ui.ColorThemeLibrary.material3_dark, ui.ColorThemeLibrary.material3_blue)), hoverable=True, clickable=True)))
        a.append((ui.Align.CENTER, ui.Label("add", [50*vw,33*vh], hoverable=True, clickable=True)))
        #a.append((ui.Align.CENTER, ui.ScrollableRow([100*ui.fill, 100*ui.vh], content = a.copy())))
        self.test_menu.layout = \
        ui.ScrollableColumn([100*fill, 100*fill], wheel_scroll_power=1, scrollbar_perc=ui.NvVector2(2,5), style=self.styles[-1](borderwidth=1),
                z = -1,
                content = a,
                )
        self.scrollable = self.test_menu.layout
        for i in range(50):
            self.add()
        #self.scrollable._test_debug_print = True
        self.test_widget = ui.Widget([0,0],)
        #gradient_shader = ui.rendering.Shader(ui.nevu_state.window.display.renderer, None, open("tests/shaders/gradient_dark.frag", "r").read())
        self.size_test = ui.NvVector2(400, 200)
        self.size_mult = 1
        self.size_znak = 1
        self.widget1: ui.Widget = self.test_menu.layout.items[0]
    def on_draw(self):
        #print(ui.time.fps)
        super().on_draw()
        #print("asd")
        #if self.size_mult > 3:
        #    self.size_znak = -1
        #elif self.size_mult < 0.5:
        #    self.size_znak = 1
        self.anim_manager.update()
        #self.timer = self.anim_manager.get_animation_value(ui.presentation.animations.AnimationType.OPACITY)
        #if self.timer and not self.timer > self.max_timer:
        #    self.widget1.style = self.widget1.style(gradient=self.create_grad(self.timer))
        #    self.widget1.clear_surfaces()
        draw_fps = True
        if draw_fps:
            if ui.nevu_state.window.renderer_type.raylib:
                rl.draw_fps(0,0)
            else:
                self.window.renderer.blit(self.font.render(f"FPS: {str(ui.time.fps)}", True, (255, 255, 255)), (10,10))
        #rl.set_target_fps(75)

        #$self.window.display.clear(rl.BLANK)
        #rl.draw_fps(10,10)
        #print(self.widget._events.content)
        #self._get_coords_toltip()
        #ui.overlay.change_action("tooltip", self.widget.tooltip.get_surf(self.widget.renderer), self.widget.absolute_coordinates, 2)
        #print(len(self.scrollable.collided_items))
        self.window.draw_overlay()
        #self.size_mult += self.size_znak * ui.time.delta_time
        #for i, item in enumerate(self.scrollable.items):
        #    if isinstance(item, ui.ElementSwitcher):
        #        #self.scrollable.items[i] = self.create_new_hohol(self.size_test * self.size_mult)
        #        self.scrollable._boot_up()
        #print(ui.get_all_colors())
    #self.test_widget.surface = self.window.surface
    #a = self.test_widget.renderer._create_surf_base((500,500), radius = 20)
        #self.window.surface.fill(ui.default_style.colortheme.get_subtheme(ui.SubThemeRole.SECONDARY).color)
        #self.window.surface.blit(a, (10,10))

ts = TestScrollable()

ts.run() 