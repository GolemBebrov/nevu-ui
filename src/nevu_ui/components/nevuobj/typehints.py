from dataclasses import dataclass
from typing import Any, NotRequired, TypedDict, Unpack

from nevu_ui.core import Annotations
from nevu_ui.core.classes import DictAccessMixin, Events, GlobalsBase, _strategy_type
from nevu_ui.overlay.tooltip import Tooltip
from nevu_ui.presentation.animations import AnimationManager
from nevu_ui.presentation.color import SubThemeRole
from nevu_ui.presentation.style import Style


class _NevuObjectKwargsBase(TypedDict, total=False):
    id: Any
    single_instance: bool
    events: Events
    tooltip: Tooltip
    subtheme_role: SubThemeRole


class _NevuObjectKwargsShort(TypedDict, total=False):
    z: int
    anim_manager: AnimationManager


class _NevuObjectKwargsLong(TypedDict, total=False):
    depth: int
    animation_manager: AnimationManager


class NevuObjectKwargsShort(_NevuObjectKwargsBase, _NevuObjectKwargsShort):
    pass


class NevuObjectKwargsLong(_NevuObjectKwargsBase, _NevuObjectKwargsLong):
    pass


class NevuObjectKwargs(NevuObjectKwargsShort, NevuObjectKwargsLong):
    pass


@dataclass
class NevuObjectTemplate(DictAccessMixin):
    size: Annotations.nevuobj_size


class _NevuObjecGlobalsKwargs(TypedDict):
    size: NotRequired[Annotations.nevuobj_size]
    style: NotRequired[Style | str]


class NevuObjectGlobalsKwargs(_NevuObjecGlobalsKwargs, NevuObjectKwargs):
    pass


class NevuObjectGlobals(GlobalsBase):
    def modify(self, **kwargs: Unpack[NevuObjectGlobalsKwargs]):
        return super().modify(**kwargs)

    def modify_temp(self, **kwargs: Unpack[NevuObjectGlobalsKwargs]):
        return super().modify_temp(**kwargs)


nevu_object_globals = NevuObjectGlobals()
