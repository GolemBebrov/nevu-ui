# distutils: language = c++
# cython: language_level=3
# cython: boundscheck=False
# cython: wraparound=False
# cython: cdivision=True
# cython: nonecheck=False
# cython: initializedcheck=False

from libc.stdint cimport uintptr_t
from cpython.object cimport PyObject
from cpython.tuple cimport PyTuple_GET_ITEM, PyTuple_GET_SIZE
from nevu_ui.fast.nvvector2.nvvector2 cimport NvVector2
from nevu_ui.fast.nvrect.nvrect cimport NvRect
from nevu_ui.fast.nvshader.nvshader cimport NvShader
from libcpp.vector cimport vector
cdef extern from "Python.h":
    float PyFloat_AsDouble(PyObject* obj) nogil
    int PyLong_AsLong(PyObject* obj) nogil

cdef struct Color:
    unsigned char r
    unsigned char g
    unsigned char b
    unsigned char a

ctypedef struct Vector3:
    float x
    float y
    float z

ctypedef struct Vector2:
    float x
    float y

ctypedef struct Rectangle:
    float x    
    float y
    float width
    float height

ctypedef struct Texture2D:
    unsigned int id
    int width
    int height
    int mipmaps
    int format

ctypedef struct Vector4:
    float x
    float y
    float z
    float w
cdef struct RenderTexture2D:
    unsigned int id
    Texture2D texture
    Texture2D depth

ctypedef struct Shader:
    unsigned int id
    int* locs

ctypedef void (*DrawTextureRec_ptr)(Texture2D texture, Rectangle source, Vector2 position, Color tint) noexcept
ctypedef void (*DrawTexturePro_ptr)(Texture2D texture, Rectangle source, Rectangle dest, Vector2 origin, float rotation, Color tint) noexcept
ctypedef void (*BeginBlendMode_ptr)(int mode) noexcept
ctypedef void (*EndBlendMode_ptr)() noexcept
ctypedef void (*BeginTextureMode_ptr)(RenderTexture2D target) noexcept
ctypedef void (*EndTextureMode_ptr)() noexcept
ctypedef void (*ClearBackground_ptr)(Color color) noexcept
ctypedef void (*BeginShaderMode_ptr)(Shader shader) noexcept
ctypedef void (*EndShaderMode_ptr)() noexcept
ctypedef void (*SetShaderValue_ptr)(Shader shader, int locIndex, const void *value, int uniformType) noexcept
ctypedef void (*SetShaderValueV_ptr)(Shader shader, int locIndex, const void *value, int uniformType, int count) noexcept
ctypedef int (*GetShaderLocation_ptr)(Shader shader, const char* uniformName)
ctypedef void (*BeginDrawing_ptr)()
ctypedef void (*EndDrawing_ptr)()

cdef EndDrawing_ptr _c_EndDrawing
cdef BeginDrawing_ptr _c_BeginDrawing
cdef DrawTextureRec_ptr _c_DrawTextureRec = NULL
cdef DrawTexturePro_ptr _c_DrawTexturePro = NULL
cdef BeginBlendMode_ptr _c_BeginBlendMode = NULL
cdef EndBlendMode_ptr _c_EndBlendMode = NULL
cdef BeginTextureMode_ptr _c_BeginTextureMode = NULL
cdef EndTextureMode_ptr _c_EndTextureMode = NULL
cdef ClearBackground_ptr _c_ClearBackground = NULL
cdef BeginShaderMode_ptr _c_BeginShaderMode = NULL
cdef EndShaderMode_ptr _c_EndShaderMode = NULL
cdef SetShaderValue_ptr _c_SetShaderValue = NULL
cdef SetShaderValueV_ptr _c_SetShaderValueV = NULL
cdef GetShaderLocation_ptr _c_GetShaderLocation = NULL

