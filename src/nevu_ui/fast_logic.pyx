# distutils: language = c++
# cython: language_level=3
# cython: boundscheck=False
# cython: wraparound=False
# cython: cdivision=True
# cython: nonecheck=False

import pygame

import cython
cimport cython

from .utils import NvVector2 as Vector2
from .fast_nvvector2 cimport NvVector2

from .animations import (
    AnimationManagerState, AnimationType
)


cdef inline float _rel_corner_helper(float result, float c_min, float c_max, bint has_min, bint has_max):
    if has_min and result < c_min:
        return c_min
    if has_max and result > c_max:
        return c_max
    return result

@cython.boundscheck(False)
@cython.wraparound(False)
cpdef float rel_helper(float num, float resize_ratio, object min_val, object max_val):
    cdef float result, c_min, c_max
    cdef bint has_min = min_val is not None
    cdef bint has_max = max_val is not None
    result = round(num * resize_ratio)
    c_min = min_val if has_min else 0.0
    c_max = max_val if has_max else 0.0
    return _rel_corner_helper(result, c_min, c_max, has_min, has_max)

@cython.boundscheck(False)
@cython.wraparound(False)
cpdef float relm_helper(float num, float resize_ratio_x, float resize_ratio_y, object min_val, object max_val):
    cdef float result, c_min, c_max
    cdef bint has_min = min_val is not None
    cdef bint has_max = max_val is not None
    result = round(num * ((resize_ratio_x + resize_ratio_y) * 0.5))
    c_min = min_val if has_min else 0.0
    c_max = max_val if has_max else 0.0
    return _rel_corner_helper(result, c_min, c_max, has_min, has_max)

@cython.boundscheck(False)
@cython.wraparound(False)
cpdef NvVector2 mass_rel_helper(object mass, float resize_ratio_x, float resize_ratio_y, bint vector):
    if not (hasattr(mass, '__getitem__') and len(mass) >= 2):
        raise ValueError("mass must be a sequence with two elements")

    cdef float x = rel_helper(mass[0], resize_ratio_x, None, None)
    cdef float y = rel_helper(mass[1], resize_ratio_y, None, None)

    return NvVector2(x, y)

cdef inline tuple _get_rect_base(NvVector2 master_coordinates, NvVector2 resize_ratio, NvVector2 size):
    return (master_coordinates.x, master_coordinates.y, size.x * resize_ratio.x, size.y * resize_ratio.y)

cpdef tuple get_rect_helper(NvVector2 master_coordinates, NvVector2 resize_ratio, NvVector2 size):
    return _get_rect_base(master_coordinates, resize_ratio, size)

cpdef get_rect_helper_pygame(NvVector2 master_coordinates, NvVector2 resize_ratio, NvVector2 size):
    return pygame.Rect(_get_rect_base(master_coordinates, resize_ratio, size))

cdef inline tuple _get_rect_base_cached(NvVector2 master_coordinates, NvVector2 csize):
    return (master_coordinates.x, master_coordinates.y, csize.x, csize.y)

cpdef tuple get_rect_helper_cached(NvVector2 master_coordinates, NvVector2 csize):
    return _get_rect_base_cached(master_coordinates, csize)

cpdef get_rect_helper_cached_pygame(NvVector2 master_coordinates, NvVector2 csize):
    return pygame.Rect(_get_rect_base_cached(master_coordinates, csize))

@cython.boundscheck(False)
@cython.wraparound(False)
cpdef logic_update_helper(
    bint optimized_dirty_rect,
    object animation_manager,
    NvVector2 csize,
    NvVector2 master_coordinates,
    list dirty_rect,
    object dr_coordinates_old,
    bint first_update,
    list first_update_functions,
    NvVector2 resize_ratio,
    object z_system
    ):

    cdef bint _first_update = first_update
    cdef object _dr_coordinates_old = dr_coordinates_old
    cdef object anim, coordinates, start, end, total_dirty_rect, start_rect, end_rect, function
    cdef object dr_coordinates_new, rect_new, rect_old

    if not optimized_dirty_rect:
        if animation_manager.state != AnimationManagerState.IDLE and animation_manager.state != AnimationManagerState.ENDED:
            anim = animation_manager.current_animations.get(AnimationType.POSITION)
            if anim:
                coordinates = get_rect_helper_cached(master_coordinates, csize)
                start = mass_rel_helper(anim.start, resize_ratio.x, resize_ratio.y, True)
                end = mass_rel_helper(anim.end, resize_ratio.x, resize_ratio.y, True)
                start_rect = pygame.Rect(
                    coordinates[0] + start[0],
                    coordinates[1] + start[1],
                    csize[0], csize[1])

                end_rect = pygame.Rect(
                    coordinates[0] + end[0],
                    coordinates[1] + end[1],
                    csize[0], csize[1])

                total_dirty_rect = start_rect.union(end_rect)
                dirty_rect.append(total_dirty_rect)
                z_system.mark_dirty()
    else:
        dr_coordinates_new = master_coordinates
        rect_new = pygame.Rect(dr_coordinates_new[0], dr_coordinates_new[1], csize[0], csize[1])
        rect_old = pygame.Rect(_dr_coordinates_old[0], _dr_coordinates_old[1], csize[0], csize[1])
        if rect_new != rect_old:
            z_system.mark_dirty()
        total_dirty_rect = rect_new.union(rect_old)
        dirty_rect.append(total_dirty_rect)
        _dr_coordinates_old = dr_coordinates_new.copy()
        

    if _first_update:
        _first_update = False
        for function in first_update_functions:
            function()

    return _dr_coordinates_old, _first_update

@cython.boundscheck(False)
@cython.wraparound(False)
cpdef _light_update_helper(
    list items,
    list cached_coordinates,
    object first_parent_menu,
    float add_x,
    float add_y,
    NvVector2 resize_ratio
    ):

    cdef Py_ssize_t i
    cdef Py_ssize_t n_items = len(items)
    cdef object item, coords, anim_coords
    cdef list last_events
    cdef object m_coords

    if cached_coordinates is None or n_items != len(cached_coordinates):
        return

    m_coords = first_parent_menu.coordinatesMW
    last_events = first_parent_menu.window.last_events if first_parent_menu.window else []

    for i in range(n_items):
        item = items[i]
        coords = cached_coordinates[i]

        anim_coords = item.animation_manager.get_animation_value(AnimationType.POSITION)
        if anim_coords is None:
            item.coordinates = Vector2(coords[0] + add_x,
                                        coords[1] + add_y)
        else:
            item.coordinates = Vector2(coords[0] + rel_helper(anim_coords[0], resize_ratio.x, None, None) + add_x,
                                        coords[1] + rel_helper(anim_coords[1], resize_ratio.y, None, None) + add_y)

        item.master_coordinates = Vector2(item.coordinates.x + m_coords[0],
                                           item.coordinates.y + m_coords[1])
        item.update(last_events)


