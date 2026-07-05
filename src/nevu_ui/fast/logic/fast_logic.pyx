# distutils: language = c++
# cython: language_level=3
# cython: boundscheck=False
# cython: wraparound=False
# cython: cdivision=True
# cython: nonecheck=False
# cython: initializedcheck=False

from cpython.object cimport PyObject, PyObject_GenericGetAttr as getattr
import nevu_ui.core.modules as md
import cython
cimport cython
from cpython.list cimport PyList_GET_SIZE, PyList_GET_ITEM, PyList_GetItemRef
from cpython.tuple cimport PyTuple_GET_SIZE, PyTuple_GET_ITEM
from cpython.object cimport PyObject, PyObject_CallFunctionObjArgs
from nevu_ui.fast.raylib.nevu_raylib cimport c_draw_nvtexture_nvvec
from nevu_ui.presentation.color import Color
cdef extern from "Python.h":
    double PyFloat_AsDouble(PyObject* obj)
    object PyObject_CallNoArgs(object func)
    object PyObject_CallMethodNoArgs(object obj, object name)
    ctypedef struct PyListObject:
        PyObject **ob_item
from nevu_ui.fast.nvrendertex.nv_render_tex cimport NvRenderTexture
from nevu_ui.core.state import nevu_state
from nevu_ui.fast.nvrect.nvrect cimport NvRect
from nevu_ui.fast.nevucobj.nevucobj cimport NevuCobject
from nevu_ui.fast.nvvector2.nvvector2 cimport NvVector2, nv_vector2_t, nv_vector2_mul_vector, nv_vector2_add, nv_vector2_sub, nv_vector2_add_triple,nv_vector2_new
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
    cdef double x = _rel_helper_c(PyFloat_AsDouble(PyList_GET_ITEM(mass, 0)), resize_ratio_x, 0, 0, 0, 0)
    cdef double y = _rel_helper_c(PyFloat_AsDouble(PyList_GET_ITEM(mass, 1)), resize_ratio_y, 0, 0, 0, 0)
    return NvVector2.new(x, y)

cpdef NvVector2 vec_rel_helper(NvVector2 vec, double resize_ratio_x, double resize_ratio_y):
    cdef double x = _rel_helper_c(vec.x, resize_ratio_x, 0, 0, 0, 0)
    cdef double y = _rel_helper_c(vec.y, resize_ratio_y, 0, 0, 0, 0)
    return NvVector2.new(x, y)

cdef inline nv_vector2_t rel_vec(nv_vector2_t vec, nv_vector2_t resize_ratio) noexcept nogil:
    return nv_vector2_mul_vector(vec, resize_ratio)

cdef inline tuple _get_rect_base(double mx, double my, double rx, double ry, double sx, double sy):
    return (mx, my, sx * rx, sy * ry)

cdef NvRect get_nvrect_helper(NvVector2 master_coordinates, NvVector2 resize_ratio, NvVector2 size):
    return NvRect.from_nv_vector_t(master_coordinates.data, nv_vector2_mul_vector(size.data, resize_ratio.data))

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
    if master_coordinates.x != dr_coordinates_old.x or master_coordinates.y != dr_coordinates_old.y:
        z_system.c_mark_dirty()
        dr_coordinates_old.x = master_coordinates.x
        dr_coordinates_old.y = master_coordinates.y

cdef inline void _light_update_helper(
    list items,
    list cached_coordinates,
    nv_vector2_t menu_vec,
    double add_x,
    double add_y
    ) noexcept:
    cdef Py_ssize_t n_items = PyList_GET_SIZE(items)
    
    cdef NevuCobject item 
    
    cdef NvVector2 coords, anim_coords
    cdef nv_vector2_t c_coords, c_anim_coords, new_coords
    cdef nv_vector2_t abs_coords

    cdef object raw_anim_val, animation_manager, anim_state

    cdef Py_ssize_t i = 0

    cdef nv_vector2_t add_vec = nv_vector2_new(add_x, add_y)
    cdef PyObject** items_ptr = (<PyListObject*>items).ob_item
    cdef PyObject** coords_ptr = (<PyListObject*>cached_coordinates).ob_item

    cdef object _pos_type = AnimationType.Position
    cdef object _state_continuous = AnimationManagerState.Continuous
    cdef object _state_ended = AnimationManagerState.Ended

    while i < n_items:
        item = <NevuCobject><void*>items_ptr[i]
        coords = <NvVector2><void*>coords_ptr[i]
        c_coords = coords.data

        animation_manager = item.animation_manager
        anim_state = animation_manager.state
        if anim_state is not _state_ended:
            raw_anim_val = animation_manager.get_animation_value(_pos_type)
            if raw_anim_val is not None:
                anim_coords = <NvVector2><void*>raw_anim_val
                c_anim_coords = anim_coords.data
                new_coords = nv_vector2_add_triple(c_coords, rel_vec(c_anim_coords, item._resize_ratio.data), add_vec)
            else:
                new_coords = nv_vector2_add(c_coords, add_vec)
        else:
            new_coords = nv_vector2_add(c_coords, add_vec)

        item.c_set_coords_xy(new_coords.x, new_coords.y)
        abs_coords = nv_vector2_add(new_coords, menu_vec)
        item.absolute_coordinates.data = abs_coords
        item.update()
        i += 1

