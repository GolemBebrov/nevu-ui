from cpython.list cimport PyList_GET_SIZE, PyList_GET_ITEM
from nevu_ui.fast.logic.fast_logic cimport get_item_abs_coords, _fast_cycle_in_list
from cpython.list cimport PyList_GET_SIZE
from cpython.object cimport PyObject
from nevu_ui.core.enums import (

    CacheType,
)
from nevu_ui.presentation.color import Color
from nevu_ui.fast.nevucobj.nevucobj cimport NevuCobject
from nevu_ui.fast.nvrect.nvrect cimport NvRect
from nevu_ui.fast.nvrendertex.nv_render_tex cimport NvRenderTexture
from nevu_ui.fast.nvvector2.nvvector2 cimport NvVector2
from nevu_ui.core.state import nevu_state
from nevu_ui.core.enums import BindType
from nevu_ui.fast.raylib.nevu_raylib cimport begin_blend_mode, end_blend_mode, begin_texture_mode, end_texture_mode, c_clear_background_blank
from nevu_ui.fast.logic.fast_logic cimport get_item_abs_coords
cdef extern from "Python.h":
    ctypedef struct PyListObject:
        PyObject **ob_item
    object PyObject_CallNoArgs(object func)

def scrollable_update_collided(list collided_items not None):
    _scrollable_update_collided(collided_items)

cdef inline void _scrollable_update_collided(list collided_items) noexcept:
    cdef Py_ssize_t n = PyList_GET_SIZE(collided_items)
    cdef Py_ssize_t i = 0 #type: ignore
    cdef NevuCobject item
    while i < n:
        item = <NevuCobject>PyList_GET_ITEM(collided_items, i)
        item.update()
        i += 1

def scrollable_recollide_items(NevuCobject self not None, list items not None):
    return _scrollable_recollide_items(self, items)

cdef inline list _scrollable_recollide_items(NevuCobject self, list items) noexcept:
    cdef NvRect true_rect = self.get_nvrect()
    self.absolute_coordinates.data.x = <double>true_rect.x
    self.absolute_coordinates.data.y = <double>true_rect.y

    cdef Py_ssize_t n = PyList_GET_SIZE(items)
    cdef NevuCobject item
    cdef Py_ssize_t i = 0 #type: ignore
    cdef list collided_items = []

    while i < n:
        item = <NevuCobject><void*>PyList_GET_ITEM(items, i)
        item.absolute_coordinates = get_item_abs_coords(self, item)
        if _widget_drawable_rect(item.get_nvrect(), true_rect):
            collided_items.append(item)
        i += 1

    return collided_items

cdef bint _widget_drawable_rect(NvRect item_rect, NvRect layout_rect) noexcept:
    return (item_rect.x < layout_rect.x + layout_rect.w and
            item_rect.x + item_rect.w > layout_rect.x and
            item_rect.y < layout_rect.y + layout_rect.h and
            item_rect.y + item_rect.h > layout_rect.y) #type: ignore

cdef NvRect white_color = NvRect.new(255, 255, 255, 255)

cpdef void _manager_main_loop_opt(self):
    c_manager_main_loop_opt(self)

cdef inline void c_manager_main_loop_opt(self):
    begin_frame = self.window.renderer.begin_frame
    end_frame = self.window.renderer.end_frame
    w_update = self.window.update
    w_clear = self.window.clear
    w_draw_overlay = self.window.draw_overlay
    cdef bint callbacks_available = self.callbacks is not None
    cdef str bind_update, bind_before_update, bind_draw, bind_before_draw
    if self.callbacks:
        bind_update = BindType.Update.value
        bind_before_update = BindType.BeforeUpdate.value
        bind_draw = BindType.Draw.value
        bind_before_draw = BindType.BeforeDraw.value
        callbacks_run = self.callbacks.run

    on_update = self.on_update
    on_draw = self.on_draw
    before_update = self.before_update
    before_draw = self.before_draw

    self._first_frame(begin_frame, end_frame)

    bg = self.background
    fps = self.fps
    draw_overlay = self.draw_overlay

    cdef str update_text = "update"
    cdef str draw_text = "draw"
    cdef list menus

    while self.running:
        menus = self.menus
        begin_frame()

        w_clear(bg)

        if callbacks_available:
            callbacks_run(bind_before_update)
        before_update()
        w_update(None, fps)
        if menus is not None:
            _fast_cycle_in_list(update_text, menus)
        if callbacks_available:
            callbacks_run(bind_update)
        on_update()

        if callbacks_available:
            callbacks_run(bind_before_draw)
        before_draw()
        if menus is not None:
            _fast_cycle_in_list(draw_text, menus)
        if callbacks_available:
            callbacks_run(bind_draw)
        on_draw()

        if draw_overlay:
            w_draw_overlay()

        end_frame()

    self._on_exit()

cpdef void _manager_main_loop_main(self):
    c_manager_main_loop_main(self)

cdef inline void c_manager_main_loop_main(self):
    begin_frame = self.window.renderer.begin_frame
    end_frame = self.window.renderer.end_frame
    w_update = self.window.update
    w_clear = self.window.clear
    w_draw_overlay = self.window.draw_overlay
    cdef bint callbacks_available = self.callbacks is not None
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

    cdef str update_text = "update"
    cdef str draw_text = "draw"
    cdef list menus

    while self.running:
        callbacks = self.callbacks
        callbacks_available = callbacks is not None

        menus = self.menus
        begin_frame()

        w_clear(self.background)

        if callbacks_available:
            callbacks.run(bind_before_update)
        before_update()
        w_update(None, self.fps)
        if menus is not None:
            _fast_cycle_in_list(update_text, menus)
        if callbacks_available:
            callbacks.run(bind_update)
        on_update()

        if callbacks_available:
            callbacks.run(bind_before_draw)
        before_draw()
        if menus is not None:
            _fast_cycle_in_list(draw_text, menus)
        if callbacks_available:
            callbacks.run(bind_draw)
        on_draw()

        if draw_overlay:
            w_draw_overlay()

        end_frame()

    self._on_exit()
