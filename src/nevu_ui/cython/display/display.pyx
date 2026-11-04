import nevu_ui.core.modules as md
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from pyray import Texture
from nevu_ui.core import Annotations
from nevu_ui.presentation.color import Color
from nevu_ui.assets.shader import ShaderLibrary #SdfShader, BorderShader, GlassySdfShader, GlassyBorderShader, LineSdfShader


from nevu_ui.cython.rect.rect cimport Rect
from nevu_ui.cython.vector2.vector2 cimport Vector2
from nevu_ui.cython.raylib.raylib cimport (
    init_raylib_pointers, begin_blend_mode, end_blend_mode, begin_texture_mode, end_texture_mode,
    c_draw_texture_pro, c_draw_texture_rec, c_draw_texture_vec, begin_nvshader_mode, end_shader_mode, begin_drawing, end_drawing,
    get_nvshader_location, set_nvshader_value_float, set_nvshader_value_vec2_nvvec, set_nvshader_value_vec4_tuple, set_nvshader_value_vec2_tuple
)
from nevu_ui.cython.raylib_shader.raylib_shader cimport RaylibShader

# Pygame
cdef type pg_surface_t, pg_rect_t #type: ignore

cdef bint window_renderer_created = False
cdef tuple fill_color = Color.White

cdef inline void check_singleton() noexcept:
    global window_renderer_created
    #if window_renderer_created: raise RuntimeError("Window renderer already created")
    window_renderer_created = True

cdef class WindowRendererBase:
    def __init__(self):
        pass #Used for typehints :D

    def get_tuple_rect(self) -> tuple: ...
    def get_rect(self) -> Rect: ...
    def get_width(self) -> int: ...
    def get_height(self) -> int: ...
    def blit(self, source, dest): ...
    def set_title(self, title: str): ...
    def begin_frame(self): ...
    def end_frame(self): ...
    def clear(self, color: Annotations.rgba_color): ...
    def get_size_tuple(self) -> tuple[int, int]: ...
    def get_size_nvvec(self) -> Vector2: ...
    @property
    def screen(self): ...

