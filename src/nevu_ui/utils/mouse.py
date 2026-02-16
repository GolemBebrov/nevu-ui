import pyray as rl
import pygame

from nevu_ui.fast.nvvector2 import NvVector2
from nevu_ui.core.enums import PressType, Backend

class MousePygame:
    def __init__(self):
        self._pos = NvVector2(0, 0)
        self._wheel_y = 0
        self._wheel_side = PressType.WheelStill # -10 = down 0 = still 10 = up
        self._states = [PressType.Still, PressType.Still, PressType.Still]
        self._up_states = {PressType.Still, PressType.Up}
        self.dragging = False

    @property
    def pos(self): return self._pos
    
    @property
    def wheel_y(self): return self._wheel_y

    @property
    def left_up(self): return self._states[0] == PressType.Up
    @property
    def left_fdown(self): return self._states[0] == PressType.Fdown
    @property
    def left_down(self): return self._states[0] == PressType.Down
    @property
    def left_still(self): return self._states[0] == PressType.Still

    @property
    def center_up(self): return self._states[1] == PressType.Up
    @property
    def center_fdown(self): return self._states[1] == PressType.Fdown
    @property
    def center_down(self): return self._states[1] == PressType.Down
    @property
    def center_still(self): return self._states[1] == PressType.Still
        
    @property
    def right_up(self): return self._states[2] == PressType.Up
    @property
    def right_fdown(self): return self._states[2] == PressType.Fdown
    @property
    def right_down(self): return self._states[2] == PressType.Down
    @property
    def right_still(self): return self._states[2] == PressType.Still
    
    @property
    def any_down(self): return self.left_down or self.right_down or self.center_down
    @property
    def any_fdown(self): return self.left_fdown or self.right_fdown or self.center_fdown
    @property
    def any_up(self): return self.left_up or self.right_up or self.center_up
    
    @property
    def wheel_up(self): return self._wheel_side == PressType.WheelUp
    @property
    def wheel_down(self): return self._wheel_side == PressType.WheelDown
    @property
    def wheel_still(self): return self._wheel_side == PressType.WheelStill
    @property
    def wheel_side(self): return self._wheel_side
    @property
    def any_wheel(self): return self._wheel_side in [PressType.WheelDown, PressType.WheelUp]
    
    def update_wheel(self, events):
        wheel_event_found = False
        for event in events:
            if event.type == pygame.MOUSEWHEEL:
                wheel_event_found = True
                new_wheel_y = event.y
                if new_wheel_y > 0: self._wheel_side = PressType.WheelUp
                elif new_wheel_y < 0: self._wheel_side = PressType.WheelDown
                else: self._wheel_side = PressType.WheelStill
                self._wheel_y += event.y
                break
        if not wheel_event_found:
            self._wheel_side = PressType.WheelStill
            
    def update(self, events: list | None = None):
        if self.left_fdown: self.dragging = True
        elif self.left_up: self.dragging = False
        self._pos = NvVector2(pygame.mouse.get_pos()[0], pygame.mouse.get_pos()[1])
        pressed = pygame.mouse.get_pressed()

        if events and len(events) != 0: self.update_wheel(events)
        else: self._wheel_side = PressType.WheelStill

        for i in range(3):
            current_state = self._states[i]
            is_up = current_state in self._up_states
            if pressed[i]:
                self._states[i] = PressType.Fdown if is_up else PressType.Down
            else:
                self._states[i] = PressType.Up if is_up else PressType.Still

class MouseRayLib(MousePygame):
    def __init__(self):
        self._pos = NvVector2(0, 0)
        self._states = [PressType.Still, PressType.Still, PressType.Still]
        self._up_states = {PressType.Still, PressType.Up}
        self._mouse_keys = tuple(enumerate((rl.MouseButton.MOUSE_BUTTON_LEFT, rl.MouseButton.MOUSE_BUTTON_MIDDLE, rl.MouseButton.MOUSE_BUTTON_RIGHT)))
        self._wheel_side = PressType.WheelStill
        
    def _get_state(self, button, state: PressType = PressType.Still):
        is_up = state in self._up_states
        if rl.is_mouse_button_down(button):
            return PressType.Fdown if is_up else PressType.Down
        else:
            return PressType.Up if is_up else PressType.Still
    
    def update_wheel(self): #type: ignore
        self._wheel_y = rl.get_mouse_wheel_move_v().y
        if self._wheel_y > 0: self._wheel_side = PressType.WheelUp
        elif self._wheel_y < 0: self._wheel_side = PressType.WheelDown
        else: self._wheel_side = PressType.WheelStill
    
    def update(self, *args, **kwargs): # type: ignore
        self.update_wheel()
        if rl.is_mouse_button_pressed(rl.MouseButton.MOUSE_BUTTON_LEFT):
            self.dragging = True
        elif rl.is_mouse_button_up(rl.MouseButton.MOUSE_BUTTON_LEFT):
            self.dragging = False
            
        for i, button in self._mouse_keys:
            self._states[i] = self._get_state(button, self._states[i])
            
        self._pos = NvVector2(rl.get_mouse_x(), rl.get_mouse_y())

def set_mouse(backend: Backend):
    assert isinstance(mouse, UnselectedMouse), "Mouse already selected"
    mouse.select(backend)

class UnselectedMouse:
    def __init__(self): pass
    def select(self, backend: Backend):
        match backend:
            case Backend.Pygame | Backend.Sdl: self.__class__ = MousePygame #type: ignore 
            case Backend.RayLib: self.__class__ = MouseRayLib #type: ignore
        self.__init__()

mouse: MousePygame | MouseRayLib = UnselectedMouse() # type: ignore