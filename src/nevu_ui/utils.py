import pygame
import numpy as np
import time as tt
import functools

from .fast_shapes import _create_outlined_rounded_rect_sdf, _create_rounded_rect_surface_optimized

from .core_types import (
    CacheName, CacheType, EventType
)
from .fast_nvvector2 import NvVector2

class Cache:
    def __init__(self):
        self.name = CacheName.MAIN
        self.cache_default = {
            CacheType.Coords: None,
            CacheType.RelSize: None,
            CacheType.Surface: None,
            CacheType.Gradient: None,
            CacheType.Image: None,
            CacheType.Borders: None,
            CacheType.Scaled_Background: None,
            CacheType.Background: None,
            CacheType.Scaled_Gradient: None
            
        }
        self.cache = {
            CacheName.MAIN: self.cache_default.copy(),
            CacheName.PREVERSED: self.cache_default.copy(),
            CacheName.CUSTOM: self.cache_default.copy()
        }
    def set_name(self, name: CacheName):
        self.name = name
    def clear(self, name = None):
        name = name if name else self.name
        self.cache[name] = self.cache_default.copy()
    def clear_selected(self, blacklist = None, whitelist = None, name = None):
        name = name if name else self.name
        cachename = self.cache[name]
        blacklist = [] if blacklist is None else blacklist
        whitelist = [CacheType.RelSize,
                     CacheType.Coords,
                     CacheType.Surface,
                     CacheType.Gradient,
                     CacheType.Image,
                     CacheType.Borders,
                     CacheType.Scaled_Background,
                     CacheType.Scaled_Gradient,
                     CacheType.Background
                    ] if whitelist is None else whitelist
        for item, value in cachename.items():
            if not item in blacklist and item in whitelist:
                cachename[item] = None
    def get(self, type: CacheType, name = None):
        name = name or self.name
        return self.cache[name][type]
    def set(self, type: CacheType, value, name = None):
        name = name or self.name
        self.cache[name][type] = value
    def get_or_set_val(self, type: CacheType, value, name = None):
        name = name or self.name
        if self.cache[name][type] is None:
            self.cache[name][type] = value
        return self.cache[name][type]
    def get_or_exec(self, type: CacheType, func, name = None):
        name = name or self.name
        if self.cache[name][type] is None:
            self.cache[name][type] = func()
        return self.cache[name][type]
    def __getattr__(self, type):
        return self.cache[self.name][type]
    def __getitem__(self, key: CacheType):
        if not isinstance(key, CacheType):
            raise TypeError("Ключ для доступа к кешу должен быть типа CacheType")
        return self.cache[self.name][key]
"""  
class NvVector2(pygame.Vector2):
    def __mul__(self, other):
        if isinstance(other, pygame.Vector2):
            return NvVector2(self.x * other.x, self.y * other.y)
        return NvVector2(super().__mul__(other))

    def __rmul__(self, other):
        return self.__mul__(other)

    def __neg__(self):
        return NvVector2(-self.x, -self.y)

    def __add__(self, other):
        if isinstance(other, pygame.Vector2):
            return NvVector2(self.x + other.x, self.y + other.y)
        return NvVector2(super().__add__(other))

    def __radd__(self, other):
        return self.__add__(other)

    def __sub__(self, other):
        if isinstance(other, pygame.Vector2):
            return NvVector2(self.x - other.x, self.y - other.y)
        return NvVector2(super().__sub__(other))

    def __rsub__(self, other):
        if isinstance(other, pygame.Vector2):
            return NvVector2(other.x - self.x, other.y - self.y)
        return NvVector2(super().__rsub__(other))

    def to_int(self):
        return NvVector2(int(self.x), int(self.y))

    def to_float(self):
        return NvVector2(float(self.x), float(self.y))

    def to_abs(self):
        return NvVector2(abs(self.x), abs(self.y))

    def to_neg(self):
        return NvVector2(-self.x, -self.y)

    def for_each(self, func):
        return NvVector2(func(self.x), func(self.y))
"""

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
class Time():
    def __init__(self):
        """
        Initializes the Time object with default delta time, frames per second (fps),
        and timestamps for time calculations.

        Attributes:
            delta_time/dt (float): The time difference between the current and last frame.
            fps (int): Frames per second, calculated based on delta time.
            now (float): The current timestamp.
            after (float): The timestamp of the previous frame.
        """
        self._delta_time = 1.0
        self._fps = np.int16()
        self._now = tt.time()
        self._after = tt.time()
    @property
    def delta_time(self):
        return float(self._delta_time)
    @property
    def dt(self):
        return float(self._delta_time)
    @property
    def fps(self):
        return int(self._fps)
    def _calculate_delta_time(self):
        self._now = tt.time()
        self._delta_time = self._now - self._after
        self._after = self._now
    def _calculate_fps(self):
        try:
            self._fps = np.int16(int(1 / (self.delta_time)))
        except:
            self._fps = 0
    def update(self):
        self._calculate_delta_time()
        self._calculate_fps()

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
time = Time()
mouse = Mouse()


