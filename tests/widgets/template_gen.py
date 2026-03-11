import nevu_ui as ui #Импортируем Nevu UI
import pygame

pygame.init()

class MyGame(ui.Manager): #Создаем базу нашего приложения
    def __init__(self):
        super().__init__(ui.Window((800, 600), title = "My Game")) #Инициализируем менеджер
        style = ui.Style(borderradius=20, colortheme=ui.ColorThemeLibrary.github_dark) #Создаем Style (необязательно)
        self.menu = ui.Menu(self.window, [100%ui.vw, 100%ui.vh], style = style, #Создаем меню
                            layout= ui.Grid([100%ui.vw, 100%ui.vh], row=3, column=3, #Создаем макет grid
                                            content = { 
                                                (2, 1.5): ui.Button(lambda: print("Играть"), "Играть", [25%ui.fill, 25%ui.gc], style=style), #Создаем кнопку
                                                (2, 2.0): ui.Button(lambda: print("Открыть"), "Настройки", [25%ui.fill, 25%ui.gc], style=style), #Создаем кнопку
                                                (2, 2.5): ui.Button(lambda: print("Выйти"), "Выйти", [25%ui.fill, 25%ui.gc], style=style,subtheme_role=ui.SubThemeRole.ERROR) #Создаем кнопку
                                            }
                                            )
                            )
    def on_draw(self):
        self.menu.draw() #рисуем меню
    def on_update(self, events):
        self.menu.update() #обновляем меню

game = MyGame()
game.run() #Запускаем готовое приложение