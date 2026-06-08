import nevu_ui as ui
import pyray as rl
import pygame
pygame.init()
class Game(ui.Manager):
    def __init__(self):
        rl.set_trace_log_level(rl.TraceLogLevel.LOG_ERROR)
        window = ui.Window((800, 600), title = "My Game", backend=ui.Backend.Pygame, resize_type=ui.ResizeType.CropToRatio, ratio = ui.NvVector2(8,6))
        ui.apply_config("structure_test.yaml", ui.ConfigLoadType.Yaml)
        super().__init__(window)
        
        self.fps = 99999
        self.menu_style = ui.Style(font_size=32, border_radius = 20, border_width=2, colortheme=ui.ColorThemeLibrary.github_dark, font_name="tests/vk_font.ttf")
        self.current_menu = self._create_menu_first()
        self.current_menu.layout = self._create_entry_layout()
        
    def _create_menu_first(self):
        return ui.Menu(self.window, [100*ui.vw, 100*ui.vh], style = self.menu_style)
    
    def _create_entry_layout(self):
        widget_size = [100*ui.gc, 66*ui.gc] 
        tooltip = ui.Tooltip(ui.TooltipType.BigCustom(ui.NvVector2(0.5, 0.8), "Are you sure?", "Pwease no i begwing you..."), self.menu_style(fontsize=9,colortheme=ui.ColorThemeLibrary.material3_blue), True)
        return ui.Grid([100*ui.fillw, 100*ui.fillh], x=3, y=6,
            content = {
                (3, 1): ui.Label("Nevui - Game", widget_size, self.menu_style(border_radius=(20,0,0,20)), subtheme_role=ui.SubThemeRole.SECONDARY),
                (2, 3): ui.Button(lambda: self.move_to(self._create_first_layout()), "Play!", widget_size, self.menu_style, subtheme_role=ui.SubThemeRole.PRIMARY, font_role=ui.PairColorRole.INVERSE_SURFACE),
                (2, 4): ui.Button(lambda: None, "Settings", widget_size, self.menu_style, subtheme_role=ui.SubThemeRole.PRIMARY, font_role=ui.PairColorRole.INVERSE_SURFACE),
                (2, 5): ui.Button(lambda: None, "Exit :(", widget_size, self.menu_style, subtheme_role=ui.SubThemeRole.ERROR, font_role=ui.PairColorRole.INVERSE_SURFACE, tooltip=tooltip),
            })
    
    def _on_first_menu_toogle(self, checkbox):
        layout = self.current_menu.layout
        assert layout
        main_label: ui.Label = layout.get_item_by_id_strict("selected_class")
        desc_label: ui.Label = layout.get_item_by_id_strict("class_desc")
        if not checkbox: 
            main_label.text = "Not selected..."
            desc_label.text = "Select your class to see details."
            return
        id = checkbox.id

        id_to_data = {
            "Warrior": ["Warrior", "You are a Warrior! +Atk +Hp -Spd -Int -Mg"],
            "Mage": ["Mage", "You are a Mage! +Int +Spd +Mg -Atk -Hp"],
            "Ranger": ["Ranger", "You are a Ranger! ++Spd +Rg -Atk -Hp"],
        }
        data = id_to_data[id]
        main_label.text = data[0]
        desc_label.text = data[1]
    
    def _create_first_layout(self):
        widget_size = [100*ui.gc, 66*ui.gc] 
        chk_group = ui.CheckBoxGroup(single_selection=True)
        chk_group.on_single_toggled = self._on_first_menu_toogle
        layout = ui.Grid([100*ui.fillw, 100*ui.fillh], x=3, y=6,
            content = {
            (2, 2): ui.Button(lambda: None, "Continue", widget_size, self.menu_style, subtheme_role=ui.SubThemeRole.PRIMARY, font_role=ui.PairColorRole.INVERSE_SURFACE),
            (2, 4): ui.Row([100*ui.fillw, 35*ui.fillh], x=3,
                content = {
                1: ui.RectCheckBox(50, self.menu_style, id="Warrior"),
                2: ui.RectCheckBox(50, self.menu_style, id="Mage"),
                3: ui.RectCheckBox(50, self.menu_style, id="Ranger")
                }),
            (2, 4.8): ui.Label("Not selected...", widget_size, self.menu_style(border_radius=20), subtheme_role=ui.SubThemeRole.SECONDARY, _draw_content = False, override_color=ui.Color.Blank, id="selected_class", _draw_borders=False), 
            (2, 6): ui.Label("Select your class to see details.", [100%ui.fillw, 100*ui.gc], self.menu_style(border_radius=20), subtheme_role=ui.SubThemeRole.SECONDARY, _draw_content = False, override_color=ui.Color.Blank, id="class_desc", _draw_borders=False), 
        })
        for item in layout._template["content"].values():
            if isinstance(item, ui.LayoutType):
                for subitem in item._template["content"].values():
                    if isinstance(subitem, ui.RectCheckBox):
                        chk_group.add_checkbox(subitem)
            if isinstance(item, ui.RectCheckBox):
                chk_group.add_checkbox(item)
        return layout
            
    def move_to(self, layout):
        self.current_menu.layout = layout
        
    def on_draw(self):
        self.current_menu.draw()
        self.window.draw_overlay()
    def on_update(self, events):
        self.current_menu.update()
        print(ui.time.fps)

if __name__ == "__main__":
    game = Game()
    game.run()