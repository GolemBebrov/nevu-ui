import pygame
from .utils import NvVector2 as Vector2
from .animations import AnimationManagerState, AnimationType

import cython
cimport cython

@cython.boundscheck(False)
@cython.wraparound(False)
cpdef logic_update_helper(
    bint optimized_dirty_rect,
    object animation_manager,
    object get_rect_opt_func, 
    object rel_func,         
    object csize,
    object master_coordinates,
    list dirty_rect,

    dr_coordinates_old,
    bint first_update,
    list first_update_functions,
    ):

    cdef bint _first_update = first_update
    cdef object _dr_coordinates_old = dr_coordinates_old

    if not optimized_dirty_rect:
        if animation_manager.state not in [AnimationManagerState.IDLE, AnimationManagerState.ENDED] and \
           animation_manager.current_animations.get(AnimationType.POSITION):
            anim = animation_manager.current_animations[AnimationType.POSITION]
            coordinates = get_rect_opt_func(without_animation=True).topleft
            start = rel_func(anim.start)
            end = rel_func(anim.end)
            start_rect = pygame.Rect(
                coordinates[0] + start[0],
                coordinates[1] + start[1],
                *csize)

            end_rect = pygame.Rect(
                coordinates[0] + end[0],
                coordinates[1] + end[1],
                *csize)

            total_dirty_rect = start_rect.union(end_rect)
            dirty_rect.append(total_dirty_rect)
    else:
        dr_coordinates_new = master_coordinates
        rect_new = pygame.Rect(*dr_coordinates_new, *csize)
        rect_old = pygame.Rect(*_dr_coordinates_old, *csize)
        total_dirty_rect = rect_new.union(rect_old)
        dirty_rect.append(total_dirty_rect)
        _dr_coordinates_old = dr_coordinates_new.copy()

    if _first_update:
        _first_update = False
        for function in first_update_functions: function()

    return _dr_coordinates_old, _first_update

@cython.boundscheck(False)
@cython.wraparound(False)
cpdef object _light_update_helper(

    list items,
    list cached_coordinates,
    object first_parent_menu,
    object relx_func,
    object rely_func,

    int add_x,
    int add_y
    ):


    cdef int i, n_items
    cdef object item
    cdef object coords
    cdef list anim_coords, last_events
    cdef object item_coordinates, item_master_coordinates

    n_items = len(items)

    if cached_coordinates is None or items is None or len(items) != len(cached_coordinates): 
        return

    for i in range(len(items)):
        item = items[i]
        coords = cached_coordinates[i]
        anim_coords = item.animation_manager.get_animation_value(AnimationType.POSITION)
        anim_coords = [0,0] if anim_coords is None else anim_coords
        item.coordinates = Vector2([coords[0] + relx_func(anim_coords[0]) + add_x,
                                    coords[1] + rely_func(anim_coords[1]) + add_y])
        item.master_coordinates = Vector2([item.coordinates[0] + first_parent_menu.coordinatesMW[0],
                                           item.coordinates[1] + first_parent_menu.coordinatesMW[1]])
        last_events = first_parent_menu.window.last_events if first_parent_menu.window else []
        item.update(last_events)


cdef inline float _rel_corner_helper(float result, float c_min, float c_max, bint has_min, bint has_max):
    if has_min and result < c_min:
        return c_min
    if has_max and result > c_max:
        return c_max
    return result

@cython.boundscheck(False)
@cython.wraparound(False)
cpdef float relx_helper(float num, float resize_ratio_x, object min_val, object max_val):

    cdef float result, c_min, c_max
    cdef bint has_min = min_val is not None
    cdef bint has_max = max_val is not None

    result = round(num * resize_ratio_x)

    c_min = min_val if has_min else 0.0
    c_max = max_val if has_max else 0.0

    # Вызываем нашу быструю C-функцию
    return _rel_corner_helper(result, c_min, c_max, has_min, has_max)

@cython.boundscheck(False)
@cython.wraparound(False)
cpdef float rely_helper(float num, float resize_ratio_y, object min_val, object max_val):
    cdef float result, c_min, c_max
    cdef bint has_min = min_val is not None
    cdef bint has_max = max_val is not None
    result = round(num * resize_ratio_y)
    c_min = min_val if has_min else 0.0
    c_max = max_val if has_max else 0.0
    return _rel_corner_helper(result, c_min, c_max, has_min, has_max)

@cython.boundscheck(False)
@cython.wraparound(False)
cpdef float relm_helper(float num, float resize_ratio_x, float resize_ratio_y, object min_val, object max_val):
    cdef float result, c_min, c_max
    cdef bint has_min = min_val is not None
    cdef bint has_max = max_val is not None
    result = round(num * ((resize_ratio_x + resize_ratio_y) / 2.0))
    c_min = min_val if has_min else 0.0
    c_max = max_val if has_max else 0.0
    return _rel_corner_helper(result, c_min, c_max, has_min, has_max)

@cython.boundscheck(False)
@cython.wraparound(False)
cpdef object rel_helper(object mass, float resize_ratio_x, float resize_ratio_y, bint vector):
    if not (hasattr(mass, '__getitem__') and len(mass) >= 2):
        raise ValueError("mass must be a sequence with two elements")
    
    cdef float x = mass[0] * resize_ratio_x
    cdef float y = mass[1] * resize_ratio_y
    
    if vector:
        return Vector2(x, y)
    else:
        return [x, y]