import pygame
from typing import Any, List, Tuple, Optional, Sequence, Callable

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
    min_val: Optional[float], 
    max_val: Optional[float]
) -> float: ...

def mass_rel_helper(
    mass: Sequence[float], 
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
) -> pygame.Rect: ...

def get_rect_helper_cached(
    master_coordinates: NvVector2, 
    csize: NvVector2
) -> Tuple[float, float, float, float]: ...

def get_rect_helper_cached_pygame(
    master_coordinates: NvVector2, 
    csize: NvVector2
) -> pygame.Rect: ...

def logic_update_helper(
    optimized_dirty_rect: bool,
    animation_manager: Any,
    csize: NvVector2,
    master_coordinates: NvVector2,
    dirty_rect: List[pygame.Rect],
    dr_coordinates_old: NvVector2,
    first_update: bool,
    first_update_functions: List[Callable[[], None]],
    resize_ratio: NvVector2,
    z_system: Any
) -> Tuple[NvVector2, bool]: ...

def _light_update_helper(
    items: List[Any],
    cached_coordinates: List[NvVector2],
    first_parent_menu: Any,
    add_x: float,
    add_y: float,
    resize_ratio: NvVector2,
    not_need_to_process: bool
) -> None: ...