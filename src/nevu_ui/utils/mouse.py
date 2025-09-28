import pygame

from nevu_ui.fast.nvvector2 import NvVector2

class Mouse:
    STILL = 0
    FDOWN = 1
    DOWN = 2
    UP = 3
    
    WHEEL_DOWN = -10
    WHEEL_UP = 10
    WHEEL_STILL = 0

    def __init__(self):
        self._pos = NvVector2(0, 0)
        self._wheel_y = 0
        self._wheel_side = self.WHEEL_STILL # -10 = down 0 = still 10 = up
        self._states = [self.STILL, self.STILL, self.STILL]
        self.dragging = False

    @property
    def pos(self):
        return self._pos
    
    @property
    def wheel_y(self):
        return self._wheel_y

    @property
    def left_up(self):
        return self._states[0] == self.UP
    
    @property
    def left_fdown(self):
        return self._states[0] == self.FDOWN

    @property
    def left_down(self):
        return self._states[0] == self.DOWN

    @property
    def left_still(self):
        return self._states[0] == self.STILL

    @property
    def center_up(self):
        return self._states[1] == self.UP

    @property
    def center_fdown(self):
        return self._states[1] == self.FDOWN

    @property
    def center_down(self):
        return self._states[1] == self.DOWN

    @property
    def center_still(self):
        return self._states[1] == self.STILL
        
    @property
    def right_up(self):
        return self._states[2] == self.UP

    @property
    def right_fdown(self):
        return self._states[2] == self.FDOWN

    @property
    def right_down(self):
        return self._states[2] == self.DOWN

    @property
    def right_still(self):
        return self._states[2] == self.STILL
    
    @property
    def any_down(self):
        return self.left_down or self.right_down or self.center_down
    
    @property
    def any_fdown(self):
        return self.left_fdown or self.right_fdown or self.center_fdown
    
    @property
    def any_up(self):
        return self.left_up or self.right_up or self.center_up
    
    @property
    def wheel_up(self):
        return self._wheel_side == self.WHEEL_UP
    
    @property
    def wheel_down(self):
        return self._wheel_side == self.WHEEL_DOWN

    @property
    def wheel_still(self):
        return self._wheel_side == self.WHEEL_STILL

    @property
    def wheel_side(self):
        return self._wheel_side
    
    @property
    def any_wheel(self):
        return self._wheel_side in [self.WHEEL_DOWN, self.WHEEL_UP]
    
    def update_wheel(self, events):
        wheel_event_found = False
        for event in events:
            if event.type == pygame.MOUSEWHEEL:
                wheel_event_found = True
                new_wheel_y = event.y
                if new_wheel_y > 0:
                    self._wheel_side = self.WHEEL_UP
                elif new_wheel_y < 0:
                    self._wheel_side = self.WHEEL_DOWN
                else:
                    self._wheel_side = self.WHEEL_STILL
                self._wheel_y += event.y
                break
        if not wheel_event_found:
            self._wheel_side = self.WHEEL_STILL
    def update(self, events: list | None = None):
        if self.left_fdown: self.dragging = True
        elif self.left_up: self.dragging = False
        self._pos = NvVector2(pygame.mouse.get_pos()[0], pygame.mouse.get_pos()[1])
        pressed = pygame.mouse.get_pressed(num_buttons=3)
        
        if events and len(events) != 0:
            self.update_wheel(events)
        else:
            self._wheel_side = self.WHEEL_STILL
        
        for i in range(3):
            current_state = self._states[i]
            
            if pressed[i]:
                if current_state == self.STILL or current_state == self.UP:
                    self._states[i] = self.FDOWN
                else:
                    self._states[i] = self.DOWN
            else:
                if current_state == self.FDOWN or current_state == self.DOWN:
                    self._states[i] = self.UP
                else:
                    self._states[i] = self.STILL

mouse = Mouse()