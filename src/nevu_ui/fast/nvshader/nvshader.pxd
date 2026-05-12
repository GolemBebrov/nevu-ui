cdef class NvShader:
    cdef unsigned int id
    cdef int* locs

    @staticmethod
    cdef NvShader c_create_from_code(str vertex_shader, str fragment_shader)