def base_light_update(NevuCobject self, double add_x = 0, double add_y = 0 ):
    cdef list cached_coordinates, items
    cdef object first_parent_menu

    first_parent_menu = self.first_parent_menu
    cached_coordinates = self.cached_coordinates
    items = self.items
    
    cdef NvVector2 mabs_coords = <NvVector2><void*>first_parent_menu.absolute_coordinates

    _light_update_helper(
        items,
        cached_coordinates,
        mabs_coords.data,
        add_x, add_y)

cpdef bint collide_horizontal(NvVector2 r1_tl, NvVector2 r1_br, NvVector2 r2_tl, NvVector2 r2_br):
    return r1_tl.x < r2_br.x and r1_br.x > r2_tl.x

cpdef bint collide_vertical(NvVector2 r1_tl, NvVector2 r1_br, NvVector2 r2_tl, NvVector2 r2_br):
    return r1_tl.y < r2_br.y and r1_br.y > r2_tl.y

cpdef bint collide_vector(NvVector2 r1_tl, NvVector2 r1_br, NvVector2 r2_tl, NvVector2 r2_br):
    return (r1_tl.x < r2_br.x and r1_br.x > r2_tl.x) and (r1_tl.y < r2_br.y and r1_br.y > r2_tl.y)

cdef inline NvVector2 get_item_abs_coords(NevuCobject layout, NevuCobject item):
    return item.coordinates._add(<NvVector2>layout.first_parent_menu.absolute_coordinates) 

def py_get_item_abs_coords(NevuCobject layout not None, NevuCobject item not None):
    return get_item_abs_coords(layout, item)

cpdef _very_light_update_helper(
    list items,
    list cached_coordinates, 
    NvVector2 menu_vec,
    NvVector2 add_vector,
    NevuCobject layout
):
    c_very_light_update_helper(
        items,
        cached_coordinates,
        menu_vec,
        add_vector,
        layout
    )


cdef inline void c_very_light_update_helper(
    list items,
    list cached_coordinates,
    NvVector2 menu_vec,
    NvVector2 add_vector,
    NevuCobject layout
    ) noexcept:

    cdef Py_ssize_t n = PyList_GET_SIZE(items)
    
    cdef PyObject** items_ptr = (<PyListObject*>items).ob_item
    cdef PyObject** coords_ptr = (<PyListObject*>cached_coordinates).ob_item

    cdef NevuCobject item
    cdef NvVector2 coords
    cdef nv_vector2_t c_coords, c_menu_vec, c_add_vector, added_vec
    
    c_add_vector = add_vector.data
    c_menu_vec = menu_vec.data
    cdef Py_ssize_t i = 0

    while i < n:
        item = <NevuCobject><void*>items_ptr[i]
        coords = <NvVector2><void*>coords_ptr[i]
        c_coords = coords.data
        
        added_vec = nv_vector2_sub(c_coords, c_add_vector)
        
        item.c_set_coords_xy(added_vec.x, added_vec.y)
        
        item.absolute_coordinates.data = nv_vector2_add(added_vec, c_menu_vec)
        i += 1

cdef inline start_item(NevuCobject item, NevuCobject layout):
    if hasattr(item , "first_parent_menu"):
        #This shit check checks for LayoutType :D
        item._connect_to_layout(layout) # type: ignore
    if layout.booted == False:  return
    item._wait_mode = False # type: ignore
    PyObject_CallNoArgs(item._init_start) # type: ignore

ctypedef void (*DrawFuncPtr)(NevuCobject, NevuCobject, NvVector2)

cdef inline void draw_item_pygame(NevuCobject layout, NevuCobject item, NvVector2 coordinates):
    if not layout.surface: return
    #pblit(item.surface, layout.surface, coordinates.to_tuple())
    layout.surface.blit(item.surface, coordinates.to_tuple()) #type: ignore

cdef inline void draw_item_sdl(NevuCobject layout, NevuCobject item, NvVector2 coordinates):
    if not hasattr(item, '_sdl2_texture'): return
    if not item._sdl2_texture: return
    cdef object rect = md.pygame.Rect(coordinates.to_tuple(), item._csize.to_tuple())
    nevu_state.renderer.blit(item._sdl2_texture, rect) #type: ignore

