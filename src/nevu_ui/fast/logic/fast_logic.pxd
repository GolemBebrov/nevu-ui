from nevu_ui.fast.nvrect.nvrect cimport NvRect
from nevu_ui.fast.nvvector2.nvvector2 cimport NvVector2
from nevu_ui.fast.zsystem.fast_zsystem cimport ZSystem

cpdef float rel_helper(float num, float resize_ratio, float min_val, float max_val)

cpdef float relm_helper(float num, float resize_ratio_x, float resize_ratio_y, float min_val, float max_val)

cpdef NvVector2 mass_rel_helper(list mass, float resize_ratio_x, float resize_ratio_y, bint vector)

cpdef NvVector2 vec_rel_helper(NvVector2 vec, float resize_ratio_x, float resize_ratio_y)

cpdef tuple get_rect_helper(NvVector2 master_coordinates, NvVector2 resize_ratio, NvVector2 size)

cpdef object get_rect_helper_pygame(NvVector2 master_coordinates, NvVector2 resize_ratio, NvVector2 size)

cpdef tuple get_rect_helper_cached(NvVector2 master_coordinates, NvVector2 csize)

cpdef object get_rect_helper_cached_pygame(NvVector2 master_coordinates, NvVector2 csize)


cdef NvRect get_nvrect_helper(NvVector2 master_coordinates, NvVector2 resize_ratio, NvVector2 size)

cpdef void logic_update_helper(
    NvVector2 csize,
    NvVector2 master_coordinates,
    NvVector2 dr_coordinates_old,
    NvVector2 resize_ratio,
    ZSystem z_system
)

cpdef void _light_update_helper(
    list items,
    list cached_coordinates,
    NvVector2 coordinatesMW,
    NvVector2 add_vector,
)

cpdef object _very_light_update_helper(
    list items,
    list cached_coordinates,
    NvVector2 add_vector,
    object _get_item_master_coordinates
)


cpdef bint collide_horizontal(NvVector2 r1_tl, NvVector2 r1_br, NvVector2 r2_tl, NvVector2 r2_br)

cpdef bint collide_vertical(NvVector2 r1_tl, NvVector2 r1_br, NvVector2 r2_tl, NvVector2 r2_br)

cpdef bint collide_vector(NvVector2 r1_tl, NvVector2 r1_br, NvVector2 r2_tl, NvVector2 r2_br)