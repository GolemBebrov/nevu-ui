import nevu_ui.core.modules as md 
from nevu_ui.core.state import nevu_state

_keys = {}
_keys_reversed = {}

def init_keys():
    global _keys, _keys_reversed
    if nevu_state.window.is_dtype.pygame or nevu_state.window.is_dtype.sdl:
        _keys = {
            "A": md.pygame.K_a, "B": md.pygame.K_b, "C": md.pygame.K_c, "D": md.pygame.K_d,
            "E": md.pygame.K_e, "F": md.pygame.K_f, "G": md.pygame.K_g, "H": md.pygame.K_h,
            "I": md.pygame.K_i, "J": md.pygame.K_j, "K": md.pygame.K_k, "L": md.pygame.K_l,
            "M": md.pygame.K_m, "N": md.pygame.K_n, "O": md.pygame.K_o, "P": md.pygame.K_p,
            "Q": md.pygame.K_q, "R": md.pygame.K_r, "S": md.pygame.K_s, "T": md.pygame.K_t,
            "U": md.pygame.K_u, "V": md.pygame.K_v, "W": md.pygame.K_w, "X": md.pygame.K_x,
            "Y": md.pygame.K_y, "Z": md.pygame.K_z,
            "Num0": md.pygame.K_0, "Num1": md.pygame.K_1, "Num2": md.pygame.K_2, "Num3": md.pygame.K_3,
            "Num4": md.pygame.K_4, "Num5": md.pygame.K_5, "Num6": md.pygame.K_6, "Num7": md.pygame.K_7,
            "Num8": md.pygame.K_8, "Num9": md.pygame.K_9,
            "F1": md.pygame.K_F1, "F2": md.pygame.K_F2, "F3": md.pygame.K_F3, "F4": md.pygame.K_F4,
            "F5": md.pygame.K_F5, "F6": md.pygame.K_F6, "F7": md.pygame.K_F7, "F8": md.pygame.K_F8,
            "F9": md.pygame.K_F9, "F10": md.pygame.K_F10, "F11": md.pygame.K_F11, "F12": md.pygame.K_F12,
            "Space": md.pygame.K_SPACE, "Escape": md.pygame.K_ESCAPE, "Enter": md.pygame.K_RETURN,
            "Tab": md.pygame.K_TAB, "Backspace": md.pygame.K_BACKSPACE, "Insert": md.pygame.K_INSERT,
            "Delete": md.pygame.K_DELETE, "Right": md.pygame.K_RIGHT, "Left": md.pygame.K_LEFT,
            "Down": md.pygame.K_DOWN, "Up": md.pygame.K_UP, "PageUp": md.pygame.K_PAGEUP,
            "PageDown": md.pygame.K_PAGEDOWN, "Home": md.pygame.K_HOME, "End": md.pygame.K_END,
            "LeftShift": md.pygame.K_LSHIFT, "RightShift": md.pygame.K_RSHIFT,
            "LeftCtrl": md.pygame.K_LCTRL, "RightCtrl": md.pygame.K_RCTRL,
            "LeftAlt": md.pygame.K_LALT, "RightAlt": md.pygame.K_RALT,
            "LeftSuper": md.pygame.K_LSUPER, "RightSuper": md.pygame.K_RSUPER,
            "Menu": md.pygame.K_MENU, "Minus": md.pygame.K_MINUS, "Equal": md.pygame.K_EQUALS,
            "LeftBracket": md.pygame.K_LEFTBRACKET, "RightBracket": md.pygame.K_RIGHTBRACKET,
            "Backslash": md.pygame.K_BACKSLASH, "Semicolon": md.pygame.K_SEMICOLON,
            "Apostrophe": md.pygame.K_QUOTE, "Grave": md.pygame.K_BACKQUOTE,
            "Comma": md.pygame.K_COMMA, "Period": md.pygame.K_PERIOD, "Slash": md.pygame.K_SLASH,
            "Kp0": md.pygame.K_KP0, "Kp1": md.pygame.K_KP1, "Kp2": md.pygame.K_KP2,
            "Kp3": md.pygame.K_KP3, "Kp4": md.pygame.K_KP4, "Kp5": md.pygame.K_KP5,
            "Kp6": md.pygame.K_KP6, "Kp7": md.pygame.K_KP7, "Kp8": md.pygame.K_KP8,
            "Kp9": md.pygame.K_KP9, "KpDecimal": md.pygame.K_KP_PERIOD,
            "KpDivide": md.pygame.K_KP_DIVIDE, "KpMultiply": md.pygame.K_KP_MULTIPLY,
            "KpMinus": md.pygame.K_KP_MINUS, "KpPlus": md.pygame.K_KP_PLUS,
            "KpEnter": md.pygame.K_KP_ENTER, "KpEqual": md.pygame.K_KP_EQUALS,
            "CapsLock": md.pygame.K_CAPSLOCK, "ScrollLock": md.pygame.K_SCROLLOCK,
            "NumLock": md.pygame.K_NUMLOCK, "PrintScreen": md.pygame.K_PRINTSCREEN,
            "Pause": md.pygame.K_PAUSE
        }
    elif nevu_state.window.is_dtype.raylib:
        _keys = {
            "A": md.rl.KeyboardKey.KEY_A, "B": md.rl.KeyboardKey.KEY_B, "C": md.rl.KeyboardKey.KEY_C, "D": md.rl.KeyboardKey.KEY_D,
            "E": md.rl.KeyboardKey.KEY_E, "F": md.rl.KeyboardKey.KEY_F, "G": md.rl.KeyboardKey.KEY_G, "H": md.rl.KeyboardKey.KEY_H,
            "I": md.rl.KeyboardKey.KEY_I, "J": md.rl.KeyboardKey.KEY_J, "K": md.rl.KeyboardKey.KEY_K, "L": md.rl.KeyboardKey.KEY_L,
            "M": md.rl.KeyboardKey.KEY_M, "N": md.rl.KeyboardKey.KEY_N, "O": md.rl.KeyboardKey.KEY_O, "P": md.rl.KeyboardKey.KEY_P,
            "Q": md.rl.KeyboardKey.KEY_Q, "R": md.rl.KeyboardKey.KEY_R, "S": md.rl.KeyboardKey.KEY_S, "T": md.rl.KeyboardKey.KEY_T,
            "U": md.rl.KeyboardKey.KEY_U, "V": md.rl.KeyboardKey.KEY_V, "W": md.rl.KeyboardKey.KEY_W, "X": md.rl.KeyboardKey.KEY_X,
            "Y": md.rl.KeyboardKey.KEY_Y, "Z": md.rl.KeyboardKey.KEY_Z,
            "Num0": md.rl.KeyboardKey.KEY_ZERO, "Num1": md.rl.KeyboardKey.KEY_ONE, "Num2": md.rl.KeyboardKey.KEY_TWO, "Num3": md.rl.KeyboardKey.KEY_THREE,
            "Num4": md.rl.KeyboardKey.KEY_FOUR, "Num5": md.rl.KeyboardKey.KEY_FIVE, "Num6": md.rl.KeyboardKey.KEY_SIX, "Num7": md.rl.KeyboardKey.KEY_SEVEN,
            "Num8": md.rl.KeyboardKey.KEY_EIGHT, "Num9": md.rl.KeyboardKey.KEY_NINE,
            "F1": md.rl.KeyboardKey.KEY_F1, "F2": md.rl.KeyboardKey.KEY_F2, "F3": md.rl.KeyboardKey.KEY_F3, "F4": md.rl.KeyboardKey.KEY_F4,
            "F5": md.rl.KeyboardKey.KEY_F5, "F6": md.rl.KeyboardKey.KEY_F6, "F7": md.rl.KeyboardKey.KEY_F7, "F8": md.rl.KeyboardKey.KEY_F8,
            "F9": md.rl.KeyboardKey.KEY_F9, "F10": md.rl.KeyboardKey.KEY_F10, "F11": md.rl.KeyboardKey.KEY_F11, "F12": md.rl.KeyboardKey.KEY_F12,
            "Space": md.rl.KeyboardKey.KEY_SPACE, "Escape": md.rl.KeyboardKey.KEY_ESCAPE, "Enter": md.rl.KeyboardKey.KEY_ENTER,
            "Tab": md.rl.KeyboardKey.KEY_TAB, "Backspace": md.rl.KeyboardKey.KEY_BACKSPACE, "Insert": md.rl.KeyboardKey.KEY_INSERT,
            "Delete": md.rl.KeyboardKey.KEY_DELETE, "Right": md.rl.KeyboardKey.KEY_RIGHT, "Left": md.rl.KeyboardKey.KEY_LEFT,
            "Down": md.rl.KeyboardKey.KEY_DOWN, "Up": md.rl.KeyboardKey.KEY_UP, "PageUp": md.rl.KeyboardKey.KEY_PAGE_UP,
            "PageDown": md.rl.KeyboardKey.KEY_PAGE_DOWN, "Home": md.rl.KeyboardKey.KEY_HOME, "End": md.rl.KeyboardKey.KEY_END,
            "LeftShift": md.rl.KeyboardKey.KEY_LEFT_SHIFT, "RightShift": md.rl.KeyboardKey.KEY_RIGHT_SHIFT,
            "LeftCtrl": md.rl.KeyboardKey.KEY_LEFT_CONTROL, "RightCtrl": md.rl.KeyboardKey.KEY_RIGHT_CONTROL,
            "LeftAlt": md.rl.KeyboardKey.KEY_LEFT_ALT, "RightAlt": md.rl.KeyboardKey.KEY_RIGHT_ALT,
            "LeftSuper": md.rl.KeyboardKey.KEY_LEFT_SUPER, "RightSuper": md.rl.KeyboardKey.KEY_RIGHT_SUPER,
            "Menu": md.rl.KeyboardKey.KEY_KB_MENU, "Minus": md.rl.KeyboardKey.KEY_MINUS, "Equal": md.rl.KeyboardKey.KEY_EQUAL,
            "LeftBracket": md.rl.KeyboardKey.KEY_LEFT_BRACKET, "RightBracket": md.rl.KeyboardKey.KEY_RIGHT_BRACKET,
            "Backslash": md.rl.KeyboardKey.KEY_BACKSLASH, "Semicolon": md.rl.KeyboardKey.KEY_SEMICOLON,
            "Apostrophe": md.rl.KeyboardKey.KEY_APOSTROPHE, "Grave": md.rl.KeyboardKey.KEY_GRAVE,
            "Comma": md.rl.KeyboardKey.KEY_COMMA, "Period": md.rl.KeyboardKey.KEY_PERIOD, "Slash": md.rl.KeyboardKey.KEY_SLASH,
            "Kp0": md.rl.KeyboardKey.KEY_KP_0, "Kp1": md.rl.KeyboardKey.KEY_KP_1, "Kp2": md.rl.KeyboardKey.KEY_KP_2,
            "Kp3": md.rl.KeyboardKey.KEY_KP_3, "Kp4": md.rl.KeyboardKey.KEY_KP_4, "Kp5": md.rl.KeyboardKey.KEY_KP_5,
            "Kp6": md.rl.KeyboardKey.KEY_KP_6, "Kp7": md.rl.KeyboardKey.KEY_KP_7, "Kp8": md.rl.KeyboardKey.KEY_KP_8,
            "Kp9": md.rl.KeyboardKey.KEY_KP_9, "KpDecimal": md.rl.KeyboardKey.KEY_KP_DECIMAL,
            "KpDivide": md.rl.KeyboardKey.KEY_KP_DIVIDE, "KpMultiply": md.rl.KeyboardKey.KEY_KP_MULTIPLY,
            "KpMinus": md.rl.KeyboardKey.KEY_KP_SUBTRACT, "KpPlus": md.rl.KeyboardKey.KEY_KP_ADD,
            "KpEnter": md.rl.KeyboardKey.KEY_KP_ENTER, "KpEqual": md.rl.KeyboardKey.KEY_KP_EQUAL,
            "CapsLock": md.rl.KeyboardKey.KEY_CAPS_LOCK, "ScrollLock": md.rl.KeyboardKey.KEY_SCROLL_LOCK,
            "NumLock": md.rl.KeyboardKey.KEY_NUM_LOCK, "PrintScreen": md.rl.KeyboardKey.KEY_PRINT_SCREEN,
            "Pause": md.rl.KeyboardKey.KEY_PAUSE, "VolumeUp": md.rl.KeyboardKey.KEY_VOLUME_UP, "VolumeDown": md.rl.KeyboardKey.KEY_VOLUME_DOWN
        }

    
    _keys_reversed = {v: k for k, v in _keys.items()}

class KeysMeta(type):
    def __getattr__(cls, key):
        return _keys[key]

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
    def revert(int_key: int) -> str: # type: ignore
        _keys_reversed[int_key]
