<p align="center">
  <img src="assets/title.png" alt="Nevu UI Intro Banner" width="800" />
</p>

![alt text](https://img.shields.io/badge/License:-MIT-orange.svg)

<a href="https://golembebrov.github.io/nevu-docs/">Nevu-UI documentation</a>

**Nevu UI** - это библиотека для простого создания GUI на `Python`. Nevu UI стремится предоставлять набор готовых настраиваемых компонентов и удобных инструментов для создания интерфейсов в играх и приложениях.

### Основные функции:
*   **Макеты:** Контейнеры, которые автоматически распологают элементы внутри себя, например `Grid`, `ScrollableColumn`.
*   **Виджеты:** Готовые графические элементы, например `Button`, `Label`, `Input`.
*   **Стилизация:** Кастомизация внешнего вида виджетов через `Style` под свои нужды.
*   **Анимации:** Поддержка анимаций через `AnimationManager`.
*   **Разные режимы создания интерфейса** Поддержка декларативного и императивного создания интерфейса с возможностью их совмещать.
*   **Несколько бекендов**: Поддержка `Raylib` и `Pygame`

---


<br>

<p align="left">
  <img src="assets/RU/separator_examples.png" alt="Style banner" width="600" />
</p>

---

![Пример1](assets/test_grid.png)

---

![Пример2](assets/test_main.png)

---

![Пример3](assets/showcase.gif)

---

### Пример: Кнопка в сетке 3x3
<h3>Декларативный способ</h3>

```python
import pygame

# Импортируем nevu-ui
import nevu_ui as ui

pygame.init()

window = ui.Window(size = (400, 300), title = "Nevu-UI application")

# Создаем стиль с какими либо визуальными параметрами
style = ui.Style(border_radius = 20, colortheme = ui.ColorThemeLibrary.material3_dark)

# Создаем главное меню
menu = ui.Menu(window, size = ui.fill_all, style = style,
    # Создаем сетку 3x3
    layout = ui.Grid(
        {
            (2, 2): ui.Button( # Создаем кнопку в ячейке 2, 2 (считая с 1)
                text = "Click me!",
                function = lambda: print("You clicked!"),
                size = (50 % ui.fill, 20 % ui.fill),
                style = style
            )
        },
        size = ui.fill_all,
        row = 3,
        column = 3
    )
)

if __name__ == "__main__":
    app = ui.Manager(window, [menu])
    app.run() # Запускаем главный цикл
```
<h3>Императивный способ</h3>

```python
import pygame

# Импортируем nevu-ui
import nevu_ui as ui

pygame.init()

# Создаем главное окно приложения
window = ui.Window(size = (400, 300), title = "Nevu-UI application")

# Создаем стиль с какими либо визуальными параметрами
style = ui.Style(
    border_radius = 20,
    colortheme = ui.ColorThemeLibrary.material3_dark
)

# Создаем начальный контейнер
menu = ui.Menu(window, size = (100 % ui.vw, 100 % ui.vh), style = style)

# Создаем сетку 3x3
grid = ui.Grid(size = (100 % ui.vw, 100 % ui.vh), row = 3, column = 3)

button = ui.Button(
    text = "Click me!",
    function = lambda: print("You clicked!"),
    size = (50 % ui.fill, 20 % ui.fill),
    style = style
)

# Добавляем виджет в ячейку с координатами 2, 2 (считая от 1)
grid.add_item(button, x = 2, y = 2)

# Передаем сетку в меню
menu.layout = grid

if __name__ == "__main__":
    while True:
        events = pygame.event.get()

        # Обновляем окно
        window.update(events)

        # Обновляем и отрисовываем menu
        menu.update()
        menu.draw()

        pygame.display.update()
```


### Результат примера:
![Пример1](assets/result.png)


<br>

<p align="left">
  <img src="assets/RU/separator_features.png" alt="Style banner" width="600" />
</p>

---



### Декларативность

  *   **Создание интерфейсов:**
      ```python
      # Указать содержимое макета можно прямо при его создании
      my_grid = Grid({(1, 1): Button(...)}, ...)
      ```
      ```python
      # При создании menu можно сразу указать макет
      menu_1 = Menu(..., layout = my_grid)
      ```
      ```python
      # Можно создать цикл отрисовки за 2 строки
      app = Manager(window, [menu_1])
      app.run()
      ```
*   **Система размеров:** Дает возможность использовать относительные величины для указания первоначальной высоты/ширины обьекта вместо пикселей.
    Пример использования:
    ```python
    from nevu_ui import vw, fill
    Widget(size = (30*vw, 50*fill))
    ```
    также можно использовать `%`
    ```python
    from nevu_ui import vw, fill
    Widget(size = (30%vw, 50%fill))
    ```
    Виды размеров:
    *   `vh` / `vw`: Проценты от высоты/ширины окна.
    *   `fillx` / `filly` / `fill`: Проценты от высоты/ширины/размера родительского макета.
    *   `gc` / `gcw` / `gch`: Проценты от размера ячейки сетки.
    *   Префикс `c`: можно поставить в начало любой величины (например `cvh`), он означает, что будет браться текущий размер окна/макета, без префикса будет браться оригинальная.
### Анимации:
  **25+ разных анимаций**
  * 2 режима работы анимаций:
      *   **Стартовая:** работает 1 раз после того как анимация загрузилась <br>```widget.animation_manager.add_start_animation(...)```
      *   **Бесконечная:** работает бесконечно и циклично. <br>```widget.animation_manager.add_continuous_animation(...)```
  * 4 вида анимаций:
      1. `Vector2Animation`: векторная анимация<br>Пример: с (0, 0) до (10, 10)
      2. `FloatAnimation`: числовая анимация<br>Пример: с 10 до 5.5
      3. `ColorAnimation`: цветовая анимация<br>Пример: с (255, 255, 200) до (0, 0, 0)
      4. `QueueAnimation`: составная анимация<br>Пример: с анимации1 до анимации2 и с анимации2 до анимации3
<br>

<p align="left">
  <img src="assets/RU/separator_installation.png" alt="Style banner" width="600" />
</p>

---

## Зависимости:
  **`Python >= 3.12`**
  * Для Сборки:
    * `setuptools`
    * `Cython`
    * `numpy`
  * Для Запуска:
    * `numpy`
  * Дополнительные библиотеки:
    * `pygame-ce`
    * `raylib`
    * `pyyaml`
 ## Установка через pip
 ```python
 pip install nevu-ui[all]
 ```

<br>

<p align="left">
  <img src="assets/RU/separator_status.png" alt="Style banner" width="600" />
</p>

---

### Список доступных элементов

### **Макеты**

*   `Grid`
*   `Row`
*   `Column`
*   `ScrollableRow`
*   `ScrollableColumn`
*   `ColorPicker`
*   `StackColumn`
*   `StackRow`
*   `CheckBoxGroup`

### **Виджеты**

*   `Widget`
*   `Button`
*   `Label`
*   `Input`
*   `EmptyWidget`
*   `Tooltip`
*   `ProgressBar`
*   `SliderBar`
*   `ElementSwitcher`
*   `RectCheckBox`
*   `Switch`

### **Доступные бэкенды**

*   `Pygame-ce`
*   `Sdl(Pygame-ce._sdl2)`
*   `RayLib`

## Бэкенд эксклюзивы

* `Эффект волны при клике` — **Raylib эксклюзив**
* `Настраиваемый центр и угол градиента` — **Raylib эксклюзив**

<br>

<p align="left">
  <img src="assets/RU/separator_license.png" alt="Style banner" width="600" />
</p>

---

### Nevu UI распространяется под лицензией MIT

<br>

<p align="left">
  <img src="assets/RU/separator_bugs.png" alt="Style banner" width="600" />
</p>

---

### `Nevu UI` - **НЕ** стабильный продукт, в нем могут встречаться много багов.
### Если вы нашли баг, пожалуйста, сообщите о нем в [Issues](https://github.com/GolemBebrov/nevu-ui/issues)
<br>

<p align="left">
  <img src="assets/RU/separator_add_info.png" alt="Style banner" width="600" />
</p>

---


### **Gmail:** bebrovgolem@gmail.com
### **Создатель:** GolemBebrov
