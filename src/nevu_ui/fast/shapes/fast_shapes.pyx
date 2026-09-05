# distutils: language = c++
# distutils: extra_compile_args = -fopenmp
# distutils: extra_link_args = -fopenmp
# cython: language_level=3
# cython: boundscheck=False
# cython: wraparound=False
# cython: cdivision=True
# cython: nonecheck=False
# cython: initializedcheck=False

cimport cython
from libc.stdint cimport uint8_t
from cython.parallel cimport prange

cdef extern from "math.h":
    float sqrtf(float) nogil
    float fabsf(float) nogil
    float fmaxf(float, float) nogil
    float fminf(float, float) nogil
    float ceilf(float) nogil

cdef str pygame_3 = "3"
cdef str pygame_A = "A"

cpdef void transform_into_outlined_rounded_rect(object surf, object radii_input, float stroke_width, tuple color, object background_color=None):
    cdef int w = surf.get_width()
    cdef int h = surf.get_height()
    cdef float half_width = stroke_width / 2.0

    cdef float r_tl, r_tr, r_br, r_bl

    cdef type radii_type = type(radii_input)

    if radii_type is int or radii_type is float:
        r_tl = r_tr = r_br = r_bl = <float>radii_input
    elif len(radii_input) is 4:
        r_tl = <float>radii_input[0]
        r_tr = <float>radii_input[1]
        r_br = <float>radii_input[2]
        r_bl = <float>radii_input[3]
    else:
        r_tl = r_tr = r_br = r_bl = 0.0

    cdef uint8_t[:, :, :] pixels3d = surf.get_view(pygame_3)
    cdef uint8_t[:, :] pixels_alpha = surf.get_view(pygame_A)

    cdef int alpha_base = color[3] if len(color) > 3 else 255
    cdef uint8_t r = color[0]
    cdef uint8_t g = color[1]
    cdef uint8_t b = color[2]

    cdef bint has_bg = background_color is not None
    cdef uint8_t bg_r = 0, bg_g = 0, bg_b = 0, bg_a = 0
    cdef float bg_alpha_mult = 0.0

    if has_bg:
        bg_r = background_color[0]
        bg_g = background_color[1]
        bg_b = background_color[2]
        bg_a = background_color[3] if len(background_color) > 3 else 255
        bg_alpha_mult = bg_a / 255.0

    if alpha_base is 0 and not has_bg:
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

    r_tl = fmaxf(r_tl - half_width, 0.0)
    r_tr = fmaxf(r_tr - half_width, 0.0)
    r_br = fmaxf(r_br - half_width, 0.0)
    r_bl = fmaxf(r_bl - half_width, 0.0)

    if has_bg:
        with nogil:
            for y in prange(h, schedule='static'):
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
            for y in prange(h, schedule='static'):
                py = y - center_y
                qy_base = fabsf(py) - box_half_h

                if py > 0.0:
                    r_right = r_br
                    r_left = r_bl
                else:
                    r_right = r_tr
                    r_left = r_tl

                for x in prange(w, schedule='static'):
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

    cdef uint8_t[:, :, :] pixels3d = surf.get_view('3')
    cdef uint8_t[:, :] pixels_alpha = surf.get_view('A')

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
            for y in prange(<int>r_tl, schedule="static"):
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
            for y in prange(<int>r_tr, schedule="static"):
                py = y - center_y
                qy_base = fabsf(py) - box_half_h
                for x in prange(width - <int>r_tr, width, schedule="static"):
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
            for y in prange(height - <int>r_bl, height, schedule="static"):
                py = y - center_y
                qy_base = fabsf(py) - box_half_h
                for x in prange(<int>r_bl, schedule="static"):
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
            for y in prange(height - <int>r_br, height, schedule="static"):
                py = y - center_y
                qy_base = fabsf(py) - box_half_h
                for x in prange(width - <int>r_br, width, schedule="static"):
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


