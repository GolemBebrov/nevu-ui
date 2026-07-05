# distutils: language = c++
# distutils: extra_compile_args = -fopenmp
# distutils: extra_link_args = -fopenmp
# cython: language_level=3
# cython: boundscheck=False
# cython: wraparound=False
# cython: cdivision=True
# cython: nonecheck=False
# cython: initializedcheck=False

import nevu_ui.core.modules as md
import numpy as np
cimport numpy as np
cimport cython
from cython.parallel import prange
from functools import lru_cache
from libc.string cimport memcpy

cdef extern from "math.h":
    float sqrtf(float) nogil
    float fabsf(float) nogil
    float fmaxf(float, float) nogil
    float fminf(float, float) nogil
    float ceilf(float) nogil

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

    cdef object surf = md.pygame.Surface((w, h), md.pygame.SRCALPHA)
    surf.fill((0, 0, 0, 0))

    cdef uint8_t[:, :, :] pixels3d = md.pygame.surfarray.pixels3d(surf)
    cdef uint8_t[:, :] pixels_alpha = md.pygame.surfarray.pixels_alpha(surf)

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

    cdef int sw = <int>ceilf(width)
    cdef int r_val = radius

    with nogil:
        for y in range(sw):
            for x in range(r_val, w - r_val):
                pixels3d[x, y, 0] = r
                pixels3d[x, y, 1] = g
                pixels3d[x, y, 2] = b
                pixels_alpha[x, y] = alpha_base

        for y in range(h - sw, h):
            for x in range(r_val, w - r_val):
                pixels3d[x, y, 0] = r
                pixels3d[x, y, 1] = g
                pixels3d[x, y, 2] = b
                pixels_alpha[x, y] = alpha_base

        for y in range(r_val, h - r_val):
            for x in range(sw):
                pixels3d[x, y, 0] = r
                pixels3d[x, y, 1] = g
                pixels3d[x, y, 2] = b
                pixels_alpha[x, y] = alpha_base

        for y in range(r_val, h - r_val):
            for x in range(w - sw, w):
                pixels3d[x, y, 0] = r
                pixels3d[x, y, 1] = g
                pixels3d[x, y, 2] = b
                pixels_alpha[x, y] = alpha_base

    cdef int box_size = radius + sw
    if box_size > w // 2: box_size = w // 2
    if box_size > h // 2: box_size = h // 2

    with nogil:
        for y in range(box_size):
            dy = fabsf(y - center_y) - centerline_h
            current_dy_dist = fmaxf(dy, 0.0)
            dy_sq = current_dy_dist * current_dy_dist
            for x in range(box_size):
                dx = fabsf(x - center_x) - centerline_w
                if dx > 0.0 and current_dy_dist > 0.0:
                    dist = sqrtf(dx*dx + dy_sq)
                else:
                    dist = fmaxf(dx, current_dy_dist)
                signed_dist = dist + fminf(fmaxf(dx, dy), 0.0) - center_radius
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

        for y in range(box_size):
            dy = fabsf(y - center_y) - centerline_h
            current_dy_dist = fmaxf(dy, 0.0)
            dy_sq = current_dy_dist * current_dy_dist
            for x in range(w - box_size, w):
                dx = fabsf(x - center_x) - centerline_w
                if dx > 0.0 and current_dy_dist > 0.0:
                    dist = sqrtf(dx*dx + dy_sq)
                else:
                    dist = fmaxf(dx, current_dy_dist)
                signed_dist = dist + fminf(fmaxf(dx, dy), 0.0) - center_radius
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

        for y in range(h - box_size, h):
            dy = fabsf(y - center_y) - centerline_h
            current_dy_dist = fmaxf(dy, 0.0)
            dy_sq = current_dy_dist * current_dy_dist
            for x in range(box_size):
                dx = fabsf(x - center_x) - centerline_w
                if dx > 0.0 and current_dy_dist > 0.0:
                    dist = sqrtf(dx*dx + dy_sq)
                else:
                    dist = fmaxf(dx, current_dy_dist)
                signed_dist = dist + fminf(fmaxf(dx, dy), 0.0) - center_radius
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

        for y in range(h - box_size, h):
            dy = fabsf(y - center_y) - centerline_h
            current_dy_dist = fmaxf(dy, 0.0)
            dy_sq = current_dy_dist * current_dy_dist
            for x in range(w - box_size, w):
                dx = fabsf(x - center_x) - centerline_w
                if dx > 0.0 and current_dy_dist > 0.0:
                    dist = sqrtf(dx*dx + dy_sq)
                else:
                    dist = fmaxf(dx, current_dy_dist)
                signed_dist = dist + fminf(fmaxf(dx, dy), 0.0) - center_radius
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

    return surf


