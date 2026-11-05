from nevu_ui.core.size import _AutoSizeUnit, _SizeUnit
from nevu_ui.core.size.rules import (
    Px,
    Auto,
    Fill,
    FillW,
    FillH,
    CFill,
    CFillW,
    CFillH,
    Vh,
    Vw,
    Cvh,
    Cvw,
    Gc,
    Gcw,
    Gch,
    Cgc,
    Cgcw,
    Cgch,
)

px = _SizeUnit(Px)
auto = _AutoSizeUnit(Auto)

fill = _SizeUnit(Fill)
fillw = _SizeUnit(FillW)
fillh = _SizeUnit(FillH)
cfill = _SizeUnit(CFill)
cfillw = _SizeUnit(CFillW)
cfillh = _SizeUnit(CFillH)
_all_fillx_units = {fill, fillw, fillh, cfill, cfillw, cfillh}

vh = _SizeUnit(Vh)
vw = _SizeUnit(Vw)
cvh = _SizeUnit(Cvh)
cvw = _SizeUnit(Cvw)
_all_vx_units = {vh, vw, cvh, cvw}

gc = _SizeUnit(Gc)
gcw = _SizeUnit(Gcw)
gch = _SizeUnit(Gch)
cgc = _SizeUnit(Cgc)
cgcw = _SizeUnit(Cgcw)
cgch = _SizeUnit(Cgch)
_all_gcx_units = {gc, gcw, gch, cgc, cgcw, cgch}

screen_full = (100 % vw, 100 % vh)
screen_half = (50 % vw, 50 % vh)
full_grid_cell = (100 % gcw, 100 % gch)
hald_grid_cell = (50 % gcw, 50 % gch)
fill_all = (100 % fillw, 100 % fillh)
fill_half = (50 % fillw, 50 % fillh)

def fill_perc(percent):
    return [percent * fillw, percent * fillh]

__all__ = [
    "px",
    "auto",

    "fill",
    "fillw",
    "fillh",
    "cfill",
    "cfillw",
    "cfillh",
    "_all_fillx_units",

    "vh",
    "vw",
    "cvh",
    "cvw",
    "_all_vx_units",

    "gc",
    "gcw",
    "gch",
    "cgc",
    "cgcw",
    "cgch",
    "_all_gcx_units",

    "screen_full",
    "screen_half",
    "full_grid_cell",
    "hald_grid_cell",
    "fill_all",
    "fill_half",
    "fill_perc",
]
