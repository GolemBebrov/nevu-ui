# distutils: language = c++
# distutils: extra_compile_args = -fopenmp
# distutils: extra_link_args = -fopenmp
# cython: language_level=3
# cython: boundscheck=False
# cython: wraparound=False
# cython: cdivision=True
# cython: nonecheck=False
# cython: initializedcheck=False

import pygame
import numpy as np
cimport numpy as np
cimport cython
from cython.parallel import prange
from libc.math cimport sqrt, fabs, fmax, fmin, ceil

ctypedef np.uint8_t uint8_t

@cython.boundscheck(False)
@cython.wraparound(False)
cpdef object _create_outlined_rounded_rect_sdf(tuple size, int radius, float width, tuple color):
    cdef int w = int(size[0])
    cdef int h = int(size[1])
    cdef float half_width = width / 2.0

    if radius * 2 > w: radius = w // 2
    if radius * 2 > h: radius = h // 2

    cdef float center_radius = float(radius) - half_width
    if center_radius < 0:
        center_radius = 0.0

    cdef object surf = pygame.Surface((w, h), pygame.SRCALPHA)
    surf.fill((0, 0, 0, 0))
    
    cdef uint8_t[:, :, :] pixels3d = pygame.surfarray.pixels3d(surf)
    cdef uint8_t[:, :] pixels_alpha = pygame.surfarray.pixels_alpha(surf)

    cdef int alpha_base = color[3] if len(color) > 3 else 255
    if alpha_base == 0:
        return surf

    cdef uint8_t r = color[0]
    cdef uint8_t g = color[1]
    cdef uint8_t b = color[2]

    cdef float center_x = (w - 1) * 0.5 
    cdef float center_y = (h - 1) * 0.5
    
    cdef float centerline_w = ((w - width) - 2.0 * center_radius - 1.0) * 0.5
    cdef float centerline_h = ((h - width) - 2.0 * center_radius - 1.0) * 0.5

    cdef int x, y
    cdef float dx, dy, dist, signed_dist, dist_from_edge, alpha_f
    cdef float dy_sq, current_dy_dist
    cdef float cutoff = half_width + 0.5

    with nogil:
        for y in prange(h, schedule='static'):
            dy = fabs(y - center_y) - centerline_h
            current_dy_dist = fmax(dy, 0.0)
            dy_sq = current_dy_dist * current_dy_dist

            for x in range(w):
                dx = fabs(x - center_x) - centerline_w
                
                if dx > 0.0 and dy > 0.0:
                    dist = sqrt(dx*dx + dy_sq)
                else:
                    dist = fmax(dx, current_dy_dist)

                signed_dist = dist + fmin(fmax(dx, dy), 0.0) - center_radius
                dist_from_edge = fabs(signed_dist)
                
                if dist_from_edge > cutoff:
                    continue
                
                alpha_f = 0.5 - (dist_from_edge - half_width)
                
                if alpha_f > 0.0:
                    pixels3d[x, y, 0] = r
                    pixels3d[x, y, 1] = g
                    pixels3d[x, y, 2] = b
                    if alpha_f >= 1.0:
                        pixels_alpha[x, y] = <uint8_t>alpha_base
                    else:
                        pixels_alpha[x, y] = <uint8_t>(alpha_f * alpha_base)

    return surf


cdef extern from "math.h":
    float sqrtf(float) nogil
    float fabsf(float) nogil
    float fmaxf(float, float) nogil
    float fminf(float, float) nogil

cpdef object _create_rounded_rect_surface_optimized(tuple size, object radii_input, tuple color):
    cdef int width = int(size[0])
    cdef int height = int(size[1])
    
    cdef float r_tl, r_tr, r_br, r_bl
    
    if isinstance(radii_input, (int, float)):
        r_tl = r_tr = r_br = r_bl = <float>radii_input
    elif len(radii_input) == 4:
        r_tl = <float>radii_input[0]
        r_tr = <float>radii_input[1]
        r_br = <float>radii_input[2]
        r_bl = <float>radii_input[3]
    else:
        r_tl = r_tr = r_br = r_bl = 0.0

    cdef float min_dim = fminf(width, height) / 2.0
    if r_tl > min_dim: r_tl = min_dim
    if r_tr > min_dim: r_tr = min_dim
    if r_br > min_dim: r_br = min_dim
    if r_bl > min_dim: r_bl = min_dim

    cdef object surf = pygame.Surface((width, height), pygame.SRCALPHA)
    
    cdef int alpha_base = color[3] if len(color) > 3 else 255
    if alpha_base == 0:
        return surf

    cdef uint8_t[:, :, :] pixels3d = pygame.surfarray.pixels3d(surf)
    cdef uint8_t[:, :] pixels_alpha = pygame.surfarray.pixels_alpha(surf)
    
    cdef uint8_t r = color[0]
    cdef uint8_t g = color[1]
    cdef uint8_t b = color[2]

    cdef float center_x = (width - 1) * 0.5
    cdef float center_y = (height - 1) * 0.5
    cdef float half_w = width * 0.5
    cdef float half_h = height * 0.5

    cdef int x, y
    cdef float px, py
    cdef float current_r
    cdef float qx, qy
    cdef float dist_outside, dist_inside
    cdef float signed_dist, alpha_f
    
    with nogil:
        for y in prange(height, schedule='static'):
            py = y - center_y
            
            for x in range(width):
                px = x - center_x
                
                if px > 0.0:
                    if py > 0.0: current_r = r_br
                    else:        current_r = r_tr
                else:
                    if py > 0.0: current_r = r_bl
                    else:        current_r = r_tl
                
                qx = fabsf(px) - half_w + current_r
                qy = fabsf(py) - half_h + current_r
                
                dist_outside = sqrtf(fmaxf(qx, 0.0)**2 + fmaxf(qy, 0.0)**2)
                dist_inside = fminf(fmaxf(qx, qy), 0.0)
                
                signed_dist = dist_outside + dist_inside - current_r
                
                if signed_dist <= -0.5:
                    pixels3d[x, y, 0] = r
                    pixels3d[x, y, 1] = g
                    pixels3d[x, y, 2] = b
                    pixels_alpha[x, y] = <uint8_t>alpha_base
                elif signed_dist < 0.5:
                    alpha_f = 0.5 - signed_dist
                    pixels3d[x, y, 0] = r
                    pixels3d[x, y, 1] = g
                    pixels3d[x, y, 2] = b
                    pixels_alpha[x, y] = <uint8_t>(alpha_f * alpha_base)
                    
    return surf

