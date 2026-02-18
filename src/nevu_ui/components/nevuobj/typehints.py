from typing import TypedDict, NotRequired, Any
from dataclasses import dataclass

from nevu_ui.core.classes import Events
from nevu_ui.overlay.tooltip import Tooltip
from nevu_ui.presentation.color import SubThemeRole
from nevu_ui.core.classes import DictAccessMixin
from nevu_ui.fast.nvvector2 import NvVector2

class NevuObjectKwargs(TypedDict):
    id: NotRequired[Any]
    floating: NotRequired[bool]
    single_instance: NotRequired[bool]
    events: NotRequired[Events]
    z: NotRequired[int]
    depth: NotRequired[int]
    tooltip: NotRequired[Tooltip]
    subtheme_role: NotRequired[SubThemeRole]

@dataclass
class NevuObjectTemplate(DictAccessMixin):
    size: list | NvVector2 