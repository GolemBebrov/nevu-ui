from .utils import *
import sys
import pygame

_context_to_draw = None

class Window:
    @staticmethod
    def cropToRatio(width: int, height: int, ratio, default=(0, 0)):
        # ...и этот метод остается без изменений, я гейлорд ска))) ЖОПА ЖОПА ЖОПА ПИСКА ЖОПА 
        if height == 0 or ratio[1] == 0: return default
        rx, ry = ratio
        aspect_ratio = width / height
        if abs(aspect_ratio - (rx / ry)) < 1e-6: return default
        
        if aspect_ratio > rx / ry:
            crop_width = width - (height * rx / ry)
            return crop_width, default[1]
        else:
            crop_height = height - (width * ry / rx)
            return default[0], crop_height

    def __init__(self, size, minsize=(10, 10), title="pygame window", resizable=True, ratio: NvVector2 | None = None):
        self._original_size = tuple(size)
        self.size = list(size)
        self.minsize = list(minsize)
        
        flags = pygame.RESIZABLE if resizable else 0
        
        flags |= pygame.HWSURFACE | pygame.DOUBLEBUF
        
        self.surface = pygame.display.set_mode(size, flags=flags)
        
        
        self._title = title
        pygame.display.set_caption(self._title)
        
        self._ratio = ratio or NvVector2(0, 0)
        self._clock = pygame.time.Clock()
        
        self._events: list[Event] = []
        self.last_events = []
        
        self._crop_width_offset = 0
        self._crop_height_offset = 0
        self._offset = NvVector2(0, 0)
        self._recalculate_render_area() 

        self._selected_context_menu = None

        self._next_update_dirty_rects = []
        
    def clear(self, color = (0, 0, 0)):
        """Fill the entire surface with the given color
        
        Args:
            color (tuple[int, int, int], optional): RGB color to fill with. Defaults to (0, 0, 0).
        """
        self.surface.fill(color)

    def _recalculate_render_area(self):
        current_w, current_h = self.surface.get_size()
        target_ratio = self._ratio if self._ratio else self._original_size
        
        self._crop_width_offset, self._crop_height_offset = self.cropToRatio(current_w, current_h, target_ratio)
        self._offset = NvVector2(self._crop_width_offset // 2, self._crop_height_offset // 2)
        
        render_width = self.size[0] - self._crop_width_offset
        render_height = self.size[1] - self._crop_height_offset

    def update(self, events, fps=60):
        
        """
        Updates the window state and processes events.

        Args:
            events (list[Event]): List of events to process.
            fps (int, optional): Desired frames per second. Defaults to 60.

        Processes all events in the list and updates the mouse, time, and keyboard states.
        If the window is resized, updates the size and recalculate the render area.
        If the right mouse button is released, opens the context menu at the mouse position.
        If the mouse is moved outside of the context menu, closes it.
        Limits the frame rate to the given value.
        """
        
        self.last_events = events
        mouse.update(events)
        time.update()
        keyboard.update()
        for item in keyboards_list:
            item.update()
            
        for event in events:
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
                
            if event.type == pygame.VIDEORESIZE:
                self.size = [event.w, event.h]
                self._recalculate_render_area()
                
                render_width = self.size[0] - self._crop_width_offset
                render_height = self.size[1] - self._crop_height_offset
                self._event_cycle(Event.RESIZE, [render_width, render_height])
                self._next_update_dirty_rects.append(pygame.Rect(0,0,*self.size))

            if mouse.right_up:
                if self._selected_context_menu:
                   self._selected_context_menu._open_context(mouse.pos)
            if mouse.any_down or mouse.any_fdown:
                if self._selected_context_menu:
                    if not self._selected_context_menu.get_rect().collidepoint(mouse.pos):
                        self._selected_context_menu._close_context()
                    
        self._clock.tick(fps)
        self._event_cycle(Event.UPDATE)

    @property
    def offset(self):
        return self._offset

    @property
    def title(self):
        return self._title

    @title.setter
    def title(self, text:str):
        self._title = text
        pygame.display.set_caption(self._title)

    @property
    def ratio(self):
        return self._ratio

    @ratio.setter
    def ratio(self, ratio: NvVector2):
        self._ratio = ratio
        self._recalculate_render_area()

    @property
    def original_size(self):
        return self._original_size

    def add_event(self,event:Event):
        self._events.append(event)

    def _event_cycle(self,type:int,*args, **kwargs):
        for event in self._events:
            if event.type == type:
                event(*args, **kwargs)
                
    @property
    def rel(self):
        render_width = self.size[0] - self._crop_width_offset
        render_height = self.size[1] - self._crop_height_offset
        return [render_width / self._original_size[0], render_height / self._original_size[1]]