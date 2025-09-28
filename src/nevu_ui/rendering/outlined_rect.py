import numpy as np
import pygame

from nevu_ui.utils import Convertor

from nevu_ui.fast.shapes import _create_outlined_rounded_rect_sdf

def _create_outlined_rounded_rect_AA(size, radius, width, color, _factor = 4):
    w, h = size
    radius = min(radius, w // 2, h // 2)
    half_width = width / 2.0
    
    supersample_factor = _factor
    sw, sh = w * supersample_factor, h * supersample_factor
    s_x = (np.arange(sw) + 0.5) / supersample_factor
    s_y = (np.arange(sh) + 0.5) / supersample_factor
    s_xx, s_yy = np.meshgrid(s_x, s_y)

    inner_w = w - 2 * radius
    inner_h = h - 2 * radius
    dist_x = np.abs(s_xx - (w - 1) / 2) - (inner_w - 1) / 2
    dist_y = np.abs(s_yy - (h - 1) / 2) - (inner_h - 1) / 2
    
    dist_from_inner_corner = np.sqrt(np.maximum(dist_x, 0)**2 + np.maximum(dist_y, 0)**2)
    signed_dist = dist_from_inner_corner - radius
    
    dist_from_edge = np.abs(signed_dist)
    
    alpha_mask_ss = np.clip(half_width - dist_from_edge + 0.5, 0, 1)

    alpha = alpha_mask_ss.reshape(h, supersample_factor, w, supersample_factor).mean(axis=(1, 3))
    
    surf = pygame.Surface(size, pygame.SRCALPHA)
    rgb_data = np.full((w, h, 3), color[:3], dtype=np.uint8)
    alpha_data = (alpha * (color[3] if len(color) > 3 else 255)).astype(np.uint8)
    pygame.surfarray.pixels3d(surf)[:] = rgb_data
    pygame.surfarray.pixels_alpha(surf)[:] = np.transpose(alpha_data, (1, 0))

    return surf

class OutlinedRoundedRect:
    _convertor = Convertor
    @classmethod
    def create_AA(cls, size, radius, width, color, AA_factor = 4):
        size = cls._convertor.convert(size, tuple)
        radius = cls._convertor.convert(radius, int)
        width = cls._convertor.convert(width, float)
        color = cls._convertor.convert(color, tuple)
        AA_factor = cls._convertor.convert(AA_factor, int)
        return _create_outlined_rounded_rect_AA(size, radius, width, color, AA_factor) # type: ignore
    
    @classmethod
    def create_sdf(cls, size, radius, width, color):
        size = cls._convertor.convert(size, tuple)
        radius = cls._convertor.convert(radius, int)
        width = cls._convertor.convert(width, float)
        color = cls._convertor.convert(color, tuple)
        return _create_outlined_rounded_rect_sdf(tuple(size), radius, width, color) # type: ignore

class OutlinedRect:
    _convertor = Convertor
    @classmethod
    def create_AA(cls, size, width, color, AA_factor = 4):
        size = cls._convertor.convert(size, tuple)
        width = cls._convertor.convert(width, float)
        color = cls._convertor.convert(color, tuple)
        AA_factor = cls._convertor.convert(AA_factor, int)
        return _create_outlined_rounded_rect_AA(size, 0, width, color, AA_factor) # type: ignore

    @classmethod
    def create_sdf(cls, size, width, color):
        size = cls._convertor.convert(size, tuple)
        width = cls._convertor.convert(width, float)
        color = cls._convertor.convert(color, tuple)
        return _create_outlined_rounded_rect_sdf(size, 0, width, color) # type: ignore

