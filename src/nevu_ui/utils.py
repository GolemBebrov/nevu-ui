import pygame
import numpy as np
import time as tt
from enum import Enum, auto, StrEnum
import functools
from .fast_shapes import _create_outlined_rounded_rect_sdf, _create_rounded_rect_surface_optimized

class RenderMode(Enum):
    AA = auto()
    SDF = auto()

class CacheType(Enum):
    #Used in widgets
    Coords = auto()
    RelSize = auto()
    Surface = auto()
    Gradient = auto()
    Image = auto()
    Borders = auto()
    Scaled_Background = auto()
    Scaled_Gradient = auto()
    Background = auto()

class CacheName(StrEnum):
    MAIN = "main"
    PREVERSED = "preversed"
    CUSTOM = "custom"
    #...

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
class NvVector3(pygame.Vector3):
    def __mul__(self, other):
        if isinstance(other, pygame.Vector3):
            return NvVector3(self.x * other.x, self.y * other.y, self.z * other.z)
        return super().__mul__(other)

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


class Mouse:
    STILL = 0
    FDOWN = 1
    DOWN = 2
    UP = 3
    
    WHEEL_DOWN = -10
    WHEEL_UP = 10
    WHEEL_STILL = 0

    def __init__(self):
        self._pos = (0, 0)
        self._wheel_y = 0
        self._wheel_side = self.WHEEL_STILL # -10 = down 0 = still 10 = up
        self._states = [self.STILL, self.STILL, self.STILL]

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
        self._pos = pygame.mouse.get_pos()
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

class EventType(Enum):
    Resize = auto()
    Render = auto()
    Draw = auto()
    Update = auto()
    OnKeyUp = auto()
    OnKeyDown = auto()
    OnHover = auto()
    OnUnhover = auto()
    OnMouseScroll = auto()
    

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

class InputType:
    NUMBERS = "0123456789"
    HEX_DIGITS = NUMBERS + "abcdefABCDEF"

    LETTERS_ENG = "qwertyuiopasdfghjklzxcvbnmQWERTYUIOPASDFGHJKLZXCVBNM"
    LETTERS_RUS = "йцукенгшщзхъфывапролджэячсмитьбюЙЦУКЕНГШЩЗХЪФЫВАПРОЛДЖЭЯЧСМИТЬБЮ"
    LETTERS_UKR = "абвгґдеєжзиіїйклмнопрстуфхцчшщьюяАБВГҐДЕЄЖЗИІЇЙКЛМНОПРСТУФХЦЧШЩЬЮЯ"
    LETTERS_BEL = "абвгдеёжзійклмнопрстуўфхцчшыьэюяАБВГДЕЁЖЗІЙКЛМНОПРСТУЎФХЦЧШЫЬЭЮЯ"
    
    LETTERS_GER = LETTERS_ENG + "äöüÄÖÜß"
    LETTERS_FR = LETTERS_ENG + "àâçéèêëîïôûüÿæœÀÂÇÉÈÊËÎÏÔÛÜŸÆŒ"
    LETTERS_ES = LETTERS_ENG + "áéíóúüñÁÉÍÓÚÜÑ"
    LETTERS_IT = LETTERS_ENG + "àèéìòóùÀÈÉÌÒÓÙ"
    LETTERS_PL = LETTERS_ENG + "ąćęłńóśźżĄĆĘŁŃÓŚŹŻ"
    LETTERS_PT = LETTERS_ENG + "àáâãçéêíóôõúüÀÁÂÃÇÉÊÍÓÔÕÚÜ"
    
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
    
    URL_SYMBOLS = LETTERS_ENG + NUMBERS + "-._~:/?#[]@!$&'()*+,;=%"
    EMAIL_SYMBOLS = LETTERS_ENG + NUMBERS + "-._%+"
    
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
    @classmethod
    def convert(cls, item, to_type):
        match to_type:
            case pygame.Vector2:
                return cls._convertion_vector2(item)
            case list() | tuple():
                return cls._to_iterable(item, to_type)
            case int():
                return cls.to_int(item)
            case float():
                return cls.to_float(item)
            case _:
                return item
    def to_int(item):
        _error = ValueError(f"Can't convert {item} to int")
        match type(item):
            case int():
                return item
            case float():
                return int(item)
            case pygame.Vector2:
                return int(item.length())
            case _:
                raise _error
    def to_float(item):
        _error = ValueError(f"Can't convert {item} to float")
        match type(item):
            case float():
                return item
            case int():
                return float(item)
            case pygame.Vector2:
                return float(item.length())
            case _:
                raise _error
    def _convertion_vector2(item):
        _error = ValueError(f"Can't convert {item} to Vector2")
        match type(item):
            case pygame.Vector2:
                return item
            case list() | tuple():
                if len(item) == 2:
                    return pygame.Vector2(item[0], item[1])
                else:
                    raise _error
        raise _error
    def _to_iterable(item, needed_type):
        _error = ValueError(f"Can't convert {item} to {needed_type}")
        match type(item):
            case needed_type():
                return item
            case list() | tuple():
                return needed_type(*item)
            case _:
                return needed_type(item)
        raise _error

