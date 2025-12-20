import nevu_ui as ui #Импортируем Nevu UI
import pygame

pygame.init()

class MyGame(ui.Manager): #Создаем базу нашего приложения
    def __init__(self):
        window = ui.Window((400, 300), title = "My Game") #Создаем окно
        super().__init__(window) #инициализируем менеджер
        self.menu = ui.Menu(self.window, [100*ui.vw, 100*ui.vh], #Создаем меню
                            layout= ui.Grid([100*ui.vw, 100*ui.vh], row=3, column=3, #Создаем макет grid
                                            content = { 
                                                (2, 2): ui.Button(lambda: print("You clicked!"), "КНОПКА!", [50*ui.fill,33*ui.fill]) #Создаем кнопку
                                            }
                                            )
                            )
    def on_draw(self):
        self.menu.draw() #рисуем меню
    def on_update(self, events):
        self.menu.update() #обновляем меню

game = MyGame()
game.run() #Запускаем готовое приложение