_base_color_raylib = NvRect.new(255, 255, 255, 255)

cdef inline void draw_item_raylib(NevuCobject layout, NevuCobject item, NvVector2 coordinates):
    cdef NvRenderTexture rend_tex = <NvRenderTexture>item.surface
    c_draw_nvtexture_nvvec(rend_tex, coordinates, _base_color_raylib, True)

cdef inline void draw_widget_optimized_pygame(DrawFuncPtr draw_item, NevuCobject layout, NevuCobject item, type layout_type, type widget_type):
    if item.node_type == 1:
        item.draw()
        return 

    if item._changed:
        item.draw()

    if item.node_type == 0:
        draw_item(layout, item, item.coordinates)

cdef inline void draw_widget_optimized_raylib(DrawFuncPtr draw_item, NevuCobject layout, NevuCobject item, type layout_type, type widget_type):
    if item.node_type == 1:
        item.draw()
        return 

    if item.node_type == 0:
        draw_item(layout, item, item.coordinates)

cdef DrawFuncPtr _cached_draw_item = NULL
cdef bint _cached_is_raylib = False
cdef bint _draw_func_resolved = False

cdef inline void _check_draw_item():
    global _cached_draw_item, _cached_is_raylib, _draw_func_resolved
    if not _draw_func_resolved:
        dtype = nevu_state.window.renderer_type
        if dtype.pygame:
            draw_func = draw_item_pygame
        elif dtype.sdl:
            draw_func = draw_item_sdl
        elif dtype.raylib:
            draw_func = draw_item_raylib
            _cached_is_raylib = True
        _cached_draw_item = draw_func
        _draw_func_resolved = True

cpdef void draw_widgets_optimized(
    NevuCobject layout,
    list items,
    type layout_type,
    type widget_type
):
    cdef Py_ssize_t n = PyList_GET_SIZE(items) 
    cdef NevuCobject item
    cdef PyObject** items_ptr = (<PyListObject*>items).ob_item
    _check_draw_item()

    cdef Py_ssize_t i = 0
    if _cached_is_raylib:
        while i < n:
            item = <NevuCobject><void*>items_ptr[i]
            if not item._visible: i += 1; continue
            draw_widget_optimized_raylib(_cached_draw_item, layout, item, layout_type, widget_type)
            i += 1
    else:
        while i < n:
            item = <NevuCobject><void*>items_ptr[i]
            if not item._visible: i += 1; continue
            draw_widget_optimized_pygame(_cached_draw_item, layout, item, layout_type, widget_type)
            i += 1
@cython.optimize.unpack_method_calls(True)
cpdef void rl_predraw_widgets(
    list items,
    type layout_type,
    type widget_type,
):
    cdef Py_ssize_t n = PyList_GET_SIZE(items)
    cdef PyObject** items_ptr = (<PyListObject*>items).ob_item
    cdef NevuCobject item
    cdef Py_ssize_t i = 0
    while i < n:
        item = <NevuCobject><void*>items_ptr[i]
        if not item._visible: i+=1; continue
        if isinstance(item, layout_type):
            item._rl_predraw_widgets() # type: ignore
        else:
            if item._changed: 
                item.draw()
        i += 1

def fast_cycle_range(object func not None, Py_ssize_t start, Py_ssize_t end, Py_ssize_t step):
    cdef Py_ssize_t i = start
    cdef object f = func
    if step == 0:
        raise ValueError("step must not be 0")
    if step > 0:
        while i < end:
            PyObject_CallNoArgs(f)
            i += step
    else:
        while i > end:
            PyObject_CallNoArgs(f)
            i += step

def fast_cycle_list(func, list items not None):
    cdef Py_ssize_t n = PyList_GET_SIZE(items)
    cdef Py_ssize_t i
    cdef object item
    cdef object call_method = func.__call__

    for i in range(n):
        item = <object>PyList_GET_ITEM(items, i)
        call_method(item)

def fast_cycle_in_list(str func_name not None, list items not None):
    _fast_cycle_in_list(func_name, items)

cdef inline void _fast_cycle_in_list(str func_name, list items):
    cdef Py_ssize_t n = PyList_GET_SIZE(items)
    cdef Py_ssize_t i = 0
    cdef object item
    while i < n:
        item = <object>PyList_GET_ITEM(items, i)
        PyObject_CallMethodNoArgs(item, func_name)
        i += 1

def fast_cycle_tuple(func, tuple items not None):
    cdef Py_ssize_t n = PyTuple_GET_SIZE(items)
    cdef Py_ssize_t i
    for i in range(n):
        item = <object>PyTuple_GET_ITEM(items, i)
        func(item)