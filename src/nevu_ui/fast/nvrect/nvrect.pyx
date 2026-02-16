# distutils: language = c++
# cython: language_level=3
# cython: boundscheck=False
# cython: wraparound=False
# cython: cdivision=True
# cython: nonecheck=False
# cython: initializedcheck=False


cimport cython
import pygame
from nevu_ui.fast.nvvector2.nvvector2 cimport NvVector2

@cython.final
@cython.freelist(32)
cdef class NvRect:
    @staticmethod
    cdef NvRect from_nvvector(NvVector2 pos, NvVector2 size):
        return NvRect.new(pos.x, pos.y, size.x, size.y)
    
    cpdef NvRect union(self, NvRect other):
        cdef float min_x, min_y, max_r, max_b
        cdef float s_right = self.x + self.w
        cdef float s_bottom = self.y + self.h
        cdef float o_right = other.x + other.w
        cdef float o_bottom = other.y + other.h

        if self.x < other.x:
            min_x = self.x
        else:
            min_x = other.x

        if self.y < other.y:
            min_y = self.y
        else:
            min_y = other.y

        if s_right > o_right:
            max_r = s_right
        else:
            max_r = o_right

        if s_bottom > o_bottom:
            max_b = s_bottom
        else:
            max_b = o_bottom
        return NvRect.new(min_x, min_y, max_r - min_x, max_b - min_y)

    @staticmethod
    cdef inline NvRect new(float x, float y, float w, float h):
        cdef NvRect rec = NvRect.__new__(NvRect)
        rec.x = x
        rec.y = y
        rec.w = w
        rec.h = h
        return rec
    
    def __init__(self, *args):
        cdef int nargs = len(args)
        if nargs == 0:
            self.x = 0.0 
            self.y = 0.0
            self.w = 0.0
            self.h = 0.0
        elif nargs == 1:
            arg = args[0]
            if isinstance(arg, pygame.Rect | NvRect):
                self.x = arg.x 
                self.y = arg.y 
                self.w = arg.w 
                self.h = arg.h 
            elif hasattr(arg, "width") and hasattr(arg, "height"):
                self.x = arg.x
                self.y = arg.y
                self.w = arg.width
                self.h = arg.height
            elif isinstance(arg, NvVector2):
                self.x = arg.x
                self.y = arg.y
                self.w = 0.0 
                self.h = 0.0 
            elif isinstance(arg, (list, tuple)):
                if len(arg) not in (2, 4):
                    raise TypeError(f"NvRect() takes a sequence of length 2/4, but got {len(arg)}")
                self.x = arg[0]
                self.y = arg[1]
                if len(arg) == 4:
                    self.w = arg[2]
                    self.h = arg[3]
            else:
                raise TypeError(f"NvRect() invalid constructor argument: {type(arg).__name__}")
        elif nargs == 2:
            if isinstance(args[0], int | float):
                self.x = args[0]
                self.y = args[1]
                self.w = 0.0 #type: ignore
                self.h = 0.0 #type: ignore
            elif isinstance(args[0], NvVector2):
                self.x = args[0].x
                self.y = args[0].y
                self.w = args[1].x
                self.h = args[1].y
        elif nargs == 4:
            self.x = args[0]
            self.y = args[1]
            self.w = args[2]
            self.h = args[3]
        else:
            raise TypeError(f"NvRect() takes 0, 1, or 2 arguments, but {nargs} were given")
    
    #2 chars swizzing
    @property
    def xx(self):
        return NvVector2.new(self.x, self.x)

    @property
    def yy(self):
        return NvVector2.new(self.y, self.y)

    @property
    def xy(self):
        return NvVector2.new(self.x, self.y)

    @property
    def yx(self):
        return NvVector2.new(self.y, self.x)

    @property
    def xw(self):
        return NvVector2.new(self.x, self.w)
    
    @property
    def yh(self):
        return NvVector2.new(self.y, self.h)
    
    @property
    def wh(self):
        return NvVector2.new(self.w, self.h)
    
    @property
    def hw(self):
        return NvVector2.new(self.h, self.w)

    #4 chars swizzing
    @property
    def xywh(self):
        return NvRect.new(self.x, self.y, self.w, self.h)

    @property
    def whxy(self):
        return NvRect.new(self.w, self.h, self.x, self.y)
    
    #Python properties
    def __getitem__(self, int index):
        if index == 0:
            return self.x
        elif index == 1:
            return self.y
        elif index == 2:
            return self.w
        elif index == 3:
            return self.h
        else:
            raise IndexError("Rect index out of range")

    def __setitem__(self, int index, float value):
        if index == 0:
            self.x = value
        elif index == 1:
            self.y = value
        elif index == 2:
            self.w = value
        elif index == 3:
            self.h = value
        else:
            raise IndexError("Rect index out of range")
    
    def __imul__(self, NvRect other):
        return self._imul(other) #type: ignore
    
    def __isub__(self, NvRect other):
        return self._isub(other) #type: ignore

    def __iadd__(self, NvRect other):
        return self._iadd(other) #type: ignore

    def __add__(self, NvRect other):
        return self._add(other) #type: ignore

    def __sub__(self, NvRect other):
        return self._sub(other) #type: ignore

    def __mul__(self, other):
        if isinstance(other, NvRect):
            return self._mul_rect(other) #type: ignore
        elif isinstance(other, (int, float)):
            return self._mul_scalar(other) #type: ignore
        else:
            return NotImplemented

    def __truediv__(self, other):
        if isinstance(other, NvRect):
            return NvRect.new(self.x / other.x, self.y / other.y, self.w / other.w, self.h / other.h)
        elif isinstance(other, (int, float)):
            return NvRect.new(self.x / other, self.y / other, self.w / other, self.h / other)
        else: return NotImplemented

    def __floordiv__(self, other):
        if isinstance(other, NvRect):
            return NvRect.new(self.x // other.x, self.y // other.y, self.w // other.w, self.h // other.h)
        elif isinstance(other, (int, float)):
            return NvRect.new(self.x // other, self.y // other, self.w // other, self.h // other)
        else: return NotImplemented

    def __neg__(self):
        return NvRect.new(-self.x, -self.y, -self.w, -self.h)

    def __repr__(self):
        return f"NvRect({self.x}, {self.y}, {self.w}, {self.h})"

    def __hash__(self):
        return hash((self.x, self.y, self.w, self.h))
    
    def __len__(self):
        return 4
    
    def __eq__(self, other):
        if isinstance(other, NvRect):
            return self.x == other.x and self.y == other.y and self.w == other.w and self.h == other.h
        else:
            return NotImplemented

    #Cython ccalls
    @cython.ccall
    cdef inline NvRect _add(self, NvRect other):
        return NvRect.new(self.x + other.x, self.y + other.y, self.w + other.w, self.h + other.h)

    @cython.ccall
    cdef inline NvRect _sub(self, NvRect other):
        return NvRect.new(self.x - other.x, self.y - other.y, self.w - other.w, self.h - other.h)

    @cython.ccall
    cdef inline NvRect _mul_scalar(self, float val):
        return NvRect.new(self.x * val, self.y * val, self.w * val, self.h * val) 

    @cython.ccall
    cdef inline NvRect _mul_rect(self, NvRect other):
        return NvRect.new(self.x * other.x, self.y * other.y, self.w * other.w, self.h * other.h)

    @cython.ccall
    cdef inline NvRect _iadd(self, NvRect other):
        self.x += other.x
        self.y += other.y
        return self

    @cython.ccall
    cdef inline NvRect _isub(self, NvRect other):
        self.x -= other.x
        self.y -= other.y
        return self

    @cython.ccall
    cdef inline NvRect _imul(self, NvRect other):
        self.x *= other.x
        self.y *= other.y
        return self

    #Python methods
    def get_tuple(self):
        return (self.x, self.y, self.w, self.h)
        
    def get_pygame_rect(self):
        return pygame.Rect(self.x, self.y, self.w, self.h)
    
    cpdef bint collide_rect(self, NvRect other):
        return self.x < other.x + other.w and self.x + self.w > other.x and self.y < other.y + other.h and self.y + self.h > other.y
    
    def collide_point(self, *args):
        cdef float nargs = len(args)
        if nargs == 1:
            if isinstance(args[0], NvVector2):
                return self.x < args[0].x < self.x + self.w and self.y < args[0].y < self.y + self.h
            elif isinstance(args[0], (list, tuple)):
                return self.x < args[0][0] < self.x + self.w and self.y < args[0][1] < self.y + self.h
        elif nargs == 2:
            x, y = args
            return self.x < x < self.x + self.w and self.y < y < self.y + self.h

    #Properties
    @property
    def size(self):
        return NvVector2.new(self.w, self.h)
    
    @size.setter
    def size(self, value):
        if isinstance(value, NvVector2):
            self.w = value.x
            self.h = value.y
        elif isinstance(value, (list, tuple)):
            self.w = value[0]
            self.h = value[1]
    
    @property
    def topleft(self):
        return NvVector2.new(self.x, self.y)
    
    @property
    def topright(self):
        return NvVector2.new(self.x + self.w, self.y)
    
    @property
    def bottomleft(self):
        return NvVector2.new(self.x, self.y + self.h)
    
    @property
    def bottomright(self):
        return NvVector2.new(self.x + self.w, self.y + self.h)

    def move_ip(self, *args):
        cdef int nargs = len(args)
        cdef object arg
        cdef NvVector2 vec_arg
        if nargs == 2:
            self.x += args[0]
            self.y += args[1]
        elif nargs == 1:
            arg = args[0]
            if isinstance(arg, NvVector2):
                vec_arg = <NvVector2>arg
                self.x += vec_arg.x
                self.y += vec_arg.y
            elif isinstance(arg, (list, tuple)):
                self.x += arg[0]
                self.y += arg[1]
            else:
                raise TypeError(f"move_ip() argument must be sequence or NvVector2, not {type(arg).__name__}")
        else:
            raise TypeError(f"move_ip() takes 1 or 2 arguments, but {nargs} were given")