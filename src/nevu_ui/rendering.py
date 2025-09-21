import pygame
import numpy as np

from .utils import Convertor

from .fast_shapes import (
    _create_rounded_rect_surface_optimized, _create_outlined_rounded_rect_sdf
)

#####################################################################
#                                                                   #
#                     LOW-LEVEL IMPLEMENTATIONS                     #
#                                                                   #
#####################################################################

########################
#       Triangle       #
########################

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

########################
#     Rounded Rect     #
########################

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

########################
#        Circle        #
########################

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

########################
#         Line         #
########################

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

########################
#    Outlined  Rect    #
########################

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

######### Useful functions #########
def _dist_to_segment_sq(px, py, ax, ay, bx, by):
    abx, aby = bx - ax, by - ay
    apx, apy = px - ax, py - ay
    ab_len_sq = abx**2 + aby**2
    ab_len_sq = np.where(ab_len_sq == 0, 1, ab_len_sq)
    dot_p = apx * abx + apy * aby
    t = np.clip(dot_p / ab_len_sq, 0, 1)
    proj_x, proj_y = ax + t * abx, ay + t * aby
    return (px - proj_x)**2 + (py - proj_y)**2

#####################################################################
#                                                                   #
#                         PUBLIC RENDER API                         #
#                                                                   #
#####################################################################

class RoundedRect:
    _convertor = Convertor
    @classmethod
    def create_AA(cls, size, radius, color, AA_factor = 4):
        size = cls._convertor.convert(size, tuple)
        radius = cls._convertor.convert(radius, int)
        color = cls._convertor.convert(color, tuple)
        AA_factor = cls._convertor.convert(AA_factor, int)
        return _create_rounded_rect_AA(size, radius, color, AA_factor)
    
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
        return _create_rounded_rect_AA(size, 0, color, AA_factor)

    @classmethod
    def create_sdf(cls, size, color):
        size = cls._convertor.convert(size, tuple)
        color = cls._convertor.convert(color, tuple)
        return _create_rounded_rect_surface_optimized(size, 0, color)

class Circle:
    _convertor = Convertor
    @classmethod
    def create_AA(cls, radius, color, AA_factor = 4):
        radius = cls._convertor.convert(radius, int)
        color = cls._convertor.convert(color, tuple)
        AA_factor = cls._convertor.convert(AA_factor, int)
        return _create_circle_AA(radius, color, AA_factor)

    @classmethod
    def create_sdf(cls, radius, color):
        radius = cls._convertor.convert(radius, int)
        color = cls._convertor.convert(color, tuple)
        return _create_circle_sdf(radius, color)

class Triangle:
    _convertor = Convertor
    @classmethod
    def create_AA(cls, p1, p2, p3, color, AA_factor = 4):
        p1 = cls._convertor.convert(p1, pygame.Vector2)
        p2 = cls._convertor.convert(p2, pygame.Vector2)
        p3 = cls._convertor.convert(p3, pygame.Vector2)
        color = cls._convertor.convert(color, tuple)
        AA_factor = cls._convertor.convert(AA_factor, int)
        return _create_triangle_AA(p1, p2, p3, color, AA_factor)

    @classmethod
    def create_sdf(cls, p1, p2, p3, color):
        p1 = cls._convertor.convert(p1, pygame.Vector2)
        p2 = cls._convertor.convert(p2, pygame.Vector2)
        p3 = cls._convertor.convert(p3, pygame.Vector2)
        color = cls._convertor.convert(color, tuple)
        return _create_triangle_sdf(p1, p2, p3, color)

class Line:
    _convertor = Convertor
    @classmethod
    def create_AA(cls, p1, p2, thickness, color, AA_factor = 4):
        p1 = cls._convertor.convert(p1, pygame.Vector2)
        p2 = cls._convertor.convert(p2, pygame.Vector2)
        thickness = cls._convertor.convert(thickness, float)
        color = cls._convertor.convert(color, tuple)
        AA_factor = cls._convertor.convert(AA_factor, int)
        return _create_line_AA(p1, p2, thickness, color, AA_factor)

    @classmethod
    def create_sdf(cls, p1, p2, thickness, color):
        p1 = cls._convertor.convert(p1, pygame.Vector2)
        p2 = cls._convertor.convert(p2, pygame.Vector2)
        thickness = cls._convertor.convert(thickness, float)
        color = cls._convertor.convert(color, tuple)
        return _create_line_sdf(p1, p2, thickness, color)

