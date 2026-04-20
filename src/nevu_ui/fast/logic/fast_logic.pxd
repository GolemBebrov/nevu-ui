from nevu_ui.fast.nvrect.nvrect cimport NvRect
from nevu_ui.fast.nvvector2.nvvector2 cimport NvVector2
from nevu_ui.fast.zsystem.fast_zsystem cimport ZSystem
from nevu_ui.fast.nevucobj.nevucobj cimport NevuCobject

cpdef double rel_helper(double num, double resize_ratio, double min_val, double max_val)

cpdef double relm_helper(double num, double resize_ratio_x, double resize_ratio_y, double min_val, double max_val)

cpdef NvVector2 mass_rel_helper(list mass, double resize_ratio_x, double resize_ratio_y, bint vector)

cpdef NvVector2 vec_rel_helper(NvVector2 vec, double resize_ratio_x, double resize_ratio_y)

cpdef tuple get_rect_helper(NvVector2 master_coordinates, NvVector2 resize_ratio, NvVector2 size)

cpdef object get_rect_helper_pygame(NvVector2 master_coordinates, NvVector2 resize_ratio, NvVector2 size)

cpdef tuple get_rect_helper_cached(NvVector2 master_coordinates, NvVector2 csize)

cpdef object get_rect_helper_cached_pygame(NvVector2 master_coordinates, NvVector2 csize)


cdef NvRect get_nvrect_helper(NvVector2 master_coordinates, NvVector2 resize_ratio, NvVector2 size)

cpdef void logic_update_helper(
    NvVector2 master_coordinates,
    NvVector2 dr_coordinates_old,
    ZSystem z_system
)

cdef start_item(NevuCobject item, NevuCobject layout)

cpdef void draw_widgets_optimized(
    list items,
    object draw_widget_func,
    NevuCobject layout,
    type layout_type,
    type widget_type
)

cpdef void rl_predraw_widgets(
    list items,
    type layout_type,
    type widget_type,
)

cpdef void _light_update_helper(
    list items,
    list cached_coordinates,
    NvVector2 coordinatesMW,
    NvVector2 add_vector,
)

cpdef _very_light_update_helper(
    list items,
    list cached_coordinates,
    NvVector2 add_vector,
    NevuCobject layout
)


cpdef bint collide_horizontal(NvVector2 r1_tl, NvVector2 r1_br, NvVector2 r2_tl, NvVector2 r2_br)

cpdef bint collide_vertical(NvVector2 r1_tl, NvVector2 r1_br, NvVector2 r2_tl, NvVector2 r2_br)

cpdef bint collide_vector(NvVector2 r1_tl, NvVector2 r1_br, NvVector2 r2_tl, NvVector2 r2_br)