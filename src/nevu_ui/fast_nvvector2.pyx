# distutils: language = c++
# cython: language_level=3
# cython: boundscheck=False
# cython: wraparound=False
# cython: cdivision=True
# cython: nonecheck=False

cimport cython
import pygame
from libc.math cimport sqrt

cdef class NvVector2:
    def __init__(self, *args):
        cdef int nargs = len(args)
        if nargs == 0:
            self.x = 0.0
            self.y = 0.0
        elif nargs == 1:
            arg = args[0]
            if isinstance(arg, NvVector2):
                self.x = arg.x
                self.y = arg.y
            elif isinstance(arg, pygame.Vector2):
                self.x = arg.x
                self.y = arg.y
            elif isinstance(arg, (list, tuple)):
                if len(arg) != 2:
                    raise TypeError(f"NvVector2() takes a sequence of length 2, but got {len(arg)}")
                self.x = arg[0]
                self.y = arg[1]
            else:
                raise TypeError(f"NvVector2() invalid constructor argument: {type(arg).__name__}")
        elif nargs == 2:
            self.x = args[0]
            self.y = args[1]
        else:
            raise TypeError(f"NvVector2() takes 0, 1, or 2 arguments, but {nargs} were given")

    @property
    def xx(self):
        return NvVector2(self.x, self.x)

    @property
    def yy(self):
        return NvVector2(self.y, self.y)

    @property
    def xy(self):
        return NvVector2(self.x, self.y)

    @property
    def yx(self):
        return NvVector2(self.y, self.x)

    def __getitem__(self, int index):
        if index == 0:
            return self.x
        elif index == 1:
            return self.y
        else:
            raise IndexError("Vector index out of range")

    def __setitem__(self, int index, float value):
        if index == 0:
            self.x = value
        elif index == 1:
            self.y = value
        else:
            raise IndexError("Vector index out of range")

    @cython.ccall
    cdef NvVector2 _add(self, NvVector2 other):
        return NvVector2(self.x + other.x, self.y + other.y)

    @cython.ccall
    cdef NvVector2 _sub(self, NvVector2 other):
        return NvVector2(self.x - other.x, self.y - other.y)

    @cython.ccall
    cdef NvVector2 _mul_scalar(self, float val):
        return NvVector2(self.x * val, self.y * val)

    @cython.ccall
    cdef NvVector2 _mul_vector(self, NvVector2 other):
        return NvVector2(self.x * other.x, self.y * other.y)

    @cython.ccall
    cdef NvVector2 _iadd(self, NvVector2 other):
        self.x += other.x
        self.y += other.y
        return self

    @cython.ccall
    cdef NvVector2 _isub(self, NvVector2 other):
        self.x -= other.x
        self.y -= other.y
        return self

    @cython.ccall
    cdef NvVector2 _imul(self, NvVector2 other):
        self.x *= other.x
        self.y *= other.y
        return self

    def __imul__(self, NvVector2 other):
        return self._imul(other)
    
    def __isub__(self, NvVector2 other):
        return self._isub(other)

    def __iadd__(self, NvVector2 other):
        return self._iadd(other)

    def __add__(self, NvVector2 other):
        return self._add(other)

    def __sub__(self, NvVector2 other):
        return self._sub(other)

    def __mul__(self, other):
        if isinstance(other, NvVector2):
            return self._mul_vector(other)
        elif isinstance(other, (int, float)):
            return self._mul_scalar(other)
        else:
            return NotImplemented

    def __truediv__(self, other):
        if isinstance(other, NvVector2):
            return NvVector2(self.x / other.x, self.y / other.y)
        elif isinstance(other, (int, float)):
            return NvVector2(self.x / other, self.y / other)
        else:
            return NotImplemented

    def __floordiv__(self, other):
        if isinstance(other, NvVector2):
            return NvVector2(self.x // other.x, self.y // other.y)
        elif isinstance(other, (int, float)):
            return NvVector2(self.x // other, self.y // other)
        else:
            return NotImplemented

    def __neg__(self):
        return NvVector2(-self.x, -self.y)

    def __repr__(self):
        return f"NvVector2({self.x}, {self.y})"

    def to_int(self):
        self.x = int(self.x)
        self.y = int(self.y)
        return self

    def get_int(self):
        return NvVector2(int(self.x), int(self.y))
    
    def to_round(self):
        self.x = round(self.x)
        self.y = round(self.y)
        return self

    def get_round(self):
        return NvVector2(round(self.x), round(self.y))

    def to_abs(self):
        self.x = abs(self.x)
        self.y = abs(self.y)
        return self

    def get_abs(self):
        return NvVector2(abs(self.x), abs(self.y))

    def to_neg(self):
        self.x = -self.x
        self.y = -self.y
        return self

    def get_neg(self):
        return NvVector2(-self.x, -self.y)

    def to_pygame(self):
        return pygame.Vector2(self.x, self.y)
    
    def copy(self):
        return NvVector2(self.x, self.y)

    def __copy__(self):
        return NvVector2(self.x, self.y)
    
    def __deepcopy__(self, memo):
        return NvVector2(self.x, self.y)
    
    def __hash__(self):
        return hash((self.x, self.y))
    
    def __len__(self):
        return 2

    def __eq__(self, other):
        if isinstance(other, NvVector2):
            return self.x == other.x and self.y == other.y
        else:
            return NotImplemented

    @property
    def length(self):
        return sqrt(self.x * self.x + self.y * self.y)
    
    def normalize(self):
        cdef float l = self.length
        if l == 0: 
            return NvVector2(0, 0)
        return NvVector2(self.x / l, self.y / l)
    
    def normalize_ip(self):
        cdef float l = self.length
        if l > 0: 
            self.x /= l
            self.y /= l
        return self
    
    def distance_to(self, NvVector2 other):
        cdef float dx = self.x - other.x
        cdef float dy = self.y - other.y
        return sqrt(dx * dx + dy * dy)

    def distance_squared_to(self, NvVector2 other):
        cdef float dx = self.x - other.x
        cdef float dy = self.y - other.y
        return dx * dx + dy * dy

    def dot(self, NvVector2 other):
        return self.x * other.x + self.y * other.y