@cython.boundscheck(False)
@cython.wraparound(False)
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

    cdef float min_dim = (width if width < height else height) * 0.5
    if r_tl > min_dim: r_tl = min_dim
    if r_tr > min_dim: r_tr = min_dim
    if r_br > min_dim: r_br = min_dim
    if r_bl > min_dim: r_bl = min_dim

    cdef object surf = md.pygame.Surface((width, height), md.pygame.SRCALPHA)

    cdef int alpha_base = color[3] if len(color) > 3 else 255
    if alpha_base == 0:
        surf.fill((0, 0, 0, 0))
        return surf

    surf.fill(color)

    cdef uint8_t[:, :, :] pixels3d = md.pygame.surfarray.pixels3d(surf)
    cdef uint8_t[:, :] pixels_alpha = md.pygame.surfarray.pixels_alpha(surf)

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
    cdef float qy_base

    with nogil:
        if r_tl > 0.0:
            current_r = r_tl
            for y in range(<int>r_tl):
                py = y - center_y
                qy_base = fabsf(py) - half_h
                for x in range(<int>r_tl):
                    px = x - center_x
                    qx = fabsf(px) - half_w + current_r
                    qy = qy_base + current_r
                    dist_outside = sqrtf(fmaxf(qx, 0.0)**2 + fmaxf(qy, 0.0)**2)
                    dist_inside = fminf(fmaxf(qx, qy), 0.0)
                    signed_dist = dist_outside + dist_inside - current_r
                    if signed_dist >= 0.5:
                        pixels_alpha[x, y] = 0
                    elif signed_dist > -0.5:
                        alpha_f = 0.5 - signed_dist
                        pixels_alpha[x, y] = <uint8_t>(alpha_f * alpha_base)

        if r_tr > 0.0:
            current_r = r_tr
            for y in range(<int>r_tr):
                py = y - center_y
                qy_base = fabsf(py) - half_h
                for x in range(width - <int>r_tr, width):
                    px = x - center_x
                    qx = fabsf(px) - half_w + current_r
                    qy = qy_base + current_r
                    dist_outside = sqrtf(fmaxf(qx, 0.0)**2 + fmaxf(qy, 0.0)**2)
                    dist_inside = fminf(fmaxf(qx, qy), 0.0)
                    signed_dist = dist_outside + dist_inside - current_r
                    if signed_dist >= 0.5:
                        pixels_alpha[x, y] = 0
                    elif signed_dist > -0.5:
                        alpha_f = 0.5 - signed_dist
                        pixels_alpha[x, y] = <uint8_t>(alpha_f * alpha_base)

        if r_bl > 0.0:
            current_r = r_bl
            for y in range(height - <int>r_bl, height):
                py = y - center_y
                qy_base = fabsf(py) - half_h
                for x in range(<int>r_bl):
                    px = x - center_x
                    qx = fabsf(px) - half_w + current_r
                    qy = qy_base + current_r
                    dist_outside = sqrtf(fmaxf(qx, 0.0)**2 + fmaxf(qy, 0.0)**2)
                    dist_inside = fminf(fmaxf(qx, qy), 0.0)
                    signed_dist = dist_outside + dist_inside - current_r
                    if signed_dist >= 0.5:
                        pixels_alpha[x, y] = 0
                    elif signed_dist > -0.5:
                        alpha_f = 0.5 - signed_dist
                        pixels_alpha[x, y] = <uint8_t>(alpha_f * alpha_base)

        if r_br > 0.0:
            current_r = r_br
            for y in range(height - <int>r_br, height):
                py = y - center_y
                qy_base = fabsf(py) - half_h
                for x in range(width - <int>r_br, width):
                    px = x - center_x
                    qx = fabsf(px) - half_w + current_r
                    qy = qy_base + current_r
                    dist_outside = sqrtf(fmaxf(qx, 0.0)**2 + fmaxf(qy, 0.0)**2)
                    dist_inside = fminf(fmaxf(qx, qy), 0.0)
                    signed_dist = dist_outside + dist_inside - current_r
                    if signed_dist >= 0.5:
                        pixels_alpha[x, y] = 0
                    elif signed_dist > -0.5:
                        alpha_f = 0.5 - signed_dist
                        pixels_alpha[x, y] = <uint8_t>(alpha_f * alpha_base)

    return surf

