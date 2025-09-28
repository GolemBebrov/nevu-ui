import functools
import pygame

def _keyboard_initialised_only(func):
    @functools.wraps(func)
    def wrapper(self, *args, **kwargs):
        return False if self._keys_now is None else func(self, *args, **kwargs)
    
    return wrapper

class Keyboard:
    def __init__(self):
        self._keys_now = None
        self._keys_prev = None
    def update(self) -> None:
        if self._keys_now is None:
            self._keys_now = pygame.key.get_pressed()
            self._keys_prev = self._keys_now
            return
        self._keys_prev = self._keys_now
        self._keys_now = pygame.key.get_pressed()

    @_keyboard_initialised_only
    def is_fdown(self, key_code: int) -> bool:
        assert self._keys_now is not None and self._keys_prev is not None
        return self._keys_now[key_code] and not self._keys_prev[key_code]
    @_keyboard_initialised_only
    def is_down(self, key_code: int) -> bool:
        assert self._keys_now is not None and self._keys_prev is not None
        return self._keys_now[key_code]
    @_keyboard_initialised_only
    def is_up(self, key_code: int) -> bool:
        assert self._keys_now is not None and self._keys_prev is not None
        return not self._keys_now[key_code] and self._keys_prev[key_code]
    
keyboards_list = [] #DO NOT ADD, its DEAD

keyboard = Keyboard()