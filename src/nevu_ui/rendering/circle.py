import numpy as np
import pygame

from nevu_ui.utils import Convertor

def _create_circle_AA(radius, color, _factor = 4):
    supersample_factor = _factor
    size = radius * 2
    ss_size = size * supersample_factor
    ss_radius = radius * supersample_factor
    
    s_x = np.arange(ss_size)
    s_y = np.arange(ss_size)
    s_xx, s_yy = np.meshgrid(s_x, s_y)

    dist_sq = (s_xx - ss_radius + 0.5)**2 + (s_yy - ss_radius + 0.5)**2
    
    alpha_mask_ss = np.where(dist_sq < ss_radius**2, 1.0, 0.0)

    alpha = alpha_mask_ss.reshape(size, supersample_factor, size, supersample_factor).mean(axis=(1, 3))
    
    surf = pygame.Surface((size, size), pygame.SRCALPHA)
    rgb_data = np.full((size, size, 3), color[:3], dtype=np.uint8)
    alpha_data = (alpha * (color[3] if len(color) > 3 else 255)).astype(np.uint8)
    
    pygame.surfarray.pixels3d(surf)[:] = rgb_data
    pygame.surfarray.pixels_alpha(surf)[:] = np.transpose(alpha_data, (1, 0))

    return surf

def _create_circle_sdf(radius, color):
    size = radius * 2
    x = np.arange(size)
    y = np.arange(size)
    xx, yy = np.meshgrid(x, y)
    
    dist = np.sqrt((xx - radius + 0.5)**2 + (yy - radius + 0.5)**2)
    
    signed_dist = dist - radius
    
    alpha = np.clip(0.5 - signed_dist, 0, 1)
    
    surf = pygame.Surface((size, size), pygame.SRCALPHA)
    rgb_data = np.full((size, size, 3), color[:3], dtype=np.uint8)
    alpha_data = (alpha * (color[3] if len(color) > 3 else 255)).astype(np.uint8)
    
    pygame.surfarray.pixels3d(surf)[:] = rgb_data
    pygame.surfarray.pixels_alpha(surf)[:] = np.transpose(alpha_data, (1, 0))
    
    return surf

class Circle:
    _convertor = Convertor
    @classmethod
    def create_AA(cls, radius, color, AA_factor = 4):
        radius = cls._convertor.convert(radius, int)
        color = cls._convertor.convert(color, tuple)
        AA_factor = cls._convertor.convert(AA_factor, int)
        return _create_circle_AA(radius, color, AA_factor) # type: ignore

    @classmethod
    def create_sdf(cls, radius, color):
        radius = cls._convertor.convert(radius, int)
        color = cls._convertor.convert(color, tuple)
        return _create_circle_sdf(radius, color)