class Event:
    DRAW = 0
    UPDATE = 1
    RESIZE = 2
    RENDER = 3
    def __init__(self,type,function,*args, **kwargs):
        """
        Initializes an Event object with a type, function, and optional arguments.

        Parameters:
        type (int): The type of event, indicating the kind of operation.
        function (callable): The function to be executed when the event is triggered.
        *args: Variable length argument list to be passed to the function.
        **kwargs: Arbitrary keyword arguments to be passed to the function.
        """
        self.type = type
        
        self._function = function
        self._args = args
        self._kwargs = kwargs
    def __call__(self,*args, **kwargs):
        if args: self._args = args
        if kwargs: self._kwargs = kwargs
        self._function(*self._args, **self._kwargs)

class NevuEvent:
    def __init__(self, sender, function, type: EventType, *args, **kwargs):
        self._sender = sender
        self._function = function
        self._type = type
        self._args = args
        self._kwargs = kwargs
        
    def __call__(self, *args, **kwargs):
        if args: self._args = args
        if kwargs: self._kwargs = kwargs
        try:
            self._function(*self._args, **self._kwargs)
        except Exception as e:
            print(f"Event function execution Error: {e}")
    def __repr__(self) -> str:
        return f"Event(sender={self._sender}, function={self._function}, type={self._type}, args={self._args}, kwargs={self._kwargs})"

