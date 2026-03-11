import pygame
import pyray
from nevu_ui.core.state import nevu_state

_pygame_keys = {
    "A": pygame.K_a, "B": pygame.K_b, "C": pygame.K_c, "D": pygame.K_d,
    "E": pygame.K_e, "F": pygame.K_f, "G": pygame.K_g, "H": pygame.K_h,
    "I": pygame.K_i, "J": pygame.K_j, "K": pygame.K_k, "L": pygame.K_l,
    "M": pygame.K_m, "N": pygame.K_n, "O": pygame.K_o, "P": pygame.K_p,
    "Q": pygame.K_q, "R": pygame.K_r, "S": pygame.K_s, "T": pygame.K_t,
    "U": pygame.K_u, "V": pygame.K_v, "W": pygame.K_w, "X": pygame.K_x,
    "Y": pygame.K_y, "Z": pygame.K_z,
    "Num0": pygame.K_0, "Num1": pygame.K_1, "Num2": pygame.K_2, "Num3": pygame.K_3,
    "Num4": pygame.K_4, "Num5": pygame.K_5, "Num6": pygame.K_6, "Num7": pygame.K_7,
    "Num8": pygame.K_8, "Num9": pygame.K_9,
    "F1": pygame.K_F1, "F2": pygame.K_F2, "F3": pygame.K_F3, "F4": pygame.K_F4,
    "F5": pygame.K_F5, "F6": pygame.K_F6, "F7": pygame.K_F7, "F8": pygame.K_F8,
    "F9": pygame.K_F9, "F10": pygame.K_F10, "F11": pygame.K_F11, "F12": pygame.K_F12,
    "Space": pygame.K_SPACE, "Escape": pygame.K_ESCAPE, "Enter": pygame.K_RETURN,
    "Tab": pygame.K_TAB, "Backspace": pygame.K_BACKSPACE, "Insert": pygame.K_INSERT,
    "Delete": pygame.K_DELETE, "Right": pygame.K_RIGHT, "Left": pygame.K_LEFT,
    "Down": pygame.K_DOWN, "Up": pygame.K_UP, "PageUp": pygame.K_PAGEUP,
    "PageDown": pygame.K_PAGEDOWN, "Home": pygame.K_HOME, "End": pygame.K_END,
    "LeftShift": pygame.K_LSHIFT, "RightShift": pygame.K_RSHIFT,
    "LeftCtrl": pygame.K_LCTRL, "RightCtrl": pygame.K_RCTRL,
    "LeftAlt": pygame.K_LALT, "RightAlt": pygame.K_RALT,
    "LeftSuper": pygame.K_LSUPER, "RightSuper": pygame.K_RSUPER,
    "Menu": pygame.K_MENU, "Minus": pygame.K_MINUS, "Equal": pygame.K_EQUALS,
    "LeftBracket": pygame.K_LEFTBRACKET, "RightBracket": pygame.K_RIGHTBRACKET,
    "Backslash": pygame.K_BACKSLASH, "Semicolon": pygame.K_SEMICOLON,
    "Apostrophe": pygame.K_QUOTE, "Grave": pygame.K_BACKQUOTE,
    "Comma": pygame.K_COMMA, "Period": pygame.K_PERIOD, "Slash": pygame.K_SLASH,
    "Kp0": pygame.K_KP0, "Kp1": pygame.K_KP1, "Kp2": pygame.K_KP2,
    "Kp3": pygame.K_KP3, "Kp4": pygame.K_KP4, "Kp5": pygame.K_KP5,
    "Kp6": pygame.K_KP6, "Kp7": pygame.K_KP7, "Kp8": pygame.K_KP8,
    "Kp9": pygame.K_KP9, "KpDecimal": pygame.K_KP_PERIOD,
    "KpDivide": pygame.K_KP_DIVIDE, "KpMultiply": pygame.K_KP_MULTIPLY,
    "KpMinus": pygame.K_KP_MINUS, "KpPlus": pygame.K_KP_PLUS,
    "KpEnter": pygame.K_KP_ENTER, "KpEqual": pygame.K_KP_EQUALS,
    "CapsLock": pygame.K_CAPSLOCK, "ScrollLock": pygame.K_SCROLLOCK,
    "NumLock": pygame.K_NUMLOCK, "PrintScreen": pygame.K_PRINTSCREEN,
    "Pause": pygame.K_PAUSE
}

