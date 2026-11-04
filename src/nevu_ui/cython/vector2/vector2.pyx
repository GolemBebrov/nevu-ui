cimport cython
import nevu_ui.core.modules as md
from libc.math cimport sqrt
from cpython.list cimport PyList_GET_ITEM
from cpython.tuple cimport PyTuple_GET_ITEM

@cython.freelist(1000)
@cython.final
cdef class Vector2:

    @property
    def x(self) -> float:
        return self.data.x

    @x.setter
    def x(self, double value):
        self.data.x = value

    @property
    def y(self) -> float:
        return self.data.y

    @y.setter
    def y(self, double value):
        self.data.y = value

    @staticmethod
    cdef inline Vector2 new(double x, double y):
        cdef Vector2 vec = Vector2.__new__(Vector2)
        vec.data.x = x
        vec.data.y = y
        return vec

    def __init__(self, *args):
        cdef int nargs = len(args)
        if nargs == 0:
            self.data.x = 0.0
            self.data.y = 0.0
        elif nargs == 1:
            arg = args[0]
            if isinstance(arg, Vector2):
                self.data = (<Vector2>arg).data
            elif hasattr(arg, "clamp_magnitude_ip"):
                self.data.x = arg.x
                self.data.y = arg.y
            elif isinstance(arg, (list, tuple)):
                if len(arg) != 2:
                    raise TypeError(f"Vector2() takes a sequence of length 2, but got {len(arg)}")
                self.data.x = arg[0]
                self.data.y = arg[1]
            else:
                raise TypeError(f"Vector2() invalid constructor argument: {type(arg).__name__}")
        elif nargs == 2:
            self.data.x = args[0]
            self.data.y = args[1]
        else:
            raise TypeError(f"Vector2() takes 0, 1, or 2 arguments, but {nargs} were given")

    @staticmethod
    cdef inline Vector2 cfrom_vector2(Vector2 other):
        return Vector2.new(other.data.x, other.data.y)

    @staticmethod
    cdef inline Vector2 cfrom_tuple(tuple other):
        cdef double x, y
        x = <double><object>PyTuple_GET_ITEM(other, 0)
        y = <double><object>PyTuple_GET_ITEM(other, 1)
        return Vector2.new(x, y)

    @staticmethod
    cdef inline Vector2 cfrom_list(list other):
        cdef double x, y
        x = <double><object>PyList_GET_ITEM(other, 0)
        y = <double><object>PyList_GET_ITEM(other, 1)
        return Vector2.new(x, y)

    @staticmethod
    cdef inline Vector2 cfrom_ints(int x, int y):
        return Vector2.new(x, y)

    @staticmethod
    cdef inline Vector2 cfrom_floats(float x, float y):
        return Vector2.new(x, y)

    @staticmethod
    cdef inline Vector2 cfrom_xy(double x, double y):
        return Vector2.new(x, y)

    @staticmethod
    def from_vector2(Vector2 other) -> Vector2:
        return Vector2.cfrom_vector2(other)

    @staticmethod
    def from_tuple(tuple other) -> Vector2:
        return Vector2.cfrom_tuple(other)

    @staticmethod
    def from_list(list other) -> Vector2:
        return Vector2.cfrom_list(other)

    @staticmethod
    def from_ints(int x, int y) -> Vector2:
        return Vector2.cfrom_ints(x, y)

    @staticmethod
    def from_floats(float x, float y) -> Vector2:
        return Vector2.cfrom_floats(x, y)

    @staticmethod
    def from_xy(double x, double y) -> Vector2:
        return Vector2.cfrom_xy(x, y)

    @property
    def xx(self) -> Vector2:
        return Vector2.new(self.data.x, self.data.x)

    @property
    def yy(self) -> Vector2:
        return Vector2.new(self.data.y, self.data.y)

    @property
    def xy(self) -> Vector2:
        return Vector2.new(self.data.x, self.data.y)

    @property
    def yx(self) -> Vector2:
        return Vector2.new(self.data.y, self.data.x)

    def to_tuple(self) -> tuple[float, float]:
        return (self.data.x, self.data.y)

    def __getitem__(self, int index):
        if index == 0:
            return self.data.x
        elif index == 1:
            return self.data.y
        else:
            raise IndexError("Vector index out of range")

    def __setitem__(self, int index, double value):
        if index == 0:
            self.data.x = value
        elif index == 1:
            self.data.y = value
        else:
            raise IndexError("Vector index out of range")

    def __add__(self, Vector2 other):
        cdef nv_vector2_t res = nv_vector2_add(self.data, other.data)
        return Vector2.new(res.x, res.y)

    def __sub__(self, Vector2 other):
        cdef nv_vector2_t res = nv_vector2_sub(self.data, other.data)
        return Vector2.new(res.x, res.y)

    def __mul__(self, other):
        cdef nv_vector2_t res
        if isinstance(other, Vector2):
            res = nv_vector2_mul_vector(self.data, (<Vector2>other).data)
            return Vector2.new(res.x, res.y)
        elif isinstance(other, (int, float)):
            res = nv_vector2_mul_scalar(self.data, other)
            return Vector2.new(res.x, res.y)
        return NotImplemented

    def __truediv__(self, other):
        cdef nv_vector2_t res
        if isinstance(other, Vector2):
            res = nv_vector2_div_vector(self.data, (<Vector2>other).data)
            return Vector2.new(res.x, res.y)
        elif isinstance(other, (int, float)):
            res = nv_vector2_div_scalar(self.data, other)
            return Vector2.new(res.x, res.y)
        return NotImplemented

    def __floordiv__(self, other):
        cdef nv_vector2_t res
        if isinstance(other, Vector2):
            res = nv_vector2_floordiv_vector(self.data, (<Vector2>other).data)
            return Vector2.new(res.x, res.y)
        elif isinstance(other, (int, float)):
            res = nv_vector2_floordiv_scalar(self.data, other)
            return Vector2.new(res.x, res.y)
        return NotImplemented

    def __iadd__(self, Vector2 other):
        nv_vector2_iadd(&self.data, other.data)
        return self

    def __isub__(self, Vector2 other):
        nv_vector2_isub(&self.data, other.data)
        return self

    def __imul__(self, Vector2 other):
        nv_vector2_imul(&self.data, other.data)
        return self

    def __neg__(self):
        return Vector2.new(-self.data.x, -self.data.y)

    def __repr__(self):
        return f"Vector2({self.data.x}, {self.data.y})"

    cdef inline Vector2 _add(self, Vector2 other):
        cdef nv_vector2_t res = nv_vector2_add(self.data, other.data)
        return Vector2.new(res.x, res.y)

    cdef inline Vector2 _sub(self, Vector2 other):
        cdef nv_vector2_t res = nv_vector2_sub(self.data, other.data)
        return Vector2.new(res.x, res.y)

    cdef inline void _iadd(self, Vector2 other) nogil:
        nv_vector2_iadd(&self.data, other.data)

    cdef inline void _sadd(self, Vector2 new_vec, Vector2 old_vec) nogil:
        self.data.x = new_vec.data.x + old_vec.data.x
        self.data.y = new_vec.data.y + old_vec.data.y

    cdef inline void _isub(self, Vector2 other) nogil:
        nv_vector2_isub(&self.data, other.data)

    cdef inline void _imul(self, Vector2 other) nogil:
        nv_vector2_imul(&self.data, other.data)

    cpdef void sadd(self, Vector2 new_vec, Vector2 old_vec):
        self._sadd(new_vec, old_vec)

    def to_int(self) -> Vector2:
        self.data.x = <int>self.data.x
        self.data.y = <int>self.data.y
        return self

    def get_int(self) -> Vector2:
        return Vector2.new(<int>self.data.x, <int>self.data.y)

    def to_round(self) -> Vector2:
        self.data.x = round(self.data.x)
        self.data.y = round(self.data.y)
        return self

    def get_round(self) -> Vector2:
        return Vector2.new(round(self.data.x), round(self.data.y))

    def to_abs(self) -> Vector2:
        self.data.x = abs(self.data.x)
        self.data.y = abs(self.data.y)
        return self

    def get_abs(self) -> Vector2:
        return Vector2.new(abs(self.data.x), abs(self.data.y))

    def to_neg(self) -> Vector2:
        self.data.x = -self.data.x
        self.data.y = -self.data.y
        return self

    def get_neg(self) -> Vector2:
        return Vector2.new(-self.data.x, -self.data.y)

    def get_int_tuple(self) -> tuple[int, int]:
        return (<int>self.data.x, <int>self.data.y)

    cdef tuple c_get_int_tuple(self):
        return (<int>self.data.x, <int>self.data.y)

    def to_pygame(self):
        return md.pygame.Vector2(self.data.x, self.data.y)

    cpdef Vector2 copy(self):
        return Vector2.new(self.data.x, self.data.y)

    def __copy__(self) -> Vector2:
        return Vector2.new(self.data.x, self.data.y)

    def __deepcopy__(self, memo) -> Vector2:
        return Vector2.new(self.data.x, self.data.y)

    def __hash__(self):
        return hash((self.data.x, self.data.y))

    def __len__(self) -> int:
        return 2

    def __eq__(self, other: Vector2):
        if type(other) is Vector2:
            return self.data.x == (<Vector2>other).data.x and self.data.y == (<Vector2>other).data.y
        return False

    @property
    def length(self) -> float:
        return nv_vector2_length(self.data)

    def normalize(self) -> Vector2:
        cdef nv_vector2_t res = nv_vector2_normalize(self.data)
        return Vector2.new(res.x, res.y)

    def normalize_ip(self) -> Vector2:
        self.data = nv_vector2_normalize(self.data)
        return self

    def distance_to(self, Vector2 other):
        return nv_vector2_distance_to(self.data, other.data)

    def distance_squared_to(self, Vector2 other):
        return nv_vector2_distance_squared_to(self.data, other.data)

    def dot(self, Vector2 other):
        return nv_vector2_dot(self.data, other.data)
