
import sys
import copy
import nevu_ui as ui
import pygame
#import taichi as ti
pygame.init()

#This is a test for global audience
#Change veve to pygame_nevui or your package name if it localy placedо

#ti.init(arch=ti.gpu) #Unused

#--------- NEW WAY ---------

class Mygame(ui.Manager):
    def __init__(self):
        super().__init__()
        self.fps = 5000000
        self._dirty_mode = True
        self.background = (0,0,100)
        self.window = ui.window.Window((300,300))
        main_style = ui.Style(borderradius=10,borderwidth=2,colortheme=ui.material3_dark_color_theme,fontname="font.ttf",gradient=ui.style.Gradient(colors=[ui.Color.AQUA,(100,100,100)],type='radial',direction=ui.style.Gradient.TOP_CENTER))
        style_mini_font = main_style(fontsize=10, border_radius=15,borderwidth=10)
        #Widget customization
        b = ui.Button(lambda: print("Button 1"), "Test Chamber", [50*ui.fill,15*ui.fill],style=main_style(borderradius=15,borderwidth=10, ),words_indent=True, alt=True)
        #b.animation_manager.transition_animation = ui.AnimationEaseIn
        #b.animation_manager.transition_time = 5
        #b.animation_manager.add_start_animation(ui.AnimationEaseInBack(1,[0,100],[0,0],ui.AnimationType.POSITION))
        #b.animation_manager.add_continuous_animation(ui.AnimationBounce(5,[90,50],[-90,50],ui.AnimationType.POSITION))
        
        i = ui.Input([100*ui.fill,33*ui.fill],main_style(borderradius=30,fontname="font.ttf"),"","Введите",multiple=True, alt=True)
        i.animation_manager.add_start_animation(ui.AnimationEaseOut(3,[0,-100],[0,0],ui.AnimationType.POSITION))
        strelka_size = [32*ui.fill,45*ui.fill]
        self.menu = ui.menu.Menu(self.window,(100*ui.vw,100*ui.vh),
                style = main_style(borderradius=30,borderwidth=5), alt=False, 
                layout = ui.Grid([100*ui.fill,100*ui.fill],3,3, 
                         content = {
                         (2,2): ui.Scrollable([70*ui.fill, 25*ui.fill], content={
                            ui.Align.CENTER: ui.Button(lambda: print("Button 1"), "Test Chamber", [50*ui.fill,15*ui.fill],style=main_style(borderradius=15,borderwidth=10, ),words_indent=True, alt=True)
                         }),
                         (2,1): i,
                         (2,3): ui.Grid([70*ui.fill, 25*ui.fill], 3,3, 
                                content={
                                        (1,1): ui.Button(lambda: print("Button Topleft"), "Test Chamber", [50*ui.fill,30*ui.fill],style=style_mini_font,words_indent=True, alt=True),
                                        (2,2): ui.Button(lambda: print("Button Center"), "Test Chamber", [50*ui.fill,30*ui.fill],style=style_mini_font,words_indent=True, alt=True),
                                        (3,3): ui.Button(lambda: print("Button BottomRight"), "Test Chamber", [50*ui.fill,30*ui.fill],style=style_mini_font,words_indent=True, alt=True),
                                        (1,3): ui.Button(lambda: print("Button BottomLeft"), "Test Chamber", [50*ui.fill,30*ui.fill],style=style_mini_font,words_indent=True, alt=True),
                                        (3,1): ui.Button(lambda: print("Button TopRight"), "Test Chamber", [50*ui.fill,30*ui.fill],style=style_mini_font,words_indent=True, alt=True),
                                    }
                         )
                     }   
                 )
             )    
         
        #l = self.menu.layout
        #l.get_item(2,1).on_click = lambda: print("JOTA")
        
    def draw_loop(self):
        self.menu.draw()
    def update_loop(self, events):
        self.menu.update()
        show_fps = True
        fps_mode = "Unslowed"
        if show_fps:
            print(f"FPS {fps_mode}: ",ui.time.fps)

        #print(f"Window: {self.window._next_update_dirty_rects}") #Window
        #print(f"Menu: {self.menu._dirty_rects}") #Menu
        #print(f"Layout: {self.menu.layout._dirty_rect}") #Layout
        #print(f"Widget: {self.menu.layout.get_widget(2,2)._dirty_rect}") #Widget

#Unused part
"""ui.Grid([30*ui.fill, 15*ui.fill], 3,2,
                                content={
                                        (2,1): ui.Button(None, "^", strelka_size,style=style_mini_font,words_indent=True, alt=True),
                                        (2,2): ui.Button(None, "v", strelka_size,style=style_mini_font,words_indent=True, alt=True),
                                        (1,2): ui.Button(None, "<", strelka_size,style=style_mini_font,words_indent=True, alt=True),
                                        (3,2): ui.Button(None, ">", strelka_size,style=style_mini_font,words_indent=True, alt=True),
                                    }
                         )"""

game = Mygame()
game.run()

sys.exit()



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
