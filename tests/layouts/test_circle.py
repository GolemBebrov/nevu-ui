import nevu_ui as ui
import pyray as rl

def create_rect_anim(x, y, anim_type = ui.animations.animations_library.smootherstep, time = 1):
    return ui.animations.AnimationQueue(ui.animations.Vector2Animation(ui.NvVector2(x, y), ui.NvVector2(x, -y), time, anim_type),
                                        ui.animations.Vector2Animation(ui.NvVector2(x, -y), ui.NvVector2(-x, -y), time, anim_type),
                                        ui.animations.Vector2Animation(ui.NvVector2(-x, -y), ui.NvVector2(-x, y), time, anim_type),
                                        ui.animations.Vector2Animation(ui.NvVector2(-x, y), ui.NvVector2(x, y), time, anim_type))
class App(ui.Manager):
    def __init__(self):
        rl.init_window(1600, 800, "Nevu UI")
        window = ui.InitializedWindow.from_raylib(ratio = ui.NvVector2(16, 8))
        self.current_menu = ui.Menu(window, [100%ui.fill, 100%ui.fill])
        super().__init__(window, [self.current_menu])
        
        label_style = ui.Style(font_name="tests/vk_font.ttf", border_radius=30, font_size=20)
        
        panel_grid = ui.Grid([100%ui.fill, 100%ui.fill], row=2, column=2, 
                             content = {
                                (1, 1): ui.Label("Panel!", [40%ui.fill, 40%ui.fill], label_style, subtheme_role=ui.SubThemeRole.PRIMARY),
                                (1, 2): ui.Label("Panel!", [40%ui.fill, 40%ui.fill], label_style, subtheme_role=ui.SubThemeRole.SECONDARY),
                                (2, 1): ui.Label("Panel!", [40%ui.fill, 40%ui.fill], label_style, subtheme_role=ui.SubThemeRole.TERTIARY),
                                (2, 2): ui.Label("Panel!", [40%ui.fill, 40%ui.fill], label_style, subtheme_role=ui.SubThemeRole.ERROR)
                             })

        panel_animations = ui.animations.AnimationManager()
        panel_animations.add_continuous_animation(ui.AnimationType.Position, create_rect_anim(300, 70))
        panel1 = ui.Panel([400, 400], ui.Style(border_radius=20), animation_manager=panel_animations, 
                          slot = panel_grid)
        
        layout = ui.Grid([100%ui.vw, 100%ui.vh], row=7, column=7,
            content = {
                (4, 1): ui.Label("Nevu UI 0.8.0!", [40%ui.vw, 10%ui.vh], label_style, subtheme_role=ui.SubThemeRole.PRIMARY),
                (4, 4): panel1
            })
        
        self.current_menu.layout = layout


App().run()