![Пример1](assets/title.png)

![alt text](https://img.shields.io/badge/License:-MIT-orange.svg)



# Краткое описание
**Nevu UI** — это библиотека для декларативного создания пользовательских интерфейсов на Pygame. Проект нацелен на предоставление разработчикам набора готовых, стилизуемых и расширяемых компонентов для быстрого создания современных и отзывчивых интерфейсов в игровых и мультимедийных приложениях.

#### Главная цель Nevu UI: сделать создание интерфейсов на python еще легче и быстрее

### Ключевые особенности включают:
*   **Система макетов:** Удобное расположение элементов, например с помощью сеток (Grid) и прокручиваемых контейнеров (Scrollable).
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

## Главные особенности

### Nevu UI позволяет описивать инферфейс с видной структурой

Примеры декларативности:
> *   **Декларативный подход:** Описывайте ваш интерфейс так же, как вы его видите.
>     ```python
>     # Указывайте контент прямо при создании макета
>     grid = ui.Grid(content={(1,1): ui.Button(...)})
>     ```
>
> *   **Адаптивная система размеров (`SizeRules`):** Забудьте о пикселях. Используйте относительные величины, которые подстраиваются под размер окна или родительского элемента.
>     *   `vh` / `vw`: Проценты от высоты/ширины окна.
>     *   `fill`: Проценты от размера родительского макета.
> *   **Мощная система стилей:** Настраивайте каждый аспект внешнего вида с помощью универсального объекта `Style`.
>     *   **Темы:** Готовые цветовые темы (`synthwave_dark_color_theme`).
>     *   **Градиенты:** Линейные и радиальные.
>     *   **И многое другое:** Шрифты, рамки, скругления, прозрачность.
>
> *   **Встроенные анимации:** Оживите ваш интерфейс с помощью готовых анимаций появления, движения и т.д.
>     ```python
>     widget.animation_manager.add_start_animation(ui.animations.EaseOut(...))
>     ```
  
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
 ## Установка через pip
 ```python 
 pip install nevu-ui
 ```

# Примеры
![Пример1](assets/test_grid.png)
---
![Пример2](assets/test_main.png)

![Пример3](assets/showcase.gif)

---
### Базовая сетка
#### Декларативный подход
```python
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
                                                (2, 2): ui.Button(lambda: print("You clicked!"), "Button", [50*ui.fill,33*ui.fill]) #Создаем кнопку
                                            }))
    def draw_loop(self):
        self.menu.draw() #рисуем меню
    def update_loop(self, events):
        self.menu.update() #обновляем меню

game = MyGame()
game.run() #Запускаем готовое приложение
```
#### Императивный подход
```python
import nevu_ui as ui #Импортируем Nevu UI
import pygame

pygame.init()

window = ui.Window((400, 300), title = "My Game") #Создаем окно

menu = ui.Menu(window, [100*ui.vw, 100*ui.vh]) #Создаем меню

layout = ui.Grid([100*ui.vw, 100*ui.vh], row=3, column=3) #Создаем макет grid
layout.add_item(ui.Button(lambda: print("You clicked!"), "Button", [50*ui.fill,33*ui.fill]), x = 2, y = 2) #Создаем кнопку

menu.layout = layout #Задаем макет меню

while True: #Главный цикл
    events = pygame.event.get() #Получаем события
    window.update(events) #Обновляем окно
    menu.update() #Обновляем меню
    menu.draw() #Рисуем меню
    pygame.display.update() #Обновляем экран
    
```


### Результат примера
![Пример1](assets/result.png)
---
# Статус Nevu UI на данный момент

### **Макеты (Layout_Type)**

(✅ - сделано, ❌ - не сделано, 💾 - устарело)

*   ✅ `Grid`
*   ✅ `Row`
*   ✅ `Column`
*   ✅ `Scrollable`
*   💾 `IntPickerGrid`
*   ✅ `Pages`
*   💾 `Gallery_Pages`
*   ✅ `StackColumn`
*   ✅ `StackRow`
*   ✅ `CheckBoxGroup`

### **Виджеты (Widget)**

*   ✅ `Widget`
*   ✅ `Button`
*   ✅ `Label`
*   ✅ `Input`
*   ✅ `EmptyWidget`
*   ❌ `Tooltip` (В 0.6.X)
*   💾 `ImageWidget`
*   💾 `GifWidget`
*   ❌ `MusicPlayer` (Будет переработан)
*   ✅ `ProgressBar`
*   ✅ `SliderBar`
*   ✅ `ElementSwitcher`
*   💾 `FileDialog`
*   ✅ `RectCheckBox`

# Лицензия

**Nevu UI защищен лицензией MIT**

# Дополнительная информация

* **Gmail:** bebrovgolem@gmail.com
* **Создатель:** Никита А.