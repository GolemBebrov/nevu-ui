import pygame
from .utils import NvVector2 as Vector2
from .nevuobj import NevuObject
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
    object update_hover_state_func
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

    update_hover_state_func()
    return _dr_coordinates_old, _first_update

@cython.boundscheck(False)
@cython.wraparound(False)
cpdef object _light_update_helper(

    list items,
    list cached_coordinates,
    object first_parent_menu,
    object relx_func,

    int add_x,
    int add_y
    ):


    cdef int i, n_items
    cdef object item
    cdef object coords
    cdef list anim_coords, last_events
    cdef object item_coordinates, item_master_coordinates

    n_items = len(items)

    if cached_coordinates is None or items is None or n_items != len(cached_coordinates):
        return

    last_events = first_parent_menu.window.last_events if first_parent_menu.window else []

    for i in range(n_items):
        item = items[i]
        coords = cached_coordinates[i]

        anim_coords = item.animation_manager.get_animation_value(AnimationType.POSITION)
        
        if anim_coords is None:
            item_coordinates = Vector2(coords[0] + add_x,
                                       coords[1] + add_y)
        else:
            item_coordinates = Vector2(coords[0] + relx_func(anim_coords[0]) + add_x,
                                       coords[1] + relx_func(anim_coords[1]) + add_y)

        item.coordinates = item_coordinates

        item_master_coordinates = Vector2(item.coordinates.x + first_parent_menu.coordinatesMW[0],
                                          item.coordinates.y + first_parent_menu.coordinatesMW[1])
        item.master_coordinates = item_master_coordinates
        
        item.update(last_events)