class InputType:
    NUMBERS = "0123456789"
    HEX_DIGITS = f"{NUMBERS}abcdefABCDEF"

    LETTERS_ENG = "qwertyuiopasdfghjklzxcvbnmQWERTYUIOPASDFGHJKLZXCVBNM"
    LETTERS_RUS = "йцукенгшщзхъфывапролджэячсмитьбюЙЦУКЕНГШЩЗХЪФЫВАПРОЛДЖЭЯЧСМИТЬБЮ"
    LETTERS_UKR = "абвгґдеєжзиіїйклмнопрстуфхцчшщьюяАБВГҐДЕЄЖЗИІЇЙКЛМНОПРСТУФХЦЧШЩЬЮЯ"
    LETTERS_BEL = "абвгдеёжзійклмнопрстуўфхцчшыьэюяАБВГДЕЁЖЗІЙКЛМНОПРСТУЎФХЦЧШЫЬЭЮЯ"
    
    LETTERS_GER = f"{LETTERS_ENG}äöüÄÖÜß"
    LETTERS_FR = f"{LETTERS_ENG}àâçéèêëîïôûüÿæœÀÂÇÉÈÊËÎÏÔÛÜŸÆŒ"
    LETTERS_ES = f"{LETTERS_ENG}áéíóúüñÁÉÍÓÚÜÑ"
    LETTERS_IT = f"{LETTERS_ENG}àèéìòóùÀÈÉÌÒÓÙ"
    LETTERS_PL = f"{LETTERS_ENG}ąćęłńóśźżĄĆĘŁŃÓŚŹŻ"
    LETTERS_PT = f"{LETTERS_ENG}àáâãçéêíóôõúüÀÁÂÃÇÉÊÍÓÔÕÚÜ"
    
    LETTERS_GR = "αβγδεζηθικλμνξοπρστυφχψωΑΒΓΔΕΖΗΘΙΚΛΜΝΞΟΠΡΣΤΥΦΧΨΩ"
    LETTERS_AR = "ءآأؤإئابةتثجحخدذرزسشصضطظعغفقكلمنهوي"
    LETTERS_HE = "אבגדהוזחטיכךלמםנןסעפףצץקרשת"
    LETTERS_JP_KANA = "ァアィイゥウェエォオカガキギクグケゲコゴサザシジスズセゼソゾタダチヂッツヅテデトドナニヌネノハバパヒビピフブプヘベペホボポマミムメモャヤュユョヨラリルレロワヲンーぁあぃいぅうぇえぉおかがきぎくぐけげこごさざしじすずせぜそぞただちぢっつづてでとどなにぬねのはばぱひびぴふぶぷへべぺほぼぽまみむめもゃやゅゆょよらりるれろゎわをん"
    LETTERS_CN_COMMON = "的一是不了人我在有他这为之大来以个中上们"
    LETTERS_KR_HANGUL = "ㄱㄲㄴㄷㄸㄹㅁㅂㅃㅅㅆㅇㅈㅉㅊㅋㅌㅍㅎㅏㅐㅑㅒㅓㅔㅕㅖㅗㅘㅙㅚㅛㅜㅝㅞㅟㅠㅡㅢㅣ"
    LETTERS_HI_DEVANAGARI = "अआइईउऊऋएऐओऔकखगघङचछजझञटठडढणतथदधनपफबभमयरलवशषसह"

    WHITESPACE = " \t\n\r\f\v"
    CONTROL_CHARS = "".join(chr(i) for i in range(32))

    PUNCTUATION = "!\"#$%&'()*+,-./:;<=>?@[\\]^_`{|}~"
    DASHES = "-—‒–"
    QUOTES = "\"'`«»"
    BRACKETS = "()[]{}"
    APOSTROPHE = "'"
    
    MATH_BASIC = "+-*/="
    MATH_ADVANCED = "><≤≥≠≈±√∑∫"
    CURRENCY = "€£¥₽$"
    MATH_GREEK = "πΩΣΔΘΛΞΦΨΓ"
    
    URL_SYMBOLS = f"{LETTERS_ENG}{NUMBERS}-._~:/?#[]@!$&'()*+,;=%"
    EMAIL_SYMBOLS = f"{LETTERS_ENG}{NUMBERS}-._%+"
    
    MARKDOWN = "*_`~>#+![]()="
    EMOJIS_BASIC = "😀😂😍🤔👍👎❤️💔"
    SPECIAL_SYMBOLS = "©®™°№§"
    BOX_DRAWING = "─│┌┐└┘├┤┬┴┼═║╔╗╚╝╠╣╦╩╬"

    ALL_CYRILLIC_LETTERS = "".join(set(LETTERS_RUS + LETTERS_UKR + LETTERS_BEL))
    ALL_LATIN_EXT_LETTERS = "".join(set(LETTERS_GER + LETTERS_FR + LETTERS_ES + LETTERS_IT + LETTERS_PL + LETTERS_PT))
    ALL_LETTERS = "".join(set(ALL_CYRILLIC_LETTERS + ALL_LATIN_EXT_LETTERS + LETTERS_GR + LETTERS_AR + LETTERS_HE + LETTERS_JP_KANA + LETTERS_CN_COMMON + LETTERS_KR_HANGUL + LETTERS_HI_DEVANAGARI))

    ALL_PUNCTUATION = "".join(set(PUNCTUATION + DASHES + QUOTES + BRACKETS + APOSTROPHE))
    ALL_MATH = "".join(set(MATH_BASIC + MATH_ADVANCED + CURRENCY + MATH_GREEK))
    ALL_SYMBOLS = "".join(set(ALL_PUNCTUATION + ALL_MATH + MARKDOWN + EMOJIS_BASIC + SPECIAL_SYMBOLS + BOX_DRAWING))
    
    ALPHANUMERIC_ENG = LETTERS_ENG + NUMBERS
    ALPHANUMERIC_RUS = LETTERS_RUS + NUMBERS

    PRINTABLE = ALL_LETTERS + NUMBERS + ALL_SYMBOLS + WHITESPACE

class Convertor:
    @staticmethod
    def convert(item, to_type):
        if to_type is pygame.Vector2:
            return Convertor._to_vector2(item)
        if to_type is tuple or to_type is list:
            return Convertor._to_iterable(item, to_type)
        if to_type is int:
            return Convertor.to_int(item)
        if to_type is float:
            return Convertor.to_float(item)
        return item

    @staticmethod
    def to_int(item):
        if isinstance(item, int):
            return item
        if isinstance(item, float):
            return int(item)
        if isinstance(item, pygame.Vector2):
            return int(item.length())
        raise ValueError(f"Can't convert {type(item).__name__} to int")

    @staticmethod
    def to_float(item):
        if isinstance(item, float):
            return item
        if isinstance(item, int):
            return float(item)
        if isinstance(item, pygame.Vector2):
            return float(item.length())
        raise ValueError(f"Can't convert {type(item).__name__} to float")

    @staticmethod
    def _to_vector2(item):
        if isinstance(item, pygame.Vector2):
            return item
        if isinstance(item, (list, tuple)) and len(item) == 2:
            return pygame.Vector2(item)
        raise ValueError(f"Can't convert {type(item).__name__} to Vector2")

    @staticmethod
    def _to_iterable(item, needed_type):
        if isinstance(item, needed_type):
            return item
        if isinstance(item, (list, tuple)):
            return needed_type(item)
        
        raise ValueError(f"Can't convert {type(item).__name__} to {needed_type.__name__}")