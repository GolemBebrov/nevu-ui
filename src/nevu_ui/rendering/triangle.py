import numpy as np
import pygame

from nevu_ui.utils import Convertor

from .dist_to_segment import _dist_to_segment_sq

def _create_triangle_AA(p1, p2, p3, color, _factor=4):
    supersample_factor = _factor

    min_x = int(min(p1.x, p2.x, p3.x))
    max_x = int(max(p1.x, p2.x, p3.x))
    min_y = int(min(p1.y, p2.y, p3.y))
    max_y = int(max(p1.y, p2.y, p3.y))
    
    width, height = max_x - min_x, max_y - min_y
    if width == 0 or height == 0: return pygame.Surface((width, height), pygame.SRCALPHA)

    cp1 = p1 - pygame.Vector2(min_x, min_y)
    cp2 = p2 - pygame.Vector2(min_x, min_y)
    cp3 = p3 - pygame.Vector2(min_x, min_y)

    sw, sh = width * supersample_factor, height * supersample_factor
    s_x = np.arange(sw)
    s_y = np.arange(sh)
    s_xx, s_yy = np.meshgrid(s_x, s_y)
    
    s_px = s_xx / supersample_factor
    s_py = s_yy / supersample_factor

    detT = (cp2.y - cp3.y) * (cp1.x - cp3.x) + (cp3.x - cp2.x) * (cp1.y - cp3.y)
    w1 = ((cp2.y - cp3.y) * (s_px - cp3.x) + (cp3.x - cp2.x) * (s_py - cp3.y)) / detT
    w2 = ((cp3.y - cp1.y) * (s_px - cp3.x) + (cp1.x - cp3.x) * (s_py - cp3.y)) / detT
    w3 = 1.0 - w1 - w2

    alpha_mask_ss = (w1 >= 0) & (w2 >= 0) & (w3 >= 0)
    
    alpha = alpha_mask_ss.reshape(height, supersample_factor, width, supersample_factor).mean(axis=(1, 3))
    
    surf = pygame.Surface((width, height), pygame.SRCALPHA)
    rgb_data = np.full((width, height, 3), color[:3], dtype=np.uint8)
    alpha_data = (alpha * (color[3] if len(color) > 3 else 255)).astype(np.uint8)
    
    pygame.surfarray.pixels3d(surf)[:] = rgb_data
    pygame.surfarray.pixels_alpha(surf)[:] = np.transpose(alpha_data, (1, 0))

    return surf

def _create_triangle_sdf(p1, p2, p3, color):
    min_x = int(min(p1.x, p2.x, p3.x)) - 2 
    max_x = int(np.ceil(max(p1.x, p2.x, p3.x))) + 2
    min_y = int(min(p1.y, p2.y, p3.y)) - 2
    max_y = int(np.ceil(max(p1.y, p2.y, p3.y))) + 2
    
    width, height = max_x - min_x, max_y - min_y
    if width <= 0 or height <= 0: return pygame.Surface((1, 1), pygame.SRCALPHA)
    
    offset = pygame.Vector2(min_x, min_y)
    cp1, cp2, cp3 = p1 - offset, p2 - offset, p3 - offset
    
    x = np.arange(width)
    y = np.arange(height)
    xx, yy = np.meshgrid(x, y)
    
    d1_sq = _dist_to_segment_sq(xx, yy, cp1.x, cp1.y, cp2.x, cp2.y)
    d2_sq = _dist_to_segment_sq(xx, yy, cp2.x, cp2.y, cp3.x, cp3.y)
    d3_sq = _dist_to_segment_sq(xx, yy, cp3.x, cp3.y, cp1.x, cp1.y)
    
    dist = np.sqrt(np.minimum(d1_sq, np.minimum(d2_sq, d3_sq)))

    s1 = (cp2.y - cp1.y) * (xx - cp1.x) - (cp2.x - cp1.x) * (yy - cp1.y)
    s2 = (cp3.y - cp2.y) * (xx - cp2.x) - (cp3.x - cp2.x) * (yy - cp2.y)
    s3 = (cp1.y - cp3.y) * (xx - cp3.x) - (cp1.x - cp3.x) * (yy - cp3.y)
    
    is_inside = (np.sign(s1) == np.sign(s2)) & (np.sign(s2) == np.sign(s3))
    
    sign = np.where(is_inside, -1.0, 1.0)

    signed_dist = dist * sign
    
    alpha = np.clip(0.5 - signed_dist, 0, 1)
    
    surf = pygame.Surface((width, height), pygame.SRCALPHA)
    rgb_data = np.full((width, height, 3), color[:3], dtype=np.uint8)
    alpha_data = (alpha * (color[3] if len(color) > 3 else 255)).astype(np.uint8)
    
    pygame.surfarray.pixels3d(surf)[:] = rgb_data
    pygame.surfarray.pixels_alpha(surf)[:] = np.transpose(alpha_data, (1, 0))
    
    return surf

class Triangle:
    _convertor = Convertor
    @classmethod
    def create_AA(cls, p1, p2, p3, color, AA_factor = 4):
        p1 = cls._convertor.convert(p1, pygame.Vector2)
        p2 = cls._convertor.convert(p2, pygame.Vector2)
        p3 = cls._convertor.convert(p3, pygame.Vector2)
        color = cls._convertor.convert(color, tuple)
        AA_factor = cls._convertor.convert(AA_factor, int)
        return _create_triangle_AA(p1, p2, p3, color, AA_factor) # type: ignore

    @classmethod
    def create_sdf(cls, p1, p2, p3, color):
        p1 = cls._convertor.convert(p1, pygame.Vector2)
        p2 = cls._convertor.convert(p2, pygame.Vector2)
        p3 = cls._convertor.convert(p3, pygame.Vector2)
        color = cls._convertor.convert(color, tuple)
        return _create_triangle_sdf(p1, p2, p3, color)

