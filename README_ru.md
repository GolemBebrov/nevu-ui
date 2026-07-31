<p align="center">
  <img src="assets/title.png" alt="Nevu UI Intro Banner" width="800" />
</p>

![alt text](https://img.shields.io/badge/License:-MIT-orange.svg)

# Wiki ссылка (БЕТА!)
 * <a href="https://golembebrov.github.io/nevu-docs/">NevuDocs</a>

### Nevu UI означает: `Nevu is Eleven times better Versus other UI's User Interface`

# Краткое описание
**Nevu UI** - это библиотека для простого создания GUI на python. Nevu UI нацелен на предоставление набора готовых, легко настраиваемых компонентов для создания интерфейсов в играх и приложениях.

### Ключевые особенности:
*   **Макеты:** Различные варианты контейнеров, которые автоматически распологают элементы внутри себя, для примера `Grid`, `ScrollableColumn`, и т.д.
*   **Виджеты:** Готовые к использованию элементы, такие как кнопки, поля ввода и метки.
*   **Кастомизация:** Поддержка кастомизации внешнего вида через `Style`, куча вариантов для кастомизации внутри `Style`.
*   **Анимации:** Встроенная поддержка анимаций через `AnimationManager`.
*   **Декларативность:** Поддержка декларативного создания интерфейса.

<br>

<p align="left">
  <img src="assets/RU/separator_style.png" alt="Style banner" width="600" />
</p>

---

### `Style` - хранилище параметров для кастомизации внешнего вида

* **`gradient`**
  * Градиент поддерживается во всех бекэндах, так-же есть 2 вида градиента: линейный и радиальный.
* **`color_theme`**
  * Аналог MaterialDesign, отвечает за визуальную состовляющую виджета и меню, можно выбрать из 10+ готовых вариантов тем или создать свою тему.
* **`font_name`/`font_size`**
  * Контролирует размер шрифта на виджетах которые ее содержат.
* **`border_width`/`bw`**
  * Дает возможность изменить размер рамки.
* **`border_radius`/`br`**
  * Дает возможность изменить радиус угла рамки.

и так далее...

<br>

<p align="left">
  <img src="assets/RU/separator_features.png" alt="Style banner" width="600" />
</p>

---

### Декларативность и её примеры в Nevu UI

*   **Декларативный подход:** Описывайте ваш интерфейс декларативно.
    ```python
    # Указывайте content прямо при создании макета
    my_grid = Grid(..., content={(1,1): Button(...)})
    ```
*   **Адаптивная система размеров - `SizeRules`:** Дает возможность использовать относительные величины для указания первоначальной высоты/ширины обьекта вместо пикселей.
    Пример использования `SizeRule`:
    ```python
    Widget(size = (30*vw, 50*fill))
    ```
    или можно использовать `%`
    ```python
    Widget(size = (30%vw, 50%fill))
    ```
    *   `vh` / `vw`: Проценты от высоты/ширины окна.
    *   `fillx` / `filly` / `fill`: Проценты от высоты/ширины/размера родительского макета.
    *   `gc` / `gcw` / `gch`: Проценты от размера ячейки сетки.
    *   Префикс `c`: можно поставить в любой SizeRule, он означает, что будет браться текущая величина, без префикса будет браться оригинальная.
### Встроенные анимации:
  * **25+ встроенных анимаций**
  * в Nevu UI есть **Два** типа анимаций:
      *   **Стартовая**.
      *   **Бесконечная**.
  * Пример использования:
     * **Стартовая:**
       ```widget.animation_manager.add_start_animation(...)```
     * **Бесконечная:**
       ```widget.animation_manager.add_continuous_animation(...)```

### Система параметров - ParamEngine:

*   `ParamEngine` - это инструмент, встроенный во все макеты и виджеты, он позволяет:
    * добавлять переменные в `__init__` объекта.
    * Проверять тип параметра во время инициализации и после.
    * Встраивать параметр в разные этапы инициализации.
    * Задавать кастомные сеттер и геттер.
*   **Примеры:**
    ```python
    import nevu_ui as ui
    from typing import Unpack, NotRequired

    # Создаем TypedDict с переменными (необязательно, но красиво)
    class MyWidgetKwargs(ui.WidgetKwargs):
        my_var: NotRequired[int | float]

    class MyWidget(ui.Widget):
        def __init__(self, size: NvVector2 | list, style: Style = default_style, **param_kwargs: Unpack[MyWidgetKwargs]):
            super().__init__(size, style, **param_kwargs)

        # Переопределяем функцию для добавления параметров (обязательно)
        def _add_params(self):
            super()._add_params()

            # Добавляем параметр (обязательно)
            self._add_param('my_var', int | float)

            # Можно еще добавить ссылку на параметр
            # self._add_param_link('my_var', 'my_var_new_name')

            # Также можно заблокировать параметр при необходимости
            # self._block_param('my_var')
    ```

<br>

<p align="left">
  <img src="assets/RU/separator_installation.png" alt="Style banner" width="600" />
</p>

---
  ## Зависимости:
  **```Python >= 3.12.*```**
  * Для Сборки:
    * ```setuptools >= 61.0```
    * ```Cython```
    * ```numpy```
  * Для Запуска:
    * ```numpy```
  * Дополнительные библиотеки:
    * ```pygame-ce>=2.3.0``` 
    * ```raylib```
    * ```pyyaml```
 ## Установка через pip
 ```python
 pip install nevu-ui[all]
 ```

<br>

<p align="left">
  <img src="assets/RU/separator_examples.png" alt="Style banner" width="600" />
</p>

---
![Пример1](assets/test_grid.png)
---
![Пример2](assets/test_main.png)

![Пример3](assets/showcase.gif)

---
### Базовая сетка
#### Декларативный подход
```python
import nevu_ui as ui # Импортируем Nevu UI
import pygame

pygame.init()

class MyGame(ui.Manager): # Создаем базу нашего приложения
    def __init__(self):
        super().__init__(ui.Window((400, 300), title = "My Game")) # Инициализируем менеджер
        style = ui.Style(borderradius=20, colortheme=ui.ColorThemeLibrary.material3_dark) # Создаем Style (необязательно)
        self.menu = ui.Menu(self.window, [100%ui.vw, 100%ui.vh], style = style, # Создаем меню
                            layout= ui.Grid([100%ui.vw, 100%ui.vh], row=3, column=3, # Создаем макет grid
                                            content = {
                                                (2, 2): ui.Button(lambda: print("You clicked!"), "КНОПКА!", [50%ui.fill, 50%ui.gc], style=style) # Создаем кнопку
                                            }
                                            )
                            )
    def on_draw(self):
        self.menu.draw() # Рисуем меню
    def on_update(self, events):
        self.menu.update() # Обновляем меню

game = MyGame()
game.run() # Запускаем готовое приложение
```
#### Императивный подход
```python
import nevu_ui as ui # Импортируем Nevu UI
import pygame

pygame.init()

window = ui.Window((400, 300), title = "My Game") # Создаем окно

style = ui.Style(borderradius=20, colortheme=ui.ColorThemeLibrary.material3_dark) # Создаем Style
menu = ui.Menu(window, [100%ui.vw, 100%ui.vh], style=style) # Создаем меню
layout = ui.Grid([100%ui.vw, 100%ui.vh], row=3, column=3) # Создаем макет grid
layout.add_item(ui.Button(lambda: print("You clicked!"), "КНОПКА!", [50%ui.fill, 50%ui.gc], style=style), x = 2, y = 2) # Создаем кнопку

menu.layout = layout # Задаем макет меню

while True: # Главный цикл
    events = pygame.event.get() # Получаем события
    window.update(events) # Обновляем окно
    menu.update() # Обновляем меню
    menu.draw() # Рисуем меню
    pygame.display.update() # Обновляем экран

```


### Результат примера
![Пример1](assets/result.png)

<br>

<p align="left">
  <img src="assets/RU/separator_status.png" alt="Style banner" width="600" />
</p>

---

### Статус Nevu UI на данный момент.

### **Макеты (Наследники Layout_Type)**

(✅ — сделано, ❌ — не сделано, 💾 — устарело/не работает)

*   ✅ `Grid`
*   ✅ `Row`
*   ✅ `Column`
*   ✅ `ScrollableRow`
*   ✅ `ScrollableColumn`
*   ✅ `ColorPicker`
*   💾 `Pages`
*   💾 `Gallery_Pages`
*   ✅ `StackColumn`
*   ✅ `StackRow`
*   ✅ `CheckBoxGroup`
*   ✅ `Panel`

### **Виджеты (Наследники Widget)**

*   ✅ `Widget`
*   ✅ `Button`
*   ✅ `Label`
*   ✅ `Input`
*   ✅ `EmptyWidget`
*   ✅ `Tooltip`
*   💾 `Gif`
*   ❌ `MusicPlayer` (Будет переработан, надеюсь)
*   ✅ `ProgressBar`
*   ✅ `SliderBar`
*   ✅ `ElementSwitcher`
*   💾 `FileDialog`
*   ✅ `RectCheckBox`
*   ✅ `Switch`

### **Доступные бэкенды**

*   ✅ `Pygame-ce`
*   ✅ `Sdl(Pygame-ce._sdl2)`
*   ✅ `RayLib`

## Бэкенд эксклюзивы

* `Ripple эффект` — **Raylib эксклюзив**
* `Настраиваемый центр и угол градиента` — **Raylib эксклюзив**
* `Tooltip` — **Pygame эксклюзив**

<br>

<p align="left">
  <img src="assets/RU/separator_license.png" alt="Style banner" width="600" />
</p>

---
### Nevu UI защищен лицензией MIT

<br>

<p align="left">
  <img src="assets/RU/separator_bugs.png" alt="Style banner" width="600" />
</p>

---
### `Nevu UI` - **НЕ** стабильный фреймворк, в нем могут встретиться много багов.
### Если вы нашли баг, пожалуйста, сообщите о нем в разделе [Issues](https://github.com/GolemBebrov/nevu-ui/issues)
<br>

<p align="left">
  <img src="assets/RU/separator_add_info.png" alt="Style banner" width="600" />
</p>

---


### **Gmail:** bebrovgolem@gmail.com
### **Создатель:** Никита А.
