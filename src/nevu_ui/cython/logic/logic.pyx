# distutils: language = c++
# cython: language_level=3
# cython: boundscheck=False
# cython: wraparound=False
# cython: cdivision=True
# cython: nonecheck=False
# cython: initializedcheck=False

import cython
cimport cython
from nevu_ui.cython.callbacks.callbacks cimport Callbacks
from nevu_ui.core.enums import BindType
from nevu_ui.core.state import nevu_state
from cpython.list cimport PyList_GET_SIZE, PyList_GET_ITEM
from nevu_ui.cython.surface.surface cimport _NvSurfRaylib
from cpython.object cimport PyObject
from nevu_ui.cython.raylib.raylib cimport c_draw_texture_maxopt, Texture2D
cdef extern from "Python.h":
    ctypedef struct PyListObject:
        PyObject **ob_item
from nevu_ui.core.state import nevu_state
from nevu_ui.cython.rect.rect cimport Rect
from nevu_ui.cython.nevucobject.nevucobject cimport NevuCobject
from nevu_ui.cython.vector2.vector2 cimport Vector2, nv_vector2_t, nv_vector2_mul_vector, nv_vector2_add, nv_vector2_sub, nv_vector2_add_triple,nv_vector2_new
from nevu_ui.cython.z_system.z_system cimport ZSystem
from nevu_ui.core.enums import AnimType

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

cpdef Vector2 vec_rel_helper(Vector2 vec, double resize_ratio_x, double resize_ratio_y):
    cdef double x = _rel_helper_c(vec.x, resize_ratio_x, 0, 0, 0, 0)
    cdef double y = _rel_helper_c(vec.y, resize_ratio_y, 0, 0, 0, 0)
    return Vector2.new(x, y)

cdef inline nv_vector2_t rel_vec(nv_vector2_t vec, nv_vector2_t resize_ratio) noexcept nogil:
    return nv_vector2_mul_vector(vec, resize_ratio)

cdef inline Rect get_rect(Vector2 absolute_coordinates, Vector2 ratio, Vector2 size):
    return Rect.from_nv_vector_t(absolute_coordinates.data, nv_vector2_mul_vector(size.data, ratio.data))

cpdef void check_moved(NevuCobject nevuobject):
    cdef nv_vector2_t absolute_coordinates = nevuobject.absolute_coordinates.data
    cdef nv_vector2_t dr_coordinates_old = nevuobject._dr_coordinates_old.data
    cdef ZSystem z_system
    if absolute_coordinates.x != dr_coordinates_old.x or absolute_coordinates.y != dr_coordinates_old.y:
        z_system = nevu_state.z_system
        z_system.c_mark_dirty()
        nevuobject._dr_coordinates_old.x = absolute_coordinates.x
        nevuobject._dr_coordinates_old.y = absolute_coordinates.y

cdef object _pos_type = AnimType.Position

cdef inline Vector2 c_get_absolute_coordinates(NevuCobject layout, NevuCobject item):
    return item.coordinates._add((<NevuCobject><void*>layout.first_parent_menu).absolute_coordinates)

def get_absolute_coordinates(NevuCobject layout not None, NevuCobject item not None):
    return c_get_absolute_coordinates(layout, item)

cpdef update_items(
    list items,
    list cached_coordinates,
    Vector2 menu_vec,
    Vector2 add_vector,
    NevuCobject layout,
    bint weak,
):
    c_update_items(
        items,
        cached_coordinates,
        menu_vec,
        add_vector,
        layout,
        weak
    )

cdef inline void c_update_items(
    list items,
    list cached_coordinates,
    Vector2 menu_vec,
    Vector2 add_vector,
    NevuCobject layout,
    bint weak
) noexcept:
    cdef void* item
    cdef nv_vector2_t coordinates, c_menu_vec, c_add_vector, added_vec
    cdef object animation_value

    c_add_vector = add_vector.data
    c_menu_vec = menu_vec.data
    cdef Py_ssize_t n_items = PyList_GET_SIZE(items)
    cdef Py_ssize_t n_coords = PyList_GET_SIZE(cached_coordinates)
    cdef Py_ssize_t count = n_items if n_items < n_coords else n_coords
    cdef Py_ssize_t i = 0

    while i < count:
        item = <void*>PyList_GET_ITEM(items, i)
        coordinates = (<Vector2><void*>PyList_GET_ITEM(cached_coordinates, i)).data
        added_vec = nv_vector2_sub(coordinates, c_add_vector)
        animation_value = (<NevuCobject>item).animation_manager.get(_pos_type)
        if animation_value is not None:
            added_vec = nv_vector2_add(
                added_vec,
                rel_vec((<Vector2><void*>animation_value).data, (<NevuCobject>item)._resize_ratio.data)
            )
        (<NevuCobject>item).c_set_coords_xy(added_vec.x, added_vec.y)
        (<NevuCobject>item).absolute_coordinates.data = nv_vector2_add(added_vec, c_menu_vec)
        if not weak:
            (<NevuCobject>item).update()
        i += 1