class RoundedRect:
    _convertor = Convertor
    @classmethod
    def create_AA(cls, size, radius, color, AA_factor = 4):
        size = cls._convertor.convert(size, tuple)
        radius = cls._convertor.convert(radius, int)
        color = cls._convertor.convert(color, tuple)
        AA_factor = cls._convertor.convert(AA_factor, int)
        return _create_rounded_rect_AA(size, radius, color, AA_factor)
    @classmethod
    def create_sdf(cls, size, radius, color):
        return _create_rounded_rect_surface_optimized(tuple(size), radius, color)

class Rect:
    _convertor = Convertor
    @classmethod
    def create_AA(cls, size, color, AA_factor = 4):
        size = cls._convertor.convert(size, tuple)
        color = cls._convertor.convert(color, tuple)
        AA_factor = cls._convertor.convert(AA_factor, int)
        return _create_rounded_rect_AA(size, 0, color, AA_factor)

    @classmethod
    def create_sdf(cls, size, color):
        size = cls._convertor.convert(size, tuple)
        color = cls._convertor.convert(color, tuple)
        return _create_rounded_rect_surface_optimized(size, 0, color)
def _create_rounded_rect_AA(size, radius, color, _factor = 4):
    """
    Создает поверхность Pygame со сглаженным скругленным прямоугольником с использованием NumPy.

    :param size: Tuple (width, height) - размеры прямоугольника.
    :param radius: int - радиус скругления углов.
    :param color: Tuple (r, g, b) or (r, g, b, a) - цвет фигуры.
    :return: pygame.Surface с альфа-каналом.
    """
    width, height = size
    radius = min(radius, width // 2, height // 2)

    supersample_factor = _factor
    sw, sh = width * supersample_factor, height * supersample_factor
    s_x = np.arange(sw)
    s_y = np.arange(sh)
    s_xx, s_yy = np.meshgrid(s_x, s_y)
    
    s_xx_f = s_xx / supersample_factor
    s_yy_f = s_yy / supersample_factor

    centers = [
        (radius, radius),
        (width - radius, radius),
        (radius, height - radius),
        (width - radius, height - radius)
    ]

    alpha_mask_ss = np.zeros((sh, sw))

    rect_mask = (s_xx_f >= radius) & (s_xx_f < width - radius) & (s_yy_f >= 0) & (s_yy_f < height)
    rect_mask |= (s_yy_f >= radius) & (s_yy_f < height - radius) & (s_xx_f >= 0) & (s_xx_f < width)
    alpha_mask_ss[rect_mask] = 1.0

    for cx, cy in centers:
        dist_sq = (s_xx_f - cx)**2 + (s_yy_f - cy)**2
        alpha_mask_ss[dist_sq < radius**2] = 1.0
    
    alpha = alpha_mask_ss.reshape(height, supersample_factor, width, supersample_factor).mean(axis=(1, 3))
    surf = pygame.Surface((width, height), pygame.SRCALPHA)
    rgb_data = np.full((width, height, 3), color[:3], dtype=np.uint8)
    alpha_data = (alpha * (color[3] if len(color) > 3 else 255)).astype(np.uint8)
    pygame.surfarray.pixels3d(surf)[:] = rgb_data
    pygame.surfarray.pixels_alpha(surf)[:] = np.transpose(alpha_data, (1, 0))

    return surf


class Circle:
    _convertor = Convertor
    @classmethod
    def create_AA(cls, radius, color, AA_factor = 4):
        radius = cls._convertor.convert(radius, int)
        color = cls._convertor.convert(color, tuple)
        AA_factor = cls._convertor.convert(AA_factor, int)
        return _create_circle_AA(radius, color, AA_factor)

    @classmethod
    def create_sdf(cls, radius, color):
        radius = cls._convertor.convert(radius, int)
        color = cls._convertor.convert(color, tuple)
        return _create_circle_sdf(radius, color)

def _create_circle_AA(radius, color, _factor = 4):
    supersample_factor = _factor
    size = radius * 2
    ss_size = size * supersample_factor
    ss_radius = radius * supersample_factor
    
    s_x = np.arange(ss_size)
    s_y = np.arange(ss_size)
    s_xx, s_yy = np.meshgrid(s_x, s_y)

    dist_sq = (s_xx - ss_radius + 0.5)**2 + (s_yy - ss_radius + 0.5)**2
    
    alpha_mask_ss = np.where(dist_sq < ss_radius**2, 1.0, 0.0)

    alpha = alpha_mask_ss.reshape(size, supersample_factor, size, supersample_factor).mean(axis=(1, 3))
    
    surf = pygame.Surface((size, size), pygame.SRCALPHA)
    rgb_data = np.full((size, size, 3), color[:3], dtype=np.uint8)
    alpha_data = (alpha * (color[3] if len(color) > 3 else 255)).astype(np.uint8)
    
    pygame.surfarray.pixels3d(surf)[:] = rgb_data
    pygame.surfarray.pixels_alpha(surf)[:] = np.transpose(alpha_data, (1, 0))

    return surf

def _create_circle_sdf(radius, color):
    size = radius * 2
    x = np.arange(size)
    y = np.arange(size)
    xx, yy = np.meshgrid(x, y)
    
    dist = np.sqrt((xx - radius + 0.5)**2 + (yy - radius + 0.5)**2)
    
    signed_dist = dist - radius
    
    alpha = np.clip(0.5 - signed_dist, 0, 1)
    
    surf = pygame.Surface((size, size), pygame.SRCALPHA)
    rgb_data = np.full((size, size, 3), color[:3], dtype=np.uint8)
    alpha_data = (alpha * (color[3] if len(color) > 3 else 255)).astype(np.uint8)
    
    pygame.surfarray.pixels3d(surf)[:] = rgb_data
    pygame.surfarray.pixels_alpha(surf)[:] = np.transpose(alpha_data, (1, 0))
    
    return surf

          
class Triangle:
    _convertor = Convertor
    @classmethod
    def create_AA(cls, p1, p2, p3, color, AA_factor = 4):
        p1 = cls._convertor.convert(p1, pygame.Vector2)
        p2 = cls._convertor.convert(p2, pygame.Vector2)
        p3 = cls._convertor.convert(p3, pygame.Vector2)
        color = cls._convertor.convert(color, tuple)
        AA_factor = cls._convertor.convert(AA_factor, int)
        return _create_triangle_AA(p1, p2, p3, color, AA_factor)

    @classmethod
    def create_sdf(cls, p1, p2, p3, color):
        p1 = cls._convertor.convert(p1, pygame.Vector2)
        p2 = cls._convertor.convert(p2, pygame.Vector2)
        p3 = cls._convertor.convert(p3, pygame.Vector2)
        color = cls._convertor.convert(color, tuple)
        return _create_triangle_sdf(p1, p2, p3, color)

def _create_triangle_AA(p1, p2, p3, color, _factor=4):
    supersample_factor = _factor

    min_x = int(min(p1.x, p2.x, p3.x))
    max_x = int(max(p1.x, p2.x, p3.x))
    min_y = int(min(p1.y, p2.y, p3.y))
    max_y = int(max(p1.y, p2.y, p3.y))
    
    width, height = max_x - min_x, max_y - min_y
    if width == 0 or height == 0: return pygame.Surface((width, height), pygame.SRCALPHA)

    cp1 = p1 - pygame.Vector2(min_x, min_y)
    cp2 = p2 - pygame.Vector2(min_x, min_y)
    cp3 = p3 - pygame.Vector2(min_x, min_y)

    sw, sh = width * supersample_factor, height * supersample_factor
    s_x = np.arange(sw)
    s_y = np.arange(sh)
    s_xx, s_yy = np.meshgrid(s_x, s_y)
    
    s_px = s_xx / supersample_factor
    s_py = s_yy / supersample_factor

    detT = (cp2.y - cp3.y) * (cp1.x - cp3.x) + (cp3.x - cp2.x) * (cp1.y - cp3.y)
    w1 = ((cp2.y - cp3.y) * (s_px - cp3.x) + (cp3.x - cp2.x) * (s_py - cp3.y)) / detT
    w2 = ((cp3.y - cp1.y) * (s_px - cp3.x) + (cp1.x - cp3.x) * (s_py - cp3.y)) / detT
    w3 = 1.0 - w1 - w2

    alpha_mask_ss = (w1 >= 0) & (w2 >= 0) & (w3 >= 0)
    
    alpha = alpha_mask_ss.reshape(height, supersample_factor, width, supersample_factor).mean(axis=(1, 3))
    
    surf = pygame.Surface((width, height), pygame.SRCALPHA)
    rgb_data = np.full((width, height, 3), color[:3], dtype=np.uint8)
    alpha_data = (alpha * (color[3] if len(color) > 3 else 255)).astype(np.uint8)
    
    pygame.surfarray.pixels3d(surf)[:] = rgb_data
    pygame.surfarray.pixels_alpha(surf)[:] = np.transpose(alpha_data, (1, 0))

    return surf

def _create_triangle_sdf(p1, p2, p3, color):
    min_x = int(min(p1.x, p2.x, p3.x)) - 2 
    max_x = int(np.ceil(max(p1.x, p2.x, p3.x))) + 2
    min_y = int(min(p1.y, p2.y, p3.y)) - 2
    max_y = int(np.ceil(max(p1.y, p2.y, p3.y))) + 2
    
    width, height = max_x - min_x, max_y - min_y
    if width <= 0 or height <= 0: return pygame.Surface((1, 1), pygame.SRCALPHA)
    
    offset = pygame.Vector2(min_x, min_y)
    cp1, cp2, cp3 = p1 - offset, p2 - offset, p3 - offset
    
    x = np.arange(width)
    y = np.arange(height)
    xx, yy = np.meshgrid(x, y)
    
    d1_sq = _dist_to_segment_sq(xx, yy, cp1.x, cp1.y, cp2.x, cp2.y)
    d2_sq = _dist_to_segment_sq(xx, yy, cp2.x, cp2.y, cp3.x, cp3.y)
    d3_sq = _dist_to_segment_sq(xx, yy, cp3.x, cp3.y, cp1.x, cp1.y)
    
    dist = np.sqrt(np.minimum(d1_sq, np.minimum(d2_sq, d3_sq)))

    s1 = (cp2.y - cp1.y) * (xx - cp1.x) - (cp2.x - cp1.x) * (yy - cp1.y)
    s2 = (cp3.y - cp2.y) * (xx - cp2.x) - (cp3.x - cp2.x) * (yy - cp2.y)
    s3 = (cp1.y - cp3.y) * (xx - cp3.x) - (cp1.x - cp3.x) * (yy - cp3.y)
    
    is_inside = (np.sign(s1) == np.sign(s2)) & (np.sign(s2) == np.sign(s3))
    
    sign = np.where(is_inside, -1.0, 1.0)

    signed_dist = dist * sign
    
    alpha = np.clip(0.5 - signed_dist, 0, 1)
    
    surf = pygame.Surface((width, height), pygame.SRCALPHA)
    rgb_data = np.full((width, height, 3), color[:3], dtype=np.uint8)
    alpha_data = (alpha * (color[3] if len(color) > 3 else 255)).astype(np.uint8)
    
    pygame.surfarray.pixels3d(surf)[:] = rgb_data
    pygame.surfarray.pixels_alpha(surf)[:] = np.transpose(alpha_data, (1, 0))
    
    return surf

def _dist_to_segment_sq(px, py, ax, ay, bx, by):
    abx, aby = bx - ax, by - ay
    apx, apy = px - ax, py - ay
    ab_len_sq = abx**2 + aby**2
    ab_len_sq = np.where(ab_len_sq == 0, 1, ab_len_sq)
    dot_p = apx * abx + apy * aby
    t = np.clip(dot_p / ab_len_sq, 0, 1)
    proj_x, proj_y = ax + t * abx, ay + t * aby
    return (px - proj_x)**2 + (py - proj_y)**2

class Line:
    _convertor = Convertor
    @classmethod
    def create_AA(cls, p1, p2, thickness, color, AA_factor = 4):
        p1 = cls._convertor.convert(p1, pygame.Vector2)
        p2 = cls._convertor.convert(p2, pygame.Vector2)
        thickness = cls._convertor.convert(thickness, float)
        color = cls._convertor.convert(color, tuple)
        AA_factor = cls._convertor.convert(AA_factor, int)
        return _create_line_AA(p1, p2, thickness, color, AA_factor)

    @classmethod
    def create_sdf(cls, p1, p2, thickness, color):
        p1 = cls._convertor.convert(p1, pygame.Vector2)
        p2 = cls._convertor.convert(p2, pygame.Vector2)
        thickness = cls._convertor.convert(thickness, float)
        color = cls._convertor.convert(color, tuple)
        return _create_line_sdf(p1, p2, thickness, color)

def _create_line_AA(p1, p2, thickness, color, _factor=4):
    half_thick = thickness / 2.0
    
    min_x = int(min(p1.x, p2.x) - half_thick)
    max_x = int(np.ceil(max(p1.x, p2.x) + half_thick))
    min_y = int(min(p1.y, p2.y) - half_thick)
    max_y = int(np.ceil(max(p1.y, p2.y) + half_thick))
    
    width, height = max_x - min_x, max_y - min_y
    if width <= 0 or height <= 0: return pygame.Surface((max(1, width), max(1, height)), pygame.SRCALPHA)
    
    offset = pygame.Vector2(min_x, min_y)
    cp1, cp2 = p1 - offset, p2 - offset

    supersample_factor = _factor
    sw, sh = width * supersample_factor, height * supersample_factor
    s_x = (np.arange(sw) + 0.5) / supersample_factor
    s_y = (np.arange(sh) + 0.5) / supersample_factor
    s_xx, s_yy = np.meshgrid(s_x, s_y)
    
    dist_sq = _dist_to_segment_sq(s_xx, s_yy, cp1.x, cp1.y, cp2.x, cp2.y)
    alpha_mask_ss = np.where(dist_sq < half_thick**2, 1.0, 0.0)
    
    alpha = alpha_mask_ss.reshape(height, supersample_factor, width, supersample_factor).mean(axis=(1, 3))
    
    surf = pygame.Surface((width, height), pygame.SRCALPHA)
    rgb_data = np.full((width, height, 3), color[:3], dtype=np.uint8)
    alpha_data = (alpha * (color[3] if len(color) > 3 else 255)).astype(np.uint8)
    
    pygame.surfarray.pixels3d(surf)[:] = rgb_data
    pygame.surfarray.pixels_alpha(surf)[:] = np.transpose(alpha_data, (1, 0))

    return surf

def _create_line_sdf(p1, p2, thickness, color):
    half_thick = thickness / 2.0
    
    min_x = int(min(p1.x, p2.x) - half_thick - 2)
    max_x = int(np.ceil(max(p1.x, p2.x) + half_thick + 2))
    min_y = int(min(p1.y, p2.y) - half_thick - 2)
    max_y = int(np.ceil(max(p1.y, p2.y) + half_thick + 2))
    
    width, height = max_x - min_x, max_y - min_y
    if width <= 0 or height <= 0: return pygame.Surface((max(1, width), max(1, height)), pygame.SRCALPHA)

    offset = pygame.Vector2(min_x, min_y)
    cp1, cp2 = p1 - offset, p2 - offset

    x = np.arange(width)
    y = np.arange(height)
    xx, yy = np.meshgrid(x, y)
    
    dist_sq = _dist_to_segment_sq(xx + 0.5, yy + 0.5, cp1.x, cp1.y, cp2.x, cp2.y)
    dist = np.sqrt(dist_sq)
    
    signed_dist = dist - half_thick
    
    alpha = np.clip(0.5 - signed_dist, 0, 1)
    
    surf = pygame.Surface((width, height), pygame.SRCALPHA)
    rgb_data = np.full((width, height, 3), color[:3], dtype=np.uint8)
    alpha_data = (alpha * (color[3] if len(color) > 3 else 255)).astype(np.uint8)
    
    pygame.surfarray.pixels3d(surf)[:] = rgb_data
    pygame.surfarray.pixels_alpha(surf)[:] = np.transpose(alpha_data, (1, 0))

    return surf

class AlphaBlit:
    @staticmethod
    def blit(dest_surf: pygame.Surface, source_surf: pygame.Surface, dest_pos: tuple[int, int]):
        x, y = dest_pos
        width, height = source_surf.get_size()
        roi_rect = pygame.Rect(x, y, width, height)
        roi_rect_clipped = roi_rect.clip(dest_surf.get_rect())

        if roi_rect_clipped.width == 0 or roi_rect_clipped.height == 0:
            return

        src_x_offset = roi_rect_clipped.x - roi_rect.x
        src_y_offset = roi_rect_clipped.y - roi_rect.y

        try:
            src_slice_x = slice(src_x_offset, src_x_offset + roi_rect_clipped.width)
            src_slice_y = slice(src_y_offset, src_y_offset + roi_rect_clipped.height)
            dest_slice_x = slice(roi_rect_clipped.x, roi_rect_clipped.right)
            dest_slice_y = slice(roi_rect_clipped.y, roi_rect_clipped.bottom)

            source_alpha_view = pygame.surfarray.pixels_alpha(source_surf)[src_slice_x, src_slice_y]
            dest_alpha_view = pygame.surfarray.pixels_alpha(dest_surf)[dest_slice_x, dest_slice_y]
            
            np.copyto(dest_alpha_view, source_alpha_view)

        except ValueError:
            clipped_source_rect = pygame.Rect(src_x_offset, src_y_offset, roi_rect_clipped.width, roi_rect_clipped.height)
            dest_surf.blit(source_surf.subsurface(clipped_source_rect), roi_rect_clipped.topleft, special_flags=pygame.BLEND_RGBA_MULT)

class FastBlit:
    @staticmethod
    def blit(dest_surf: pygame.Surface, source_surf: pygame.Surface, dest_pos: tuple[int, int]):
        x, y = dest_pos
        width, height = source_surf.get_size()
        roi_rect = pygame.Rect(x, y, width, height)
        roi_rect_clipped = roi_rect.clip(dest_surf.get_rect())

        if roi_rect_clipped.width == 0 or roi_rect_clipped.height == 0:
            return

        src_x_offset = roi_rect_clipped.x - roi_rect.x
        src_y_offset = roi_rect_clipped.y - roi_rect.y

        try:
            src_slice_x = slice(src_x_offset, src_x_offset + roi_rect_clipped.width)
            src_slice_y = slice(src_y_offset, src_y_offset + roi_rect_clipped.height)
            dest_slice_x = slice(roi_rect_clipped.x, roi_rect_clipped.right)
            dest_slice_y = slice(roi_rect_clipped.y, roi_rect_clipped.bottom)

            source_rgb_view = pygame.surfarray.pixels3d(source_surf)[src_slice_x, src_slice_y]
            dest_rgb_view = pygame.surfarray.pixels3d(dest_surf)[dest_slice_x, dest_slice_y]
            np.copyto(dest_rgb_view, source_rgb_view)
            
            source_alpha_view = pygame.surfarray.pixels_alpha(source_surf)[src_slice_x, src_slice_y]
            dest_alpha_view = pygame.surfarray.pixels_alpha(dest_surf)[dest_slice_x, dest_slice_y]
            np.copyto(dest_alpha_view, source_alpha_view)

        except ValueError:
            clipped_source_rect = pygame.Rect(src_x_offset, src_y_offset, roi_rect_clipped.width, roi_rect_clipped.height)
            dest_surf.blit(source_surf.subsurface(clipped_source_rect), roi_rect_clipped.topleft)
class OutlinedRoundedRect:
    _convertor = Convertor
    @classmethod
    def create_AA(cls, size, radius, width, color, AA_factor = 4):
        size = cls._convertor.convert(size, tuple)
        radius = cls._convertor.convert(radius, int)
        width = cls._convertor.convert(width, float)
        color = cls._convertor.convert(color, tuple)
        AA_factor = cls._convertor.convert(AA_factor, int)
        return _create_outlined_rounded_rect_AA(size, radius, width, color, AA_factor)
    @classmethod
    def create_sdf(cls, size, radius, width, color):
        size = cls._convertor.convert(size, tuple)
        radius = cls._convertor.convert(radius, int)
        width = cls._convertor.convert(width, float)
        color = cls._convertor.convert(color, tuple)
        return _create_outlined_rounded_rect_sdf(tuple(size), radius, width, color)

class OutlinedRect:
    _convertor = Convertor
    @classmethod
    def create_AA(cls, size, width, color, AA_factor = 4):
        size = cls._convertor.convert(size, tuple)
        width = cls._convertor.convert(width, float)
        color = cls._convertor.convert(color, tuple)
        AA_factor = cls._convertor.convert(AA_factor, int)
        return _create_outlined_rounded_rect_AA(size, 0, width, color, AA_factor)

    @classmethod
    def create_sdf(cls, size, width, color):
        size = cls._convertor.convert(size, tuple)
        width = cls._convertor.convert(width, float)
        color = cls._convertor.convert(color, tuple)
        return _create_outlined_rounded_rect_sdf(size, 0, width, color)

def _create_outlined_rounded_rect_AA(size, radius, width, color, _factor = 4):
    w, h = size
    radius = min(radius, w // 2, h // 2)
    half_width = width / 2.0
    
    supersample_factor = _factor
    sw, sh = w * supersample_factor, h * supersample_factor
    s_x = (np.arange(sw) + 0.5) / supersample_factor
    s_y = (np.arange(sh) + 0.5) / supersample_factor
    s_xx, s_yy = np.meshgrid(s_x, s_y)

    inner_w = w - 2 * radius
    inner_h = h - 2 * radius
    dist_x = np.abs(s_xx - (w - 1) / 2) - (inner_w - 1) / 2
    dist_y = np.abs(s_yy - (h - 1) / 2) - (inner_h - 1) / 2
    
    dist_from_inner_corner = np.sqrt(np.maximum(dist_x, 0)**2 + np.maximum(dist_y, 0)**2)
    signed_dist = dist_from_inner_corner - radius
    
    dist_from_edge = np.abs(signed_dist)
    
    alpha_mask_ss = np.clip(half_width - dist_from_edge + 0.5, 0, 1)

    alpha = alpha_mask_ss.reshape(h, supersample_factor, w, supersample_factor).mean(axis=(1, 3))
    
    surf = pygame.Surface(size, pygame.SRCALPHA)
    rgb_data = np.full((w, h, 3), color[:3], dtype=np.uint8)
    alpha_data = (alpha * (color[3] if len(color) > 3 else 255)).astype(np.uint8)
    pygame.surfarray.pixels3d(surf)[:] = rgb_data
    pygame.surfarray.pixels_alpha(surf)[:] = np.transpose(alpha_data, (1, 0))

    return surf
