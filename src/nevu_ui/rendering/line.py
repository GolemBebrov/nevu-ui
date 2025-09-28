import numpy as np
import pygame

from nevu_ui.utils import Convertor

from .dist_to_segment import _dist_to_segment_sq

def _create_line_AA(p1, p2, thickness, color, _factor=4):
    half_thick = thickness / 2.0
    
    min_x = int(min(p1.x, p2.x) - half_thick)
    max_x = int(np.ceil(max(p1.x, p2.x) + half_thick))
    min_y = int(min(p1.y, p2.y) - half_thick)
    max_y = int(np.ceil(max(p1.y, p2.y) + half_thick))
    
    width, height = max_x - min_x, max_y - min_y
    if width <= 0 or height <= 0: return pygame.Surface((max(1, width), max(1, height)), pygame.SRCALPHA)
    
    offset = pygame.Vector2(min_x, min_y)
    cp1, cp2 = p1 - offset, p2 - offset

    supersample_factor = _factor
    sw, sh = width * supersample_factor, height * supersample_factor
    s_x = (np.arange(sw) + 0.5) / supersample_factor
    s_y = (np.arange(sh) + 0.5) / supersample_factor
    s_xx, s_yy = np.meshgrid(s_x, s_y)
    
    dist_sq = _dist_to_segment_sq(s_xx, s_yy, cp1.x, cp1.y, cp2.x, cp2.y)
    alpha_mask_ss = np.where(dist_sq < half_thick**2, 1.0, 0.0)
    
    alpha = alpha_mask_ss.reshape(height, supersample_factor, width, supersample_factor).mean(axis=(1, 3))
    
    surf = pygame.Surface((width, height), pygame.SRCALPHA)
    rgb_data = np.full((width, height, 3), color[:3], dtype=np.uint8)
    alpha_data = (alpha * (color[3] if len(color) > 3 else 255)).astype(np.uint8)
    
    pygame.surfarray.pixels3d(surf)[:] = rgb_data
    pygame.surfarray.pixels_alpha(surf)[:] = np.transpose(alpha_data, (1, 0))

    return surf

def _create_line_sdf(p1, p2, thickness, color):
    half_thick = thickness / 2.0
    
    min_x = int(min(p1.x, p2.x) - half_thick - 2)
    max_x = int(np.ceil(max(p1.x, p2.x) + half_thick + 2))
    min_y = int(min(p1.y, p2.y) - half_thick - 2)
    max_y = int(np.ceil(max(p1.y, p2.y) + half_thick + 2))
    
    width, height = max_x - min_x, max_y - min_y
    if width <= 0 or height <= 0: return pygame.Surface((max(1, width), max(1, height)), pygame.SRCALPHA)

    offset = pygame.Vector2(min_x, min_y)
    cp1, cp2 = p1 - offset, p2 - offset

    x = np.arange(width)
    y = np.arange(height)
    xx, yy = np.meshgrid(x, y)
    
    dist_sq = _dist_to_segment_sq(xx + 0.5, yy + 0.5, cp1.x, cp1.y, cp2.x, cp2.y)
    dist = np.sqrt(dist_sq)
    
    signed_dist = dist - half_thick
    
    alpha = np.clip(0.5 - signed_dist, 0, 1)
    
    surf = pygame.Surface((width, height), pygame.SRCALPHA)
    rgb_data = np.full((width, height, 3), color[:3], dtype=np.uint8)
    alpha_data = (alpha * (color[3] if len(color) > 3 else 255)).astype(np.uint8)
    
    pygame.surfarray.pixels3d(surf)[:] = rgb_data
    pygame.surfarray.pixels_alpha(surf)[:] = np.transpose(alpha_data, (1, 0))

    return surf

class Line:
    _convertor = Convertor
    @classmethod
    def create_AA(cls, p1, p2, thickness, color, AA_factor = 4):
        p1 = cls._convertor.convert(p1, pygame.Vector2)
        p2 = cls._convertor.convert(p2, pygame.Vector2)
        thickness = cls._convertor.convert(thickness, float)
        color = cls._convertor.convert(color, tuple)
        AA_factor = cls._convertor.convert(AA_factor, int)
        return _create_line_AA(p1, p2, thickness, color, AA_factor) # type: ignore

    @classmethod
    def create_sdf(cls, p1, p2, thickness, color):
        p1 = cls._convertor.convert(p1, pygame.Vector2)
        p2 = cls._convertor.convert(p2, pygame.Vector2)
        thickness = cls._convertor.convert(thickness, float)
        color = cls._convertor.convert(color, tuple)
        return _create_line_sdf(p1, p2, thickness, color)