ctypedef void (*DrawFuncPtr)(NevuCobject, NevuCobject, Vector2)

cdef inline void draw_item_pygame(NevuCobject layout, NevuCobject item, Vector2 coordinates):
    if not layout.surface: return
    layout.surface.blit(item.surface, coordinates.to_tuple()) #type: ignore

cdef inline void draw_item_raylib(NevuCobject layout, NevuCobject item, Vector2 coordinates):
    c_draw_texture_maxopt(<Texture2D>(<_NvSurfRaylib>(item.surface).c_native_texture), coordinates.data, True)

cdef inline void draw_widget_optimized_pygame(DrawFuncPtr draw_item, NevuCobject layout, NevuCobject item, type layout_type, type widget_type):
    if item.node_type == 1:
        item.draw()
        return

    if item._changed:
        item.draw()

    if item.node_type == 0 and item.surface is not None:
        draw_item(layout, item, item.coordinates)

cdef inline void draw_widget_optimized_pygame_rel(DrawFuncPtr draw_item, NevuCobject layout, NevuCobject item, type layout_type, type widget_type):
    if item.node_type == 1:
        item.draw()
        return

    if item._changed:
        item.draw()

    if item.node_type == 0 and item.surface is not None:
        draw_item(layout, item, layout.coordinates + item.rel(item.coordinates))

cdef inline void draw_widget_optimized_raylib(DrawFuncPtr draw_item, NevuCobject layout, NevuCobject item, type layout_type, type widget_type):
    if item.node_type == 1:
        item.draw()
        return

    if item.node_type == 0 and item.surface is not None:
        draw_item(layout, item, item.coordinates)

cdef inline void draw_widget_optimized_raylib_rel(DrawFuncPtr draw_item, NevuCobject layout, NevuCobject item, type layout_type, type widget_type):
    if item.node_type == 1:
        item.draw()
        return

    if item.node_type == 0 and item.surface is not None:
        draw_item(layout, item, layout.coordinates + item.rel(item.coordinates))

cdef DrawFuncPtr _cached_draw_item = NULL
cdef bint _cached_is_raylib = False
cdef bint _draw_func_resolved = False

cdef inline void _check_draw_item() noexcept:
    global _cached_draw_item, _cached_is_raylib, _draw_func_resolved
    if _draw_func_resolved: return
    cdef DrawFuncPtr draw_func
    dtype = nevu_state.window.renderer_type
    if dtype.pygame:
        draw_func = draw_item_pygame
    elif dtype.raylib:
        draw_func = draw_item_raylib
        _cached_is_raylib = True
    _cached_draw_item = <DrawFuncPtr>draw_func
    _draw_func_resolved = True

cpdef void draw_items(
    NevuCobject layout,
    list items,
    type layout_type,
    type widget_type
):
    cdef NevuCobject item
    _check_draw_item()

    cdef Py_ssize_t i = 0
    if _cached_is_raylib:
        while i < PyList_GET_SIZE(items):
            item = <NevuCobject><void*>PyList_GET_ITEM(items, i)
            if item._visible and not item._wait_mode and not item._dead:
                draw_widget_optimized_raylib(_cached_draw_item, layout, item, layout_type, widget_type)
            i += 1
    else:
        while i < PyList_GET_SIZE(items):
            item = <NevuCobject><void*>PyList_GET_ITEM(items, i)
            if item._visible and not item._wait_mode and not item._dead:
                draw_widget_optimized_pygame(_cached_draw_item, layout, item, layout_type, widget_type)
            i += 1

cpdef void draw_floating_items(
    NevuCobject layout,
    list items,
    type layout_type,
    type widget_type
):
    cdef NevuCobject item
    _check_draw_item()

    cdef Py_ssize_t i = 0
    if _cached_is_raylib:
        while i < PyList_GET_SIZE(items):
            item = <NevuCobject><void*>PyList_GET_ITEM(items, i)
            if item._visible and not item._wait_mode and not item._dead:
                draw_widget_optimized_raylib_rel(_cached_draw_item, layout, item, layout_type, widget_type)
            i += 1
    else:
        while i < PyList_GET_SIZE(items):
            item = <NevuCobject><void*>PyList_GET_ITEM(items, i)
            if item._visible and not item._wait_mode and not item._dead:
                draw_widget_optimized_pygame_rel(_cached_draw_item, layout, item, layout_type, widget_type)
            i += 1

