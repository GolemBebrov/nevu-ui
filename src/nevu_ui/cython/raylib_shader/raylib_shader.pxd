cdef class RaylibShader:
    cdef unsigned int id
    cdef int* locs

    @staticmethod
    cdef RaylibShader c_create_from_code(str vertex_shader, str fragment_shader)