cpdef void init_raylib_pointers(dict pointers):
    global _c_DrawTextureRec, _c_DrawTexturePro, _c_BeginBlendMode, _c_EndBlendMode, _c_BeginTextureMode, _c_EndTextureMode, _c_ClearBackground
    global _c_BeginShaderMode, _c_EndShaderMode, _c_SetShaderValue, _c_GetShaderLocation, _c_BeginDrawing, _c_EndDrawing, _c_SetShaderValueV
    if "DrawTextureRec" in pointers:
        _c_DrawTextureRec = <DrawTextureRec_ptr><void*><uintptr_t>pointers["DrawTextureRec"]
    if "DrawTexturePro" in pointers:
        _c_DrawTexturePro = <DrawTexturePro_ptr><void*><uintptr_t>pointers["DrawTexturePro"]
    if "BeginBlendMode" in pointers:
        _c_BeginBlendMode = <BeginBlendMode_ptr><void*><uintptr_t>pointers["BeginBlendMode"]
    if "EndBlendMode" in pointers:
        _c_EndBlendMode = <EndBlendMode_ptr><void*><uintptr_t>pointers["EndBlendMode"]
    if "BeginTextureMode" in pointers:
        _c_BeginTextureMode = <BeginTextureMode_ptr><void*><uintptr_t>pointers["BeginTextureMode"]
    if "EndTextureMode" in pointers:
        _c_EndTextureMode = <EndTextureMode_ptr><void*><uintptr_t>pointers["EndTextureMode"]
    if "ClearBackground" in pointers:
        _c_ClearBackground = <ClearBackground_ptr><void*><uintptr_t>pointers["ClearBackground"]
    if "BeginShaderMode" in pointers:
        _c_BeginShaderMode = <BeginShaderMode_ptr><void*><uintptr_t>pointers["BeginShaderMode"]
    if "EndShaderMode" in pointers:
        _c_EndShaderMode = <EndShaderMode_ptr><void*><uintptr_t>pointers["EndShaderMode"]
    if "SetShaderValue" in pointers:
        _c_SetShaderValue = <SetShaderValue_ptr><void*><uintptr_t>pointers["SetShaderValue"]
    if "GetShaderLocation" in pointers:
        _c_GetShaderLocation = <GetShaderLocation_ptr><void*><uintptr_t>pointers["GetShaderLocation"]
    if "BeginDrawing" in pointers:
        _c_BeginDrawing = <BeginDrawing_ptr><void*><uintptr_t>pointers["BeginDrawing"]
    if "EndDrawing" in pointers:
        _c_EndDrawing = <EndDrawing_ptr><void*><uintptr_t>pointers["EndDrawing"]
    if "SetShaderValueV" in pointers:
        _c_SetShaderValueV = <SetShaderValueV_ptr><void*><uintptr_t>pointers["SetShaderValueV"]
cdef Texture2D _get_c_texture(object py_tex):
    cdef Texture2D c_tex
    c_tex.id = py_tex.id
    c_tex.width = py_tex.width
    c_tex.height = py_tex.height
    c_tex.mipmaps = py_tex.mipmaps
    c_tex.format = py_tex.format
    return c_tex

cdef Shader _get_c_shader(object py_shader):
    cdef Shader c_shader
    c_shader.id = py_shader.id
    c_shader.locs = <int*><uintptr_t>py_shader.locs
    return c_shader

cdef Shader _get_c_shader_from_nvshader(NvShader nv_shader):
    cdef Shader c_shader
    c_shader.id = nv_shader.id
    c_shader.locs = nv_shader.locs
    return c_shader

cdef RenderTexture2D _get_c_render_texture(object py_rt):
    cdef RenderTexture2D c_rt
    c_rt.id = py_rt.id
    c_rt.texture = _get_c_texture(py_rt.texture)
    c_rt.depth = _get_c_texture(py_rt.depth)
    return c_rt

cdef void set_rectangle_4vals(Rectangle* rect, float x, float y, int width, int height) noexcept nogil:
    rect.x = x
    rect.y = y
    rect.width = width
    rect.height = height

cdef void set_rectangle_1tuple(Rectangle* rect, tuple rect_value):
    rect.x = PyFloat_AsDouble(PyTuple_GET_ITEM(rect_value, 0))
    rect.y = PyFloat_AsDouble(PyTuple_GET_ITEM(rect_value, 1))
    rect.width = rect_value[2]
    rect.height = rect_value[3]