@cython.boundscheck(False)
@cython.wraparound(False)
@cython.cdivision(True)
cpdef void draw_sdf_line(object surf, object pos_from, object pos_to, float width, float border_radius, tuple color):
    cdef int surf_w = surf.get_width()
    cdef int surf_h = surf.get_height()

    cdef float x1 = <float>pos_from[0]
    cdef float y1 = <float>pos_from[1]
    cdef float x2 = <float>pos_to[0]
    cdef float y2 = <float>pos_to[1]

    cdef int alpha_base = color[3] if len(color) > 3 else 255
    if alpha_base == 0 or width <= 0.0:
        return

    cdef uint8_t r = color[0]
    cdef uint8_t g = color[1]
    cdef uint8_t b = color[2]
    cdef float color_alpha_mult = alpha_base / 255.0

    cdef float dx_line = x2 - x1
    cdef float dy_line = y2 - y1
    cdef float length = sqrtf(dx_line * dx_line + dy_line * dy_line)

    cdef float center_x = (x1 + x2) * 0.5
    cdef float center_y = (y1 + y2) * 0.5

    cdef float half_len = length * 0.5
    cdef float half_width = width * 0.5

    cdef float r_val = border_radius
    if r_val < 0.0:
        r_val = 0.0
    if r_val > half_width:
        r_val = half_width
    if r_val > half_len and length > 0.0:
        r_val = half_len

    cdef float inner_bx = half_len - r_val
    cdef float inner_by = half_width - r_val

    cdef float ux, uy, vx, vy
    if length > 1e-5:
        ux = dx_line / length
        uy = dy_line / length
        vx = -uy
        vy = ux
    else:
        ux = 1.0
        uy = 0.0
        vx = 0.0
        vy = 1.0

    cdef float margin = half_width + 1.5
    cdef float min_x_f = (x1 if x1 < x2 else x2) - margin
    cdef float max_x_f = (x1 if x1 > x2 else x2) + margin
    cdef float min_y_f = (y1 if y1 < y2 else y2) - margin
    cdef float max_y_f = (y1 if y1 > y2 else y2) + margin

    cdef int min_x = <int>min_x_f
    cdef int max_x = <int>ceilf(max_x_f) + 1
    cdef int min_y = <int>min_y_f
    cdef int max_y = <int>ceilf(max_y_f) + 1

    if min_x < 0: min_x = 0
    if min_y < 0: min_y = 0
    if max_x > surf_w: max_x = surf_w
    if max_y > surf_h: max_y = surf_h

    if min_x >= max_x or min_y >= max_y:
        return

    cdef uint8_t[:, :, :] pixels3d = surf.get_view('3')
    cdef uint8_t[:, :] pixels_alpha = surf.get_view('A')

    cdef int x, y
    cdef float px, py, lx, ly, qx, qy
    cdef float dist_outside, dist_inside, signed_dist, sa
    cdef float orig_a, orig_r, orig_g, orig_b, total_a, inv_total_a
    cdef float out_r, out_g, out_b

    with nogil:
        for y in range(min_y, max_y):
            py = y - center_y
            for x in range(min_x, max_x):
                px = x - center_x

                lx = px * ux + py * uy
                ly = px * vx + py * vy

                qx = fabsf(lx) - inner_bx
                qy = fabsf(ly) - inner_by

                dist_outside = sqrtf(fmaxf(qx, 0.0)**2 + fmaxf(qy, 0.0)**2)
                dist_inside = fminf(fmaxf(qx, qy), 0.0)
                signed_dist = dist_outside + dist_inside - r_val

                if signed_dist >= 0.5:
                    continue

                if signed_dist <= -0.5:
                    sa = 1.0 * color_alpha_mult
                else:
                    sa = (0.5 - signed_dist) * color_alpha_mult

                if sa <= 0.0:
                    continue

                orig_a = pixels_alpha[x, y] / 255.0

                if orig_a <= 0.0:
                    pixels3d[x, y, 0] = r
                    pixels3d[x, y, 1] = g
                    pixels3d[x, y, 2] = b
                    pixels_alpha[x, y] = <uint8_t>(sa * 255.0)
                elif sa >= 1.0:
                    pixels3d[x, y, 0] = r
                    pixels3d[x, y, 1] = g
                    pixels3d[x, y, 2] = b
                    pixels_alpha[x, y] = 255
                else:
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
