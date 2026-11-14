from nevu_ui.cython.rect.rect cimport Rect
from nevu_ui.cython.vector2.vector2 cimport Vector2, nv_vector2_t
from nevu_ui.cython.z_system.z_system cimport ZSystem
from nevu_ui.cython.nevucobject.nevucobject cimport NevuCobject

cpdef double rel_helper(double num, double resize_ratio, double min_val, double max_val)
cpdef double relm_helper(double num, double resize_ratio_x, double resize_ratio_y, double min_val, double max_val)
cpdef Vector2 vec_rel_helper(Vector2 vec, double resize_ratio_x, double resize_ratio_y)
cdef Vector2 c_get_absolute_coordinates(NevuCobject layout, NevuCobject item)
cpdef void draw_floating_items(
    NevuCobject layout,
    list items,
    type layout_type,
    type widget_type
)
cdef Rect get_rect(Vector2 absolute_coordinates, Vector2 ratio, Vector2 size)
cpdef void check_moved(NevuCobject nevuobject)
cpdef void predraw_raylib_widgets(
    list items,
    type layout_type,
    type widget_type,
)
