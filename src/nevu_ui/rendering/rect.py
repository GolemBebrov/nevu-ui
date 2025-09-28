import numpy as np
import pygame

from nevu_ui.utils import Convertor

from nevu_ui.fast.shapes import _create_rounded_rect_surface_optimized

def _create_rounded_rect_AA(size, radius, color, _factor = 4):
    """
    Создает поверхность Pygame со сглаженным скругленным прямоугольником с использованием NumPy.

    :param size: Tuple (width, height) - размеры прямоугольника.
    :param radius: int - радиус скругления углов.
    :param color: Tuple (r, g, b) or (r, g, b, a) - цвет фигуры.
    :return: pygame.Surface с альфа-каналом.
    """
    width, height = size
    radius = min(radius, width // 2, height // 2)

    supersample_factor = _factor
    sw, sh = width * supersample_factor, height * supersample_factor
    s_x = np.arange(sw)
    s_y = np.arange(sh)
    s_xx, s_yy = np.meshgrid(s_x, s_y)
    
    s_xx_f = s_xx / supersample_factor
    s_yy_f = s_yy / supersample_factor

    centers = [
        (radius, radius),
        (width - radius, radius),
        (radius, height - radius),
        (width - radius, height - radius)
    ]

    alpha_mask_ss = np.zeros((sh, sw))

    rect_mask = (s_xx_f >= radius) & (s_xx_f < width - radius) & (s_yy_f >= 0) & (s_yy_f < height)
    rect_mask |= (s_yy_f >= radius) & (s_yy_f < height - radius) & (s_xx_f >= 0) & (s_xx_f < width)
    alpha_mask_ss[rect_mask] = 1.0

    for cx, cy in centers:
        dist_sq = (s_xx_f - cx)**2 + (s_yy_f - cy)**2
        alpha_mask_ss[dist_sq < radius**2] = 1.0
    
    alpha = alpha_mask_ss.reshape(height, supersample_factor, width, supersample_factor).mean(axis=(1, 3))
    surf = pygame.Surface((width, height), pygame.SRCALPHA)
    rgb_data = np.full((width, height, 3), color[:3], dtype=np.uint8)
    alpha_data = (alpha * (color[3] if len(color) > 3 else 255)).astype(np.uint8)
    pygame.surfarray.pixels3d(surf)[:] = rgb_data
    pygame.surfarray.pixels_alpha(surf)[:] = np.transpose(alpha_data, (1, 0))

    return surf

class RoundedRect:
    _convertor = Convertor
    @classmethod
    def create_AA(cls, size, radius, color, AA_factor = 4):
        size = cls._convertor.convert(size, tuple)
        radius = cls._convertor.convert(radius, int)
        color = cls._convertor.convert(color, tuple)
        AA_factor = cls._convertor.convert(AA_factor, int)
        return _create_rounded_rect_AA(size, radius, color, AA_factor) # type: ignore
    
    @classmethod
    def create_sdf(cls, size, radius, color):
        return _create_rounded_rect_surface_optimized(tuple(size), radius, color)

class Rect:
    _convertor = Convertor
    @classmethod
    def create_AA(cls, size, color, AA_factor = 4):
        size = cls._convertor.convert(size, tuple)
        color = cls._convertor.convert(color, tuple)
        AA_factor = cls._convertor.convert(AA_factor, int)
        return _create_rounded_rect_AA(size, 0, color, AA_factor) # type: ignore

    @classmethod
    def create_sdf(cls, size, color):
        size = cls._convertor.convert(size, tuple)
        color = cls._convertor.convert(color, tuple)
        return _create_rounded_rect_surface_optimized(size, 0, color) # type: ignore