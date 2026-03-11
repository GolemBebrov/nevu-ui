from typing import Any
from nevu_ui.core import Annotations
def init_raylib_pointers(pointers: Annotations.dest_like) -> None: ...

def draw_texture_rec(
    texture: Any, 
    source_rec: Annotations.rect_like, 
    position: Annotations.dest_like, 
    color: Annotations.rgba_color
) -> None: ...

def draw_texture_pro(
    texture: Any, 
    source_rec: Annotations.rect_like, 
    dest_rec: Annotations.rect_like, 
    origin: Annotations.dest_like, 
    rotation: float, 
    color: Annotations.rgba_color
) -> None: ...

def begin_blend_mode(mode: int) -> None: ...

def end_blend_mode() -> None: ...

def begin_texture_mode(target: Any) -> None: ...

def end_texture_mode() -> None: ...