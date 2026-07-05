from cpython.list cimport PyList_GET_SIZE, PyList_GET_ITEM
from nevu_ui.fast.logic.fast_logic cimport get_item_abs_coords
from cpython.list cimport PyList_GET_SIZE
from cpython.object cimport PyObject

from nevu_ui.presentation.color import Color
from nevu_ui.fast.nevucobj.nevucobj cimport NevuCobject
from nevu_ui.fast.nvrect.nvrect cimport NvRect
from nevu_ui.fast.nvrendertex.nv_render_tex cimport NvRenderTexture
from nevu_ui.fast.nvvector2.nvvector2 cimport NvVector2
from nevu_ui.core.state import nevu_state
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

def menu_draw_raylib(object self not None, NvRenderTexture bg not None):
    _menu_draw_raylib(self, bg)

cdef NvRect white_color = NvRect.new(255, 255, 255, 255)

cdef inline void _menu_draw_raylib(object self, NvRenderTexture bg):
    cdef NevuCobject layout
    cdef NvRenderTexture main_nvtex
    cdef NvVector2 abs_coords
    cdef bint has_layout

    main_nvtex = self._surface #type: ignore

    abs_coords = self.absolute_coordinates #type: ignore
    has_layout = <bint>(self._layout is not None) #type: ignore
    if has_layout:
        layout = self._layout #type: ignore
        PyObject_CallNoArgs(layout._rl_predraw_widgets) #type: ignore

    begin_texture_mode(main_nvtex)
    c_clear_background_blank()
    begin_blend_mode(5)
    main_nvtex.c_fast_nvblit(bg, NvVector2.new(0, 0), -1, True, white_color)
    if has_layout:
        layout.draw() #type: ignore
    end_blend_mode()
    end_texture_mode()

    main_nvtex.c_fast_nvblit(main_nvtex, abs_coords, 5, True, white_color)

def menu_draw_sdl(object self not None, bg not None):
    _menu_draw_sdl(self, bg)

cdef inline void _menu_draw_sdl(self, bg):
    cdef object sdl_texture = self._sdl_texture
    cdef object renderer = nevu_state.renderer
    cdef NevuCobject layout = self._layout
    if layout is not None:
        renderer.target = self._sdl_texture
        renderer.blit(bg, PyObject_CallNoArgs(self.get_rect))
        layout.draw()
        renderer.target = None
    self._window._renderer.blit(sdl_texture, self._tuple_absolute_coordinates)

def menu_draw_pygame(object self not None, bg not None):
    _menu_draw_pygame(self, bg)

cdef inline void _menu_draw_pygame(self, bg):
    cdef object surface = self._surface
    cdef NevuCobject layout
    surface.fill(Color.Blank)
    surface.blit(bg, (0, 0))
    layout = self._layout
    if layout is not None: 
        layout.draw() 
    self._window._renderer.blit(surface, self._tuple_absolute_coordinates)