class OutlinedRoundedRect:
    _convertor = Convertor
    @classmethod
    def create_AA(cls, size, radius, width, color, AA_factor = 4):
        size = cls._convertor.convert(size, tuple)
        radius = cls._convertor.convert(radius, int)
        width = cls._convertor.convert(width, float)
        color = cls._convertor.convert(color, tuple)
        AA_factor = cls._convertor.convert(AA_factor, int)
        return _create_outlined_rounded_rect_AA(size, radius, width, color, AA_factor)
    
    @classmethod
    def create_sdf(cls, size, radius, width, color):
        size = cls._convertor.convert(size, tuple)
        radius = cls._convertor.convert(radius, int)
        width = cls._convertor.convert(width, float)
        color = cls._convertor.convert(color, tuple)
        return _create_outlined_rounded_rect_sdf(tuple(size), radius, width, color)

class OutlinedRect:
    _convertor = Convertor
    @classmethod
    def create_AA(cls, size, width, color, AA_factor = 4):
        size = cls._convertor.convert(size, tuple)
        width = cls._convertor.convert(width, float)
        color = cls._convertor.convert(color, tuple)
        AA_factor = cls._convertor.convert(AA_factor, int)
        return _create_outlined_rounded_rect_AA(size, 0, width, color, AA_factor)

    @classmethod
    def create_sdf(cls, size, width, color):
        size = cls._convertor.convert(size, tuple)
        width = cls._convertor.convert(width, float)
        color = cls._convertor.convert(color, tuple)
        return _create_outlined_rounded_rect_sdf(size, 0, width, color)

class AlphaBlit:
    @staticmethod
    def blit(dest_surf: pygame.Surface, source_surf: pygame.Surface, dest_pos: tuple[int, int]):
        x, y = dest_pos
        width, height = source_surf.get_size()
        roi_rect = pygame.Rect(x, y, width, height)
        roi_rect_clipped = roi_rect.clip(dest_surf.get_rect())

        if roi_rect_clipped.width == 0 or roi_rect_clipped.height == 0:
            return

        src_x_offset = roi_rect_clipped.x - roi_rect.x
        src_y_offset = roi_rect_clipped.y - roi_rect.y

        try:
            src_slice_x = slice(src_x_offset, src_x_offset + roi_rect_clipped.width)
            src_slice_y = slice(src_y_offset, src_y_offset + roi_rect_clipped.height)
            dest_slice_x = slice(roi_rect_clipped.x, roi_rect_clipped.right)
            dest_slice_y = slice(roi_rect_clipped.y, roi_rect_clipped.bottom)

            source_alpha_view = pygame.surfarray.pixels_alpha(source_surf)[src_slice_x, src_slice_y]
            dest_alpha_view = pygame.surfarray.pixels_alpha(dest_surf)[dest_slice_x, dest_slice_y]
            
            np.copyto(dest_alpha_view, source_alpha_view)

        except ValueError:
            clipped_source_rect = pygame.Rect(src_x_offset, src_y_offset, roi_rect_clipped.width, roi_rect_clipped.height)
            dest_surf.blit(source_surf.subsurface(clipped_source_rect), roi_rect_clipped.topleft, special_flags=pygame.BLEND_RGBA_MULT)

class FastBlit:
    @staticmethod
    def blit(dest_surf: pygame.Surface, source_surf: pygame.Surface, dest_pos: tuple[int, int]):
        x, y = dest_pos
        width, height = source_surf.get_size()
        roi_rect = pygame.Rect(x, y, width, height)
        roi_rect_clipped = roi_rect.clip(dest_surf.get_rect())

        if roi_rect_clipped.width == 0 or roi_rect_clipped.height == 0:
            return

        src_x_offset = roi_rect_clipped.x - roi_rect.x
        src_y_offset = roi_rect_clipped.y - roi_rect.y

        try:
            src_slice_x = slice(src_x_offset, src_x_offset + roi_rect_clipped.width)
            src_slice_y = slice(src_y_offset, src_y_offset + roi_rect_clipped.height)
            dest_slice_x = slice(roi_rect_clipped.x, roi_rect_clipped.right)
            dest_slice_y = slice(roi_rect_clipped.y, roi_rect_clipped.bottom)

            source_rgb_view = pygame.surfarray.pixels3d(source_surf)[src_slice_x, src_slice_y]
            dest_rgb_view = pygame.surfarray.pixels3d(dest_surf)[dest_slice_x, dest_slice_y]
            np.copyto(dest_rgb_view, source_rgb_view)
            
            source_alpha_view = pygame.surfarray.pixels_alpha(source_surf)[src_slice_x, src_slice_y]
            dest_alpha_view = pygame.surfarray.pixels_alpha(dest_surf)[dest_slice_x, dest_slice_y]
            np.copyto(dest_alpha_view, source_alpha_view)

        except ValueError:
            clipped_source_rect = pygame.Rect(src_x_offset, src_y_offset, roi_rect_clipped.width, roi_rect_clipped.height)
            dest_surf.blit(source_surf.subsurface(clipped_source_rect), roi_rect_clipped.topleft)