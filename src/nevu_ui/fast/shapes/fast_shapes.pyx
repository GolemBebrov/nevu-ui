# distutils: language = c++
# distutils: extra_compile_args = -fopenmp
# distutils: extra_link_args = -fopenmp
# cython: language_level=3
# cython: boundscheck=False
# cython: wraparound=False
# cython: cdivision=True
# cython: nonecheck=False

import pygame
import numpy as np
cimport numpy as np
cimport cython
from cython.parallel import prange
from libc.math cimport sqrt, fabs, fmax, fmin

ctypedef np.uint8_t uint8_t

@cython.boundscheck(False)
@cython.wraparound(False)
cpdef object _create_outlined_rounded_rect_sdf(tuple size, int radius, float width, tuple color):
    cdef int w = int(size[0])
    cdef int h = int(size[1])
    cdef float half_width = width / 2.0

    if radius * 2 > w: radius = w // 2
    if radius * 2 > h: radius = h // 2

    cdef float center_radius = radius - half_width
    if center_radius < 0:
        center_radius = 0.0

    cdef object surf = pygame.Surface((w, h), pygame.SRCALPHA)
    
    cdef uint8_t[:, :, :] pixels3d = pygame.surfarray.pixels3d(surf)
    cdef uint8_t[:, :] pixels_alpha = pygame.surfarray.pixels_alpha(surf)

    cdef int alpha_val = color[3] if len(color) > 3 else 255
    cdef uint8_t r = color[0]
    cdef uint8_t g = color[1]
    cdef uint8_t b = color[2]

    cdef float center_x = (w - 1) * 0.5
    cdef float center_y = (h - 1) * 0.5
    
    cdef float centerline_w = ((w - width) - 2 * center_radius - 1) * 0.5
    cdef float centerline_h = ((h - width) - 2 * center_radius - 1) * 0.5

    cdef int x, y
    cdef float dx, dy, dist, signed_dist, dist_from_edge, alpha_f

    with nogil:
        for y in prange(h, schedule='static'):
            for x in range(w):
                dx = fabs(x - center_x) - centerline_w
                dy = fabs(y - center_y) - centerline_h

                dist = sqrt(fmax(dx, 0.0)**2 + fmax(dy, 0.0)**2)
                signed_dist = dist + fmin(fmax(dx, dy), 0.0) - center_radius
                
                dist_from_edge = fabs(signed_dist)
                
                alpha_f = 0.5 - (dist_from_edge - half_width)
                
                if alpha_f < 0.0: alpha_f = 0.0
                elif alpha_f > 1.0: alpha_f = 1.0

                pixels3d[x, y, 0] = r
                pixels3d[x, y, 1] = g
                pixels3d[x, y, 2] = b
                pixels_alpha[x, y] = <uint8_t>(alpha_f * alpha_val)

    return surf

@cython.boundscheck(False)
@cython.wraparound(False)
cpdef object _create_rounded_rect_surface_optimized(tuple size, int radius, tuple color):
    cdef int width = int(size[0])
    cdef int height = int(size[1])
    
    if radius * 2 > width: radius = width // 2
    if radius * 2 > height: radius = height // 2

    cdef object surf = pygame.Surface((width, height), pygame.SRCALPHA)

    if radius <= 0:
        surf.fill(color)
        return surf

    cdef int alpha_val = color[3] if len(color) > 3 else 255
    if alpha_val == 0:
        return surf
        
    cdef uint8_t[:, :, :] pixels3d = pygame.surfarray.pixels3d(surf)
    cdef uint8_t[:, :] pixels_alpha = pygame.surfarray.pixels_alpha(surf)
    
    cdef float center_x = (width - 1) * 0.5
    cdef float center_y = (height - 1) * 0.5
    cdef float inner_width_half = (width - 2 * radius - 1) * 0.5
    cdef float inner_height_half = (height - 2 * radius - 1) * 0.5
    
    cdef uint8_t r = color[0]
    cdef uint8_t g = color[1]
    cdef uint8_t b = color[2]
    
    cdef int x, y
    cdef float dx, dy, dist, signed_dist, alpha_f
    
    with nogil:
        for y in prange(height, schedule='static'):
            for x in range(width):
                dx = fabs(x - center_x) - inner_width_half
                dy = fabs(y - center_y) - inner_height_half
                
                dist = sqrt(fmax(dx, 0.0)**2 + fmax(dy, 0.0)**2)
                signed_dist = dist - radius
                
                alpha_f = 0.5 - signed_dist
                if alpha_f < 0.0: alpha_f = 0.0
                elif alpha_f > 1.0: alpha_f = 1.0
                
                pixels3d[x, y, 0] = r
                pixels3d[x, y, 1] = g
                pixels3d[x, y, 2] = b
                pixels_alpha[x, y] = <uint8_t>(alpha_f * alpha_val)

    return surf