cdef void set_vector2_tuple(Vector2* vec, tuple pos):
    vec.x = PyFloat_AsDouble(PyTuple_GET_ITEM(pos, 0))
    vec.y = PyFloat_AsDouble(PyTuple_GET_ITEM(pos, 1))

cdef void set_vector2_nvvector2(Vector2* vec, NvVector2 pos):
    vec.x = pos.x
    vec.y = pos.y

cdef void set_color(Color* col, tuple color):
    cdef Py_ssize_t color_size = PyTuple_GET_SIZE(color)
    col.r = <unsigned char>PyFloat_AsDouble(PyTuple_GET_ITEM(color, 0))
    col.g = <unsigned char>PyFloat_AsDouble(PyTuple_GET_ITEM(color, 1))
    col.b = <unsigned char>PyFloat_AsDouble(PyTuple_GET_ITEM(color, 2))
    if color_size > 3:
        col.a = <unsigned char>PyFloat_AsDouble(PyTuple_GET_ITEM(color, 3))
    else:
        col.a = 255

cdef void c_draw_texture_rec(object texture, tuple source_rec, tuple position, tuple color):
    cdef Texture2D c_tex = _get_c_texture(texture)
    cdef Rectangle c_source
    cdef Vector2 c_pos
    cdef Color c_col

    set_rectangle_1tuple(&c_source, source_rec)
    
    set_vector2_tuple(&c_pos, position)
    
    set_color(&c_col, color)

    _c_DrawTextureRec(c_tex, c_source, c_pos, c_col)

cpdef void draw_texture_rec(object texture, tuple source_rec, tuple position, tuple color):
    c_draw_texture_rec(texture, source_rec, position, color)

cpdef void draw_texture_rec_ez(object texture, tuple source_rec, tuple position):
    c_draw_texture_rec(texture, source_rec, position, (255, 255, 255, 255))

cdef void c_draw_texture_vec(object texture, tuple position, tuple color, bint flip):
    cdef Texture2D c_tex = _get_c_texture(texture)
    cdef Rectangle c_source
    cdef Vector2 c_pos
    cdef Color c_col

    h = c_tex.height
    if flip:
        h = -h

    set_rectangle_4vals(&c_source, 0, 0, c_tex.width, h)
    
    set_vector2_tuple(&c_pos, position)

    set_color(&c_col, color)

    _c_DrawTextureRec(c_tex, c_source, c_pos, c_col)

cpdef void draw_texture_vec(object texture, tuple position, tuple color, bint flip):
    c_draw_texture_vec(texture, position, color, flip)

cpdef void draw_texture_vec_ez(object texture, tuple position, bint flip):
    c_draw_texture_vec(texture, position, (255, 255, 255, 255), flip)

cdef void c_draw_texture_nvvec(object texture, NvVector2 position, tuple color, bint flip):
    cdef Texture2D c_tex = _get_c_texture(texture)
    cdef Rectangle c_source
    cdef Vector2 c_pos
    cdef Color c_col

    h = c_tex.height
    if flip:
        h = -h
    
    set_rectangle_4vals(&c_source, 0, 0, c_tex.width, h)

    set_vector2_nvvector2(&c_pos, position)

    set_color(&c_col, color)

    _c_DrawTextureRec(c_tex, c_source, c_pos, c_col)

cpdef void draw_texture_nvvec(object texture, NvVector2 position, tuple color, bint flip):
    c_draw_texture_nvvec(texture, position, color, flip)

cpdef void draw_texture_nvvec_ez(object texture, NvVector2 position, bint flip):
    c_draw_texture_nvvec(texture, position, (255, 255, 255, 255), flip)

cdef void c_draw_texture_pro(object texture, tuple source_rec, tuple dest_rec, tuple origin, float rotation, tuple color):
    cdef Texture2D c_tex = _get_c_texture(texture)
    cdef Rectangle c_source
    cdef Rectangle c_dest
    cdef Vector2 c_origin
    cdef Color c_col
    
    set_rectangle_1tuple(&c_source, source_rec)
    
    set_rectangle_1tuple(&c_dest, dest_rec)
    
    set_vector2_tuple(&c_origin, origin)
    
    set_color(&c_col, color)

    _c_DrawTexturePro(c_tex, c_source, c_dest, c_origin, rotation, c_col)