_pyray_keys = {
    "A": pyray.KeyboardKey.KEY_A, "B": pyray.KeyboardKey.KEY_B, "C": pyray.KeyboardKey.KEY_C, "D": pyray.KeyboardKey.KEY_D,
    "E": pyray.KeyboardKey.KEY_E, "F": pyray.KeyboardKey.KEY_F, "G": pyray.KeyboardKey.KEY_G, "H": pyray.KeyboardKey.KEY_H,
    "I": pyray.KeyboardKey.KEY_I, "J": pyray.KeyboardKey.KEY_J, "K": pyray.KeyboardKey.KEY_K, "L": pyray.KeyboardKey.KEY_L,
    "M": pyray.KeyboardKey.KEY_M, "N": pyray.KeyboardKey.KEY_N, "O": pyray.KeyboardKey.KEY_O, "P": pyray.KeyboardKey.KEY_P,
    "Q": pyray.KeyboardKey.KEY_Q, "R": pyray.KeyboardKey.KEY_R, "S": pyray.KeyboardKey.KEY_S, "T": pyray.KeyboardKey.KEY_T,
    "U": pyray.KeyboardKey.KEY_U, "V": pyray.KeyboardKey.KEY_V, "W": pyray.KeyboardKey.KEY_W, "X": pyray.KeyboardKey.KEY_X,
    "Y": pyray.KeyboardKey.KEY_Y, "Z": pyray.KeyboardKey.KEY_Z,
    "Num0": pyray.KeyboardKey.KEY_ZERO, "Num1": pyray.KeyboardKey.KEY_ONE, "Num2": pyray.KeyboardKey.KEY_TWO, "Num3": pyray.KeyboardKey.KEY_THREE,
    "Num4": pyray.KeyboardKey.KEY_FOUR, "Num5": pyray.KeyboardKey.KEY_FIVE, "Num6": pyray.KeyboardKey.KEY_SIX, "Num7": pyray.KeyboardKey.KEY_SEVEN,
    "Num8": pyray.KeyboardKey.KEY_EIGHT, "Num9": pyray.KeyboardKey.KEY_NINE,
    "F1": pyray.KeyboardKey.KEY_F1, "F2": pyray.KeyboardKey.KEY_F2, "F3": pyray.KeyboardKey.KEY_F3, "F4": pyray.KeyboardKey.KEY_F4,
    "F5": pyray.KeyboardKey.KEY_F5, "F6": pyray.KeyboardKey.KEY_F6, "F7": pyray.KeyboardKey.KEY_F7, "F8": pyray.KeyboardKey.KEY_F8,
    "F9": pyray.KeyboardKey.KEY_F9, "F10": pyray.KeyboardKey.KEY_F10, "F11": pyray.KeyboardKey.KEY_F11, "F12": pyray.KeyboardKey.KEY_F12,
    "Space": pyray.KeyboardKey.KEY_SPACE, "Escape": pyray.KeyboardKey.KEY_ESCAPE, "Enter": pyray.KeyboardKey.KEY_ENTER,
    "Tab": pyray.KeyboardKey.KEY_TAB, "Backspace": pyray.KeyboardKey.KEY_BACKSPACE, "Insert": pyray.KeyboardKey.KEY_INSERT,
    "Delete": pyray.KeyboardKey.KEY_DELETE, "Right": pyray.KeyboardKey.KEY_RIGHT, "Left": pyray.KeyboardKey.KEY_LEFT,
    "Down": pyray.KeyboardKey.KEY_DOWN, "Up": pyray.KeyboardKey.KEY_UP, "PageUp": pyray.KeyboardKey.KEY_PAGE_UP,
    "PageDown": pyray.KeyboardKey.KEY_PAGE_DOWN, "Home": pyray.KeyboardKey.KEY_HOME, "End": pyray.KeyboardKey.KEY_END,
    "LeftShift": pyray.KeyboardKey.KEY_LEFT_SHIFT, "RightShift": pyray.KeyboardKey.KEY_RIGHT_SHIFT,
    "LeftCtrl": pyray.KeyboardKey.KEY_LEFT_CONTROL, "RightCtrl": pyray.KeyboardKey.KEY_RIGHT_CONTROL,
    "LeftAlt": pyray.KeyboardKey.KEY_LEFT_ALT, "RightAlt": pyray.KeyboardKey.KEY_RIGHT_ALT,
    "LeftSuper": pyray.KeyboardKey.KEY_LEFT_SUPER, "RightSuper": pyray.KeyboardKey.KEY_RIGHT_SUPER,
    "Menu": pyray.KeyboardKey.KEY_KB_MENU, "Minus": pyray.KeyboardKey.KEY_MINUS, "Equal": pyray.KeyboardKey.KEY_EQUAL,
    "LeftBracket": pyray.KeyboardKey.KEY_LEFT_BRACKET, "RightBracket": pyray.KeyboardKey.KEY_RIGHT_BRACKET,
    "Backslash": pyray.KeyboardKey.KEY_BACKSLASH, "Semicolon": pyray.KeyboardKey.KEY_SEMICOLON,
    "Apostrophe": pyray.KeyboardKey.KEY_APOSTROPHE, "Grave": pyray.KeyboardKey.KEY_GRAVE,
    "Comma": pyray.KeyboardKey.KEY_COMMA, "Period": pyray.KeyboardKey.KEY_PERIOD, "Slash": pyray.KeyboardKey.KEY_SLASH,
    "Kp0": pyray.KeyboardKey.KEY_KP_0, "Kp1": pyray.KeyboardKey.KEY_KP_1, "Kp2": pyray.KeyboardKey.KEY_KP_2,
    "Kp3": pyray.KeyboardKey.KEY_KP_3, "Kp4": pyray.KeyboardKey.KEY_KP_4, "Kp5": pyray.KeyboardKey.KEY_KP_5,
    "Kp6": pyray.KeyboardKey.KEY_KP_6, "Kp7": pyray.KeyboardKey.KEY_KP_7, "Kp8": pyray.KeyboardKey.KEY_KP_8,
    "Kp9": pyray.KeyboardKey.KEY_KP_9, "KpDecimal": pyray.KeyboardKey.KEY_KP_DECIMAL,
    "KpDivide": pyray.KeyboardKey.KEY_KP_DIVIDE, "KpMultiply": pyray.KeyboardKey.KEY_KP_MULTIPLY,
    "KpMinus": pyray.KeyboardKey.KEY_KP_SUBTRACT, "KpPlus": pyray.KeyboardKey.KEY_KP_ADD,
    "KpEnter": pyray.KeyboardKey.KEY_KP_ENTER, "KpEqual": pyray.KeyboardKey.KEY_KP_EQUAL,
    "CapsLock": pyray.KeyboardKey.KEY_CAPS_LOCK, "ScrollLock": pyray.KeyboardKey.KEY_SCROLL_LOCK,
    "NumLock": pyray.KeyboardKey.KEY_NUM_LOCK, "PrintScreen": pyray.KeyboardKey.KEY_PRINT_SCREEN,
    "Pause": pyray.KeyboardKey.KEY_PAUSE, "VolumeUp": pyray.KeyboardKey.KEY_VOLUME_UP, "VolumeDown": pyray.KeyboardKey.KEY_VOLUME_DOWN
}

