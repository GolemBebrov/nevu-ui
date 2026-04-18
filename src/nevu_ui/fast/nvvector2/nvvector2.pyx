# distutils: language = c++
# cython: language_level=3
# cython: boundscheck=False
# cython: wraparound=False
# cython: cdivision=True
# cython: nonecheck=False
# cython: initializedcheck=False

cimport cython
import nevu_ui.core.modules as md
from libc.math cimport sqrt
from cpython.list cimport PyList_GET_ITEM
from cpython.tuple cimport PyTuple_GET_ITEM

@cython.freelist(1000)
@cython.final
cdef class NvVector2:
    @staticmethod
    cdef inline NvVector2 new(double x, double y) noexcept:
        cdef NvVector2 vec = NvVector2.__new__(NvVector2)
        vec.x = x
        vec.y = y
        return vec

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
            elif hasattr(arg, "clamp_magnitude_ip"):
                #VECTOR 2 FROM PYGAME!!! ! ! !! 
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

    @staticmethod
    cdef inline NvVector2 cfrom_nvvector2(NvVector2 other):
        return NvVector2.new(other.x, other.y)
    
    @staticmethod
    cdef inline NvVector2 cfrom_tuple(tuple other):
        cdef double x, y
        x = <double><object>PyTuple_GET_ITEM(other, 0)
        y = <double><object>PyTuple_GET_ITEM(other, 1)
        return NvVector2.new(x, y)
    
    @staticmethod
    cdef inline NvVector2 cfrom_list(list other):
        cdef double x, y
        x = <double><object>PyList_GET_ITEM(other, 0)
        y = <double><object>PyList_GET_ITEM(other, 1)
        return NvVector2.new(x, y)
    
    @staticmethod
    cdef inline NvVector2 cfrom_ints(int x, int y):
        return NvVector2.new(x, y)
    
    @staticmethod
    cdef inline NvVector2 cfrom_floats(float x, float y):
        return NvVector2.new(x, y)

    @staticmethod
    cdef inline NvVector2 cfrom_xy(double x, double y):
        return NvVector2.new(x, y)

    @staticmethod
    def from_nvvector2(NvVector2 other):
        return NvVector2.cfrom_nvvector2(other)
    
    @staticmethod
    def from_tuple(tuple other):
        return NvVector2.cfrom_tuple(other)
    
    @staticmethod
    def from_list(list other):
        return NvVector2.cfrom_list(other)
    
    @staticmethod
    def from_ints(int x, int y):
        return NvVector2.cfrom_ints(x, y)
    
    @staticmethod
    def from_floats(float x, float y):
        return NvVector2.cfrom_floats(x, y)

    @staticmethod
    def from_xy(double x, double y):
        return NvVector2.cfrom_xy(x, y)

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

    def to_tuple(self):
        return (self.x, self.y)
    
    cpdef void sadd(self, NvVector2 new_vec, NvVector2 old_vec):
        self._sadd(new_vec, old_vec)

    def __getitem__(self, int index):
        if index == 0:
            return self.x
        elif index == 1:
            return self.y
        else:
            raise IndexError("Vector index out of range")

    def __setitem__(self, int index, double value):
        if index == 0:
            self.x = value
        elif index == 1:
            self.y = value
        else:
            raise IndexError("Vector index out of range")

    cdef inline NvVector2 _add(self, NvVector2 other):
        return NvVector2.new(self.x + other.x, self.y + other.y)

    cdef inline NvVector2 _sub(self, NvVector2 other):
        return NvVector2.new(self.x - other.x, self.y - other.y)

    cdef inline NvVector2 _mul_scalar(self, double val):
        return NvVector2.new(self.x * val, self.y * val)

    cdef inline NvVector2 _mul_vector(self, NvVector2 other):
        return NvVector2.new(self.x * other.x, self.y * other.y)

    cdef inline void _iadd(self, NvVector2 other) nogil:
        self.x += other.x
        self.y += other.y

    cdef inline void _sadd(self, NvVector2 new_vec, NvVector2 old_vec) nogil:
        self.x = new_vec.x + old_vec.x
        self.y = new_vec.y + old_vec.y

    cdef inline void _isub(self, NvVector2 other) nogil:
        self.x -= other.x
        self.y -= other.y

    cdef inline void _imul(self, NvVector2 other) nogil:
        self.x *= other.x
        self.y *= other.y

    def __imul__(self, NvVector2 other):
        self._imul(other)
        return self
    
    def __isub__(self, NvVector2 other):
        self._isub(other)
        return self # type: ignore

    def __iadd__(self, NvVector2 other):
        self._iadd(other)
        return self # type: ignore

    def __add__(self, NvVector2 other):
        return self._add(other) # type: ignore

    def __sub__(self, NvVector2 other):
        return self._sub(other) # type: ignore

    def __mul__(self, other):
        if isinstance(other, NvVector2):
            return self._mul_vector(other) # type: ignore
        elif isinstance(other, (int, float)):
            return self._mul_scalar(other) # type: ignore
        else:
            return NotImplemented

    def __truediv__(self, other):
        if isinstance(other, NvVector2):
            return NvVector2.new(self.x / other.x, self.y / other.y)
        elif isinstance(other, (int, float)):
            return NvVector2.new(self.x / other, self.y / other)
        else:
            return NotImplemented

    def __floordiv__(self, other):
        if isinstance(other, NvVector2):
            return NvVector2.new(self.x // other.x, self.y // other.y)
        elif isinstance(other, (int, float)):
            return NvVector2.new(self.x // other, self.y // other)
        else:
            return NotImplemented

    def __neg__(self):
        return NvVector2.new(-self.x, -self.y)

    def __repr__(self):
        return f"NvVector2({self.x}, {self.y})"

    def to_int(self):
        self.x = int(self.x)
        self.y = int(self.y)
        return self

    def get_int(self):
        return NvVector2.new(int(self.x), int(self.y))
    
    def to_round(self):
        self.x = round(self.x)
        self.y = round(self.y)
        return self

    def get_round(self):
        return NvVector2.new(round(self.x), round(self.y))

    def to_abs(self):
        self.x = abs(self.x)
        self.y = abs(self.y)
        return self

    def get_abs(self):
        return NvVector2.new(abs(self.x), abs(self.y))

    def to_neg(self):
        self.x = -self.x
        self.y = -self.y
        return self

    def get_neg(self):
        return NvVector2.new(-self.x, -self.y)

    def get_int_tuple(self):
        return (int(self.x), int(self.y))

    def to_pygame(self):
        return md.pygame.Vector2(self.x, self.y)
    
    cpdef NvVector2 copy(self):
        return NvVector2.new(self.x, self.y)

    def __copy__(self):
        return NvVector2.new(self.x, self.y)
    
    def __deepcopy__(self, memo):
        return NvVector2.new(self.x, self.y)
    
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
        return sqrt(self.x * self.x + self.y * self.y) # type: ignore
    
    def normalize(self):
            cdef double l = sqrt(self.x * self.x + self.y * self.y) # type: ignore
            cdef double inv_l
            
            if l == 0: 
                return NvVector2.new(0.0, 0.0)
            
            inv_l = 1.0 / l
            return NvVector2.new(self.x * inv_l, self.y * inv_l)
    
    def normalize_ip(self):
        cdef double l = sqrt(self.x * self.x + self.y * self.y) # type: ignore
        cdef double inv_l
        
        if l > 0: 
            inv_l = 1.0 / l
            self.x *= inv_l
            self.y *= inv_l
        return self
    
    def distance_to(self, NvVector2 other):
        cdef double dx = self.x - other.x
        cdef double dy = self.y - other.y
        return sqrt(dx * dx + dy * dy) # type: ignore

    def distance_squared_to(self, NvVector2 other):
        cdef double dx = self.x - other.x
        cdef double dy = self.y - other.y
        return dx * dx + dy * dy

    def dot(self, NvVector2 other):
        return self.x * other.x + self.y * other.y