@cython.optimize.unpack_method_calls(True)
cpdef void predraw_raylib_widgets(
    list items,
    type layout_type,
    type widget_type,
):
    cdef NevuCobject item
    cdef Py_ssize_t i = 0
    while i < PyList_GET_SIZE(items):
        item = <NevuCobject><void*>PyList_GET_ITEM(items, i)
        if item._visible and not item._wait_mode and not item._dead:
            if item.node_type == 1:
                item._rl_predraw_widgets()
            else:
                if item._changed:
                    item.draw()
        i += 1

def scrollable_update_collided(list collided_items not None):
    _scrollable_update_collided(collided_items)

cdef inline void _scrollable_update_collided(list collided_items) noexcept:
    cdef Py_ssize_t i = 0
    cdef NevuCobject item
    while i < PyList_GET_SIZE(collided_items):
        item = <NevuCobject>PyList_GET_ITEM(collided_items, i)
        item.update()
        i += 1

def scrollable_recollide_items(NevuCobject self not None, list items not None):
    return _scrollable_recollide_items(self, items)

cdef list _scrollable_recollide_items(NevuCobject self, list items):
    cdef Rect true_rect = self.get_rect()
    self.absolute_coordinates.data.x = <double>true_rect.x
    self.absolute_coordinates.data.y = <double>true_rect.y

    cdef Py_ssize_t n = PyList_GET_SIZE(items)
    cdef NevuCobject item
    cdef Py_ssize_t i = 0
    cdef list collided_items = []

    while i < n:
        item = <NevuCobject><void*>PyList_GET_ITEM(items, i)
        item.absolute_coordinates = c_get_absolute_coordinates(self, item)
        if _widget_drawable_rect(item.get_rect(), true_rect):
            collided_items.append(item)
            item._set_inner_active(True)
        else:
            item._set_inner_active(False)
        i += 1

    return collided_items

cdef bint _widget_drawable_rect(Rect item_rect, Rect layout_rect) noexcept:
    return (item_rect.x < layout_rect.x + layout_rect.w and
            item_rect.x + item_rect.w > layout_rect.x and
            item_rect.y < layout_rect.y + layout_rect.h and
            item_rect.y + item_rect.h > layout_rect.y)

cpdef void _manager_main_loop_main(self):
    c_manager_main_loop_main(self)

cdef inline void update_menu_list(list menus, Py_ssize_t n):
    cdef Py_ssize_t i = 0
    if n == 0: return

    cdef void* menu

    while i < PyList_GET_SIZE(menus):
        menu = <void*>PyList_GET_ITEM(menus, i)
        (<NevuCobject>menu).update()
        i += 1

cdef inline void draw_menu_list(list menus, Py_ssize_t n):
    cdef Py_ssize_t i = 0
    if n == 0: return

    cdef void* menu

    while i < PyList_GET_SIZE(menus):
        menu = <void*>PyList_GET_ITEM(menus, i)
        (<NevuCobject>menu).draw()
        i += 1

cdef inline void c_manager_main_loop_main(self):
    begin_frame = self.window.renderer.begin_frame
    end_frame = self.window.renderer.end_frame
    w_update = self.window.update
    w_clear = self.window.clear
    w_draw_overlay = self.window.draw_overlay
    cdef bint callbacks_available
    cdef str bind_update, bind_before_update, bind_draw, bind_before_draw
    bind_update = BindType.Update.value
    bind_before_update = BindType.BeforeUpdate.value
    bind_draw = BindType.Draw.value
    bind_before_draw = BindType.BeforeDraw.value

    on_update = self.on_update
    on_draw = self.on_draw
    before_update = self.before_update
    before_draw = self.before_draw

    self._first_frame(begin_frame, end_frame)
    draw_overlay = self.draw_overlay

    cdef list menus
    cdef Py_ssize_t menus_size
    cdef Callbacks callbacks
    cdef tuple empty_args = tuple()
    cdef dict empty_kwargs = {}

    while self.running:
        callbacks = self.callbacks
        callbacks_available = callbacks is not None

        menus = self.menus
        if menus is not None:
            menus_size = PyList_GET_SIZE(self.menus)
        else:
            menus_size = 0
        begin_frame()

        w_clear(self.background)

        if callbacks_available:
            callbacks._frun(bind_before_update, empty_args, empty_kwargs)
        before_update()
        w_update(None, self.fps)
        if menus_size > 0:
            update_menu_list(menus, menus_size)
        if callbacks_available:
            callbacks._frun(bind_update, empty_args, empty_kwargs)
        on_update()

        if callbacks_available:
            callbacks._frun(bind_before_draw, empty_args, empty_kwargs)
        before_draw()
        if menus_size > 0:
            draw_menu_list(menus, menus_size)
        if callbacks_available:
            callbacks._frun(bind_draw, empty_args, empty_kwargs)
        on_draw()

        if draw_overlay:
            w_draw_overlay()

        end_frame()

    self._on_exit()
