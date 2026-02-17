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
    csize: NvVector2,
    master_coordinates: NvVector2,
    dr_coordinates_old: NvVector2,
    resize_ratio: NvVector2,
    z_system: Any
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
    _get_item_master_coordinates: Callable[[Any], NvVector2]
) -> None: ...