cdef class WindowRendererRaylib:
    cdef public RaylibShader _sdf_shader, _border_shader, _glassy_sdf_shader, _glassy_border_shader, _line_sdf_shader
    cdef public dict _sdf_locs, _border_locs, _glassy_sdf_locs, _glassy_border_locs, _line_sdf_locs
    cdef public object root, _blank_texture

    @staticmethod
    def create_initialized(window):
        cdef WindowRendererRaylib self = WindowRendererRaylib.__new__(WindowRendererRaylib)
        check_singleton()
        self._init_base(window)
        return self

    def __init__(self, title, size, root, **kwargs):
        check_singleton()
        self._init_window(title, size, kwargs.get('resizable', False))
        self._init_base(root)

    cdef inline void _init_window(self, str title, tuple size, bint resizable):
        if resizable:
            md.rl.set_config_flags(md.rl.ConfigFlags.FLAG_WINDOW_RESIZABLE)
        md.rl.init_window(int(size[0]), int(size[1]), title)

    cdef inline void _init_base(self, root):
        self.root = root
        self.load_raylib_fast_bindings()
        self._sdf_shader = RaylibShader.c_create_from_code(ShaderLibrary.BaseVertex.read_text(), ShaderLibrary.StandardSDF.read_text())
        self._sdf_locs = {
            "texture0": get_nvshader_location(self._sdf_shader, "texture0"),
            "colDiffuse": get_nvshader_location(self._sdf_shader, "colDiffuse"),
            "rectSize": get_nvshader_location(self._sdf_shader, "rectSize"),
            "radius": get_nvshader_location(self._sdf_shader, "radius"),
            }
        self._glassy_sdf_shader = RaylibShader.c_create_from_code(ShaderLibrary.BaseVertex.read_text(), ShaderLibrary.GlassySDF.read_text())
        self._glassy_sdf_locs = {
            "texture0": get_nvshader_location(self._glassy_sdf_shader, "texture0"),
            "colDiffuse": get_nvshader_location(self._glassy_sdf_shader, "colDiffuse"),
            "rectSize": get_nvshader_location(self._glassy_sdf_shader, "rectSize"),
            "radius": get_nvshader_location(self._glassy_sdf_shader, "radius"),
        }
        set_nvshader_value_vec4_tuple(self._sdf_shader, self._sdf_locs['colDiffuse'], (1.0, 1.0, 1.0, 1.0))
        self._glassy_border_shader = RaylibShader.c_create_from_code(ShaderLibrary.BaseVertex.read_text(), ShaderLibrary.GlassyBorder.read_text())
        self._glassy_border_locs = {
            "texture0": get_nvshader_location(self._glassy_border_shader, "texture0"),
            "colDiffuse": get_nvshader_location(self._glassy_border_shader, "colDiffuse"),
            "rectSize": get_nvshader_location(self._glassy_border_shader, "rectSize"),
            "radius": get_nvshader_location(self._glassy_border_shader, "radius"),
            "borderColor": get_nvshader_location(self._glassy_border_shader, "borderColor"),
            "thickness": get_nvshader_location(self._glassy_border_shader, "thickness")
        }
        set_nvshader_value_vec4_tuple(self._glassy_border_shader, self._glassy_border_locs['colDiffuse'], (1.0, 1.0, 1.0, 1.0))

        self._border_shader = RaylibShader.c_create_from_code(ShaderLibrary.BaseVertex.read_text(), ShaderLibrary.StandardBorder.read_text())
        self._border_locs = {
            "texture0": get_nvshader_location(self._border_shader, "texture0"),
            "colDiffuse": get_nvshader_location(self._border_shader, "colDiffuse"),
            "rectSize": get_nvshader_location(self._border_shader, "rectSize"),
            "radius": get_nvshader_location(self._border_shader, "radius"),
            "borderColor": get_nvshader_location(self._border_shader, "borderColor"),
            "thickness": get_nvshader_location(self._border_shader, "thickness"),
        }
        set_nvshader_value_vec4_tuple(self._border_shader, self._border_locs['colDiffuse'], (1.0, 1.0, 1.0, 1.0),)

        self._line_sdf_shader = RaylibShader.c_create_from_code(ShaderLibrary.BaseVertex.read_text(), ShaderLibrary.StandardLine.read_text())
        self._line_sdf_locs = {
            "p1": get_nvshader_location(self._line_sdf_shader, "p1"),
            "p2": get_nvshader_location(self._line_sdf_shader, "p2"),
            "thickness": get_nvshader_location(self._line_sdf_shader, "thickness"),
            "radius": get_nvshader_location(self._line_sdf_shader, "radius"),
            "lineColor": get_nvshader_location(self._line_sdf_shader, "lineColor"),
            "bboxPos": get_nvshader_location(self._line_sdf_shader, "bboxPos"),
            "bboxSize": get_nvshader_location(self._line_sdf_shader, "bboxSize"),
        }

        img = md.rl.gen_image_color(1, 1, md.rl.WHITE)
        self._blank_texture = md.rl.load_texture_from_image(img)
        md.rl.unload_image(img)

    cpdef load_raylib_fast_bindings(self):
        functions_to_load = [
            "DrawTextureRec",
            "DrawTexturePro",
            "BeginBlendMode",
            "EndBlendMode",
            "BeginTextureMode",
            "EndTextureMode",
            "ClearBackground",
            "BeginShaderMode",
            "EndShaderMode",
            "SetShaderValue",
            "GetShaderLocation",
            "BeginDrawing",
            "EndDrawing",
            "SetShaderValueV",
            "IsMouseButtonPressed",
            "IsMouseButtonDown",
            "IsMouseButtonUp",
            "GetMousePosition",
            "GetMouseWheelMoveV",
            "IsKeyPressed",
            "IsKeyDown",
            "IsKeyUp",
            "GetCharPressed",
            "WindowShouldClose",
            "IsWindowResized",
            "GetScreenWidth",
            "GetScreenHeight",
            "SetTargetFPS"
        ]
        pointer_dict = {}
        for func_name in functions_to_load:
            try:
                from raylib import ffi, rl as rlc_code
                c_ptr = ffi.addressof(rlc_code, func_name)
                addr = int(ffi.cast("uintptr_t", c_ptr))
                pointer_dict[func_name] = addr
            except AttributeError:
                print(f"Warning: Could not load function {func_name} from raylib backend")
        init_raylib_pointers(pointer_dict)
        print(f"Successfully loaded {len(pointer_dict)} fast raylib functions.")

    cpdef void draw_sdf_rect(self, tuple pos, tuple size, object radii, tuple color, bint glassy = False):
        cdef float w = <float>size[0]
        cdef float h = <float>size[1]
        if w <= 0.0 or h <= 0.0:
            return

        cdef float x = <float>pos[0]
        cdef float y = <float>pos[1]

        cdef tuple rad_tuple
        if isinstance(radii, (int, float)):
            rad_tuple = (float(radii), float(radii), float(radii), float(radii))
        elif isinstance(radii, (tuple, list)):
            rad_tuple = (float(radii[0]), float(radii[1]), float(radii[2]), float(radii[3]))
        else:
            rad_tuple = (0.0, 0.0, 0.0, 0.0)

        cdef tuple c = color
        if len(c) == 3:
            c = (c[0], c[1], c[2], 255)

        if glassy:
            self._begin_glassy_sdf(w, h, rad_tuple)
        else:
            self._begin_sdf(w, h, rad_tuple)

        begin_blend_mode(md.rl.BlendMode.BLEND_ALPHA_PREMULTIPLY)
        c_draw_texture_pro(
            self._blank_texture,
            (0.0, 0.0, 1.0, -1.0),
            (x, y, w, h),
            (0.0, 0.0),
            0.0,
            c
        )
        end_blend_mode()
        self._end_shader()

    cpdef void draw_sdf_line(self, object pos_from, object pos_to, float width, object radius, tuple color, tuple max_bounds):
        if width <= 0.0:
            return

        cdef float p1_x = <float>pos_from[0]
        cdef float p1_y = <float>pos_from[1]
        cdef float p2_x = <float>pos_to[0]
        cdef float p2_y = <float>pos_to[1]

        cdef float r_val
        if isinstance(radius, (tuple, list)):
            r_val = <float>radius[0] if len(radius) > 0 else (width * 0.5)
        elif radius is not None:
            r_val = <float>radius
        else:
            r_val = width * 0.5

        cdef float pad = width * 0.5 + 2.0
        cdef float min_x = max(0.0, min(p1_x, p2_x) - pad)
        cdef float min_y = max(0.0, min(p1_y, p2_y) - pad)
        cdef float max_x = min(<float>max_bounds[0], max(p1_x, p2_x) + pad)
        cdef float max_y = min(<float>max_bounds[1], max(p1_y, p2_y) + pad)
        cdef float bbox_w = max_x - min_x
        cdef float bbox_h = max_y - min_y

        if bbox_w <= 0.0 or bbox_h <= 0.0:
            return

        cdef float r = color[0] / 255.0
        cdef float g = color[1] / 255.0
        cdef float b = color[2] / 255.0
        cdef float a = (color[3] / 255.0) if len(color) > 3 else 1.0

        begin_nvshader_mode(self._line_sdf_shader)
        set_nvshader_value_vec2_tuple(self._line_sdf_shader, self._line_sdf_locs["p1"], (p1_x, p1_y))
        set_nvshader_value_vec2_tuple(self._line_sdf_shader, self._line_sdf_locs["p2"], (p2_x, p2_y))
        set_nvshader_value_float(self._line_sdf_shader, self._line_sdf_locs["thickness"], width)
        set_nvshader_value_float(self._line_sdf_shader, self._line_sdf_locs["radius"], r_val)
        set_nvshader_value_vec4_tuple(self._line_sdf_shader, self._line_sdf_locs["lineColor"], (r, g, b, a))
        set_nvshader_value_vec2_tuple(self._line_sdf_shader, self._line_sdf_locs["bboxPos"], (min_x, min_y))
        set_nvshader_value_vec2_tuple(self._line_sdf_shader, self._line_sdf_locs["bboxSize"], (bbox_w, bbox_h))

        begin_blend_mode(md.rl.BlendMode.BLEND_ALPHA_PREMULTIPLY)
        c_draw_texture_pro(self._blank_texture, (0.0, 0.0, 1.0, 1.0), (min_x, min_y, bbox_w, bbox_h), (0.0, 0.0), 0.0, (255, 255, 255, 255))
        end_blend_mode()
        self._end_shader()

    # === Blit ===
    cpdef blit(self, source, tuple dest, bint flip = True, tuple color = Color.White, double angle = 0.0):
        if isinstance(color, tuple) and len(color) == 3:
            color = (*color, 255)
        self.blit_rect_pro(source, (dest[0], dest[1], source.width, source.height), flip, color, angle)

    cpdef fast_blit(self, source, tuple dest, tuple color = Color.White):
        c_draw_texture_vec(source, dest, color, True)

    cpdef fast_blit_pro(self, source, tuple dest, bint flip = True, tuple color = Color.White):
        if isinstance(color, tuple) and len(color) == 3:
            color = (*color, 255)
        h = -source.height if flip else source.height
        c_draw_texture_rec(source, (0,0, source.width, h), dest, color)

    cpdef blit_rect_pro(self, source, tuple dest, bint flip = True, tuple color = Color.White, double angle = 0.0, source_rect: Annotations.rect_like | None = None, int mode = 0):
        if source_rect: source_rec = source_rect
        elif flip: source_rec = (0, 0, source.width, -source.height)
        else: source_rec = (0, 0, source.width, source.height)
        begin_blend_mode(mode or md.rl.BlendMode.BLEND_ALPHA)
        c_draw_texture_pro(source, <tuple>source_rec, dest, (0,0), angle, color)
        end_blend_mode()

    cpdef blit_rect_vec(self, source, tuple coordinates, bint flip = True, tuple color = Color.White, source_rect: Annotations.rect_like | None = None, int mode = 0):
        if source_rect: source_rec = source_rect
        elif flip: source_rec = (0, 0, source.width, -source.height)
        else: source_rec = (0, 0, source.width, source.height)
        begin_blend_mode(mode or md.rl.BlendMode.BLEND_ALPHA)
        c_draw_texture_rec(source, source_rec, coordinates, color)
        end_blend_mode()

    cpdef blit_sdf(self, source, tuple dest, object radii, bint flip = True, int mode = 0):
        if isinstance(radii, int | float): radii = (radii, radii, radii, radii)
        self._begin_sdf(dest[2], dest[3], <tuple>radii)
        self.blit_rect_pro(source, dest, flip, mode=mode)
        self._end_shader()

    cpdef blit_sdf_vec(self, source, tuple coordinates, object radii, bint flip = True, int mode = 0):
        if isinstance(radii, int | float): radii = (radii, radii, radii, radii)
        self._begin_sdf(source.width, source.height, <tuple>radii)
        self.blit_rect_vec(source, coordinates, flip, mode=mode)
        self._end_shader()

    cpdef blit_glassy_sdf_vec(self, source, tuple coordinates, object radii, bint flip = True, int mode = 0):
        if isinstance(radii, int | float): radii = (radii, radii, radii, radii)
        self._begin_glassy_sdf(source.width, source.height, <tuple>radii)
        self.blit_rect_vec(source, coordinates, flip, mode=mode)
        self._end_shader()

    cpdef fast_blit_sdf_vec(self, source, tuple coordinates, object radii, bint flip = True, tuple color = Color.White):
        if isinstance(radii, int | float): radii = (radii, radii, radii, radii)
        self._begin_sdf(source.width, source.height, <tuple>radii)
        self.fast_blit_pro(source, coordinates, flip, color = color)
        self._end_shader()

    cpdef fast_blit_glassy_sdf_vec(self, source, tuple coordinates, object radii, bint flip = True, tuple color = Color.White):
        if isinstance(radii, int | float): radii = (radii, radii, radii, radii)
        self._begin_glassy_sdf(source.width, source.height, <tuple>radii)
        self.fast_blit_pro(source, coordinates, flip, color = color)
        self._end_shader()

    cpdef blit_borders(self, source, tuple dest_rect, tuple radii, tuple border_color, tuple color = Color.White, double thickness = 1, bint flip = True, int mode = 0):
        self._begin_borders(dest_rect[2], dest_rect[3], radii, border_color, thickness)
        self.blit_rect_pro(source, dest_rect, flip, color, mode=mode)
        self._end_shader()

    cpdef blit_borders_vec(self, source, tuple coordinates, tuple radii, tuple border_color, tuple color = Color.White, double thickness = 1, bint flip = True):
        self._begin_borders(source.width, source.height, radii, border_color, thickness)
        self.blit_rect_vec(source, coordinates, flip, color)
        self._end_shader()

    cpdef fast_blit_borders_vec(self, source, tuple coordinates, tuple radii, tuple border_color, double thickness = 1, bint flip = True):
        self._begin_borders(source.width, source.height, radii, border_color, thickness)
        self.fast_blit_pro(source, coordinates, flip)
        self._end_shader()

    cpdef fast_blit_glassy_borders_vec(self, source, tuple coordinates, tuple radii, tuple border_color, double thickness = 1, bint flip = True):
        self._begin_glassy_borders(source.width, source.height, radii, border_color, thickness)
        self.fast_blit_pro(source, coordinates, flip)
        self._end_shader()

    # === Shaders ===
    cpdef _begin_sdf(self, float width, float height, tuple radii):
        cdef list list_radii
        list_radii = list(radii)
        minside = min(width, height) / 2
        for i in range(4):
            list_radii[i] = min(radii[i], minside)
        begin_nvshader_mode(self._sdf_shader)
        set_nvshader_value_vec2_tuple(self._sdf_shader, self._sdf_locs['rectSize'], (width, height))
        set_nvshader_value_vec4_tuple(self._sdf_shader, self._sdf_locs['radius'], tuple(list_radii))

    cpdef _begin_glassy_sdf(self, float width, float height, tuple radii):
        cdef list list_radii
        list_radii = list(radii)
        minside = min(width, height) / 2.0
        for i in range(4):
            list_radii[i] = min(radii[i], minside)
        begin_nvshader_mode(self._glassy_sdf_shader)
        set_nvshader_value_vec2_tuple(self._glassy_sdf_shader, self._glassy_sdf_locs['rectSize'], (width, height))
        set_nvshader_value_vec4_tuple(self._glassy_sdf_shader, self._glassy_sdf_locs['radius'], tuple(list_radii))

    cpdef _begin_glassy_borders(self, double width, double height, tuple radii, tuple border_color, double thickness):
        begin_nvshader_mode(self._glassy_border_shader)
        cdef list list_radii
        list_radii = list(radii)
        minside = min(width, height) / 2.0
        for i in range(4):
            list_radii[i] = min(radii[i], minside)
        cdef Vector2 rec_size
        rec_size = Vector2.new(width, height)
        set_nvshader_value_vec2_nvvec(self._glassy_border_shader, self._glassy_border_locs['rectSize'], rec_size)
        set_nvshader_value_vec4_tuple(self._glassy_border_shader, self._glassy_border_locs['radius'], tuple(list_radii))
        r, g, b, a = 255, 255, 255, 255
        if hasattr(border_color, 'r'):
            r, g, b, a = border_color.r, border_color.g, border_color.b, border_color.a
        elif len(border_color) >= 3:
            r, g, b = border_color[0], border_color[1], border_color[2]
            if len(border_color) > 3: a = border_color[3]
        b_color_vec = (r/255, g/255, b/255, a/255)
        set_nvshader_value_vec4_tuple(self._glassy_border_shader, self._glassy_border_locs['borderColor'], b_color_vec)
        set_nvshader_value_float(self._glassy_border_shader, self._glassy_border_locs['thickness'], <float>thickness)

    cpdef _begin_borders(self, double width, double height, tuple radii, tuple border_color, double thickness):
        begin_nvshader_mode(self._border_shader)
        cdef list list_radii
        list_radii = list(radii)
        minside = min(width, height) / 2.0
        for i in range(4):
            list_radii[i] = min(radii[i], minside)
        cdef Vector2 rec_size
        rec_size = Vector2.new(width, height)
        set_nvshader_value_vec2_nvvec(self._border_shader, self._border_locs['rectSize'], rec_size)
        set_nvshader_value_vec4_tuple(self._border_shader, self._border_locs['radius'], tuple(list_radii))
        r, g, b, a = 255, 255, 255, 255
        if hasattr(border_color, 'r'):
            r, g, b, a = border_color.r, border_color.g, border_color.b, border_color.a
        elif len(border_color) >= 3:
            r, g, b = border_color[0], border_color[1], border_color[2]
            if len(border_color) > 3: a = border_color[3]
        b_color_vec = (r/255, g/255, b/255, a/255)
        set_nvshader_value_vec4_tuple(self._border_shader, self._border_locs['borderColor'], b_color_vec)
        set_nvshader_value_float(self._border_shader, self._border_locs['thickness'], <float>thickness)

    cdef inline void _end_shader(self) noexcept: end_shader_mode()

    # === Sizes ===
    cpdef tuple get_tuple_rect(self): return (0, 0, self.c_get_width(), self.c_get_height())
    cpdef Rect get_rect(self): return Rect.new(0, 0, self.c_get_width(), self.c_get_height())

    cdef inline tuple c_get_tuple_size(self) noexcept: return (md.rl.get_screen_width(), md.rl.get_screen_height())
    cdef inline Vector2 c_get_nvvec_size(self): return Vector2.cfrom_ints(md.rl.get_screen_width(), md.rl.get_screen_height())
    cdef inline int c_get_width(self) noexcept: return md.rl.get_screen_width()
    cdef inline int c_get_height(self) noexcept: return md.rl.get_screen_height()

    cpdef tuple get_size_tuple(self): return self.c_get_tuple_size()
    cpdef Vector2 get_size_nvvec(self): return self.c_get_nvvec_size()

    cpdef int get_width(self): return md.rl.get_screen_width()
    cpdef int get_height(self): return md.rl.get_screen_height()

    # === Misc ===
    @property
    def screen(self): return None
    cpdef void set_title(self, str title): md.rl.set_window_title(title)
    cpdef void clear(self, color = fill_color): md.rl.clear_background(color)
    cpdef void begin_frame(self): begin_drawing()
    cpdef void end_frame(self): end_drawing()
    cpdef load_image(self, str path): return md.rl.load_texture(path)

