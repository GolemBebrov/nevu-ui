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
from nevu_ui.fast.nvrect.nvrect cimport NvRect
from libc.math cimport round as c_round
from nevu_ui.fast.nevucobj.nevucobj cimport NevuCobject
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
    return NvVector2.new(x, y)

cpdef NvVector2 vec_rel_helper(NvVector2 vec, float resize_ratio_x, float resize_ratio_y):
    cdef float x = _rel_helper_c(vec.x, resize_ratio_x, 0, 0, 0, 0)
    cdef float y = _rel_helper_c(vec.y, resize_ratio_y, 0, 0, 0, 0)
    return NvVector2.new(x, y)

cdef inline tuple _get_rect_base(float mx, float my, float rx, float ry, float sx, float sy):
    return (mx, my, sx * rx, sy * ry)

cdef NvRect get_nvrect_helper(NvVector2 master_coordinates, NvVector2 resize_ratio, NvVector2 size):
    return NvRect.from_nvvector(master_coordinates, size._mul_vector(resize_ratio))

cpdef tuple get_rect_helper(NvVector2 master_coordinates, NvVector2 resize_ratio, NvVector2 size):
    return _get_rect_base(master_coordinates.x, master_coordinates.y, resize_ratio.x, resize_ratio.y, size.x, size.y)

cpdef get_rect_helper_pygame(NvVector2 master_coordinates, NvVector2 resize_ratio, NvVector2 size):
    return pygame.Rect(_get_rect_base(master_coordinates.x, master_coordinates.y, resize_ratio.x, resize_ratio.y, size.x, size.y))

cdef inline tuple _get_rect_base_cached(float mx, float my, float csx, float csy): return (mx, my, csx, csy)

cpdef tuple get_rect_helper_cached(NvVector2 master_coordinates, NvVector2 csize):
    return _get_rect_base_cached(master_coordinates.x, master_coordinates.y, csize.x, csize.y)

cpdef get_rect_helper_cached_pygame(NvVector2 master_coordinates, NvVector2 csize):
    return pygame.Rect(_get_rect_base_cached(master_coordinates.x, master_coordinates.y, csize.x, csize.y))

ctypedef struct NvRectStruct:
    float x
    float y
    float w
    float h

cdef inline bint is_nvrect_eq(NvRectStruct rect1, NvRectStruct rect2) nogil:
    return rect1.x == rect2.x and rect1.y == rect2.y and rect1.w == rect2.w and rect1.h == rect2.h

cpdef void logic_update_helper(
    NvVector2 csize,
    NvVector2 master_coordinates,
    NvVector2 dr_coordinates_old,
    NvVector2 resize_ratio,
    ZSystem z_system
    ):
    cdef NvRectStruct rect_new, rect_old
    with nogil:
        rect_new.x = master_coordinates.x
        rect_new.y = master_coordinates.y
        rect_new.w = csize.x
        rect_new.h = csize.y
        rect_old.x = dr_coordinates_old.x
        rect_old.y = dr_coordinates_old.y
        rect_old.w = csize.x
        rect_old.h = csize.y

        if is_nvrect_eq(rect_new, rect_old) == False:
            z_system.c_mark_dirty()
        
        dr_coordinates_old.x = master_coordinates.x
        dr_coordinates_old.y = master_coordinates.y

cpdef void _light_update_helper(
    list items,
    list cached_coordinates,
    NvVector2 coordinatesMW,
    NvVector2 add_vector,
    ):
    cdef Py_ssize_t n_items = len(items)
    
    cdef NevuCobject item 
    
    cdef NvVector2 coords, anim_coords, coordinates

    cdef object raw_anim_val

    for i in range(n_items):
        item = items[i]
        
        coords = <NvVector2>cached_coordinates[i] 
        if not(item.animation_manager.state == AnimationManagerState.IDLE or item.animation_manager.state == AnimationManagerState.ENDED):
            raw_anim_val = item.animation_manager.get_animation_value(AnimationType.POSITION)
        else:
            raw_anim_val = None
        if raw_anim_val is None:
            coordinates = coords._add(add_vector)
        else:
            if isinstance(raw_anim_val, NvVector2):
                anim_coords = <NvVector2>raw_anim_val
            else:
                anim_coords = NvVector2(raw_anim_val)
            
            correct_coords = coords._add(item.rel(anim_coords))
            coordinates = correct_coords + add_vector

        #print(item.get_param_strict("id").value)
        item.set_coordinates(coordinates)
        item.absolute_coordinates = coordinates._add(coordinatesMW)
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
    cdef NevuCobject item
    cdef NvVector2 coords, res

    for i in range(n):
        item = items[i]
        coords = <NvVector2>cached_coordinates[i]
        
        res = coords._sub(add_vector)
        
        item.set_coordinates(res)
        item.absolute_coordinates = _get_item_master_coordinates(item)