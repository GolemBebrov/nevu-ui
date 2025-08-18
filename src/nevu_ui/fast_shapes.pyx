
import pygame
import numpy as np

cimport numpy as np

import cython

@cython.boundscheck(False)
@cython.wraparound(False)
cpdef _create_outlined_rounded_rect_sdf(tuple size, int radius, float width, tuple color):
    # Объявляем простые переменные как C-типы. Это быстро.
    cdef int w = size[0]
    cdef int h = size[1]
    cdef float half_width = width / 2.0

    radius = min(radius, w // 2, h // 2)

    x = np.arange(w)
    y = np.arange(h)
    xx, yy = np.meshgrid(x, y)

    inner_w = w - 2 * radius
    inner_h = h - 2 * radius
    dist_x = np.abs(xx - (w - 1) / 2.0) - (inner_w - 1) / 2.0
    dist_y = np.abs(yy - (h - 1) / 2.0) - (inner_h - 1) / 2.0
    
    dist_from_inner_corner = np.sqrt(np.maximum(dist_x, 0)**2 + np.maximum(dist_y, 0)**2)
    
    signed_dist = dist_from_inner_corner + np.minimum(np.maximum(dist_x, dist_y), 0) - radius
    
    dist_from_edge = np.abs(signed_dist)
    
    alpha = np.clip(0.5 - (dist_from_edge - half_width), 0, 1)

    # Эта часть также остается без изменений
    surf = pygame.Surface(size, pygame.SRCALPHA)
    
    # Мы можем немного ускорить создание массива, указав dtype сразу
    rgb_data = np.full((h, w, 3), color[:3], dtype=np.uint8)
    pygame.surfarray.pixels3d(surf)[:] = rgb_data.transpose((1, 0, 2))

    alpha_data = (alpha * (color[3] if len(color) > 3 else 255)).astype(np.uint8)
    pygame.surfarray.pixels_alpha(surf)[:] = alpha_data.T

    return surf
    
@cython.boundscheck(False)
@cython.wraparound(False)
cpdef _create_rounded_rect_surface_optimized(tuple size, int radius, tuple color):
    cdef int width, height, alpha_value
    width, height = int(size[0]), int(size[1])
    radius = min(radius, width // 2, height // 2)

    if radius <= 0:
        surf = pygame.Surface(size, pygame.SRCALPHA)
        surf.fill(color)
        return surf

    alpha_value = color[3] if len(color) > 3 else 255
    if alpha_value == 0:
        return pygame.Surface(size, pygame.SRCALPHA)

    center_x = (width - 1) / 2.0
    center_y = (height - 1) / 2.0
    inner_width_half = (width - 2 * radius - 1) / 2.0
    inner_height_half = (height - 2 * radius - 1) / 2.0
    
    y, x = np.ogrid[:height, :width]

    dx = np.abs(x - center_x) - inner_width_half
    dy = np.abs(y - center_y) - inner_height_half

    dist = np.sqrt(np.maximum(dx, 0.0)**2 + np.maximum(dy, 0.0)**2)
    signed_dist = dist - radius
    alpha_field = np.maximum(0.0, np.minimum(1.0, 0.5 - signed_dist))

    surf = pygame.Surface(size, pygame.SRCALPHA)
    rgb_data = np.full((height, width, 3), color[:3], dtype=np.uint8)
    pygame.surfarray.pixels3d(surf)[:] = rgb_data.transpose((1, 0, 2))

    alpha_data = (alpha_field * alpha_value).astype(np.uint8)
    pygame.surfarray.pixels_alpha(surf)[:] = alpha_data.T

    return surf