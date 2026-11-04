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
from nevu_ui.fast.nvvector2.nvvector2 cimport NvVector2, nv_vector2_t
from nevu_ui.fast.nvrect.nvrect cimport NvRect
from nevu_ui.fast.nvshader.nvshader cimport NvShader
from libcpp.vector cimport vector
from libcpp cimport bool
from libc.math cimport roundf

cdef extern from "Python.h":
    float PyFloat_AsDouble(PyObject* obj) nogil

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

ctypedef struct Vector4:
    float x
    float y
    float z
    float w

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

ctypedef bool (*IsMouseButtonPressed_ptr)(int button) noexcept
ctypedef bool (*IsMouseButtonDown_ptr)(int button) noexcept
ctypedef bool (*IsMouseButtonUp_ptr)(int button) noexcept
ctypedef Vector2 (*GetMousePosition_ptr)() noexcept
ctypedef Vector2 (*GetMouseWheelMoveV_ptr)() noexcept
ctypedef bool (*IsKeyPressed_ptr)(int key) noexcept
ctypedef bool (*IsKeyDown_ptr)(int key) noexcept
ctypedef bool (*IsKeyUp_ptr)(int key) noexcept
ctypedef int (*GetCharPressed_ptr)() noexcept
ctypedef bool (*WindowShouldClose_ptr)() noexcept
ctypedef bool (*IsWindowResized_ptr)() noexcept
ctypedef int (*GetScreenWidth_ptr)() noexcept
ctypedef int (*GetScreenHeight_ptr)() noexcept
ctypedef void (*SetTargetFPS_ptr)(int fps) noexcept

cdef EndDrawing_ptr _c_EndDrawing = NULL
cdef BeginDrawing_ptr _c_BeginDrawing = NULL
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

cdef IsMouseButtonPressed_ptr _c_IsMouseButtonPressed = NULL
cdef IsMouseButtonDown_ptr _c_IsMouseButtonDown = NULL
cdef IsMouseButtonUp_ptr _c_IsMouseButtonUp = NULL
cdef GetMousePosition_ptr _c_GetMousePosition = NULL
cdef GetMouseWheelMoveV_ptr _c_GetMouseWheelMoveV = NULL
cdef IsKeyPressed_ptr _c_IsKeyPressed = NULL
cdef IsKeyDown_ptr _c_IsKeyDown = NULL
cdef IsKeyUp_ptr _c_IsKeyUp = NULL
cdef GetCharPressed_ptr _c_GetCharPressed = NULL
cdef WindowShouldClose_ptr _c_WindowShouldClose = NULL
cdef IsWindowResized_ptr _c_IsWindowResized = NULL
cdef GetScreenWidth_ptr _c_GetScreenWidth = NULL
cdef GetScreenHeight_ptr _c_GetScreenHeight = NULL
cdef SetTargetFPS_ptr _c_SetTargetFPS = NULL

cdef object _ffi = None
cdef object _rlc_code = None

cdef inline void _ensure_ffi():
    global _ffi, _rlc_code
    if _ffi is None:
        try:
            from raylib import ffi, rl
            _ffi = ffi
            _rlc_code = rl
        except Exception:
            pass

cdef inline uintptr_t _resolve_pointer(dict pointers, str name):
    if pointers is not None and name in pointers:
        return <uintptr_t>pointers[name]
    _ensure_ffi()
    if _ffi is not None and _rlc_code is not None and hasattr(_rlc_code, name):
        try:
            c_ptr = _ffi.addressof(_rlc_code, name)
            return <uintptr_t>int(_ffi.cast("uintptr_t", c_ptr))
        except Exception:
            return 0
    return 0

