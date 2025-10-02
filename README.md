![Example1](assets/title.png)

![alt text](https://img.shields.io/badge/License:-MIT-orange.svg)


# Brief Description
**Nevu UI** is a library for the declarative creation of user interfaces in Pygame. The project aims to provide developers with a set of ready-made, stylable, and extensible components for the rapid creation of modern and responsive interfaces in games and multimedia applications.

#### The main goal of Nevu UI: to make creating interfaces in python even easier and faster

### Key features include:
*   **Layout system:** Convenient arrangement of elements, for example, using grids (Grid) and scrollable containers (Scrollable).
*   **Set of widgets:** Ready-to-use elements such as buttons, input fields, and labels.
*   **Flexible styling:** The ability to customize the appearance through a style system that supports colors, gradients, and borders.
*   **Animations:** Built-in support for animations to create dynamic and lively interfaces.
*   **Declarativeness:** Support for declarative interface creation

## Style

### Style - a universal storage of parameters for customizing the appearance
Editable parameters:

* **Gradient**
* **ColorTheme** - Analogous to MaterialDesign
* **Font name/size**
* **Border Width/Radius**
* **Text Align X/Y**
* **Transparency**

## Main Features

### Nevu UI allows you to describe an interface with a clear structure

Examples of declarativeness:
> *   **Declarative approach:** Describe your interface just as you see it.
>     ```python
>     # Specify content directly when creating the layout
>     grid = ui.Grid(content={(1,1): ui.Button(...)})
>     ```
>
> *   **Adaptive size system (`SizeRules`):** Forget about pixels. Use relative values that adjust to the size of the window or parent element.
>     *   `vh` / `vw`: Percentage of the window's height/width.
>     *   `fill`: Percentage of the parent layout's size.
> *   **Powerful style system:** Customize every aspect of the appearance using the universal `Style` object.
>     *   **Themes:** Ready-made color themes (`synthwave_dark_color_theme`).
>     *   **Gradients:** Linear and radial.
>     *   **And much more:** Fonts, borders, rounding, transparency.
>
> *   **Built-in animations:** Bring your interface to life with ready-made animations for appearance, movement, etc.
>     ```python
>     widget.animation_manager.add_start_animation(ui.animations.EaseOut(...))
>     ```

# Installation
  ## Dependencies:
  **```Python >= 3.12.*```**
  * For Building:
    * ```setuptools >= 61.0```
    * ```Cython```
    * ```numpy```
  * For Running:
    * ```pygame-ce>=2.3.0```
    * ```numpy```
    * ```Pillow```
 ## Installation via pip
 ```python
 pip install nevu-ui
 ```

# Examples
![Example1](assets/test_grid.png)
---
![Example2](assets/test_main.png)

---
### Basic Grid
#### Declarative Approach
```python
import nevu_ui as ui #Import Nevu UI
import pygame

pygame.init()

class MyGame(ui.Manager): #Create the base of our application
    def __init__(self):
        window = ui.Window((400, 300), title = "My Game") #Create a window
        super().__init__(window) #initialize the manager
        self.menu = ui.Menu(self.window, [100*ui.vw, 100*ui.vh], #Create a menu
                            layout= ui.Grid([100*ui.vw, 100*ui.vh], row=3, column=3, #Create a grid layout
                                            content = {
                                                (2, 2): ui.Button(lambda: print("You clicked!"), "Button", [50*ui.fill,33*ui.fill]) #Create a button
                                            }))
    def draw_loop(self):
        self.menu.draw() #draw the menu
    def update_loop(self, events):
        self.menu.update() #update the menu

game = MyGame()
game.run() #Run the finished application
```
#### Imperative Approach
```python
import nevu_ui as ui #Import Nevu UI
import pygame

pygame.init()

window = ui.Window((400, 300), title = "My Game") #Create a window

menu = ui.Menu(window, [100*ui.vw, 100*ui.vh]) #Create a menu

layout = ui.Grid([100*ui.vw, 100*ui.vh], row=3, column=3) #Create a grid layout
layout.add_item(ui.Button(lambda: print("You clicked!"), "Button", [50*ui.fill,33*ui.fill]), x = 2, y = 2) #Create a button

menu.layout = layout #Set the menu layout

while True: #Main loop
    events = pygame.event.get() #Get events
    window.update(events) #Update the window
    menu.update() #Update the menu
    menu.draw() #Draw the menu
    pygame.display.update() #Update the screen

```


### Example Result
![Example1](assets/result.png)
---
# Nevu UI Status at the Moment

### **Layouts (Layout_Type)**

(✅ - done, ❌ - not done, 💾 - deprecated)

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

### **Widgets (Widget)**

*   ✅ `Widget`
*   ✅ `Button`
*   ✅ `Label`
*   ✅ `Input`
*   ✅ `EmptyWidget`
*   ❌ `Tooltip` (In 0.6.X)
*   💾 `ImageWidget`
*   💾 `GifWidget`
*   ❌ `MusicPlayer` (Will be reworked)
*   💾 `ProgressBar`
*   💾 `SliderBar`
*   ✅ `ElementSwitcher`
*   💾 `FileDialog`
*   ✅ `RectCheckBox`

# License

**Nevu UI is protected by the MIT license**

# Additional Information

* **Gmail:** bebrovgolem@gmail.com
* **Creator:** Nikita A.