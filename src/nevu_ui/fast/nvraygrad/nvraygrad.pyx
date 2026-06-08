# distutils: language = c++

from nevu_ui.fast.nvrendertex.nv_render_tex cimport NvRenderTexture
from nevu_ui.fast.nvvector2.nvvector2 cimport NvVector2
from nevu_ui.fast.nvshader.nvshader cimport NvShader
import nevu_ui.core.modules as md
from nevu_ui.fast import GradientShader
from nevu_ui.rendering.pygame.gradient import GradientPygame
from nevu_ui.core import GradientType
from libcpp.vector cimport vector
from nevu_ui.fast.raylib.nevu_raylib cimport (
    begin_blend_mode, end_blend_mode, begin_texture_mode, end_texture_mode, begin_nvshader_mode, end_shader_mode, draw_texture_pro,
    set_nvshader_value_float, get_nvshader_location, set_nvshader_value_vec4_v, set_nvshader_value_float_v, set_nvshader_value_int, 
    set_nvshader_value_vec2_nvvec, Vector4, set_nvshader_value_vec2_tuple
    )
from libcpp.numeric cimport accumulate

cdef inline Vector4 tuple_to_vector4(tuple t):
    cdef Vector4 v
    v.x = t[0] / 255
    v.y = t[1] / 255
    v.z = t[2] / 255
    v.w = t[3] / 255
    return v
cdef NvShader _SHARED_SHADER = None
cdef object _SHARED_BLANK_TEXTURE = None
cdef int _LOC_TYPE = -1
cdef int _LOC_ANGLE = -1
cdef int _LOC_CENTER = -1
cdef int _LOC_COLORS = -1
cdef int _LOC_STOPS = -1
cdef int _LOC_COUNT = -1
cdef int _LOC_ALPHA = -1
cdef int _LOC_SIZE = -1