cpdef void draw_texture_pro(object texture, tuple source_rec, tuple dest_rec, tuple origin, float rotation, tuple color):
    c_draw_texture_pro(texture, source_rec, dest_rec, origin, rotation, color)

cpdef void begin_blend_mode(int mode):
    _c_BeginBlendMode(mode)

cpdef void end_blend_mode():
    _c_EndBlendMode()

cpdef void begin_texture_mode(object target):
    cdef RenderTexture2D c_rt = _get_c_render_texture(target)
    _c_BeginTextureMode(c_rt)

cpdef void end_texture_mode():
    _c_EndTextureMode()

cdef void c_clear_background(tuple color):
    cdef Color c_col
    set_color(&c_col, color)
    _c_ClearBackground(c_col)

cpdef void clear_background(tuple color):
    c_clear_background(color)

cpdef void begin_shader_mode(object shader):
    cdef Shader c_shader = _get_c_shader(shader)
    _c_BeginShaderMode(c_shader)

cpdef void end_shader_mode():
    _c_EndShaderMode()

cdef begin_nvshader_mode(NvShader shader):
    cdef Shader c_shader
    c_shader.id = shader.id
    c_shader.locs = shader.locs
    _c_BeginShaderMode(c_shader)

cpdef void set_shader_value(object shader, int loc_index, tuple value, int uniform_type):
    cdef Shader c_shader = _get_c_shader(shader)
    cdef float[4] f_val
    cdef int[4] i_val
    cdef int i
    cdef Py_ssize_t val_size = PyTuple_GET_SIZE(value)
    
    if val_size > 4:
        val_size = 4
        
    if uniform_type >= 0 and uniform_type <= 3:
        for i in range(val_size):
            f_val[i] = PyFloat_AsDouble(PyTuple_GET_ITEM(value, i))
        _c_SetShaderValue(c_shader, loc_index, <const void*>f_val, uniform_type)
    else:
        for i in range(val_size):
            i_val[i] = PyLong_AsLong(PyTuple_GET_ITEM(value, i))
        _c_SetShaderValue(c_shader, loc_index, <const void*>i_val, uniform_type)
    
cpdef void set_nvshader_value(NvShader shader, int loc_index, tuple value, int uniform_type):
    cdef Shader c_shader = _get_c_shader_from_nvshader(shader)
    cdef float[4] f_val
    cdef int[4] i_val
    cdef int i
    cdef Py_ssize_t val_size = PyTuple_GET_SIZE(value)
    
    if val_size > 4:
        val_size = 4
        
    if uniform_type >= 0 and uniform_type <= 3:
        for i in range(val_size):
            f_val[i] = PyFloat_AsDouble(PyTuple_GET_ITEM(value, i))
        _c_SetShaderValue(c_shader, loc_index, <const void*>f_val, uniform_type)
    else:
        for i in range(val_size):
            i_val[i] = PyLong_AsLong(PyTuple_GET_ITEM(value, i))
        _c_SetShaderValue(c_shader, loc_index, <const void*>i_val, uniform_type)

cpdef int get_shader_location(object shader, str name):
    cdef Shader c_shader = _get_c_shader(shader)
    cdef bytes c_name = name.encode('utf-8')
    return _c_GetShaderLocation(c_shader, <const char*>c_name)

cpdef int get_nvshader_location(NvShader shader, str name):
    cdef Shader c_shader = _get_c_shader_from_nvshader(shader)
    cdef bytes c_name = name.encode('utf-8')
    return _c_GetShaderLocation(c_shader, <const char*>c_name)

cdef inline void set_fval_from_nvvector2(float* f_val, NvVector2 value):
    f_val[0] = value.x
    f_val[1] = value.y

cdef inline void set_fval_from_tuple(float* f_val, tuple value):
    f_val[0] = PyFloat_AsDouble(PyTuple_GET_ITEM(value, 0))
    f_val[1] = PyFloat_AsDouble(PyTuple_GET_ITEM(value, 1))

