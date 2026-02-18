from nevu_ui.components.nevuobj.typehints import NevuObjectTemplate
from dataclasses import dataclass
from nevu_ui.components.nevuobj import NevuObject
from nevu_ui.core.enums import Align

@dataclass
class LayoutTemplate(NevuObjectTemplate):
    content: list | None = None

@dataclass
class GridTemplate(NevuObjectTemplate):
    content: dict[tuple[int | float, int | float], NevuObject] | None = None

@dataclass
class Grid1xTemplate(NevuObjectTemplate):
    content: dict[int | float, NevuObject] | None = None

@dataclass
class AlignTemplate(NevuObjectTemplate):
    content: list[tuple[Align, NevuObject]] | None = None