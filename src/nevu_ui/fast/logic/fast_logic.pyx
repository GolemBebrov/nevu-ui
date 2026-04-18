# distutils: language = c++
# cython: language_level=3
# cython: boundscheck=False
# cython: wraparound=False
# cython: cdivision=True
# cython: nonecheck=False
# cython: initializedcheck=False

import nevu_ui.core.modules as md
import cython
cimport cython
from cpython.list cimport PyList_GET_SIZE, PyList_GET_ITEM
from cpython.tuple cimport PyTuple_GET_SIZE, PyTuple_GET_ITEM
from cpython.object cimport PyObject, PyObject_CallFunctionObjArgs
import numpy as np
cimport numpy as np
from nevu_ui.core.state import nevu_state
from nevu_ui.fast.nvrect.nvrect cimport NvRect
from libc.math cimport round as c_round
from nevu_ui.fast.nevucobj.nevucobj cimport NevuCobject
from nevu_ui.fast.nvvector2.nvvector2 cimport NvVector2
from nevu_ui.fast.zsystem.fast_zsystem cimport ZSystem
from nevu_ui.core.enums import AnimationManagerState, AnimationType

cdef inline double _rel_corner_helper_c(double result, double c_min, double c_max, bint has_min, bint has_max) nogil:
    if has_min and result < c_min: return c_min
    if has_max and result > c_max: return c_max
    return result

cdef inline double _rel_helper_c(double num, double resize_ratio, double c_min, double c_max, bint has_min, bint has_max) nogil:
    cdef double result = num * resize_ratio
    return _rel_corner_helper_c(result, c_min, c_max, has_min, has_max)

cpdef double rel_helper(double num, double resize_ratio, double min_val, double max_val):
    cdef bint has_min = min_val != -1.0
    cdef bint has_max = max_val != -1.0
    cdef double c_min = min_val if has_min else 0.0
    cdef double c_max = max_val if has_max else 0.0
    return _rel_helper_c(num, resize_ratio, c_min, c_max, has_min, has_max)

cpdef double relm_helper(double num, double resize_ratio_x, double resize_ratio_y, double min_val, double max_val):
    cdef bint has_min = min_val != -1.0
    cdef bint has_max = max_val != -1.0
    cdef double result = num * ((resize_ratio_x + resize_ratio_y) * 0.5)
    cdef double c_min = min_val if has_min else 0.0
    cdef double c_max = max_val if has_max else 0.0
    return _rel_corner_helper_c(result, c_min, c_max, has_min, has_max)

cpdef NvVector2 mass_rel_helper(list mass, double resize_ratio_x, double resize_ratio_y, bint vector):
    if len(mass) < 2:
        raise ValueError("mass must be a sequence with two elements")
    cdef double x = _rel_helper_c(<double><object>PyList_GET_ITEM(mass, 0), resize_ratio_x, 0, 0, 0, 0)
    cdef double y = _rel_helper_c(<double><object>PyList_GET_ITEM(mass, 1), resize_ratio_y, 0, 0, 0, 0)
    return NvVector2.new(x, y)

cpdef NvVector2 vec_rel_helper(NvVector2 vec, double resize_ratio_x, double resize_ratio_y):
    cdef double x = _rel_helper_c(vec.x, resize_ratio_x, 0, 0, 0, 0)
    cdef double y = _rel_helper_c(vec.y, resize_ratio_y, 0, 0, 0, 0)
    return NvVector2.new(x, y)

cdef inline tuple _get_rect_base(double mx, double my, double rx, double ry, double sx, double sy):
    return (mx, my, sx * rx, sy * ry)

cdef NvRect get_nvrect_helper(NvVector2 master_coordinates, NvVector2 resize_ratio, NvVector2 size):
    return NvRect.from_nvvector(master_coordinates, size._mul_vector(resize_ratio))

cpdef tuple get_rect_helper(NvVector2 master_coordinates, NvVector2 resize_ratio, NvVector2 size):
    return _get_rect_base(master_coordinates.x, master_coordinates.y, resize_ratio.x, resize_ratio.y, size.x, size.y)

cpdef get_rect_helper_pygame(NvVector2 master_coordinates, NvVector2 resize_ratio, NvVector2 size):
    return md.pygame.Rect(_get_rect_base(master_coordinates.x, master_coordinates.y, resize_ratio.x, resize_ratio.y, size.x, size.y))

cdef inline tuple _get_rect_base_cached(double mx, double my, double csx, double csy): return (mx, my, csx, csy)

cpdef tuple get_rect_helper_cached(NvVector2 master_coordinates, NvVector2 csize):
    return _get_rect_base_cached(master_coordinates.x, master_coordinates.y, csize.x, csize.y)

cpdef get_rect_helper_cached_pygame(NvVector2 master_coordinates, NvVector2 csize):
    return md.pygame.Rect(_get_rect_base_cached(master_coordinates.x, master_coordinates.y, csize.x, csize.y))

cpdef void logic_update_helper (
    NvVector2 master_coordinates,
    NvVector2 dr_coordinates_old,
    ZSystem z_system):
    with nogil: # type: ignore
        if master_coordinates.x != dr_coordinates_old.x or master_coordinates.y != dr_coordinates_old.y:
            z_system.c_mark_dirty()
            dr_coordinates_old.x = master_coordinates.x
            dr_coordinates_old.y = master_coordinates.y

