from libc.math cimport sqrt

ctypedef struct nv_vector2_t:
    double x
    double y

cdef inline nv_vector2_t nv_vector2_new(double x, double y) noexcept nogil:
    cdef nv_vector2_t v
    v.x = x
    v.y = y
    return v

cdef inline nv_vector2_t nv_vector2_add(nv_vector2_t a, nv_vector2_t b) noexcept nogil:
    return nv_vector2_new(a.x + b.x, a.y + b.y)

cdef inline nv_vector2_t nv_vector2_add_triple(nv_vector2_t a, nv_vector2_t b, nv_vector2_t c) noexcept nogil:
    return nv_vector2_new(a.x + b.x + c.x, a.y + b.y + c.y)

cdef inline nv_vector2_t nv_vector2_sub(nv_vector2_t a, nv_vector2_t b) noexcept nogil:
    return nv_vector2_new(a.x - b.x, a.y - b.y)

cdef inline nv_vector2_t nv_vector2_mul_scalar(nv_vector2_t a, double val) noexcept nogil:
    return nv_vector2_new(a.x * val, a.y * val)

cdef inline nv_vector2_t nv_vector2_mul_vector(nv_vector2_t a, nv_vector2_t b) noexcept nogil:
    return nv_vector2_new(a.x * b.x, a.y * b.y)

cdef inline nv_vector2_t nv_vector2_div_scalar(nv_vector2_t a, double val) noexcept nogil:
    return nv_vector2_new(a.x / val, a.y / val)

cdef inline nv_vector2_t nv_vector2_div_vector(nv_vector2_t a, nv_vector2_t b) noexcept nogil:
    return nv_vector2_new(a.x / b.x, a.y / b.y)

cdef inline nv_vector2_t nv_vector2_floordiv_scalar(nv_vector2_t a, double val) noexcept nogil:
    return nv_vector2_new(a.x // val, a.y // val)

cdef inline nv_vector2_t nv_vector2_floordiv_vector(nv_vector2_t a, nv_vector2_t b) noexcept nogil:
    return nv_vector2_new(a.x // b.x, a.y // b.y)

cdef inline void nv_vector2_iadd(nv_vector2_t *self, nv_vector2_t other) noexcept nogil:
    self.x += other.x
    self.y += other.y

cdef inline void nv_vector2_isub(nv_vector2_t *self, nv_vector2_t other) noexcept nogil:
    self.x -= other.x
    self.y -= other.y

cdef inline void nv_vector2_imul(nv_vector2_t *self, nv_vector2_t other) noexcept nogil:
    self.x *= other.x
    self.y *= other.y

cdef inline double nv_vector2_length(nv_vector2_t v) noexcept nogil:
    return sqrt(v.x * v.x + v.y * v.y)

cdef inline nv_vector2_t nv_vector2_normalize(nv_vector2_t v) noexcept nogil:
    cdef double l = sqrt(v.x * v.x + v.y * v.y)
    if l == 0.0:
        return nv_vector2_new(0.0, 0.0)
    cdef double inv_l = 1.0 / l
    return nv_vector2_new(v.x * inv_l, v.y * inv_l)

cdef inline double nv_vector2_distance_to(nv_vector2_t a, nv_vector2_t b) noexcept nogil:
    cdef double dx = a.x - b.x
    cdef double dy = a.y - b.y
    return sqrt(dx * dx + dy * dy)

cdef inline double nv_vector2_distance_squared_to(nv_vector2_t a, nv_vector2_t b) noexcept nogil:
    cdef double dx = a.x - b.x
    cdef double dy = a.y - b.y
    return dx * dx + dy * dy

cdef inline double nv_vector2_dot(nv_vector2_t a, nv_vector2_t b) noexcept nogil:
    return a.x * b.x + a.y * b.y

cdef class NvVector2:
    cdef nv_vector2_t data
    
    @staticmethod
    cdef inline NvVector2 new(double x, double y)

    @staticmethod
    cdef inline NvVector2 cfrom_list(list other)
    
    @staticmethod
    cdef inline NvVector2 cfrom_ints(int x, int y)
    
    @staticmethod
    cdef inline NvVector2 cfrom_floats(float x, float y)
    
    @staticmethod
    cdef inline NvVector2 cfrom_tuple(tuple other)
    
    @staticmethod
    cdef inline NvVector2 cfrom_nvvector2(NvVector2 other)
    
    @staticmethod
    cdef inline NvVector2 cfrom_xy(double x, double y)

    cdef tuple c_get_int_tuple(self)
    cdef NvVector2 _add(self, NvVector2 other)
    cdef NvVector2 _sub(self, NvVector2 other)
    cdef void _iadd(self, NvVector2 other) nogil
    cdef void _isub(self, NvVector2 other) nogil
    cdef void _imul(self, NvVector2 other) nogil 
    cdef void _sadd(self, NvVector2 new_vec, NvVector2 old_vec) nogil
    cpdef NvVector2 copy(self)
    cpdef void sadd(self, NvVector2 new_vec, NvVector2 old_vec)