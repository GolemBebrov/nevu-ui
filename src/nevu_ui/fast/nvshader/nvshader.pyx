import nevu_ui.core.modules as md
from libc.stdint cimport uintptr_t
from nevu_ui.fast.raylib.nevu_raylib cimport begin_nvshader_mode, end_shader_mode

cdef NvShader _get_nv_shader(object py_shader):
    cdef NvShader nv_shader = NvShader() 
    nv_shader.id = py_shader.id

    cdef uintptr_t addr = <uintptr_t>int(md.rl.ffi.cast("uintptr_t", py_shader.locs))
    nv_shader.locs = <int*>addr
    return nv_shader

cdef class NvShader:
    @staticmethod
    cdef NvShader c_create_from_code(str vertex_shader, str fragment_shader):
        cdef object pyray_shader = md.rl.load_shader_from_memory(vertex_shader, fragment_shader)
        return _get_nv_shader(pyray_shader)

    @staticmethod
    def create_from_code(str vertex_shader, str fragment_shader):
        return NvShader.c_create_from_code(vertex_shader, fragment_shader)

    def __enter__(self):
        begin_nvshader_mode(self)
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        end_shader_mode()