cpdef void _light_update_helper(
    list items,
    list cached_coordinates,
    NvVector2 coordinatesMW,
    NvVector2 add_vector,
    ):
    cdef Py_ssize_t n_items = PyList_GET_SIZE(items)
    
    cdef NevuCobject item 
    
    cdef NvVector2 coords, anim_coords, coordinates, correct_coords

    cdef object raw_anim_val, animation_manager
    cdef int animation_manager_state

    cdef Py_ssize_t i

    for i in range(n_items):
        item = <NevuCobject>PyList_GET_ITEM(items, i)
        coords = <NvVector2>PyList_GET_ITEM(cached_coordinates, i)

        animation_manager = item.animation_manager
        animation_manager_state = <int>animation_manager.state.value # type: ignore
        if not(animation_manager_state == 3 or animation_manager_state == 4):
            raw_anim_val = animation_manager.get_animation_value(AnimationType.Position) # type: ignore
        else:
            raw_anim_val = None
        if raw_anim_val is None:
            coordinates = coords._add(add_vector)
        else:
            anim_coords = <NvVector2>raw_anim_val
            correct_coords = coords._add(item.rel(anim_coords))
            coordinates = correct_coords._add(add_vector) # type: ignore

        item.set_coordinates(coordinates)
        item.absolute_coordinates = coordinates._add(coordinatesMW)
        item.update() # type: ignore

cpdef bint collide_horizontal(NvVector2 r1_tl, NvVector2 r1_br, NvVector2 r2_tl, NvVector2 r2_br):
    return r1_tl.x < r2_br.x and r1_br.x > r2_tl.x

cpdef bint collide_vertical(NvVector2 r1_tl, NvVector2 r1_br, NvVector2 r2_tl, NvVector2 r2_br):
    return r1_tl.y < r2_br.y and r1_br.y > r2_tl.y

cpdef bint collide_vector(NvVector2 r1_tl, NvVector2 r1_br, NvVector2 r2_tl, NvVector2 r2_br):
    return (r1_tl.x < r2_br.x and r1_br.x > r2_tl.x) and (r1_tl.y < r2_br.y and r1_br.y > r2_tl.y)

cdef inline get_item_abs_coords(NevuCobject layout, NevuCobject item):
    return item.coordinates + layout.first_parent_menu.absolute_coordinates 
    

cpdef _very_light_update_helper(
    list items,
    list cached_coordinates,
    NvVector2 add_vector,
    NevuCobject layout
    ):

    cdef Py_ssize_t n = PyList_GET_SIZE(items)
    cdef NevuCobject item
    cdef NvVector2 coords, res
    cdef Py_ssize_t i = 0

    while i < n:
        item = <NevuCobject>PyList_GET_ITEM(items, i)
        coords = <NvVector2>PyList_GET_ITEM(cached_coordinates, i)
        
        res = coords._sub(add_vector)
        
        item.set_coordinates(res)
        item.absolute_coordinates = get_item_abs_coords(layout, item)
        i += 1

cdef inline start_item(NevuCobject item, NevuCobject layout):
    if hasattr(item , "first_parent_menu"):
        #This shit check checks for LayoutType :D
        item._connect_to_layout(layout) # type: ignore
    if layout.booted == False:  return
    item._wait_mode = False # type: ignore
    item._init_start() # type: ignore

cpdef void draw_widgets_optimized(
    list items,
    object draw_widget_func,
    NevuCobject layout,
):
    cdef Py_ssize_t n = PyList_GET_SIZE(items) 
    cdef NevuCobject item
    cdef Py_ssize_t i = 0
    while i < n:
        item = <NevuCobject>PyList_GET_ITEM(items, i)
        if not item._visible: i+=1; continue
        if not item.booted:
            item.booted = True # type: ignore
            item._boot_up() # type: ignore
            start_item(item, layout)
        draw_widget_func(item) # type: ignore
        i += 1

cpdef void rl_predraw_widgets(
    list items,
    type layout_type,
    type widget_type,
):
    cdef Py_ssize_t n = PyList_GET_SIZE(items)
    cdef NevuCobject item
    cdef Py_ssize_t i = 0
    while i < n:
        item = <NevuCobject>PyList_GET_ITEM(items, i)
        if not item._visible: i+=1;continue
        if isinstance(item, layout_type):
            item._rl_predraw_widgets() # type: ignore
        elif isinstance(item, widget_type):
            if item._changed: item.draw() # type: ignore
        i += 1

def fast_cycle_range(object func not None, Py_ssize_t start, Py_ssize_t end, Py_ssize_t step):
    cdef Py_ssize_t i = start
    cdef object f = func
    if step == 0:
        raise ValueError("step must not be 0")
    if step > 0:
        while i < end:
            f()
            i += step
    else:
        while i > end:
            f()
            i += step

def fast_cycle_list(func, list items not None):
    cdef Py_ssize_t n = PyList_GET_SIZE(items)
    cdef Py_ssize_t i
    cdef object item
    cdef object call_method = func.__call__
    
    for i in range(n):
        item = <object>PyList_GET_ITEM(items, i)
        call_method(item)

def fast_cycle_tuple(func, tuple items not None):
    cdef Py_ssize_t n = PyTuple_GET_SIZE(items)
    cdef Py_ssize_t i
    for i in range(n):
        item = <object>PyTuple_GET_ITEM(items, i)
        func(item)