cpdef void init_raylib_pointers(dict pointers):
    global _c_DrawTextureRec, _c_DrawTexturePro, _c_BeginBlendMode, _c_EndBlendMode, _c_BeginTextureMode, _c_EndTextureMode, _c_ClearBackground
    global _c_BeginShaderMode, _c_EndShaderMode, _c_SetShaderValue, _c_GetShaderLocation, _c_BeginDrawing, _c_EndDrawing, _c_SetShaderValueV
    global _c_IsMouseButtonPressed, _c_IsMouseButtonDown, _c_IsMouseButtonUp, _c_GetMousePosition, _c_GetMouseWheelMoveV
    global _c_IsKeyPressed, _c_IsKeyDown, _c_IsKeyUp, _c_GetCharPressed, _c_WindowShouldClose, _c_IsWindowResized, _c_GetScreenWidth, _c_GetScreenHeight, _c_SetTargetFPS

    cdef uintptr_t addr

    addr = _resolve_pointer(pointers, "DrawTextureRec")
    if addr != 0: _c_DrawTextureRec = <DrawTextureRec_ptr><void*>addr
    addr = _resolve_pointer(pointers, "DrawTexturePro")
    if addr != 0: _c_DrawTexturePro = <DrawTexturePro_ptr><void*>addr
    addr = _resolve_pointer(pointers, "BeginBlendMode")
    if addr != 0: _c_BeginBlendMode = <BeginBlendMode_ptr><void*>addr
    addr = _resolve_pointer(pointers, "EndBlendMode")
    if addr != 0: _c_EndBlendMode = <EndBlendMode_ptr><void*>addr
    addr = _resolve_pointer(pointers, "BeginTextureMode")
    if addr != 0: _c_BeginTextureMode = <BeginTextureMode_ptr><void*>addr
    addr = _resolve_pointer(pointers, "EndTextureMode")
    if addr != 0: _c_EndTextureMode = <EndTextureMode_ptr><void*>addr
    addr = _resolve_pointer(pointers, "ClearBackground")
    if addr != 0: _c_ClearBackground = <ClearBackground_ptr><void*>addr
    addr = _resolve_pointer(pointers, "BeginShaderMode")
    if addr != 0: _c_BeginShaderMode = <BeginShaderMode_ptr><void*>addr
    addr = _resolve_pointer(pointers, "EndShaderMode")
    if addr != 0: _c_EndShaderMode = <EndShaderMode_ptr><void*>addr
    addr = _resolve_pointer(pointers, "SetShaderValue")
    if addr != 0: _c_SetShaderValue = <SetShaderValue_ptr><void*>addr
    addr = _resolve_pointer(pointers, "GetShaderLocation")
    if addr != 0: _c_GetShaderLocation = <GetShaderLocation_ptr><void*>addr
    addr = _resolve_pointer(pointers, "BeginDrawing")
    if addr != 0: _c_BeginDrawing = <BeginDrawing_ptr><void*>addr
    addr = _resolve_pointer(pointers, "EndDrawing")
    if addr != 0: _c_EndDrawing = <EndDrawing_ptr><void*>addr
    addr = _resolve_pointer(pointers, "SetShaderValueV")
    if addr != 0: _c_SetShaderValueV = <SetShaderValueV_ptr><void*>addr

    addr = _resolve_pointer(pointers, "IsMouseButtonPressed")
    if addr != 0: _c_IsMouseButtonPressed = <IsMouseButtonPressed_ptr><void*>addr
    addr = _resolve_pointer(pointers, "IsMouseButtonDown")
    if addr != 0: _c_IsMouseButtonDown = <IsMouseButtonDown_ptr><void*>addr
    addr = _resolve_pointer(pointers, "IsMouseButtonUp")
    if addr != 0: _c_IsMouseButtonUp = <IsMouseButtonUp_ptr><void*>addr
    addr = _resolve_pointer(pointers, "GetMousePosition")
    if addr != 0: _c_GetMousePosition = <GetMousePosition_ptr><void*>addr
    addr = _resolve_pointer(pointers, "GetMouseWheelMoveV")
    if addr != 0: _c_GetMouseWheelMoveV = <GetMouseWheelMoveV_ptr><void*>addr
    addr = _resolve_pointer(pointers, "IsKeyPressed")
    if addr != 0: _c_IsKeyPressed = <IsKeyPressed_ptr><void*>addr
    addr = _resolve_pointer(pointers, "IsKeyDown")
    if addr != 0: _c_IsKeyDown = <IsKeyDown_ptr><void*>addr
    addr = _resolve_pointer(pointers, "IsKeyUp")
    if addr != 0: _c_IsKeyUp = <IsKeyUp_ptr><void*>addr
    addr = _resolve_pointer(pointers, "GetCharPressed")
    if addr != 0: _c_GetCharPressed = <GetCharPressed_ptr><void*>addr
    addr = _resolve_pointer(pointers, "WindowShouldClose")
    if addr != 0: _c_WindowShouldClose = <WindowShouldClose_ptr><void*>addr
    addr = _resolve_pointer(pointers, "IsWindowResized")
    if addr != 0: _c_IsWindowResized = <IsWindowResized_ptr><void*>addr
    addr = _resolve_pointer(pointers, "GetScreenWidth")
    if addr != 0: _c_GetScreenWidth = <GetScreenWidth_ptr><void*>addr
    addr = _resolve_pointer(pointers, "GetScreenHeight")
    if addr != 0: _c_GetScreenHeight = <GetScreenHeight_ptr><void*>addr
    addr = _resolve_pointer(pointers, "SetTargetFPS")
    if addr != 0: _c_SetTargetFPS = <SetTargetFPS_ptr><void*>addr

cdef inline Texture2D get_c_texture(object py_tex):
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