cpdef void transform_into_outlined_rounded_rect(object surf, object radii_input, float stroke_width, tuple color):
    cdef int w = surf.get_width()
    cdef int h = surf.get_height()
    cdef float half_width = stroke_width / 2.0
    
    cdef float r_tl, r_tr, r_br, r_bl
    
    if isinstance(radii_input, (int, float)):
        r_tl = r_tr = r_br = r_bl = <float>radii_input
    elif len(radii_input) == 4:
        r_tl = <float>radii_input[0]
        r_tr = <float>radii_input[1]
        r_br = <float>radii_input[2]
        r_bl = <float>radii_input[3]
    else:
        r_tl = r_tr = r_br = r_bl = 0.0

    r_tl = fmaxf(r_tl - half_width, 0.0)
    r_tr = fmaxf(r_tr - half_width, 0.0)
    r_br = fmaxf(r_br - half_width, 0.0)
    r_bl = fmaxf(r_bl - half_width, 0.0)

    surf.fill((0, 0, 0, 0))
    
    cdef uint8_t[:, :, :] pixels3d = pygame.surfarray.pixels3d(surf)
    cdef uint8_t[:, :] pixels_alpha = pygame.surfarray.pixels_alpha(surf)

    cdef int alpha_base = color[3] if len(color) > 3 else 255
    if alpha_base == 0:
        return

    cdef uint8_t r = color[0]
    cdef uint8_t g = color[1]
    cdef uint8_t b = color[2]

    cdef float center_x = (w - 1) * 0.5
    cdef float center_y = (h - 1) * 0.5
    
    cdef float box_half_w = (w - stroke_width) * 0.5
    cdef float box_half_h = (h - stroke_width) * 0.5

    cdef int x, y
    cdef float px, py
    cdef float current_r
    cdef float qx, qy
    cdef float dist_outside, dist_inside
    cdef float signed_dist, dist_from_edge, alpha_f
    cdef float cutoff = half_width + 0.5

    with nogil:
        for y in prange(h, schedule='static'):
            py = y - center_y
            
            for x in range(w):
                px = x - center_x
                
                if px > 0.0:
                    if py > 0.0: current_r = r_br
                    else:        current_r = r_tr
                else:
                    if py > 0.0: current_r = r_bl
                    else:        current_r = r_tl
                
                qx = fabsf(px) - box_half_w + current_r
                qy = fabsf(py) - box_half_h + current_r
                
                dist_outside = sqrtf(fmaxf(qx, 0.0)**2 + fmaxf(qy, 0.0)**2)
                dist_inside = fminf(fmaxf(qx, qy), 0.0)
                
                signed_dist = dist_outside + dist_inside - current_r
                dist_from_edge = fabsf(signed_dist)
                
                if dist_from_edge > cutoff:
                    continue
                
                alpha_f = 0.5 - (dist_from_edge - half_width)
                
                if alpha_f > 0.0:
                    pixels3d[x, y, 0] = r
                    pixels3d[x, y, 1] = g
                    pixels3d[x, y, 2] = b
                    if alpha_f >= 1.0:
                        pixels_alpha[x, y] = <uint8_t>alpha_base
                    else:
                        pixels_alpha[x, y] = <uint8_t>(alpha_f * alpha_base)

@cython.boundscheck(False)
@cython.wraparound(False)
cpdef void transform_into_rounded_rect(object surf, int radius, tuple color):
    cdef int width = surf.get_width()
    cdef int height = surf.get_height()
    
    if radius * 2 > width: radius = width // 2
    if radius * 2 > height: radius = height // 2

    surf.fill((0, 0, 0, 0))

    if radius <= 0:
        surf.fill(color)
        return

    cdef int alpha_base = color[3] if len(color) > 3 else 255
    if alpha_base == 0:
        return
        
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
    cdef float dy_sq, current_dy_dist
    
    with nogil:
        for y in prange(height, schedule='static'):
            dy = fabs(y - center_y) - inner_height_half
            current_dy_dist = fmax(dy, 0.0)
            dy_sq = current_dy_dist * current_dy_dist
            
            for x in range(width):
                dx = fabs(x - center_x) - inner_width_half
                
                if dx > 0.0 and dy > 0.0:
                    dist = sqrt(dx*dx + dy_sq)
                else:
                    dist = fmax(dx, current_dy_dist)
                
                signed_dist = dist - radius
                
                if signed_dist <= -0.5:
                    pixels3d[x, y, 0] = r
                    pixels3d[x, y, 1] = g
                    pixels3d[x, y, 2] = b
                    pixels_alpha[x, y] = <uint8_t>alpha_base
                elif signed_dist < 0.5:
                    alpha_f = 0.5 - signed_dist
                    pixels3d[x, y, 0] = r
                    pixels3d[x, y, 1] = g
                    pixels3d[x, y, 2] = b
                    pixels_alpha[x, y] = <uint8_t>(alpha_f * alpha_base)