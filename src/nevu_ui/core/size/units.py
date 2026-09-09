from nevu_ui.core.size.base import _SizeUnit
from nevu_ui.core.size.rules import *

px = _SizeUnit(Px)

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

fill_all = (100 * fillw, 100 * fillh)
fill_half = (50 * fillw, 50 * fillh)

fill_perc = lambda percent: [percent * fillw, percent * fillh]
