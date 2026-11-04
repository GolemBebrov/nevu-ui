from nevu_ui.cython.rect.rect cimport Rect
from nevu_ui.cython.vector2.vector2 cimport Vector2, nv_vector2_t
from nevu_ui.cython.z_system.z_system cimport ZSystem
from nevu_ui.cython.nevucobject.nevucobject cimport NevuCobject

cpdef double rel_helper(double num, double resize_ratio, double min_val, double max_val)

cpdef double relm_helper(double num, double resize_ratio_x, double resize_ratio_y, double min_val, double max_val)

cpdef Vector2 mass_rel_helper(list mass, double resize_ratio_x, double resize_ratio_y, bint vector)

cpdef Vector2 vec_rel_helper(Vector2 vec, double resize_ratio_x, double resize_ratio_y)

cpdef object get_rect_helper_pygame(Vector2 master_coordinates, Vector2 resize_ratio, Vector2 size)

cpdef tuple get_rect_helper_cached(Vector2 master_coordinates, Vector2 csize)

cpdef object get_rect_helper_cached_pygame(Vector2 master_coordinates, Vector2 csize)
cdef inline Vector2 get_item_abs_coords(NevuCobject layout, NevuCobject item)
cpdef void draw_floating_items_optimized(
    NevuCobject layout,
    list items,
    type layout_type,
    type widget_type
)
cdef Rect get_rect_helper(Vector2 master_coordinates, Vector2 resize_ratio, Vector2 size)
cdef inline void _fast_cycle_in_list(str func_name, list items)
cpdef void logic_update_helper (
    NevuCobject self
)

cpdef void draw_widgets_optimized(
    NevuCobject layout,
    list items,
    type layout_type,
    type widget_type
)

cpdef void rl_predraw_widgets(
    list items,
    type layout_type,
    type widget_type,
)

cdef inline void _light_update_helper(
    list items,
    list cached_coordinates,
    nv_vector2_t menu_vec,
    double add_x,
    double add_y
) noexcept

cpdef _very_light_update_helper(
    list items,
    list cached_coordinates,
    Vector2 menu_vec,
    Vector2 add_vector,
    NevuCobject layout
)


cpdef bint collide_horizontal(Vector2 r1_tl, Vector2 r1_br, Vector2 r2_tl, Vector2 r2_br)

cpdef bint collide_vertical(Vector2 r1_tl, Vector2 r1_br, Vector2 r2_tl, Vector2 r2_br)

cpdef bint collide_vector(Vector2 r1_tl, Vector2 r1_br, Vector2 r2_tl, Vector2 r2_br)