cdef class WindowRendererPygame:
    cdef public object window, root

    @staticmethod
    def create_initialized(window, screen):
        cdef WindowRendererPygame self = WindowRendererPygame.__new__(WindowRendererPygame)
        check_singleton()
        self.window = screen
        self._init_base(window)
        return self

    def __init__(self, title, size, root, flags = 0, **kwargs):
        check_singleton()
        self._init_window(title, size, flags)
        self._init_base(root)

    cdef inline void _init_base(self, object root): self.root = root
    cdef inline void _init_window(self, title, size, flags):
        self.window = md.pygame.display.set_mode(size, flags)
        md.pygame.display.set_caption(title)

    # === Sizes ===
    cpdef tuple get_tuple_rect(self): return (0, 0, self.c_get_width(), self.c_get_height())
    cpdef Rect get_rect(self): return Rect.new(0, 0, self.c_get_width(), self.c_get_height())

    cdef inline tuple c_get_tuple_size(self) noexcept: return self.window.size
    cdef inline Vector2 c_get_nvvec_size(self): return Vector2.cfrom_ints(self.window.width, self.window.height)
    cdef inline int c_get_width(self) noexcept: return self.window.width
    cdef inline int c_get_height(self) noexcept: return self.window.height

    cpdef int get_width(self): return self.c_get_width()
    cpdef int get_height(self): return self.c_get_height()
    cpdef Vector2 get_size_nvvec(self): return self.c_get_nvvec_size()
    cpdef tuple get_size_tuple(self): return self.c_get_tuple_size()

    # === Misc ===
    @property
    def screen(self): return self.window
    cpdef void end_frame(self): md.pygame.display.update()
    cpdef void begin_frame(self): pass
    cpdef void clear(self, color = fill_color): self.window.fill(color)
    cpdef void flip(self): md.pygame.display.flip()
    cpdef void blit(self, source, dest): self.window.blit(source, dest)
    cpdef load_image(self, path: str): return md.pygame.image.load(path)
    cpdef set_title(self, title: str): md.pygame.display.set_caption(title)
