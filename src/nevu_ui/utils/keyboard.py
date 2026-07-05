import functools

import nevu_ui.core.modules as md
from nevu_ui.core.enums import Backend


class _BaseKeyboard:
    def update(self):
        pass

    def is_fdown(self, key_code: int):
        pass

    def is_down(self, key_code: int):
        pass

    def is_up(self, key_code: int):
        pass


def _keyboard_initialised_only(func):
    @functools.wraps(func)
    def wrapper(self, *args, **kwargs):
        return False if self._keys_now is None else func(self, *args, **kwargs)

    return wrapper


class PygameKeyboard:
    def __init__(self):
        self._keys_now = None
        self._keys_prev = None

    def update(self) -> None:
        if self._keys_now is None:
            self._keys_now = md.pygame.key.get_pressed()
            self._keys_prev = self._keys_now
            return
        self._keys_prev = self._keys_now
        self._keys_now = md.pygame.key.get_pressed()

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


class RaylibKeyboard:
    def __init__(self):
        pass

    def update(self):
        pass

    def is_fdown(self, key_code: int):
        """USE RAYLIB OR NEVU UI KEYS"""
        return md.rl.is_key_pressed(key_code)

    def is_down(self, key_code: int):
        """USE RAYLIB OR NEVU UI KEYS"""
        return md.rl.is_key_down(key_code)

    def is_up(self, key_code: int):
        """USE RAYLIB OR NEVU UI KEYS"""
        return md.rl.is_key_up(key_code)


def set_keyboard(backend: Backend):
    global keyboard
    if not isinstance(keyboard, UnselectedKeyboard):
        keyboard = UnselectedKeyboard()
    keyboard.select(backend)


class UnselectedKeyboard(_BaseKeyboard):
    def __init__(self):
        pass

    def select(self, backend: Backend):
        match backend:
            case Backend.Pygame | Backend.Sdl:
                self.__class__ = PygameKeyboard  # type: ignore
            case Backend.RayLib:
                self.__class__ = RaylibKeyboard  # type: ignore
        self.__init__()


keyboard: _BaseKeyboard = UnselectedKeyboard()  # type: ignore
