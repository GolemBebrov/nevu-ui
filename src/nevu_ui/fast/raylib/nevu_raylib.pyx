# distutils: language = c++
# cython: language_level=3
# cython: boundscheck=False
# cython: wraparound=False
# cython: cdivision=True
# cython: nonecheck=False
# cython: initializedcheck=False

from libc.stdint cimport uintptr_t

cdef struct Color:
    unsigned char r
    unsigned char g
    unsigned char b
    unsigned char a

cdef struct Vector2:
    float x
    float y

cdef struct Rectangle:
    float x
    float y
    float width
    float height

cdef struct Texture2D:
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

cdef DrawTextureRec_ptr _c_DrawTextureRec = NULL
cdef DrawTexturePro_ptr _c_DrawTexturePro = NULL
cdef BeginBlendMode_ptr _c_BeginBlendMode = NULL
cdef EndBlendMode_ptr _c_EndBlendMode = NULL
cdef BeginTextureMode_ptr _c_BeginTextureMode = NULL
cdef EndTextureMode_ptr _c_EndTextureMode = NULL

cpdef void init_raylib_pointers(dict pointers):
    global _c_DrawTextureRec, _c_DrawTexturePro, _c_BeginBlendMode, _c_EndBlendMode, _c_BeginTextureMode, _c_EndTextureMode
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

cpdef void draw_texture_rec(object texture, tuple source_rec, tuple position, tuple color):
    cdef Texture2D c_tex = _get_c_texture(texture)
    cdef Rectangle c_source
    cdef Vector2 c_pos
    cdef Color c_col
    
    c_source.x = source_rec[0]
    c_source.y = source_rec[1]
    c_source.width = source_rec[2]
    c_source.height = source_rec[3]
    
    c_pos.x = position[0]
    c_pos.y = position[1]
    
    c_col.r = color[0]
    c_col.g = color[1]
    c_col.b = color[2]
    c_col.a = color[3] if len(color) > 3 else 255

    _c_DrawTextureRec(c_tex, c_source, c_pos, c_col)

cpdef void draw_texture_pro(object texture, tuple source_rec, tuple dest_rec, tuple origin, float rotation, tuple color):
    cdef Texture2D c_tex = _get_c_texture(texture)
    cdef Rectangle c_source
    cdef Rectangle c_dest
    cdef Vector2 c_origin
    cdef Color c_col
    
    c_source.x = source_rec[0]
    c_source.y = source_rec[1]
    c_source.width = source_rec[2]
    c_source.height = source_rec[3]
    
    c_dest.x = dest_rec[0]
    c_dest.y = dest_rec[1]
    c_dest.width = dest_rec[2]
    c_dest.height = dest_rec[3]
    
    c_origin.x = origin[0]
    c_origin.y = origin[1]
    
    c_col.r = color[0]
    c_col.g = color[1]
    c_col.b = color[2]
    c_col.a = color[3] if len(color) > 3 else 255

    _c_DrawTexturePro(c_tex, c_source, c_dest, c_origin, rotation, c_col)

cpdef void begin_blend_mode(int mode):
    _c_BeginBlendMode(mode)

cpdef void end_blend_mode():
    _c_EndBlendMode()

cpdef void begin_texture_mode(object target):
    cdef RenderTexture2D c_rt = _get_c_render_texture(target)
    _c_BeginTextureMode(c_rt)

cpdef void end_texture_mode():
    _c_EndTextureMode()