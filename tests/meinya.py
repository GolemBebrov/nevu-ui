import nevu_ui as ui
import pygame

pygame.init()

class Game(ui.Manager):
    def __init__(self):
        window = ui.Window((800, 600), title = "My Game", backend=ui.Backend.RayLib, resize_type=ui.ResizeType.CropToRatio, ratio = ui.NvVector2(8,6))
        super().__init__(window)
        self.fps = 75
        self.menu_style = ui.Style(fontsize=32, borderradius = 20, borderwidth=2, colortheme=ui.ColorThemeLibrary.github_dark, fontname="tests/vk_font.ttf")
        self.current_menu = self._create_menu_first()
        self.current_menu.layout = self._create_entry_layout()
        
    def _create_menu_first(self):
        return ui.Menu(self.window, [100*ui.vw, 100*ui.vh], style = self.menu_style, alt=True)
    
    def _create_entry_layout(self):
        widget_size = [100*ui.gc, 66*ui.gc] 
        tooltip = ui.Tooltip(ui.TooltipType.BigCustom(ui.NvVector2(0.5, 0.8),"Are you sure?", "Pwease no i begwing you..."), self.menu_style(fontsize=9), False)
        return ui.Grid([100*ui.fillw, 100*ui.fillh], x=3, y=6,
            content = {
                (3, 1): ui.Label("Nevui - Game", widget_size, self.menu_style(borderradius=(20,0,0,20)), subtheme_role=ui.SubThemeRole.SECONDARY),
                (2, 3): ui.Button(lambda: None, "Play!", widget_size, self.menu_style, subtheme_role=ui.SubThemeRole.PRIMARY, font_role=ui.PairColorRole.INVERSE_SURFACE),
                (2, 4): ui.Button(lambda: None, "Settings", widget_size, self.menu_style, subtheme_role=ui.SubThemeRole.PRIMARY, font_role=ui.PairColorRole.INVERSE_SURFACE),
                (2, 5): ui.Button(lambda: None, "Exit :(", widget_size, self.menu_style, subtheme_role=ui.SubThemeRole.ERROR, font_role=ui.PairColorRole.INVERSE_SURFACE, tooltip=tooltip),
            })
        
    def on_draw(self):
        self.current_menu.draw()
        #self.window.draw_overlay()
    def on_update(self, events):
        self.current_menu.update()

if __name__ == "__main__":
    game = Game()
    game.run()