from typing import Tuple, Union, TYPE_CHECKING

if TYPE_CHECKING:
    from pygame import Surface

def _create_outlined_rounded_rect_sdf(
    size: Tuple[int, int], 
    radius: int, 
    width: float, 
    color: Union[Tuple[int, int, int], Tuple[int, int, int, int]]
) -> "Surface": ...

def _create_rounded_rect_surface_optimized(
    size: Tuple[int, int], 
    radius: int | float | tuple, 
    color: Union[Tuple[int, int, int], Tuple[int, int, int, int]]
) -> "Surface": ...

def transform_into_outlined_rounded_rect(
    surf: "Surface", 
    radius: int, 
    width: float, 
    color: Union[Tuple[int, int, int], Tuple[int, int, int, int]],
    background_color = None
) -> None: ...

def transform_into_rounded_rect(
    surf: "Surface", 
    radius: int | float | tuple, 
    color: Union[Tuple[int, int, int], Tuple[int, int, int, int]]
) -> None: ...