import nevu_ui.core.modules as md
from typing import Any, List, Tuple, Optional, Sequence, Callable, TYPE_CHECKING
if TYPE_CHECKING:
    from pygame import Rect

from nevu_ui.fast.nvvector2 import NvVector2

def rel_helper(
    num: float, 
    resize_ratio: float, 
    min_val: Optional[float], 
    max_val: Optional[float]
) -> float: ...

def relm_helper(
    num: float, 
    resize_ratio_x: float, 
    resize_ratio_y: float, 
    min_val: float, 
    max_val: float
) -> float: ...

def vec_rel_helper(
    vec: NvVector2, 
    resize_ratio_x: float, 
    resize_ratio_y: float
) -> NvVector2: ...

def mass_rel_helper(
    mass: list, 
    resize_ratio_x: float, 
    resize_ratio_y: float, 
    vector: bool
) -> NvVector2: ...

def get_rect_helper(
    master_coordinates: NvVector2, 
    resize_ratio: NvVector2, 
    size: NvVector2
) -> Tuple[float, float, float, float]: ...

def get_rect_helper_pygame(
    master_coordinates: NvVector2, 
    resize_ratio: NvVector2, 
    size: NvVector2
) -> "Rect": ...

def get_rect_helper_cached(
    master_coordinates: NvVector2, 
    csize: NvVector2
) -> Tuple[float, float, float, float]: ...

def get_rect_helper_cached_pygame(
    master_coordinates: NvVector2, 
    csize: NvVector2
) -> "Rect": ...

def logic_update_helper(
    master_coordinates: NvVector2,
    dr_coordinates_old: NvVector2,
    z_system: Any
): ...

def draw_widgets_optimized(
    items: List[Any],
    draw_widget_func: Callable,
    layout: Any,
    layout_type: Any,
    widget_type: Any
): ...

def rl_predraw_widgets(
    items: List[Any],
    layout_type: Any,
    widget_type: Any
): ...

def _light_update_helper(
    items: List[Any],
    cached_coordinates: List[NvVector2],
    coordinatesMW: NvVector2,
    add_vector: NvVector2,
) -> None: ...

def collide_vector(
    r1_tl: NvVector2,
    r1_br: NvVector2,
    r2_tl: NvVector2,
    r2_br: NvVector2
) -> bool: ...

def collide_horizontal(
    r1_tl: NvVector2,
    r1_br: NvVector2,
    r2_tl: NvVector2,
    r2_br: NvVector2
) -> bool: ...

def collide_vertical(
    r1_tl: NvVector2,
    r1_br: NvVector2,
    r2_tl: NvVector2,
    r2_br: NvVector2
) -> bool: ...

def _very_light_update_helper(
    items: List[Any],
    cached_coordinates: List[NvVector2],
    add_vector: NvVector2,
    layout: Any
) -> None: ...

def fast_cycle_range(
    func: Callable,
    start: int,
    end: int,
    step: int
): ...

def fast_cycle_list(
    func: Callable,
    items: list[Any]
): ...

def fast_cycle_tuple(
    func: Callable,
    items: Sequence[Any]
): ...