cdef class GradientRaylib:
    cdef public list raw_colors
    cdef int _transparency
    cdef float _angle
    cdef NvVector2 _center
    cdef public object type
    cdef vector[Vector4] _colors
    cdef vector[float] _stops

    def __init__(self, list colors, type = GradientType.Linear, direction = None, angle = None, center = None, transparency = None):
        self.raw_colors = colors
        self.type = type
        self._transparency = transparency if transparency is not None else 255
        
        self._angle = 0.0
        self._center = NvVector2.new(0.5, 0.5)

        if direction is not None:
            if type == GradientType.Linear:
                if hasattr(direction, 'name'):
                    mapping = {
                        "Right": 0.0, "Left": 180.0,
                        "Bottom": 90.0, "Top": 270.0,
                        "BottomRight": 45.0, "TopLeft": 225.0,
                        "TopRight": 315.0, "BottomLeft": 135.0
                    }
                    self._angle = mapping.get(direction.name, 0.0)
                elif isinstance(direction, (int, float)):
                    self._angle = float(direction)
            elif type == GradientType.Radial:
                if hasattr(direction, 'name'):
                    mapping = {
                        "Center": (0.5, 0.5),
                        "TopCenter": (0.5, 0.0), "TopLeft": (0.0, 0.0), "TopRight": (1.0, 0.0),
                        "BottomCenter": (0.5, 1.0), "BottomLeft": (0.0, 1.0), "BottomRight": (1.0, 1.0)
                    }
                    center_coords = mapping.get(direction.name, (0.5, 0.5))
                    self._center = NvVector2.new(center_coords[0], center_coords[1])
                elif isinstance(direction, tuple):
                    self._center = NvVector2.new(direction[0], direction[1])

        if angle is not None:
            self._angle = <float>angle
        if center is not None:
            self._center = NvVector2.new(center[0], center[1])
        
        self._update_colors(colors)
        self._ensure_resources()

    cdef void _update_colors(self, list colors):
        self._colors.clear()
        cdef vector[float] weights
        weights.clear()
        
        self._colors.reserve(len(colors))
        weights.reserve(len(colors))
        for item in colors:
            if isinstance(item, tuple) and len(item) == 2 and isinstance(item[1], (int, float)):
                self._colors.push_back(tuple_to_vector4(item[0]))
                weights.push_back(float(item[1]))
            else:
                self._colors.push_back(tuple_to_vector4(item))
                weights.push_back(1.0)
        total_weight = accumulate(weights.begin(), weights.end(), 0.0)
        if total_weight <= 0:
            total_weight = 1.0
        
        cdef vector[float] boundaries = <vector[float]>[0.0]
        cdef float current = 0.0
        for w in weights:
            current += w / total_weight
            boundaries.push_back(current)
        
        self._stops = <vector[float]>[]
        n = weights.size()
        for i in range(n):
            if n == 1:
                self._stops.push_back(0.0)
            elif i == 0:
                rb = boundaries[1]
                self._stops.push_back(max(0.0, rb - min(rb, 1.0 - rb)))
            elif i == n - 1:
                lb = boundaries[i]
                self._stops.push_back(min(1.0, lb + min(lb, 1.0 - lb)))
            else:
                self._stops.push_back((boundaries[i] + boundaries[i+1]) / 2.0)

    @property
    def transparency(self):
        return self._transparency

    @transparency.setter
    def transparency(self, int value):
        self._transparency = value

    @property
    def angle(self):
        return self._angle

    @angle.setter
    def angle(self, float value):
        self._angle = value

    @property
    def center(self):
        return self._center

    @center.setter
    def center(self, value):
        if isinstance(value, NvVector2):
            self._center = value
        elif isinstance(value, tuple) and len(value) == 2:
            self._center = NvVector2.new(value[0], value[1])
        else:
            raise TypeError("center must be an NvVector2 instance or a tuple of (x, y)")

    @property
    def colors(self):
        return self.raw_colors

    @colors.setter
    def colors(self, list value):
        self.raw_colors = value
        self._update_colors(value)

    @classmethod
    def _ensure_resources(cls):
        global _SHARED_SHADER
        global _SHARED_BLANK_TEXTURE
        global _LOC_TYPE, _LOC_ANGLE, _LOC_CENTER, _LOC_COLORS, _LOC_STOPS, _LOC_COUNT, _LOC_ALPHA, _LOC_SIZE
        if _SHARED_SHADER == None:
            _SHARED_SHADER = NvShader.c_create_from_code(GradientShader.VERTEX_SHADER, GradientShader.FRAGMENT_SHADER)
            
            _LOC_TYPE = get_nvshader_location(_SHARED_SHADER, "gradientType")
            _LOC_ANGLE = get_nvshader_location(_SHARED_SHADER, "angle")
            _LOC_CENTER = get_nvshader_location(_SHARED_SHADER, "centerPos")
            _LOC_COLORS = get_nvshader_location(_SHARED_SHADER, "colors")
            _LOC_STOPS = get_nvshader_location(_SHARED_SHADER, "stops")
            _LOC_COUNT = get_nvshader_location(_SHARED_SHADER, "colorCount")
            _LOC_ALPHA = get_nvshader_location(_SHARED_SHADER, "alpha")
            _LOC_SIZE = get_nvshader_location(_SHARED_SHADER, "size")

        if _SHARED_BLANK_TEXTURE == None:
            img = md.rl.gen_image_color(1, 1, md.rl.WHITE)
            _SHARED_BLANK_TEXTURE = md.rl.load_texture_from_image(img)
            md.rl.unload_image(img)

    def generate_texture(self, int width, int height):
        gradient_type_int = 0 if self.type == GradientType.Linear else 1
        alpha_val = (self._transparency / 255.0)

        cdef NvVector2 size = NvVector2.new(width, height)
        set_nvshader_value_int(_SHARED_SHADER, _LOC_TYPE, gradient_type_int)
        set_nvshader_value_float(_SHARED_SHADER, _LOC_ANGLE, self._angle)
        set_nvshader_value_vec2_nvvec(_SHARED_SHADER, _LOC_CENTER, self._center)
        set_nvshader_value_int(_SHARED_SHADER, _LOC_COUNT, <int>self._colors.size())
        set_nvshader_value_float(_SHARED_SHADER, _LOC_ALPHA, 1.0)
        set_nvshader_value_vec4_v(_SHARED_SHADER, _LOC_COLORS, self._colors)
        set_nvshader_value_float_v(_SHARED_SHADER, _LOC_STOPS, self._stops)
        set_nvshader_value_vec2_nvvec(_SHARED_SHADER, _LOC_SIZE, size)

        cdef NvRenderTexture target = NvRenderTexture.new(size)
        
        begin_texture_mode(target.render_texture)
        begin_blend_mode(md.rl.BlendMode.BLEND_ALPHA_PREMULTIPLY)
        begin_nvshader_mode(_SHARED_SHADER)
        target.c_fast_clear((0, 0, 0, 0))
        
        source_rec = (0, 0, 1, 1)
        dest_rec = (0, 0, width, height)
        draw_texture_pro(_SHARED_BLANK_TEXTURE, source_rec, dest_rec, (0, 0), 0.0, (255, 255, 255, 255))
        
        end_shader_mode()
        end_blend_mode()
        end_texture_mode()
        return target