_pygame_keys_reversed = {v: k for k, v in _pygame_keys.items()}
_pyray_keys_reversed = {v: k for k, v in _pyray_keys.items()}

class KeysMeta(type):
    def __getattr__(cls, key):
        if not cls._main_keys:
            if nevu_state.window.is_dtype.raylib:
                cls._main_keys = _pyray_keys
            else:
                cls._main_keys = _pygame_keys
        return cls._main_keys[key]

class Keys(metaclass=KeysMeta):
    _main_keys = None
    A: int; B: int; C: int; D: int; E: int; F: int; G: int; H: int; I: int; J: int
    K: int; L: int; M: int; N: int; O: int; P: int; Q: int; R: int; S: int; T: int
    U: int; V: int; W: int; X: int; Y: int; Z: int
    Num0: int; Num1: int; Num2: int; Num3: int; Num4: int
    Num5: int; Num6: int; Num7: int; Num8: int; Num9: int
    F1: int; F2: int; F3: int; F4: int; F5: int; F6: int
    F7: int; F8: int; F9: int; F10: int; F11: int; F12: int
    Space: int; Escape: int; Enter: int; Tab: int; Backspace: int
    Insert: int; Delete: int; Right: int; Left: int; Down: int; Up: int
    PageUp: int; PageDown: int; Home: int; End: int
    LeftShift: int; RightShift: int; LeftCtrl: int; RightCtrl: int
    LeftAlt: int; RightAlt: int; LeftSuper: int; RightSuper: int; Menu: int
    Minus: int; Equal: int; LeftBracket: int; RightBracket: int
    Backslash: int; Semicolon: int; Apostrophe: int; Grave: int
    Comma: int; Period: int; Slash: int
    Kp0: int; Kp1: int; Kp2: int; Kp3: int; Kp4: int; Kp5: int
    Kp6: int; Kp7: int; Kp8: int; Kp9: int
    KpDecimal: int; KpDivide: int; KpMultiply: int; KpMinus: int
    KpPlus: int; KpEnter: int; KpEqual: int
    CapsLock: int; ScrollLock: int; NumLock: int
    PrintScreen: int; Pause: int; VolumeUp: int; VolumeDown: int
    @staticmethod
    def revert(int_key: int) -> str:
        if nevu_state.window.is_dtype.raylib:
            return _pyray_keys_reversed[int_key]
        return _pygame_keys_reversed[int_key]