cpdef void transform_into_outlined_rounded_rect(object surf, object radii_input, float stroke_width, tuple color, object background_color=None):
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

    cdef uint8_t[:, :, :] pixels3d = md.pygame.surfarray.pixels3d(surf)
    cdef uint8_t[:, :] pixels_alpha = md.pygame.surfarray.pixels_alpha(surf)

    cdef int alpha_base = color[3] if len(color) > 3 else 255
    cdef uint8_t r = color[0]
    cdef uint8_t g = color[1]
    cdef uint8_t b = color[2]

    cdef int has_bg = 1 if background_color is not None else 0
    cdef uint8_t bg_r = 0, bg_g = 0, bg_b = 0, bg_a = 0
    cdef float bg_alpha_mult = 0.0

    if has_bg:
        bg_r = background_color[0]
        bg_g = background_color[1]
        bg_b = background_color[2]
        bg_a = background_color[3] if len(background_color) > 3 else 255
        bg_alpha_mult = bg_a / 255.0

    if alpha_base == 0 and not has_bg:
        return

    cdef float stroke_alpha_mult = alpha_base / 255.0

    cdef float center_x = (w - 1) * 0.5
    cdef float center_y = (h - 1) * 0.5

    cdef float box_half_w = (w - stroke_width) * 0.5
    cdef float box_half_h = (h - stroke_width) * 0.5

    cdef int x, y
    cdef float px, py
    cdef float current_r
    cdef float qx, qy
    cdef float dist_outside, dist_inside
    cdef float signed_dist, dist_from_edge

    cdef float sa, ba_eff, total_a, out_r, out_g, out_b, inv_total_a
    cdef float orig_a, orig_r, orig_g, orig_b

    cdef float qy_base
    cdef float r_right, r_left

    if has_bg:
        with nogil:
            for y in range(h):
                py = y - center_y
                qy_base = fabsf(py) - box_half_h

                if py > 0.0:
                    r_right = r_br
                    r_left = r_bl
                else:
                    r_right = r_tr
                    r_left = r_tl

                for x in range(w):
                    px = x - center_x

                    if px > 0.0:
                        current_r = r_right
                    else:
                        current_r = r_left

                    qx = fabsf(px) - box_half_w + current_r
                    qy = qy_base + current_r

                    dist_outside = sqrtf(fmaxf(qx, 0.0)**2 + fmaxf(qy, 0.0)**2)
                    dist_inside = fminf(fmaxf(qx, qy), 0.0)

                    signed_dist = dist_outside + dist_inside - current_r

                    if signed_dist > half_width + 0.5:
                        pixels_alpha[x, y] = 0
                        continue

                    dist_from_edge = fabsf(signed_dist)

                    sa = 0.5 - (dist_from_edge - half_width)
                    sa = fminf(fmaxf(sa, 0.0), 1.0) * stroke_alpha_mult

                    ba_eff = half_width - signed_dist
                    ba_eff = fminf(fmaxf(ba_eff, 0.0), 1.0) * bg_alpha_mult

                    total_a = sa + ba_eff * (1.0 - sa)
                    if total_a > 0.0:
                        inv_total_a = 1.0 / total_a
                        out_r = (r * sa + bg_r * ba_eff * (1.0 - sa)) * inv_total_a
                        out_g = (g * sa + bg_g * ba_eff * (1.0 - sa)) * inv_total_a
                        out_b = (b * sa + bg_b * ba_eff * (1.0 - sa)) * inv_total_a

                        pixels3d[x, y, 0] = <uint8_t>out_r
                        pixels3d[x, y, 1] = <uint8_t>out_g
                        pixels3d[x, y, 2] = <uint8_t>out_b

                        if total_a >= 1.0:
                            pixels_alpha[x, y] = 255
                        else:
                            pixels_alpha[x, y] = <uint8_t>(total_a * 255.0)
                    else:
                        pixels_alpha[x, y] = 0
    else:
        with nogil:
            for y in range(h):
                py = y - center_y
                qy_base = fabsf(py) - box_half_h

                if py > 0.0:
                    r_right = r_br
                    r_left = r_bl
                else:
                    r_right = r_tr
                    r_left = r_tl

                for x in range(w):
                    px = x - center_x

                    if px > 0.0:
                        current_r = r_right
                    else:
                        current_r = r_left

                    qx = fabsf(px) - box_half_w + current_r
                    qy = qy_base + current_r

                    dist_outside = sqrtf(fmaxf(qx, 0.0)**2 + fmaxf(qy, 0.0)**2)
                    dist_inside = fminf(fmaxf(qx, qy), 0.0)

                    signed_dist = dist_outside + dist_inside - current_r

                    if signed_dist > half_width + 0.5:
                        pixels_alpha[x, y] = 0
                        continue

                    dist_from_edge = fabsf(signed_dist)

                    sa = 0.5 - (dist_from_edge - half_width)
                    sa = fminf(fmaxf(sa, 0.0), 1.0) * stroke_alpha_mult

                    if signed_dist < -(half_width + 0.5):
                        continue

                    if sa > 0.0:
                        if signed_dist > 0.0:
                            pixels3d[x, y, 0] = r
                            pixels3d[x, y, 1] = g
                            pixels3d[x, y, 2] = b
                            if sa >= 1.0:
                                pixels_alpha[x, y] = <uint8_t>alpha_base
                            else:
                                pixels_alpha[x, y] = <uint8_t>(sa * 255.0)
                        else:
                            if sa >= 1.0:
                                pixels3d[x, y, 0] = r
                                pixels3d[x, y, 1] = g
                                pixels3d[x, y, 2] = b
                                pixels_alpha[x, y] = <uint8_t>alpha_base
                            else:
                                orig_a = pixels_alpha[x, y] / 255.0
                                orig_r = pixels3d[x, y, 0]
                                orig_g = pixels3d[x, y, 1]
                                orig_b = pixels3d[x, y, 2]

                                total_a = sa + orig_a * (1.0 - sa)
                                if total_a > 0.0:
                                    inv_total_a = 1.0 / total_a
                                    out_r = (r * sa + orig_r * orig_a * (1.0 - sa)) * inv_total_a
                                    out_g = (g * sa + orig_g * orig_a * (1.0 - sa)) * inv_total_a
                                    out_b = (b * sa + orig_b * orig_a * (1.0 - sa)) * inv_total_a

                                    pixels3d[x, y, 0] = <uint8_t>out_r
                                    pixels3d[x, y, 1] = <uint8_t>out_g
                                    pixels3d[x, y, 2] = <uint8_t>out_b

                                    if total_a >= 1.0:
                                        pixels_alpha[x, y] = 255
                                    else:
                                        pixels_alpha[x, y] = <uint8_t>(total_a * 255.0)
                                else:
                                    pixels_alpha[x, y] = 0