cdef class ClickGradient(GradientRaylib):
    cdef public vector[float] weights

    def __init__(self, list colors, type = GradientType.Radial, direction = None, angle = None, center = None, transparency = None):
        super().__init__(colors, type, direction, angle, center, transparency)

    cdef void _update_colors(self, list colors):
        self.weights.clear()
        self.weights.reserve(len(colors))
        for item in colors:
            if isinstance(item, tuple) and len(item) == 2 and isinstance(item[1], (int, float)):
                self.weights.push_back(float(item[1]))
            else:
                self.weights.push_back(1.0)
        
        self._colors.clear()
        self._colors.reserve(len(colors))
        for item in colors:
            if isinstance(item, tuple) and len(item) == 2 and isinstance(item[1], (int, float)):
                self._colors.push_back(tuple_to_vector4(item[0]))
            else:
                self._colors.push_back(tuple_to_vector4(item))

        self._recalculate_stops()

    def set_weight(self, int index, float weight):
        if 0 <= index < <int>self.weights.size():
            self.weights[index] = weight
            self._recalculate_stops()
        else:
            raise IndexError(f"Color index out of range! Max: {self.weights.size() - 1}")

    def set_center(self, tuple center):
        self._center = NvVector2.new(center[0], center[1])

    def set_center_nvvec(self, NvVector2 center):
        self._center = NvVector2.new(center.x, center.y)

    def _recalculate_stops(self):
        total_weight = accumulate(self.weights.begin(), self.weights.end(), 0.0)
        if total_weight <= 0:
            total_weight = 1.0
            
        cdef vector[float] boundaries
        boundaries.clear()
        boundaries.push_back(0.0)
        cdef float current = 0.0
        for i in range(self.weights.size()):
            w = self.weights[i]
            current += w / total_weight
            boundaries.push_back(current)
            
        self._stops.clear()
        cdef size_t n = self.weights.size()
        for i in range(n):
            if n == 1:
                self._stops.push_back(0.0)
            elif i == 0:
                rb = boundaries[1]
                self._stops.push_back(max(0.0, rb - min(rb, 1.0 - rb)))
            elif i == n - 1:
                lb = boundaries[i]
                self._stops.push_back(min(1.0, lb + min(lb, 1.0 - lb)))
            else:
                self._stops.push_back((boundaries[i] + boundaries[i+1]) / 2.0)

    def draw(self, float x, float y, float width, float height):
        self._ensure_resources()
    
        gradient_type_int = 0 if self.type == GradientType.Linear else 1
        alpha_val = (self._transparency / 255.0)
        
        cdef NvVector2 size = NvVector2.new(width, height)
        
        set_nvshader_value_int(_SHARED_SHADER, _LOC_TYPE, gradient_type_int)
        set_nvshader_value_float(_SHARED_SHADER, _LOC_ANGLE, self._angle)
        set_nvshader_value_vec2_tuple(_SHARED_SHADER, _LOC_CENTER, (self._center.x, self._center.y))
        set_nvshader_value_int(_SHARED_SHADER, _LOC_COUNT, <int>self._colors.size())
        set_nvshader_value_float(_SHARED_SHADER, _LOC_ALPHA, alpha_val)
        set_nvshader_value_vec4_v(_SHARED_SHADER, _LOC_COLORS, self._colors)
        set_nvshader_value_float_v(_SHARED_SHADER, _LOC_STOPS, self._stops)
        set_nvshader_value_vec2_nvvec(_SHARED_SHADER, _LOC_SIZE, size)
        
        begin_nvshader_mode(_SHARED_SHADER)
        
        source_rec = (0, 0, 1, 1)
        dest_rec = (x, y, width, height)
        draw_texture_pro(_SHARED_BLANK_TEXTURE, source_rec, dest_rec, (0, 0), 0.0, md.rl.WHITE)
        
        end_shader_mode()