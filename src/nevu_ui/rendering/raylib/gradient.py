import pyray as rl

from nevu_ui.fast import GradientShader
from nevu_ui.rendering.pygame.gradient import GradientPygame

from nevu_ui.core import (
    LinearSide, RadialPosition, GradientType, GradientConfig
)

import pyray as rl

from nevu_ui.rendering.pygame.gradient import GradientPygame
from nevu_ui.core import GradientType
class GradientRaylib(GradientPygame):
    _shader = None
    _locs = {}
    _blank_texture = None 

    def __init__(self, colors, type: GradientType = GradientType.Linear, direction=None, angle=None, center=None, transparency=None):
        self.raw_colors = colors
        self.type = type
        self.transparency = transparency if transparency is not None else 255
        
        self.angle = 0.0
        self.center = (0.5, 0.5)

        if direction is not None:
            if type == GradientType.Linear:
                if hasattr(direction, 'name'):
                    mapping = {
                        "Right": 0.0, "Left": 180.0,
                        "Bottom": 90.0, "Top": 270.0,
                        "BottomRight": 45.0, "TopLeft": 225.0,
                        "TopRight": 315.0, "BottomLeft": 135.0
                    }
                    self.angle = mapping.get(direction.name, 0.0)
                elif isinstance(direction, (int, float)):
                    self.angle = float(direction)
            elif type == GradientType.Radial:
                if hasattr(direction, 'name'):
                    mapping = {
                        "Center": (0.5, 0.5),
                        "TopCenter": (0.5, 0.0), "TopLeft": (0.0, 0.0), "TopRight": (1.0, 0.0),
                        "BottomCenter": (0.5, 1.0), "BottomLeft": (0.0, 1.0), "BottomRight": (1.0, 1.0)
                    }
                    self.center = mapping.get(direction.name, (0.5, 0.5))
                elif isinstance(direction, tuple):
                    self.center = direction

        if angle is not None:
            self.angle = float(angle)
        if center is not None:
            self.center = tuple(center)

        self.colors = []
        weights =[]
        
        for item in colors:
            if isinstance(item, tuple) and len(item) == 2 and isinstance(item[1], (int, float)):
                self.colors.append(item[0])
                weights.append(float(item[1]))
            else:
                self.colors.append(item)
                weights.append(1.0)
                
        total_weight = sum(weights)
        if total_weight <= 0:
            total_weight = 1.0
            
        boundaries = [0.0]
        current = 0.0
        for w in weights:
            current += w / total_weight
            boundaries.append(current)
            
        self.stops =[]
        n = len(weights)
        for i in range(n):
            if n == 1:
                self.stops.append(0.0)
            elif i == 0:
                rb = boundaries[1]
                self.stops.append(max(0.0, rb - min(rb, 1.0 - rb)))
            elif i == n - 1:
                lb = boundaries[i]
                self.stops.append(min(1.0, lb + min(lb, 1.0 - lb)))
            else:
                self.stops.append((boundaries[i] + boundaries[i+1]) / 2.0)
            
        self._ensure_resources()

    @staticmethod
    def from_pygame(pygame_gradient):
        direction = getattr(pygame_gradient, 'direction', None)
        angle = getattr(pygame_gradient, 'angle', None)
        center = getattr(pygame_gradient, 'center', None)
        raw_cols = getattr(pygame_gradient, 'raw_colors', pygame_gradient.colors)
        return GradientRaylib(raw_cols, pygame_gradient.type, direction=direction, angle=angle, center=center, transparency=pygame_gradient.transparency)
    
    @classmethod
    def _ensure_resources(cls):
        if cls._shader is None:
            cls._shader = rl.load_shader_from_memory(GradientShader.VERTEX_SHADER, GradientShader.FRAGMENT_SHADER)
            
            if cls._shader.id == 0:
                print("ERROR: Shader failed to compile!")
            
            cls._locs = {
                'gradientType': rl.get_shader_location(cls._shader, "gradientType"),
                'angle': rl.get_shader_location(cls._shader, "angle"),
                'centerPos': rl.get_shader_location(cls._shader, "centerPos"),
                'colors': rl.get_shader_location(cls._shader, "colors"),
                'stops': rl.get_shader_location(cls._shader, "stops"),
                'colorCount': rl.get_shader_location(cls._shader, "colorCount"),
                'alpha': rl.get_shader_location(cls._shader, "alpha"),
                'size': rl.get_shader_location(cls._shader, "size"),
            }

        if cls._blank_texture is None:
            img = rl.gen_image_color(1, 1, rl.WHITE)
            cls._blank_texture = rl.load_texture_from_image(img)
            rl.unload_image(img)

    def generate_texture(self, width: int, height: int) -> rl.Texture:
        colors_flat =[]
        for c in self.colors:
            colors_flat.extend([c[0]/255.0, c[1]/255.0, c[2]/255.0, c[3]/255.0 if len(c) == 4 else 1.0])
        
        gradient_type_int = 0 if self.type == GradientType.Linear else 1
        alpha_val = (self.transparency / 255.0) if self.transparency is not None else 1.0
        
        grad_type_ptr = rl.ffi.new("int *", gradient_type_int)
        angle_ptr = rl.ffi.new("float *", float(self.angle))
        center_ptr = rl.ffi.new("float[]", [float(self.center[0]), float(self.center[1])])
        count_ptr = rl.ffi.new("int *", len(self.colors))
        alpha_ptr = rl.ffi.new("float *", float(alpha_val))
        colors_ptr = rl.ffi.new("float[]", colors_flat)
        stops_ptr = rl.ffi.new("float[]", self.stops)
        size_ptr = rl.ffi.new("float[]",[float(width), float(height)])

        assert self._shader and self._blank_texture
        
        rl.set_shader_value(self._shader, self._locs['gradientType'], grad_type_ptr, rl.ShaderUniformDataType.SHADER_UNIFORM_INT)
        rl.set_shader_value(self._shader, self._locs['angle'], angle_ptr, rl.ShaderUniformDataType.SHADER_UNIFORM_FLOAT)
        rl.set_shader_value(self._shader, self._locs['centerPos'], center_ptr, rl.ShaderUniformDataType.SHADER_UNIFORM_VEC2)
        rl.set_shader_value(self._shader, self._locs['colorCount'], count_ptr, rl.ShaderUniformDataType.SHADER_UNIFORM_INT)
        rl.set_shader_value(self._shader, self._locs['alpha'], alpha_ptr, rl.ShaderUniformDataType.SHADER_UNIFORM_FLOAT)
        rl.set_shader_value_v(self._shader, self._locs['colors'], colors_ptr, rl.ShaderUniformDataType.SHADER_UNIFORM_VEC4, len(self.colors))
        rl.set_shader_value_v(self._shader, self._locs['stops'], stops_ptr, rl.ShaderUniformDataType.SHADER_UNIFORM_FLOAT, len(self.stops))
        rl.set_shader_value(self._shader, self._locs['size'], size_ptr, rl.ShaderUniformDataType.SHADER_UNIFORM_VEC2)

        target = rl.load_render_texture(width, height)
        
        rl.begin_texture_mode(target)
        rl.clear_background(rl.BLANK)
        rl.begin_shader_mode(self._shader)
        
        source_rec = rl.Rectangle(0, 0, 1, 1)
        dest_rec = rl.Rectangle(0, 0, width, height)
        rl.draw_texture_pro(self._blank_texture, source_rec, dest_rec, (0,0), 0.0, rl.WHITE)
        
        rl.end_shader_mode()
        rl.end_texture_mode()

        image = rl.load_image_from_texture(target.texture)
        final_texture = rl.load_texture_from_image(image)
        
        rl.unload_image(image)          
        rl.unload_render_texture(target)
        return final_texture

