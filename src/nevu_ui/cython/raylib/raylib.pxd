# distutils: language = c++

from nevu_ui.cython.nvvector2.nvvector2 cimport NvVector2, nv_vector2_t
from nevu_ui.cython.raylib_shader.raylib_shader cimport RaylibShader
from libcpp.vector cimport vector
from nevu_ui.cython.nvrect.nvrect cimport NvRect
ctypedef struct Vector4:
    float x
    float y
    float z
    float w

ctypedef struct Texture2D:
    unsigned int id
    int width
    int height
    int mipmaps
    int format

cdef struct RenderTexture2D:
    unsigned int id
    Texture2D texture
    Texture2D depth

cdef inline Texture2D get_c_texture(object py_tex)
cdef inline void begin_texture_mode_raw(RenderTexture2D target)
cpdef void draw_texture_pro(object texture, tuple source_rec, tuple dest_rec, tuple origin, float rotation, tuple color)
cpdef void begin_blend_mode(int mode)
cpdef void end_blend_mode()
cdef inline RenderTexture2D get_c_render_texture(object py_rt)
cpdef void begin_texture_mode(object target)
cpdef void end_texture_mode()
cpdef void clear_background(tuple color)
cdef void c_draw_texture_pro(object texture, tuple source_rec, tuple dest_rec, tuple origin, float rotation, tuple color)
cdef void c_draw_texture_vec(object texture, tuple position, tuple color, bint flip)
cdef void c_draw_texture_rec(object texture, tuple source_rec, tuple position, tuple color)
cdef void c_clear_background(tuple color)
cdef begin_nvshader_mode(RaylibShader shader)
cpdef void end_shader_mode()
cpdef void init_raylib_pointers(dict pointers)
cpdef int get_nvshader_location(RaylibShader shader, str name)
cpdef void set_nvshader_value_float(RaylibShader shader, int loc_index, float value)
cpdef void set_nvshader_value_vec4_tuple(RaylibShader shader, int loc_index, tuple value)
cpdef void set_nvshader_value_vec2_nvvec(RaylibShader shader, int loc_index, NvVector2 value)
cpdef void set_nvshader_value_vec2_tuple(RaylibShader shader, int loc_index, tuple value)
cpdef void begin_drawing()
cpdef void end_drawing()
cpdef void set_nvshader_value_float_v(RaylibShader shader, int loc_index, vector[float] values)
cpdef void set_nvshader_value_vec4_v(RaylibShader shader, int loc_index, vector[Vector4] values)
cpdef void set_nvshader_value_int(RaylibShader shader, int loc_index, int value)
cdef inline void c_draw_texture_maxopt(Texture2D texture, nv_vector2_t pos, bint flip) noexcept
