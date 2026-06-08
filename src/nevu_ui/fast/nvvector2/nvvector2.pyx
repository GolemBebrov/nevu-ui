cimport cython
import nevu_ui.core.modules as md
from libc.math cimport sqrt
from cpython.list cimport PyList_GET_ITEM
from cpython.tuple cimport PyTuple_GET_ITEM

@cython.freelist(1000)
@cython.final
cdef class NvVector2:

    @property
    def x(self):
        return self.data.x

    @x.setter
    def x(self, double value):
        self.data.x = value

    @property
    def y(self):
        return self.data.y

    @y.setter
    def y(self, double value):
        self.data.y = value

    @staticmethod
    cdef inline NvVector2 new(double x, double y):
        cdef NvVector2 vec = NvVector2.__new__(NvVector2)
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
            if isinstance(arg, NvVector2):
                self.data = (<NvVector2>arg).data
            elif hasattr(arg, "clamp_magnitude_ip"):
                self.data.x = arg.x
                self.data.y = arg.y
            elif isinstance(arg, (list, tuple)):
                if len(arg) != 2:
                    raise TypeError(f"NvVector2() takes a sequence of length 2, but got {len(arg)}")
                self.data.x = arg[0]
                self.data.y = arg[1]
            else:
                raise TypeError(f"NvVector2() invalid constructor argument: {type(arg).__name__}")
        elif nargs == 2:
            self.data.x = args[0]
            self.data.y = args[1]
        else:
            raise TypeError(f"NvVector2() takes 0, 1, or 2 arguments, but {nargs} were given")

    @staticmethod
    cdef inline NvVector2 cfrom_nvvector2(NvVector2 other):
        return NvVector2.new(other.data.x, other.data.y)
    
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
        return NvVector2.new(self.data.x, self.data.x)

    @property
    def yy(self):
        return NvVector2.new(self.data.y, self.data.y)

    @property
    def xy(self):
        return NvVector2.new(self.data.x, self.data.y)

    @property
    def yx(self):
        return NvVector2.new(self.data.y, self.data.x)

    def to_tuple(self):
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

    def __add__(self, NvVector2 other):
        cdef nv_vector2_t res = nv_vector2_add(self.data, other.data)
        return NvVector2.new(res.x, res.y)

    def __sub__(self, NvVector2 other):
        cdef nv_vector2_t res = nv_vector2_sub(self.data, other.data)
        return NvVector2.new(res.x, res.y)

    def __mul__(self, other):
        cdef nv_vector2_t res
        if isinstance(other, NvVector2):
            res = nv_vector2_mul_vector(self.data, (<NvVector2>other).data)
            return NvVector2.new(res.x, res.y)
        elif isinstance(other, (int, float)):
            res = nv_vector2_mul_scalar(self.data, other)
            return NvVector2.new(res.x, res.y)
        return NotImplemented

    def __truediv__(self, other):
        cdef nv_vector2_t res
        if isinstance(other, NvVector2):
            res = nv_vector2_div_vector(self.data, (<NvVector2>other).data)
            return NvVector2.new(res.x, res.y)
        elif isinstance(other, (int, float)):
            res = nv_vector2_div_scalar(self.data, other)
            return NvVector2.new(res.x, res.y)
        return NotImplemented

    def __floordiv__(self, other):
        cdef nv_vector2_t res
        if isinstance(other, NvVector2):
            res = nv_vector2_floordiv_vector(self.data, (<NvVector2>other).data)
            return NvVector2.new(res.x, res.y)
        elif isinstance(other, (int, float)):
            res = nv_vector2_floordiv_scalar(self.data, other)
            return NvVector2.new(res.x, res.y)
        return NotImplemented

    def __iadd__(self, NvVector2 other):
        nv_vector2_iadd(&self.data, other.data)
        return self

    def __isub__(self, NvVector2 other):
        nv_vector2_isub(&self.data, other.data)
        return self

    def __imul__(self, NvVector2 other):
        nv_vector2_imul(&self.data, other.data)
        return self

    def __neg__(self):
        return NvVector2.new(-self.data.x, -self.data.y)

    def __repr__(self):
        return f"NvVector2({self.data.x}, {self.data.y})"

    cdef inline NvVector2 _add(self, NvVector2 other):
        cdef nv_vector2_t res = nv_vector2_add(self.data, other.data)
        return NvVector2.new(res.x, res.y)

    cdef inline NvVector2 _sub(self, NvVector2 other):
        cdef nv_vector2_t res = nv_vector2_sub(self.data, other.data)
        return NvVector2.new(res.x, res.y)

    cdef inline void _iadd(self, NvVector2 other) nogil:
        nv_vector2_iadd(&self.data, other.data)

    cdef inline void _sadd(self, NvVector2 new_vec, NvVector2 old_vec) nogil:
        self.data.x = new_vec.data.x + old_vec.data.x
        self.data.y = new_vec.data.y + old_vec.data.y

    cdef inline void _isub(self, NvVector2 other) nogil:
        nv_vector2_isub(&self.data, other.data)

    cdef inline void _imul(self, NvVector2 other) nogil:
        nv_vector2_imul(&self.data, other.data)

    cpdef void sadd(self, NvVector2 new_vec, NvVector2 old_vec):
        self._sadd(new_vec, old_vec)

    def to_int(self):
        self.data.x = <int>self.data.x
        self.data.y = <int>self.data.y
        return self

    def get_int(self):
        return NvVector2.new(<int>self.data.x, <int>self.data.y)
    
    def to_round(self):
        self.data.x = round(self.data.x)
        self.data.y = round(self.data.y)
        return self

    def get_round(self):
        return NvVector2.new(round(self.data.x), round(self.data.y))

    def to_abs(self):
        self.data.x = abs(self.data.x)
        self.data.y = abs(self.data.y)
        return self

    def get_abs(self):
        return NvVector2.new(abs(self.data.x), abs(self.data.y))

    def to_neg(self):
        self.data.x = -self.data.x
        self.data.y = -self.data.y
        return self

    def get_neg(self):
        return NvVector2.new(-self.data.x, -self.data.y)

    def get_int_tuple(self):
        return (<int>self.data.x, <int>self.data.y)
    
    cdef tuple c_get_int_tuple(self):
        return (<int>self.data.x, <int>self.data.y)

    def to_pygame(self):
        return md.pygame.Vector2(self.data.x, self.data.y)
    
    cpdef NvVector2 copy(self):
        return NvVector2.new(self.data.x, self.data.y)

    def __copy__(self):
        return NvVector2.new(self.data.x, self.data.y)
    
    def __deepcopy__(self, memo):
        return NvVector2.new(self.data.x, self.data.y)
    
    def __hash__(self):
        return hash((self.data.x, self.data.y))
    
    def __len__(self):
        return 2

    def __eq__(self, other):
        if isinstance(other, NvVector2):
            return self.data.x == (<NvVector2>other).data.x and self.data.y == (<NvVector2>other).data.y
        return NotImplemented

    @property
    def length(self):
        return nv_vector2_length(self.data)
    
    def normalize(self):
        cdef nv_vector2_t res = nv_vector2_normalize(self.data)
        return NvVector2.new(res.x, res.y)
    
    def normalize_ip(self):
        self.data = nv_vector2_normalize(self.data)
        return self
    
    def distance_to(self, NvVector2 other):
        return nv_vector2_distance_to(self.data, other.data)

    def distance_squared_to(self, NvVector2 other):
        return nv_vector2_distance_squared_to(self.data, other.data)

    def dot(self, NvVector2 other):
        return nv_vector2_dot(self.data, other.data)