class ClickGradient(GradientRaylib):
    def __init__(self, colors, type: GradientType = GradientType.Radial, direction=None, angle=None, center=None, transparency=None):
        super().__init__(colors, type, direction, angle, center, transparency)
        self.weights =[]
        for item in colors:
            if isinstance(item, tuple) and len(item) == 2 and isinstance(item[1], (int, float)):
                self.weights.append(float(item[1]))
            else:
                self.weights.append(1.0)

    def set_weight(self, index: int, weight: float):
        if 0 <= index < len(self.weights):
            self.weights[index] = float(weight)
            self._recalculate_stops()
        else:
            raise IndexError(f"Color index out of range! Max: {len(self.weights)-1}")

    def set_center(self, center: tuple):
        self.center = tuple(center)

    def _recalculate_stops(self):
        total_weight = sum(self.weights)
        if total_weight <= 0:
            total_weight = 1.0
            
        boundaries = [0.0]
        current = 0.0
        for w in self.weights:
            current += w / total_weight
            boundaries.append(current)
            
        self.stops =[]
        n = len(self.weights)
        for i in range(n):
            if n == 1:
                self.stops.append(0.0)
            elif i == 0:
                rb = boundaries[1]
                self.stops.append(max(0.0, rb - min(rb, 1.0 - rb)))
            elif i == n - 1:
                lb = boundaries[i]
                self.stops.append(min(1.0, lb + min(lb, 1.0 - lb)))
            else:
                self.stops.append((boundaries[i] + boundaries[i+1]) / 2.0)

    def draw(self, x: float, y: float, width: float, height: float):
        self._ensure_resources()
        
        colors_flat =[]
        for c in self.colors:
            colors_flat.extend([c[0]/255.0, c[1]/255.0, c[2]/255.0, c[3]/255.0 if len(c) == 4 else 1.0])
        
        gradient_type_int = 0 if self.type == GradientType.Linear else 1
        alpha_val = (self.transparency / 255.0) if self.transparency is not None else 1.0
        
        grad_type_ptr = rl.ffi.new("int *", gradient_type_int)
        angle_ptr = rl.ffi.new("float *", float(self.angle))
        center_ptr = rl.ffi.new("float[]",[float(self.center[0]), float(self.center[1])])
        count_ptr = rl.ffi.new("int *", len(self.colors))
        alpha_ptr = rl.ffi.new("float *", float(alpha_val))
        colors_ptr = rl.ffi.new("float[]", colors_flat)
        stops_ptr = rl.ffi.new("float[]", self.stops)
        size_ptr = rl.ffi.new("float[]", [float(width), float(height)])

        assert self._shader and self._blank_texture
        
        rl.set_shader_value(self._shader, self._locs['gradientType'], grad_type_ptr, rl.ShaderUniformDataType.SHADER_UNIFORM_INT)
        rl.set_shader_value(self._shader, self._locs['angle'], angle_ptr, rl.ShaderUniformDataType.SHADER_UNIFORM_FLOAT)
        rl.set_shader_value(self._shader, self._locs['centerPos'], center_ptr, rl.ShaderUniformDataType.SHADER_UNIFORM_VEC2)
        rl.set_shader_value(self._shader, self._locs['colorCount'], count_ptr, rl.ShaderUniformDataType.SHADER_UNIFORM_INT)
        rl.set_shader_value(self._shader, self._locs['alpha'], alpha_ptr, rl.ShaderUniformDataType.SHADER_UNIFORM_FLOAT)
        rl.set_shader_value_v(self._shader, self._locs['colors'], colors_ptr, rl.ShaderUniformDataType.SHADER_UNIFORM_VEC4, len(self.colors))
        rl.set_shader_value_v(self._shader, self._locs['stops'], stops_ptr, rl.ShaderUniformDataType.SHADER_UNIFORM_FLOAT, len(self.stops))
        rl.set_shader_value(self._shader, self._locs['size'], size_ptr, rl.ShaderUniformDataType.SHADER_UNIFORM_VEC2)
        
        rl.begin_shader_mode(self._shader)
        
        source_rec = (0, 0, 1, 1)
        dest_rec = (x, y, width, height)
        rl.draw_texture_pro(self._blank_texture, source_rec, dest_rec, (0, 0), 0.0, rl.WHITE)
        
        rl.end_shader_mode()