
import sys
import nevu_ui as ui
import pygame
import random
pygame.init()

class Mygame(ui.Manager):
    def __init__(self):
        self.window = ui.Window((400,400), resize_type=ui.ResizeType.CropToRatio ,ratio=ui.NvVector2(1,1), backend=ui.Backend.RayLib)
        super().__init__(self.window)
        self.fps = 75999999999999999 #Задаем нуженый fps
        self._dirty_mode = False #Для тольео оптимизации(не рекомендуется включать)
        self.background = (0,0,100) #Цвет фона
         #Создаем окно
        main_style = ui.Style( #Гланый стиль
            borderradius=10, borderwidth=2,
            fontname="tests/vk_font.ttf", gradient=ui.GradientPygame(colors=[ui.Color.AQUA,(100,100,100)],type=ui.GradientType.Linear,direction=ui.LinearSide.Right))
        style_mini_font = main_style( #Подстиль
            fontsize=15, borderradius=(5,0,0,5),  
            borderwidth=4, gradient=ui.GradientPygame(colors=[ui.Color.REBECCAPURPLE,ui.Color.mix(ui.Color.AQUA,ui.Color.REBECCAPURPLE)],type=ui.GradientType.Linear,direction=ui.LinearSide.Top))

        b = ui.Button(lambda: print("Button 1"), "Test Chamber", [50*ui.fill,11*ui.fill], style=style_mini_font(borderradius=5, borderwidth=2, fontsize=10), words_indent=True, alt=True) #Создаем кнопку
        i = ui.Input([100*ui.fill,30*ui.fill],style_mini_font(borderradius=30,borderwidth=0,fontname="tests/vk_font.ttf"),"","Введите", alt=True, multiple=True) #Создаем инпут
        conf = i.constant_kwargs.copy()
        conf['single_instance'] = True
        self.icopy = ui.Input([100*ui.fill,30*ui.fill],**conf)
        self.icopy.animation_manager.add_start_animation(ui.animations.EaseOut(6,[0,-100],[0,0],ui.animations.AnimationType.POSITION)) #Добавляем анимацию в начало
        self.icopy.animation_manager.add_start_animation(ui.animations.EaseOut(6,0, 255,ui.animations.AnimationType.OPACITY)) #Добавляем анимацию в начало
        "ss" if True else "dd"
        "ss" if True else "dd"
        #создаем макет
        gridmenu = ui.Grid([66*ui.fill, 40*ui.fill], x=3,y=3, 
                                content={
                                        (2,1): b,
                                        (2,2): i
                                    }
                         )
        gridmenu.booted = True
        gridmenu._boot_up()
        gridmenu._boot_up()
        gridmenu._boot_up()
        gridmenu._boot_up()
        gridmenu._boot_up()
        gridmenu._connect_to_layout(gridmenu)
        gridmenu._boot_up()

        self.menu = ui.menu.Menu(self.window,(100*ui.vw,100*ui.vh),
                style = main_style(borderradius=20,borderwidth=1, gradient=ui.GradientPygame(colors=[ui.Color.BLACK, ui.Color.PURPLE],type=ui.GradientType.Linear,direction=ui.LinearSide.Bottom)), alt=False, 
                layout = ui.Grid([100*ui.fill,100*ui.fill],x=3,y=3, 
                         content = {
                         (2,1.2): gridmenu,
                         (2,2.1): gridmenu, 
                         (2,3): self.icopy   
                     }   
                 )
             )    
        print(gridmenu.layout)
        gridmenu._connect_to_menu(self.menu)
        print(gridmenu.layout)
        print(gridmenu.first_parent_menu)
        items = self.menu.layout.items
        
        items = items[:2]
        for item in items:
            ititems = item.items
            anims = ui.animations
            anim = [anims.Bounce, anims.EaseInBack, anims.EaseIn, anims.EaseOut, anims.EaseInOut][random.randint(0,4)]
            ititems[0].animation_manager.add_continuous_animation(anim(random.randint(2,5),[125,0],[-125,0],ui.animations.AnimationType.POSITION))
            ititems[1].animation_manager.add_continuous_animation(ui.animations.Glitch(random.randint(2,5),[-70,0],[70,0],ui.animations.AnimationType.POSITION))
        print(items)
        self.surf_test = pygame.Surface((100,100))
        self.surf_test.fill((255,0,0))
        self.test_coords = ui.NvVector2(0.0,0.0)
        ui.overlay.change_element("test", self.surf_test, self.test_coords, 0)
        

    def on_draw(self):
        #self.menu.surface.fill(self.background)
        self.menu.draw()
        #рисуем меню
        self.window.draw_overlay()
      
    def on_update(self, events):
        self.menu.update()
        if self.test_coords.x > self.window.size.x - self.window._crop_width_offset // 2: 
            self.test_coords.x = -100 + self.window._crop_width_offset // 2
            self.test_coords.y += 1 + self.window._crop_height_offset // 2
           # self.test_coords += 
        else: 
            self.test_coords += ui.NvVector2(100*ui.time.dt*self.window.ratio.x,0)
            #print(self.test_coords)
        ui.overlay.change_element("test", self.surf_test, self.test_coords, 0)
        #print(self.menu.layout.items[-1].texture.alpha) if hasattr(self.menu.layout.items[-1],"texture") else None
        show_fps = True
        fps_mode = "Unslowed"
        #Для показа фпс
        #if show_fps:
            #print(f"FPS {fps_mode}: ",ui.time.fps)
        #print("anim_value:", self.icopy.animation_manager.get_animation_value(ui.animations.AnimationType.POSITION))

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

