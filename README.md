# Краткое описание
**Nevu UI** — это библиотека для декларативного создания пользовательских интерфейсов на Pygame. Проект нацелен на предоставление разработчикам набора готовых, стилизуемых и расширяемых компонентов для быстрого создания современных и отзывчивых интерфейсов в игровых и мультимедийных приложениях.

#### Главная цель Nevu UI: сделать создание интерфейсов на python еще легче и быстрее

### Ключевые особенности включают:
*   **Система макетов:** Удобное расположение элементов с помощью сеток (Grid) и прокручиваемых контейнеров (Scrollable).
*   **Набор виджетов:** Готовые к использованию элементы, такие как кнопки, поля ввода и метки.
*   **Гибкая стилизация:** Возможность кастомизации внешнего вида через систему стилей, поддерживающую цвета, градиенты и рамки.
*   **Анимации:** Встроенная поддержка анимаций для создания динамичных и живых интерфейсов.
*   **Декларативность:** Поддержка декларативного создания интерфейса

## Стиль

### Style - универсальное хранилище параметров для кастомизации внешнего вида
Изменяемые параметры:

* **Gradient** 
* **ColorTheme** - Аналог MaterialDesign
* **Font name/size**
* **Border Width/Radius**
* **Text Align X/Y**
* **Transparency**

## Деклараративность

### Nevu UI позволяет описивать инферфейс с видной структурой

Примеры декларативности:

* **SizeRules** - относительные величины (Vh Vw Fill)
* **Content** - можно указывать его при создании макета
* **Gradient** - описывается
* **Animations** - Можно задавать начальные и постоянные анимации 
  
# Установка
  ## Зависимости:
  **```Python >= 3.12.*```**
  * Для Сборки:
    * ```setuptools >= 61.0```
    * ```Cython```
    * ```numpy```
  * Для Запуска:
    * ```pygame-ce>=2.3.0``` 
    * ```numpy```
    * ```Pillow```
 ---
 ****На Данный момент Nevu UI еще нет в pypi****

# Примеры
![Пример1](assets/test_grid.png)
---
![Пример2](assets/test_main.png)

---
### Продвинутая сетка
```python
import nevu_ui as ui
import pygame
pygame.init()

class Mygame(ui.Manager):
    def __init__(self):
        super().__init__()
        self.fps = 75 #Задаем нуженый fps
        self.background = (0,0,100) #Цвет фона
        self.window = ui.window.Window((300,300), resize_type=ui.ResizeType.FillAllScreen) #Создаем окно
        main_style = ui.Style( #Гланый стиль
            borderradius=10, borderwidth=2, colortheme=ui.synthwave_dark_color_theme,
            fontname="vk_font.ttf", gradient=ui.style.Gradient(colors=[ui.Color.AQUA,(100,100,100)],type='radial',direction=ui.style.Gradient.TOP_CENTER))
        style_mini_font = main_style( #Подстиль
            fontsize=15, border_radius=15,  
            borderwidth=10, gradient=ui.style.Gradient(colors=[ui.Color.REBECCAPURPLE,ui.Color.mix(ui.Color.AQUA,ui.Color.REBECCAPURPLE)],type='linear',direction=ui.style.Gradient.TO_TOP))
    
        b = ui.Button(lambda: print("Button 1"), "Test Chamber", [100*ui.fill,33*ui.fill], style=style_mini_font(borderradius=15, borderwidth=10), words_indent=True, alt=True) #Создаем кнопку
        i = ui.Input([100*ui.fill,33*ui.fill],style_mini_font(borderradius=30,fontname="vk_font.ttf"),"","Введите",multiple=True, alt=True) #Создаем инпут
        
        i.animation_manager.add_start_animation(ui.AnimationEaseOut(3,[0,-100],[0,0],ui.AnimationType.POSITION)) #Добавляем анимацию в начало
        
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
```
---
# Статус Nevu UI на данный момент

### **Макеты (Layout_Type)**

(✅ - сделано, ❌ - не сделано, 💾 - устарело)

*   ✅ `Grid`
*   ✅ `Scrollable`
*   ❌ `CheckBoxGrid` (Скорее всего будет вырезан)
*   💾 `IntPickerGrid`
*   ✅ `Pages`
*   💾 `Gallery_Pages`
*   💾 `Appending_Layout_H`
*   💾 `Appending_Layout_V`

### **Виджеты (Widget)**

*   ✅ `Widget`
*   ✅ `Button`
*   ✅ `Label`
*   ✅ `Input`
*   ✅ `Empty_Widget`
*   ❌ `Tooltip`
*   ❌ `CheckBox` (Будет переработан)
*   💾 `ImageWidget`
*   💾 `GifWidget`
*   ❌ `MusicPlayer` (Будет переработан)
*   💾 `ProgressBar`
*   💾 `SliderBar`
*   💾 `ElementSwitcher`
*   💾 `FileDialog`
*   💾 `RectCheckBox`

# Лицензия

**Nevu UI защищен лицензией MIT**

# Дополнительная информация

* **Gmail:** bebrovgolem@gmail.com
* **Создатель:** Никита А.