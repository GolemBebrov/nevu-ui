# distutils: language = c++

from nevu_ui.fast.nvvector2.nvvector2 cimport NvVector2
from nevu_ui.fast.nvshader.nvshader cimport NvShader
from libcpp.vector cimport vector
from nevu_ui.fast.nvrendertex.nv_render_tex cimport NvRenderTexture
from nevu_ui.fast.nvrect.nvrect cimport NvRect
ctypedef struct Vector4:
    float x
    float y
    float z
    float w

cpdef void draw_texture_rec(object texture, tuple source_rec, tuple position, tuple color)
cpdef void draw_texture_pro(object texture, tuple source_rec, tuple dest_rec, tuple origin, float rotation, tuple color)
cpdef void begin_blend_mode(int mode)
cpdef void end_blend_mode()
cpdef void begin_texture_mode(object target)
cdef void nv_clear_background(NvRect color)
cdef void c_clear_background_blank() noexcept
cpdef void end_texture_mode()
cpdef void draw_texture_vec(object texture, tuple position, tuple color, bint flip)
cpdef void clear_background(tuple color)
cdef void c_draw_texture_pro(object texture, tuple source_rec, tuple dest_rec, tuple origin, float rotation, tuple color)
cdef void c_draw_texture_vec(object texture, tuple position, tuple color, bint flip)
cdef void c_draw_texture_rec(object texture, tuple source_rec, tuple position, tuple color)
cdef void c_clear_background(tuple color)
cdef void c_draw_texture_nvvec(object texture, NvVector2 position, NvRect color, bint flip)
cdef void c_draw_nvtexture_nvvec(NvRenderTexture texture, NvVector2 position, NvRect color, bint flip)
cdef begin_nvshader_mode(NvShader shader)
cpdef void end_shader_mode()
cpdef void init_raylib_pointers(dict pointers)
cpdef void set_nvshader_value(NvShader shader, int loc_index, tuple value, int uniform_type)
cpdef int get_nvshader_location(NvShader shader, str name)
cpdef void set_nvshader_value_float(NvShader shader, int loc_index, float value)
cpdef void set_nvshader_value_vec4_tuple(NvShader shader, int loc_index, tuple value)
cpdef void set_nvshader_value_vec2_nvvec(NvShader shader, int loc_index, NvVector2 value)
cpdef void set_nvshader_value_vec2_tuple(NvShader shader, int loc_index, tuple value)
cpdef void begin_drawing()
cpdef void end_drawing()
cpdef void set_nvshader_value_float_v(NvShader shader, int loc_index, vector[float] values)
cpdef void set_nvshader_value_vec4_v(NvShader shader, int loc_index, vector[Vector4] values)
cpdef void set_nvshader_value_int(NvShader shader, int loc_index, int value)