cdef inline RenderTexture2D get_c_render_texture(object py_rt):
    cdef RenderTexture2D c_rt
    c_rt.id = py_rt.id
    c_rt.texture = get_c_texture(py_rt.texture)
    c_rt.depth = get_c_texture(py_rt.depth)
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
    cdef Texture2D c_tex = get_c_texture(texture)
    cdef Rectangle c_source
    cdef Vector2 c_pos
    cdef Color c_col

    set_rectangle_1tuple(&c_source, source_rec)
    set_vector2_tuple(&c_pos, position)
    set_color(&c_col, color)

    _c_DrawTextureRec(c_tex, c_source, c_pos, c_col)

cdef void c_draw_texture_vec(object texture, tuple position, tuple color, bint flip):
    cdef Texture2D c_tex = get_c_texture(texture)
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

cdef Color color_white
color_white.r = <unsigned char>255
color_white.g = <unsigned char>255
color_white.b = <unsigned char>255
color_white.a = <unsigned char>255

cdef inline Vector2 nv_vector2_t_to_vector2(nv_vector2_t pos) noexcept:
    cdef Vector2 result
    result.x = roundf(<float>pos.x)
    result.y = roundf(<float>pos.y)
    return result

cdef inline void c_draw_texture_maxopt(Texture2D texture, nv_vector2_t pos, bint flip) noexcept:
    cdef float h = texture.height

    if flip: h = -h

    cdef Rectangle c_source
    c_source.x = 0
    c_source.y = 0
    c_source.width = texture.width
    c_source.height = h
    _c_DrawTextureRec(texture, c_source, nv_vector2_t_to_vector2(pos), color_white)

cdef void c_draw_texture_pro(object texture, tuple source_rec, tuple dest_rec, tuple origin, float rotation, tuple color):
    cdef Texture2D c_tex = get_c_texture(texture)
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
    cdef RenderTexture2D c_rt = get_c_render_texture(target)
    _c_BeginTextureMode(c_rt)

cdef inline void begin_texture_mode_raw(RenderTexture2D target):
    _c_BeginTextureMode(target)

cpdef void end_texture_mode():
    _c_EndTextureMode()

cdef void c_clear_background(tuple color):
    cdef Color c_col
    set_color(&c_col, color)
    _c_ClearBackground(c_col)

cpdef void clear_background(tuple color):
    c_clear_background(color)

cpdef void end_shader_mode():
    _c_EndShaderMode()

cdef begin_nvshader_mode(NvShader shader):
    cdef Shader c_shader
    c_shader.id = shader.id
    c_shader.locs = shader.locs
    _c_BeginShaderMode(c_shader)

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

cpdef bint is_mouse_button_pressed(int button):
    if _c_IsMouseButtonPressed != NULL:
        return _c_IsMouseButtonPressed(button)
    return False

cpdef bint is_mouse_button_down(int button):
    if _c_IsMouseButtonDown != NULL:
        return _c_IsMouseButtonDown(button)
    return False

cpdef bint is_mouse_button_up(int button):
    if _c_IsMouseButtonUp != NULL:
        return _c_IsMouseButtonUp(button)
    return False

cpdef NvVector2 get_mouse_position():
    cdef Vector2 pos
    if _c_GetMousePosition != NULL:
        pos = _c_GetMousePosition()
        return NvVector2.new(pos.x, pos.y)
    return NvVector2.new(0, 0)

cpdef NvVector2 get_mouse_wheel_move_v():
    cdef Vector2 v
    if _c_GetMouseWheelMoveV != NULL:
        v = _c_GetMouseWheelMoveV()
        return NvVector2.new(v.x, v.y)
    return NvVector2.new(0, 0)

cpdef float get_mouse_wheel_move_y():
    cdef Vector2 v
    if _c_GetMouseWheelMoveV != NULL:
        v = _c_GetMouseWheelMoveV()
        return v.y
    return 0.0

cpdef bint is_key_pressed(int key):
    if _c_IsKeyPressed != NULL:
        return _c_IsKeyPressed(key)
    return False

cpdef bint is_key_down(int key):
    if _c_IsKeyDown != NULL:
        return _c_IsKeyDown(key)
    return False

cpdef bint is_key_up(int key):
    if _c_IsKeyUp != NULL:
        return _c_IsKeyUp(key)
    return False

cpdef int get_char_pressed():
    if _c_GetCharPressed != NULL:
        return _c_GetCharPressed()
    return 0

cpdef bint window_should_close():
    if _c_WindowShouldClose != NULL:
        return _c_WindowShouldClose()
    return False

cpdef bint is_window_resized():
    if _c_IsWindowResized != NULL:
        return _c_IsWindowResized()
    return False

cpdef int get_screen_width():
    if _c_GetScreenWidth != NULL:
        return _c_GetScreenWidth()
    return 0

cpdef int get_screen_height():
    if _c_GetScreenHeight != NULL:
        return _c_GetScreenHeight()
    return 0

cpdef void set_target_fps(int fps):
    if _c_SetTargetFPS != NULL:
        _c_SetTargetFPS(fps)
