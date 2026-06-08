from cpython.list cimport PyList_GET_SIZE, PyList_GET_ITEM
from nevu_ui.fast.nevucobj.nevucobj cimport NevuCobject

def scrollable_update_collided(list collided_items not None):
    _scrollable_update_collided(collided_items)

cdef inline void _scrollable_update_collided(list collided_items) noexcept:
    cdef Py_ssize_t n = PyList_GET_SIZE(collided_items)
    cdef Py_ssize_t i = 0
    cdef NevuCobject item
    while i < n:
        item = <NevuCobject>PyList_GET_ITEM(collided_items, i)
        item.update()
        i += 1