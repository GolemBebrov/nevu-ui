# distutils: language = c++
# cython: language_level=3
# cython: boundscheck=False
# cython: wraparound=False
# cython: cdivision=True
# cython: nonecheck=False
# cython: initializedcheck=False

import pygame
import cython
cimport cython
import numpy as np
cimport numpy as np
from libc.math cimport round as c_round

from nevu_ui.fast.nvvector2.nvvector2 cimport NvVector2
from nevu_ui.fast.zsystem.fast_zsystem cimport ZSystem
from nevu_ui.core.enums import AnimationManagerState, AnimationType

cdef inline float _rel_corner_helper_c(float result, float c_min, float c_max, bint has_min, bint has_max) nogil:
    if has_min and result < c_min: return c_min
    if has_max and result > c_max: return c_max
    return result

cdef inline float _rel_helper_c(float num, float resize_ratio, float c_min, float c_max, bint has_min, bint has_max) nogil:
    cdef float result = c_round(num * resize_ratio)
    return _rel_corner_helper_c(result, c_min, c_max, has_min, has_max)

cpdef float rel_helper(float num, float resize_ratio, float min_val, float max_val):
    cdef bint has_min = min_val != -1.0
    cdef bint has_max = max_val != -1.0
    cdef float c_min = min_val if has_min else 0.0
    cdef float c_max = max_val if has_max else 0.0
    return _rel_helper_c(num, resize_ratio, c_min, c_max, has_min, has_max)

cpdef float relm_helper(float num, float resize_ratio_x, float resize_ratio_y, float min_val, float max_val):
    cdef bint has_min = min_val != -1.0
    cdef bint has_max = max_val != -1.0
    cdef float result = c_round(num * ((resize_ratio_x + resize_ratio_y) * 0.5))
    cdef float c_min = min_val if has_min else 0.0
    cdef float c_max = max_val if has_max else 0.0
    return _rel_corner_helper_c(result, c_min, c_max, has_min, has_max)

cpdef NvVector2 mass_rel_helper(list mass, float resize_ratio_x, float resize_ratio_y, bint vector):
    if len(mass) < 2:
        raise ValueError("mass must be a sequence with two elements")
    cdef float x = _rel_helper_c(mass[0], resize_ratio_x, 0, 0, 0, 0)
    cdef float y = _rel_helper_c(mass[1], resize_ratio_y, 0, 0, 0, 0)
    return NvVector2(x, y)

cpdef NvVector2 vec_rel_helper(NvVector2 vec, float resize_ratio_x, float resize_ratio_y):
    cdef float x = _rel_helper_c(vec.x, resize_ratio_x, 0, 0, 0, 0)
    cdef float y = _rel_helper_c(vec.y, resize_ratio_y, 0, 0, 0, 0)
    return NvVector2(x, y)

cdef inline tuple _get_rect_base(float mx, float my, float rx, float ry, float sx, float sy):
    return (mx, my, sx * rx, sy * ry)

cpdef tuple get_rect_helper(NvVector2 master_coordinates, NvVector2 resize_ratio, NvVector2 size):
    return _get_rect_base(master_coordinates.x, master_coordinates.y, resize_ratio.x, resize_ratio.y, size.x, size.y)

cpdef get_rect_helper_pygame(NvVector2 master_coordinates, NvVector2 resize_ratio, NvVector2 size):
    return pygame.Rect(_get_rect_base(master_coordinates.x, master_coordinates.y, resize_ratio.x, resize_ratio.y, size.x, size.y))

cdef inline tuple _get_rect_base_cached(float mx, float my, float csx, float csy): return (mx, my, csx, csy)

cpdef tuple get_rect_helper_cached(NvVector2 master_coordinates, NvVector2 csize):
    return _get_rect_base_cached(master_coordinates.x, master_coordinates.y, csize.x, csize.y)

cpdef get_rect_helper_cached_pygame(NvVector2 master_coordinates, NvVector2 csize):
    return pygame.Rect(_get_rect_base_cached(master_coordinates.x, master_coordinates.y, csize.x, csize.y))

cpdef logic_update_helper(
    bint optimized_dirty_rect,
    NvVector2 csize,
    NvVector2 master_coordinates,
    list dirty_rect,
    NvVector2 dr_coordinates_old,
    bint first_update,
    list first_update_functions,
    NvVector2 resize_ratio,
    ZSystem z_system
    ):

    cdef bint _first_update = first_update
    cdef NvVector2 _dr_coordinates_old = dr_coordinates_old
    cdef object anim, function
    cdef NvVector2 start, end
    cdef NvVector2 dr_coordinates_new
    cdef object rect_new, rect_old, start_rect, end_rect, total_dirty_rect
    cdef float rr_x = resize_ratio.x
    cdef float rr_y = resize_ratio.y

    dr_coordinates_new = master_coordinates
    rect_new = pygame.Rect(dr_coordinates_new.x, dr_coordinates_new.y, csize.x, csize.y)
    rect_old = pygame.Rect(_dr_coordinates_old.x, _dr_coordinates_old.y, csize.x, csize.y)
    if rect_new != rect_old:
        z_system.mark_dirty()
    
    total_dirty_rect = rect_new.union(rect_old)
    _dr_coordinates_old = dr_coordinates_new.copy()

    if _first_update:
        _first_update = False
        for function in first_update_functions:
            function()

    return _dr_coordinates_old, _first_update

cpdef _light_update_helper(
    list items,
    list cached_coordinates,
    NvVector2 coordinatesMW,
    NvVector2 add_vector,
    NvVector2 resize_ratio,
    ):
    cdef int i
    cdef int n_items = len(items)
    cdef object item
    cdef NvVector2 coords, anim_coords
    cdef NvVector2 m_coords

    m_coords = coordinatesMW

    for i in range(n_items):
        item = items[i]
        coords = cached_coordinates[i]
        anim_coords = NvVector2(item.animation_manager.get_animation_value(AnimationType.POSITION)) if item.animation_manager.get_animation_value(AnimationType.POSITION) is not None else None
        if anim_coords is None:
            item.coordinates = coords + add_vector
        else:
            correct_coords = coords + vec_rel_helper(anim_coords, resize_ratio.x, resize_ratio.y)
            item.coordinates = correct_coords + add_vector

        item.absolute_coordinates = item.coordinates + m_coords
        item.update()

cpdef bint collide_horizontal(NvVector2 r1_tl, NvVector2 r1_br, NvVector2 r2_tl, NvVector2 r2_br):
    return r1_tl.x < r2_br.x and r1_br.x > r2_tl.x

cpdef bint collide_vertical(NvVector2 r1_tl, NvVector2 r1_br, NvVector2 r2_tl, NvVector2 r2_br):
    return r1_tl.y < r2_br.y and r1_br.y > r2_tl.y

cpdef bint collide_vector(NvVector2 r1_tl, NvVector2 r1_br, NvVector2 r2_tl, NvVector2 r2_br):
    return (r1_tl.x < r2_br.x and r1_br.x > r2_tl.x) and (r1_tl.y < r2_br.y and r1_br.y > r2_tl.y)

cpdef _very_light_update_helper(
    list items,
    list cached_coordinates,
    NvVector2 add_vector,
    object _get_item_master_coordinates
    ):

    cdef Py_ssize_t n = len(items)
    cdef object item
    cdef NvVector2 coords

    for i in range(n):
        item = items[i]
        coords = cached_coordinates[i]
        
        res = coords - add_vector
        
        item.coordinates = NvVector2(res.x, res.y)
        item.master_coordinates = _get_item_master_coordinates(item)