![Example1](assets/title.png)

![alt text](https://img.shields.io/badge/License:-MIT-orange.svg)



# Brief Description
**Nevu UI** is a library for the declarative creation of user interfaces in Pygame. The project aims to provide developers with a set of ready-made, stylable, and extensible components for the rapid creation of modern and responsive interfaces in games and multimedia applications.

#### The main goal of Nevu UI: to make creating interfaces in python even easier and faster

### Key features include:
*   **Layout system:** Convenient arrangement of elements, for example, using grids (Grid) and scrollable containers (ScrollableColumn).
*   **Set of widgets:** Ready-to-use elements such as buttons, input fields, and labels.
*   **Flexible styling:** The ability to customize the appearance through a style system that supports colors, gradients, and borders.
*   **Animations:** Built-in support for animations to create dynamic and lively interfaces.
*   **Declarativeness:** Support for declarative interface creation

## Style

### Style - storage of parameters for customizing the appearance
Editable parameters:

* **Gradient**
* **ColorTheme** - Analogous to MaterialDesign, there is a ready-made set of themes - `ColorThemeLibrary`
* **Font name/size**
* **Border Width/Radius**
* **Text Align X/Y**
* **Transparency**

## Main Features

### Nevu UI allows you to describe an interface with a clear structure

Examples of declarativeness:

*   **Declarative approach:** Describe your interface just as you see it.
    ```python
    # Specify content directly when creating the layout
    grid = ui.Grid(content={(1,1): ui.Button(...)})
    ```
*   **Adaptive size system (`SizeRules`):** Forget about pixels. Use relative values that adjust to the size of the window or parent element.
    *   `vh` / `vw`: Percentage of the window's height/width.
    *   `fillx` / `filly` / `fill`: Percentage of the parent layout's height/width/size.
    *   `gc` / `gcw` / `gch`: Percentage of the grid cell size.
    *   Prefix `c`: can be placed in any SizeRule, it means that the current value will be taken (without the prefix, the original will be taken).
*   **Powerful style system:** Customize every aspect of the appearance using the universal `Style` object.
    *   **Themes:** Ready-made color themes in `ColorThemeLibrary`.
    *   **Gradients:** Support for linear and radial.
    *   **Inheritance:** Styles can be created based on existing ones.
    *   **And much more:** Fonts, borders, rounding, transparency.
*   **Built-in animations:** Bring your interface to life with ready-made animations for movement, transparency, etc.
    * There are **2** types of animations:
        *   **Start** - Allows you to set the initial appearance of the widget.
        *   **Infinite** - Produces an infinite animation defined in `animation_manager`.
    * Usage example:
       * ```widget.animation_manager.add_start_animation(ui.animations.EaseOut(...))```

Constant System (Constant Engine):

*   `ConstantEngine` is a convenient tool built into all layouts and widgets, it allows you to:
    * Declaratively add variables to the object's `__init__`
    * Check the variable type during initialization and after
    * The variable will not be visible in hints for `__init__` if it was not added to the class `TypedDict`
    * The variable will not be visible **IN ALL** hints if you do not specify the name and type at the beginning of the class
*   **Examples:**
    ```python
    import nevu_ui as ui
    from typing import Unpack, NotRequired

    #Create a TypedDict with variables (optional)
    class MyWidgetKwargs(ui.WidgetKwargs):
        my_var: NotRequired[int | float]

    class MyWidget(ui.Widget):
        #Create a typehint for the variable (optional but recommended)
        my_var: int | float
        def __init__(self, size: NvVector2 | list, style: Style = default_style, **constant_kwargs: Unpack[MyWidgetKwargs]):
            super().__init__(size, style, **constant_kwargs)

        #Override the function to add constants (mandatory)
        def _add_constants(self):
            super()._add_constants()

          #Add a constant (mandatory)
            self._add_constant('my_var', int | float)

            #You can also add a link to a constant
            #self._add_constant_link('my_var', 'my_var_new_name')

            #You can also block a constant if necessary
            #self._block_constant('my_var')
    ```

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
    * ```moderngl```
 ## Installation via pip
 ```python
 pip install nevu-ui
 ```

# Examples
![Example1](assets/test_grid.png)
---
![Example2](assets/test_main.png)

![Example3](assets/showcase.gif)

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
    def on_draw(self):
        self.menu.draw() #draw the menu
    def on_update(self, events):
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
*   ✅ `ScrollableRow`
*   ✅ `ScrollableColumn`
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
*   💾 `Image`
*   💾 `Gif`
*   ❌ `MusicPlayer` (Will be reworked)
*   ✅ `ProgressBar`
*   ✅ `SliderBar`
*   ✅ `ElementSwitcher`
*   💾 `FileDialog`
*   ✅ `RectCheckBox`

# License

**Nevu UI is protected by the MIT license**

# Additional Information

* **Gmail:** bebrovgolem@gmail.com
* **Creator:** Nikita A.