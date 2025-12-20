import pygame
from typing import Tuple, Union

def _create_outlined_rounded_rect_sdf(
    size: Tuple[int, int], 
    radius: int, 
    width: float, 
    color: Union[Tuple[int, int, int], Tuple[int, int, int, int]]
) -> pygame.Surface: ...

def _create_rounded_rect_surface_optimized(
    size: Tuple[int, int], 
    radius: int, 
    color: Union[Tuple[int, int, int], Tuple[int, int, int, int]]
) -> pygame.Surface: ...

def transform_into_outlined_rounded_rect_sdf(
    surf: pygame.Surface, 
    radius: int, 
    width: float, 
    color: Union[Tuple[int, int, int], Tuple[int, int, int, int]]
) -> None: ...

def transform_into_outlined_rounded_rect(
    surf: pygame.Surface, 
    radius: int, 
    width: float,
    color: Union[Tuple[int, int, int], Tuple[int, int, int, int]]
) -> None: ...