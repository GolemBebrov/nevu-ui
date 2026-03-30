import pyray as rl
from typing import Any, Type, TypeVar, Optional
from nevu_ui.fast.nvvector2.nvvector2 import NvVector2
from nevu_ui.fast.nvrect import NvRect
from nevu_ui.presentation.color import Color
from nevu_ui.core.annotations import Annotations

_T = TypeVar("_T", bound="NvRenderTexture")

class NvRenderTexture:
    render_texture: Any
    size: NvVector2
    loaded: bool

    @classmethod
    def from_rl_render_texture(cls: Type[_T], rl_render_texture: rl.RenderTexture) -> _T: ...
    
    def __init__(self, size: NvVector2) -> None: ...
    
    @property
    def texture(self) -> Any: ...
    
    @property
    def id(self) -> Any: ...
    
    @property
    def depth(self) -> Any: ...
    
    def blit(
        self, 
        nv_texture: NvRenderTexture, 
        dest: Annotations.dest_like, 
        blend_mode: int = ..., 
        flip: bool = ..., 
        color: Annotations.rgba_color = ...
    ) -> None: ...
    
    def fast_blit(
        self, 
        nv_texture: NvRenderTexture, 
        dest: Annotations.dest_like, 
        blend_mode: int = ..., 
        flip: bool = ..., 
        color: Annotations.rgba_color = ...
    ) -> None: ...
        
    def clear(self, color: Annotations.rgba_color) -> None: ...
    
    def fast_clear(self, color: Annotations.rgba_color) -> None: ...
    
    def fill(self, color: Annotations.rgba_color) -> None: ...
        
    def kill(self) -> None: ...
    
    def get_rect(self) -> NvRect: ...
    
    def copy(self, flip: bool = ...) -> NvRenderTexture: ...
    
    def __enter__(self) -> NvRenderTexture: ...

    def __exit__(self, exc_type: Optional[Type[BaseException]], exc_val: Optional[BaseException], exc_tb: Any) -> None: ...