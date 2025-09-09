import pygame
import numpy as np
cimport numpy as np
import cython

@cython.boundscheck(False)
@cython.wraparound(False)
cpdef object _create_outlined_rounded_rect_sdf(tuple size, int radius, float width, tuple color):
    cdef int w = size[0]
    cdef int h = size[1]
    cdef float half_width = width / 2.0

    radius = min(radius, w // 2, h // 2)

    cdef float center_radius = radius - half_width
    if center_radius < 0:
        center_radius = 0.0

    cdef object surf = pygame.Surface(size, pygame.SRCALPHA)

    cdef np.ndarray y, x
    y, x = np.ogrid[:h, :w]

    cdef float centerline_straight_half_w = ((w - width) - 2 * center_radius - 1) / 2.0
    cdef float centerline_straight_half_h = ((h - width) - 2 * center_radius - 1) / 2.0

    cdef np.ndarray dist_x = np.abs(x - (w - 1) / 2.0) - centerline_straight_half_w
    cdef np.ndarray dist_y = np.abs(y - (h - 1) / 2.0) - centerline_straight_half_h

    cdef np.ndarray dist_from_inner_corner = np.sqrt(np.maximum(dist_x, 0.0)**2 + np.maximum(dist_y, 0.0)**2)
    cdef np.ndarray signed_dist = dist_from_inner_corner + np.minimum(np.maximum(dist_x, dist_y), 0.0) - center_radius
    
    cdef np.ndarray dist_from_edge = np.abs(signed_dist)
    
    cdef np.ndarray alpha = np.clip(0.5 - (dist_from_edge - half_width), 0.0, 1.0)

    cdef np.ndarray[np.uint8_t, ndim=3] pixels3d = pygame.surfarray.pixels3d(surf)
    cdef np.ndarray[np.uint8_t, ndim=2] pixels_alpha = pygame.surfarray.pixels_alpha(surf)

    pixels3d[:] = color[:3]
    pixels_alpha[:] = (alpha * (color[3] if len(color) > 3 else 255)).astype(np.uint8).T

    del pixels3d
    del pixels_alpha

    return surf


@cython.boundscheck(False)
@cython.wraparound(False)
cpdef object _create_rounded_rect_surface_optimized(tuple size, int radius, tuple color):
    cdef int width, height, alpha_value
    width, height = int(size[0]), int(size[1])
    radius = min(radius, width // 2, height // 2)

    cdef object surf = pygame.Surface(size, pygame.SRCALPHA)

    if radius <= 0:
        surf.fill(color)
        return surf

    alpha_value = color[3] if len(color) > 3 else 255
    if alpha_value == 0:
        return surf

    cdef float center_x = (width - 1) / 2.0
    cdef float center_y = (height - 1) / 2.0
    cdef float inner_width_half = (width - 2 * radius - 1) / 2.0
    cdef float inner_height_half = (height - 2 * radius - 1) / 2.0

    cdef np.ndarray y, x
    y, x = np.ogrid[:height, :width]

    cdef np.ndarray dx = np.abs(x - center_x) - inner_width_half
    cdef np.ndarray dy = np.abs(y - center_y) - inner_height_half

    cdef np.ndarray dist = np.sqrt(np.maximum(dx, 0.0)**2 + np.maximum(dy, 0.0)**2)
    cdef np.ndarray signed_dist = dist - radius
    cdef np.ndarray alpha_field = np.maximum(0.0, np.minimum(1.0, 0.5 - signed_dist))

    cdef np.ndarray[np.uint8_t, ndim=3] pixels3d = pygame.surfarray.pixels3d(surf)
    cdef np.ndarray[np.uint8_t, ndim=2] pixels_alpha = pygame.surfarray.pixels_alpha(surf)

    pixels3d[:] = color[:3]
    pixels_alpha[:] = (alpha_field * alpha_value).astype(np.uint8).T

    del pixels3d
    del pixels_alpha

    return surf