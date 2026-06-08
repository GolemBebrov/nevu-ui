import nevu_ui as ui #Импортируем Nevu UI
import pygame

pygame.init()

class MyGame(ui.Manager): #Создаем базу нашего приложения
    def __init__(self):
        super().__init__(ui.Window((400, 300), title = "My Game", backend=ui.Backend.RayLib, base_fps = 120)) #Инициализируем менеджер
        style = ui.Style(border_radius=20, colortheme=ui.ColorThemeLibrary.material3_dark, subtheme_role=ui.SubThemeRole.PRIMARY, font_name="tests/vk_font.ttf") #Создаем Style (необязательно)
        self.menu = ui.Menu(self.window, [100%ui.vw, 100%ui.vh], style=style(borderwidth=0),  #Создаем меню
                            layout= ui.Grid([100%ui.vw, 100%ui.vh], row=3, column=3, #Создаем макет grid
                                            content = { 
                                                (2, 2): ui.Button(lambda: print("You clicked!"), "КНОПКА!", [50%ui.fill, 50%ui.gc], style, subtheme_role=ui.SubThemeRole.PRIMARY) #Создаем кнопку
                                            }
                                            )
                            )
        self.fps = None
    def on_draw(self):
        self.menu.draw() #рисуем меню
    def on_update(self, events):
        print(ui.time.fps)
        self.menu.update() #обновляем меню

game = MyGame()
game.run() #Запускаем готовое приложение