cdef inline void set_fval_from_tuple4(float* f_val, tuple value):
    f_val[0] = PyFloat_AsDouble(PyTuple_GET_ITEM(value, 0))
    f_val[1] = PyFloat_AsDouble(PyTuple_GET_ITEM(value, 1))
    f_val[2] = PyFloat_AsDouble(PyTuple_GET_ITEM(value, 2))
    f_val[3] = PyFloat_AsDouble(PyTuple_GET_ITEM(value, 3))

cpdef void set_shader_value_vec2_nvvec(object shader, int loc_index, NvVector2 value):
    cdef Shader c_shader = _get_c_shader(shader)
    cdef float[2] f_val
    set_fval_from_nvvector2(f_val, value)
    _c_SetShaderValue(c_shader, loc_index, <const void*>f_val, 1)

cpdef void set_shader_value_vec2_tuple(object shader, int loc_index, tuple value):
    cdef Shader c_shader = _get_c_shader(shader)
    cdef float[2] f_val 
    set_fval_from_tuple(f_val, value)
    _c_SetShaderValue(c_shader, loc_index, <const void*>f_val, 1)

cpdef void set_nvshader_value_vec2_nvvec(NvShader shader, int loc_index, NvVector2 value):
    cdef Shader c_shader = _get_c_shader_from_nvshader(shader)
    cdef float[2] f_val 
    set_fval_from_nvvector2(f_val, value)
    _c_SetShaderValue(c_shader, loc_index, <const void*>f_val, 1)

cpdef void set_nvshader_value_vec2_tuple(NvShader shader, int loc_index, tuple value):
    cdef Shader c_shader = _get_c_shader_from_nvshader(shader)
    cdef float[2] f_val
    set_fval_from_tuple(f_val, value)
    _c_SetShaderValue(c_shader, loc_index, <const void*>f_val, 1)

cpdef void set_shader_value_vec4_tuple(object shader, int loc_index, tuple value):
    cdef Shader c_shader = _get_c_shader(shader)
    cdef float[4] f_val
    set_fval_from_tuple4(f_val, value)
    _c_SetShaderValue(c_shader, loc_index, <const void*>f_val, 3)

cpdef void set_nvshader_value_vec4_tuple(NvShader shader, int loc_index, tuple value):
    cdef Shader c_shader = _get_c_shader_from_nvshader(shader)
    cdef float[4] f_val
    set_fval_from_tuple4(f_val, value)
    _c_SetShaderValue(c_shader, loc_index, <const void*>f_val, 3)

cpdef void set_nvshader_value_vec4_v(NvShader shader, int loc_index, vector[Vector4] values):
    cdef Shader c_shader = _get_c_shader_from_nvshader(shader)
    if not values.empty():
        _c_SetShaderValueV(c_shader, loc_index, <const void*>&values[0], 3, <int>values.size())

cpdef void set_nvshader_value_float_v(NvShader shader, int loc_index, vector[float] values):
    cdef Shader c_shader = _get_c_shader_from_nvshader(shader)
    if not values.empty():
        _c_SetShaderValueV(c_shader, loc_index, <const void*>&values[0], 0, <int>values.size())

cpdef void set_shader_value_float(object shader, int loc_index, float value):
    cdef Shader c_shader = _get_c_shader(shader)
    _c_SetShaderValue(c_shader, loc_index, <const void*>&value, 0)

cpdef void set_nvshader_value_float(NvShader shader, int loc_index, float value):
    cdef Shader c_shader = _get_c_shader_from_nvshader(shader)
    _c_SetShaderValue(c_shader, loc_index, <const void*>&value, 0)

cpdef void set_nvshader_value_int(NvShader shader, int loc_index, int value):
    cdef Shader c_shader = _get_c_shader_from_nvshader(shader)
    _c_SetShaderValue(c_shader, loc_index, <const void*>&value, 4)

cpdef void begin_drawing():
    _c_BeginDrawing()

cpdef void end_drawing():
    _c_EndDrawing()