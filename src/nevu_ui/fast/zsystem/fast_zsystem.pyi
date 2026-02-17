from typing import Any, Optional, Callable
from nevu_ui.fast.nvvector2 import NvVector2

class ZRequest:
    link: Any
    on_hover_func: Optional[Callable[[], None]]
    on_unhover_func: Optional[Callable[[], None]]
    on_click_func: Optional[Callable[[], None]]
    on_keyup_func: Optional[Callable[[], None]]
    on_keyup_abandon_func: Optional[Callable[[], None]]
    on_scroll_func: Optional[Callable[[bool], None]]

    def __init__(
        self,
        link: Any,
        on_hover_func: Optional[Callable[[], None]] = ...,
        on_unhover_func: Optional[Callable[[], None]] = ...,
        on_click_func: Optional[Callable[[], None]] = ...,
        on_keyup_func: Optional[Callable[[], None]] = ...,
        on_keyup_abandon_func: Optional[Callable[[], None]] = ...,
        on_scroll_func: Optional[Callable[[bool], None]] = ...
    ) -> None: ...

class ZSystem:
    def __init__(self) -> None: ...

    def add(self, z_request: ZRequest) -> None: ...

    def mark_dirty(self) -> None: ...

    def cycle(
        self,
        mouse_pos: NvVector2,
        mouse_down: bool,
        mouse_up: bool,
        any_wheel: bool,
        wheel_down: bool,
    ) -> None: ...