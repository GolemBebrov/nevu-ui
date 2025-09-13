
import sys
import nevu_ui as ui
import pygame
pygame.init()

class Mygame(ui.Manager):
    def __init__(self):
        super().__init__()
        self.fps = 75 #Задаем нуженый fps
        self._dirty_mode = False #Для оптимизации(не рекомендуется включать)
        self.background = (0,0,100) #Цвет фона
        self.window = ui.window.Window((300,300), resize_type=ui.ResizeType.FillAllScreen) #Создаем окно
        main_style = ui.Style( #Гланый стиль
            borderradius=10, borderwidth=2, colortheme=ui.synthwave_dark_color_theme,
            fontname="vk_font.ttf", gradient=ui.style.Gradient(colors=[ui.Color.AQUA,(100,100,100)],type='radial',direction=ui.style.Gradient.TOP_CENTER))
        style_mini_font = main_style( #Подстиль
            fontsize=15, border_radius=15,  
            borderwidth=4, gradient=ui.style.Gradient(colors=[ui.Color.REBECCAPURPLE,ui.Color.mix(ui.Color.AQUA,ui.Color.REBECCAPURPLE)],type='linear',direction=ui.style.Gradient.TO_TOP))
    
        b = ui.Button(lambda: print("Button 1"), "Test Chamber", [50*ui.fill,11*ui.fill], style=style_mini_font(borderradius=15, borderwidth=2, fontsize=10), words_indent=True, alt=True, will_resize=True) #Создаем кнопку
        i = ui.Input([100*ui.fill,66*ui.fill],style_mini_font(borderradius=30,fontname="vk_font.ttf"),"","Введите", alt=True, will_resize=True, multiple=True) #Создаем инпут
        
        i.animation_manager.add_start_animation(ui.AnimationEaseOut(3,[0,-100],[0,0],ui.AnimationType.POSITION)) #Добавляем анимацию в начало
        "ss" if True else "dd"
        #создаем макет
        gridmenu = ui.Grid([66*ui.fill, 40*ui.fill], x=3,y=3, 
                                content={
                                        (2,1): b,
                                        (2,2): i
                                    }
                         )
        
        self.menu = ui.menu.Menu(self.window,(100*ui.vw,100*ui.vh),
                style = main_style(borderradius=20,borderwidth=1), alt=False, 
                layout = ui.Grid([100*ui.fill,100*ui.fill],x=3,y=3, 
                         content = {
                         (2,1.2): gridmenu,
                         (2,2.1): gridmenu, #Внимание: Grid поддерживает 
                         (2,3): gridmenu    #Координаты с плавающими числами в допустимом диапозоне
                     }   
                 )
             )    
        self.menu.quality = ui.Quality.Best #Для качества(по умолчанию Quality.Decent)
        self.menu.will_resize = True #Для оптимизации

    def draw_loop(self):
        self.menu.surface.fill(self.background)
        self.menu.draw()
        #рисуем меню
      
    def update_loop(self, events):
        self.menu.update()
        show_fps = True
        fps_mode = "Unslowed"
        #Для показа фпс
        if show_fps:
            print(f"FPS {fps_mode}: ",ui.time.fps)

def test_main():
    #Запускаем
    game = Mygame()
    game.run()

    sys.exit()

test_main()

#Unused part
"""ui.Grid([30*ui.fill, 15*ui.fill], 3,2,
                                content={
                                        (2,1): ui.Button(None, "^", strelka_size,style=style_mini_font,words_indent=True, alt=True),
                                        (2,2): ui.Button(None, "v", strelka_size,style=style_mini_font,words_indent=True, alt=True),
                                        (1,2): ui.Button(None, "<", strelka_size,style=style_mini_font,words_indent=True, alt=True),
                                        (3,2): ui.Button(None, ">", strelka_size,style=style_mini_font,words_indent=True, alt=True),
                                    }
                         )
ui.Scrollable([70*ui.fill, 50*ui.fill], wheel_scroll_power=5, 
                                content=(
                                        [ui.Align.CENTER, copy.copy(b)],
                                        [ui.Align.CENTER, copy.copy(l)],
                                        [ui.Align.CENTER, copy.copy(b)],
                                        [ui.Align.CENTER, copy.copy(b)],
                                        [ui.Align.CENTER, copy.copy(l)],
                                        [ui.Align.CENTER, copy.copy(b)],
                                    )
                         )"""





#--------- OLD WAY ---------
main_style = ui.Style(borderradius=10,borderwidth=2,colortheme=ui.material3_dark_color_theme,fontname="font.ttf",)

w = ui.window.Window((300,300))
menu = ui.menu.Menu(w,(300,300),style = main_style(borderradius=30,borderwidth=5,), alt=False)#
l = ui.Grid([300,300],3,3)
b = ui.Button(lambda: print("Button 1"), "Test Chamber", [120,80], style=main_style(borderradius=15,borderwidth=10 ),words_indent=True, alt=True)
b.animation_manager.transition_animation = ui.AnimationEaseIn
b.animation_manager.transition_time = 5
b.animation_manager.add_start_animation(ui.AnimationEaseInBack(1,[0,100],[0,0],ui.AnimationType.POSITION))
b.animation_manager.add_continuous_animation(ui.AnimationBounce(5,[90,50],[-90,50],ui.AnimationType.POSITION))
l.add_widget(b,2,2)
i = ui.Input([200,100],main_style(borderradius=20,fontname="font.ttf"),"","Введите",multiple=True, alt=True)
i.animation_manager.add_start_animation(ui.AnimationEaseOut(1,[0,-100],[0,0],ui.AnimationType.POSITION))
l.add_widget(i,2,1)
l.get_widget(2,1).on_click = lambda: print("JOTA")

menu.layout = l
fps_list = []
while True:
    events = pygame.event.get()
    w.clear((200,200,200))
    menu.update()
    menu.draw()
    #DEBUG!
    #pygame.draw.rect(w.surface,(0,0,0),b.get_rect(),5)
    #print(menu._resize_ratio)
    print(ui.time.fps)
    #fps_list.append(ui.time.fps)
    #if len(fps_list) > 300: print(f"Avg FPS: {int(sum(fps_list)/len(fps_list))}"); fps_list.clear()
    w.update(events, 99999)
    pygame.display.update()

