# cython: language_level=3
# cython: boundscheck=False
# cython: wraparound=False
# cython: cdivision=True
# cython: nonecheck=False
# cython: initializedcheck=False

from libc.stdint cimport uintptr_t
from cpython.object cimport PyObject
from cpython.tuple cimport PyTuple_GET_ITEM, PyTuple_GET_SIZE

cdef extern from "Python.h":
    float PyFloat_AsDouble(PyObject* obj) nogil
    int PyLong_AsLong(PyObject* obj) nogil

cdef struct Color:
    unsigned char r
    unsigned char g
    unsigned char b
    unsigned char a

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

cdef struct RenderTexture2D:
    unsigned int id
    Texture2D texture
    Texture2D depth

ctypedef void (*DrawTextureRec_ptr)(Texture2D texture, Rectangle source, Vector2 position, Color tint) noexcept
ctypedef void (*DrawTexturePro_ptr)(Texture2D texture, Rectangle source, Rectangle dest, Vector2 origin, float rotation, Color tint) noexcept
ctypedef void (*BeginBlendMode_ptr)(int mode) noexcept
ctypedef void (*EndBlendMode_ptr)() noexcept
ctypedef void (*BeginTextureMode_ptr)(RenderTexture2D target) noexcept
ctypedef void (*EndTextureMode_ptr)() noexcept
ctypedef void (*ClearBackground_ptr)(Color color) noexcept

cdef DrawTextureRec_ptr _c_DrawTextureRec = NULL
cdef DrawTexturePro_ptr _c_DrawTexturePro = NULL
cdef BeginBlendMode_ptr _c_BeginBlendMode = NULL
cdef EndBlendMode_ptr _c_EndBlendMode = NULL
cdef BeginTextureMode_ptr _c_BeginTextureMode = NULL
cdef EndTextureMode_ptr _c_EndTextureMode = NULL
cdef ClearBackground_ptr _c_ClearBackground = NULL

cpdef void init_raylib_pointers(dict pointers):
    global _c_DrawTextureRec, _c_DrawTexturePro, _c_BeginBlendMode, _c_EndBlendMode, _c_BeginTextureMode, _c_EndTextureMode, _c_ClearBackground
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

cdef Texture2D _get_c_texture(object py_tex):
    cdef Texture2D c_tex
    c_tex.id = py_tex.id
    c_tex.width = py_tex.width
    c_tex.height = py_tex.height
    c_tex.mipmaps = py_tex.mipmaps
    c_tex.format = py_tex.format
    return c_tex

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

cdef void set_rectangle_2tuple(Rectangle* rect, tuple pos, tuple size):
    rect.x = PyFloat_AsDouble(PyTuple_GET_ITEM(pos, 0))
    rect.y = PyFloat_AsDouble(PyTuple_GET_ITEM(pos, 1))
    rect.width = PyLong_AsLong(PyTuple_GET_ITEM(size, 0))
    rect.height = PyLong_AsLong(PyTuple_GET_ITEM(size, 1))

cdef void set_rectangle_1tuple(Rectangle* rect, tuple rect_value):
    rect.x = PyFloat_AsDouble(PyTuple_GET_ITEM(rect_value, 0))
    rect.y = PyFloat_AsDouble(PyTuple_GET_ITEM(rect_value, 1))
    rect.width = rect_value[2]
    rect.height = rect_value[3]

cdef void set_vector2_tuple(Vector2* vec, tuple pos):
    vec.x = PyFloat_AsDouble(PyTuple_GET_ITEM(pos, 0))
    vec.y = PyFloat_AsDouble(PyTuple_GET_ITEM(pos, 1))

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