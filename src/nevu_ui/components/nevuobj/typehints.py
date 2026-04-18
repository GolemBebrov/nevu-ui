from typing import TypedDict, NotRequired, Any, Unpack
from dataclasses import dataclass

from nevu_ui.core.classes import Events
from nevu_ui.overlay.tooltip import Tooltip
from nevu_ui.presentation.color import SubThemeRole
from nevu_ui.core.classes import DictAccessMixin, GlobalsBase
from nevu_ui.fast.nvvector2 import NvVector2
from nevu_ui.presentation.animations import AnimationManager
from nevu_ui.presentation.style import Style
from nevu_ui.core import Annotations

class NevuObjectKwargs(TypedDict):
    id: NotRequired[Any]
    floating: NotRequired[bool]
    single_instance: NotRequired[bool]
    events: NotRequired[Events]
    z: NotRequired[int]
    depth: NotRequired[int]
    tooltip: NotRequired[Tooltip]
    subtheme_role: NotRequired[SubThemeRole]
    animation_manager: NotRequired[AnimationManager]

@dataclass
class NevuObjectTemplate(DictAccessMixin):
    size: Annotations.nevuobj_size


class _NevuObjecGlobalsKwargs(TypedDict):
    size: NotRequired[Annotations.nevuobj_size]
    style: NotRequired[Style | str]

class NevuObjectGlobalsKwargs(_NevuObjecGlobalsKwargs, NevuObjectKwargs): pass

class NevuObjectGlobals(GlobalsBase):
    def modify(self, **kwargs: Unpack[NevuObjectGlobalsKwargs]):
        return super().modify(**kwargs)
    def modify_temp(self, **kwargs: Unpack[NevuObjectGlobalsKwargs]):
        return super().modify_temp(**kwargs)

nevu_object_globals = NevuObjectGlobals()