import nevu_ui as ui
import pygame

def create_test_instances():
    ui.default_style = ui.default_style(colortheme=ui.ColorThemeLibrary.gruvbox_light)
    test_window = ui.Window((300,300), title="Test Window", resize_type=ui.ResizeType.CropToRatio, ratio=ui.NvVector2(1,1))
    test_widget = ui.RectCheckBox(50 ,ui.default_style(borderradius=999, borderwidth=0 ), active_rect_factor=0.9, alt=True)#ui.Button(lambda: print("pressed"), "Nevu UI!", (100, 100), ui.default_style(borderwidth=10, borderradius = 15),single_instance=False)
    tooglegroup = ui.CheckBoxGroup([test_widget], single_selection=True)
    tooglegroup.on_single_toggled = lambda checkbox: print(checkbox)
    #tooglegroup.on_multiple_toggled = lambda checkbox: print(checkbox)
    
    test_widget.active_rect_factor = 0.1
    test_widget.subtheme_role = ui.SubThemeRole.ERROR
    super_duper_test_button = lambda print_text, text: ui.Button(lambda: print(print_text), text, [50*ui.fill,30*ui.fill], style = ui.default_style(borderradius=5, colortheme=ui.ColorThemeLibrary.synthwave_dark), alt = False)
    test_hard_widget = ui.Input([70*ui.vw, 20*ui.vh],ui.default_style(borderradius=30),"InputTest",multiple=True,single_instance=True, alt=True)

    test_inner_layout = ui.Grid([50*ui.vw, 35*ui.vh], x=3,y=3, single_instance=True, 
                                    content={
                                        (1,1): super_duper_test_button("Button Topleft", "Test Chamber"),
                                        (2,2): super_duper_test_button("Button Center", "Test Chamber"),
                                        (3,3): super_duper_test_button("Button BottomRight", "Test Chamber"),
                                        (1,3): super_duper_test_button("Button BottomLeft", "Test Chamber"),
                                        (3,1): super_duper_test_button("Button TopRight", "Test Chamber"),
                                    }
                            )
    test_inner_layout.border_name = "Inner Layout"
    test_inner_layout.borders = True
    test_menu = ui.Menu(test_window,[100*ui.vw, 100*ui.vh],ui.default_style(borderradius=10))
    return test_window, test_widget, test_hard_widget, test_inner_layout, test_menu, tooglegroup

class NevuTest(ui.Manager):
    def __init__(self):
        self.window, self.test_widget, self.test_hard_widget, self.test_inner_layout, self.test_menu, self.tooglegroup = create_test_instances()
        super().__init__(self.window)
        
        self.do_fps_test = False
        self._dirty_mode = False
        self.add_to_layout()
    def add_to_layout(self):
        pass
        #Override in test
    def on_draw(self):
        super().on_draw()
        self.test_menu.draw()
    def on_update(self, events = None):
        super().on_update(events)
        self.test_menu.update()
        if self.do_fps_test:
            print(f"Debug: FPS-{ui.time.fps}")

#to create test:
#   1. Override add_to_layout
#   2. Run it via manager.run()

#import nevu_ui as ui #Импортируем Nevu UI
#import pygame
#
#import pyray as rl
#pygame.init()
#class MyGame(ui.Manager): #Создаем базу нашего приложения
#    def __init__(self):
#        window = ui.Window((400, 300), title = "My Game", ratio=ui.NvVector2(4, 3), backend=ui.Backend.RayLib) #Создаем окно
#        super().__init__(window) #инициализируем менеджер
#        self.fps = 999999999
#        buton = ui.Button(lambda: print("КПОНКА!"), "Кнопка", [50*ui.fill,33*ui.fill], ui.Style(fontname="tests/vk_font.ttf"), single_instance=True)
#        buton.animation_manager.add_continuous_animation(ui.animations.Shake(3, [0,0], [0,100], ui.animations.AnimationType.POSITION))
#        self.menu = ui.Menu(self.window, [100%ui.vw, 100%ui.vh], #Создаем меню
#                            layout= ui.Grid([100%ui.vw, 100%ui.vh], row=3, column=3, #Создаем макет grid
#                                            content = { 
#                                                (2, 2):buton  #Создаем кнопку
#                                            }
#                                            )
#                            )
#    def on_draw(self):
#        self.menu.draw() #рисуем меню
#        rl.draw_fps(10, 10)
#    def on_update(self, events):
#        self.menu.update() #обновляем меню
#        #print(ui.time.fps)
#
#game = MyGame()
#game.run() #Запускаем готовое приложение