@cython.boundscheck(False)
@cython.wraparound(False)
cpdef void transform_into_rounded_rect(object surf, object radii_input, object color=None):
    cdef int width = surf.get_width()
    cdef int height = surf.get_height()

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

    cdef float max_radius_w = width / 2.0
    cdef float max_radius_h = height / 2.0
    cdef float max_radius = max_radius_w if max_radius_w < max_radius_h else max_radius_h

    r_tl = fminf(fmaxf(r_tl, 0.0), max_radius)
    r_tr = fminf(fmaxf(r_tr, 0.0), max_radius)
    r_br = fminf(fmaxf(r_br, 0.0), max_radius)
    r_bl = fminf(fmaxf(r_bl, 0.0), max_radius)

    cdef int has_color = 1 if color is not None else 0
    cdef int alpha_base = 0
    cdef uint8_t r = 0, g = 0, b = 0

    if has_color:
        alpha_base = color[3] if len(color) > 3 else 255
        r = color[0]
        g = color[1]
        b = color[2]

    if r_tl <= 0.0 and r_tr <= 0.0 and r_br <= 0.0 and r_bl <= 0.0:
        if has_color:
            surf.fill(color)
        return

    if has_color and alpha_base == 0:
        surf.fill((0, 0, 0, 0))
        return

    if has_color:
        surf.fill(color)

    cdef uint8_t[:, :, :] pixels3d = md.pygame.surfarray.pixels3d(surf)
    cdef uint8_t[:, :] pixels_alpha = md.pygame.surfarray.pixels_alpha(surf)

    cdef float center_x = (width - 1) * 0.5
    cdef float center_y = (height - 1) * 0.5

    cdef float box_half_w = (width - 1) * 0.5
    cdef float box_half_h = (height - 1) * 0.5

    cdef int x, y
    cdef float px, py, current_r
    cdef float qx, qy, dist_outside, dist_inside, signed_dist, alpha_f
    cdef float qy_base

    with nogil:
        if r_tl > 0.0:
            current_r = r_tl
            for y in range(<int>r_tl):
                py = y - center_y
                qy_base = fabsf(py) - box_half_h
                for x in range(<int>r_tl):
                    px = x - center_x
                    qx = fabsf(px) - box_half_w + current_r
                    qy = qy_base + current_r
                    dist_outside = sqrtf(fmaxf(qx, 0.0)**2 + fmaxf(qy, 0.0)**2)
                    dist_inside = fminf(fmaxf(qx, qy), 0.0)
                    signed_dist = dist_outside + dist_inside - current_r
                    if signed_dist >= 0.5:
                        pixels_alpha[x, y] = 0
                    elif signed_dist > -0.5:
                        alpha_f = 0.5 - signed_dist
                        if has_color:
                            pixels_alpha[x, y] = <uint8_t>(alpha_f * alpha_base)
                        else:
                            pixels_alpha[x, y] = <uint8_t>(pixels_alpha[x, y] * alpha_f)

        if r_tr > 0.0:
            current_r = r_tr
            for y in range(<int>r_tr):
                py = y - center_y
                qy_base = fabsf(py) - box_half_h
                for x in range(width - <int>r_tr, width):
                    px = x - center_x
                    qx = fabsf(px) - box_half_w + current_r
                    qy = qy_base + current_r
                    dist_outside = sqrtf(fmaxf(qx, 0.0)**2 + fmaxf(qy, 0.0)**2)
                    dist_inside = fminf(fmaxf(qx, qy), 0.0)
                    signed_dist = dist_outside + dist_inside - current_r
                    if signed_dist >= 0.5:
                        pixels_alpha[x, y] = 0
                    elif signed_dist > -0.5:
                        alpha_f = 0.5 - signed_dist
                        if has_color:
                            pixels_alpha[x, y] = <uint8_t>(alpha_f * alpha_base)
                        else:
                            pixels_alpha[x, y] = <uint8_t>(pixels_alpha[x, y] * alpha_f)

        if r_bl > 0.0:
            current_r = r_bl
            for y in range(height - <int>r_bl, height):
                py = y - center_y
                qy_base = fabsf(py) - box_half_h
                for x in range(<int>r_bl):
                    px = x - center_x
                    qx = fabsf(px) - box_half_w + current_r
                    qy = qy_base + current_r
                    dist_outside = sqrtf(fmaxf(qx, 0.0)**2 + fmaxf(qy, 0.0)**2)
                    dist_inside = fminf(fmaxf(qx, qy), 0.0)
                    signed_dist = dist_outside + dist_inside - current_r
                    if signed_dist >= 0.5:
                        pixels_alpha[x, y] = 0
                    elif signed_dist > -0.5:
                        alpha_f = 0.5 - signed_dist
                        if has_color:
                            pixels_alpha[x, y] = <uint8_t>(alpha_f * alpha_base)
                        else:
                            pixels_alpha[x, y] = <uint8_t>(pixels_alpha[x, y] * alpha_f)

        if r_br > 0.0:
            current_r = r_br
            for y in range(height - <int>r_br, height):
                py = y - center_y
                qy_base = fabsf(py) - box_half_h
                for x in range(width - <int>r_br, width):
                    px = x - center_x
                    qx = fabsf(px) - box_half_w + current_r
                    qy = qy_base + current_r
                    dist_outside = sqrtf(fmaxf(qx, 0.0)**2 + fmaxf(qy, 0.0)**2)
                    dist_inside = fminf(fmaxf(qx, qy), 0.0)
                    signed_dist = dist_outside + dist_inside - current_r
                    if signed_dist >= 0.5:
                        pixels_alpha[x, y] = 0
                    elif signed_dist > -0.5:
                        alpha_f = 0.5 - signed_dist
                        if has_color:
                            pixels_alpha[x, y] = <uint8_t>(alpha_f * alpha_base)
                        else:
                            pixels_alpha[x, y] = <uint8_t>(pixels_alpha[x, y] * alpha_f)


@lru_cache(maxsize=256)
def _get_cached_rounded_rect_surface(tuple size, tuple radii, tuple color):
    return _create_rounded_rect_surface_optimized(size, radii, color)

def create_rounded_rect_surface(size, radii_input, color):
    if isinstance(radii_input, list):
        radii_input = tuple(radii_input)
    return _get_cached_rounded_rect_surface(size, radii_input, color)

@lru_cache(maxsize=256)
def _get_cached_outlined_rounded_rect_sdf(tuple size, int radius, float width, tuple color):
    return _create_outlined_rounded_rect_sdf(size, radius, width, color)

def create_outlined_rounded_rect_sdf(size, radius, width, color):
    return _get_cached_outlined_rounded_rect_sdf(size, radius, width, color)
