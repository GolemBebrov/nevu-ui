from __future__ import annotations

from typing import Any

from nevu_ui.fast.nvvector2.nvvector2 import NvVector2
from nevu_ui.fast.nvparam.nvparam import NvParam
from nevu_ui.presentation.animations.animation_manager import AnimationManager
from nevu_ui.fast.nvrect.nvrect import NvRect
from nevu_ui.fast.nevucache.nevucache import Cache
class NevuCobject:
    coordinates: NvVector2
    absolute_coordinates: NvVector2
    size: NvVector2
    _resize_ratio: NvVector2

    params: list[NvParam]
    _blacklisted_params: list[str]
    _param_links: dict[str, str]
    cache: Cache
    _sended_z_link: bool
    _dragging: bool
    _is_kup: bool
    _kup_abandoned: bool
    _force_state_set_continue: bool
    _visible: bool
    _active: bool
    _changed: bool
    _first_update: bool
    _wait_mode: bool
    _dead: bool
    booted: bool

    def __init__(self, *args: Any, **kwargs: Any) -> None: ...
    def _get_param_names(self) -> list[str]: ...
    def _find_param(self, name: str) -> NvParam | None: ...
    def _add_param(self, name: str, supported_classes: Any, default: Any, getter: Any, setter: Any, layer: int) -> None: ...
    def get_param_strict(self, name: str) -> NvParam: ...
    def get_param(self, name: str) -> NvParam | None: ...
    def get_param_value(self, name: str) -> Any: ...
    def set_param_value(self, name: str, value: Any) -> None: ...
    def get_nvrect(self) -> NvRect: ...
    def rel(self, vec: NvVector2) -> NvVector2: ...
    def relx(self, num: float) -> float: ...
    def rely(self, num: float) -> float: ...
    def relm(self, num: float) -> float: ...
    def relx_custom(self, num: float, min: float, max: float) -> float: ...
    def rely_custom(self, num: float, min: float, max: float) -> float: ...
    def relm_custom(self, num: float, min: float, max: float) -> float: ...
    def set_coordinates(self, coordinates: NvVector2) -> None: ...
    def _coordinates_setter(self, coordinates: NvVector2) -> bool: ...
    
    def clear_all(self):
        """
        Clears all cached data by invoking the clear method on the cache. 
        !WARNING!: may cause bugs and errors
        """
        
    def clear_surfaces(self):
        """
        Clears specific cached surface-related data by invoking the clear_selected 
        method on the cache with a whitelist of CacheTypes related to surfaces. 
        This includes Image, Scaled_Gradient, Surface, and Borders.
        Highly recommended to use this method instead of clear_all.
        """