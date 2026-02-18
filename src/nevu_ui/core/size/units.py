from nevu_ui.core.size.rules import *
from nevu_ui.core.size.base import SizeUnit

px = SizeUnit(Px)

fill = SizeUnit(Fill)
fillw = SizeUnit(FillW)
fillh = SizeUnit(FillH)
cfill = SizeUnit(CFill)
cfillw = SizeUnit(CFillW)
cfillh = SizeUnit(CFillH)
_all_fillx_units = {fill, fillw, fillh, cfill, cfillw, cfillh}

vh = SizeUnit(Vh)
vw = SizeUnit(Vw)
cvh = SizeUnit(Cvh)
cvw = SizeUnit(Cvw)
_all_vx_units = {vh, vw, cvh, cvw}

gc = SizeUnit(Gc)
gcw = SizeUnit(Gcw)
gch = SizeUnit(Gch)
cgc = SizeUnit(Cgc)
cgcw = SizeUnit(Cgcw)
cgch = SizeUnit(Cgch)
_all_gcx_units = {gc, gcw, gch, cgc, cgcw, cgch}

fill_all = (100*fillw, 100*fillh)
fill_half = (50*fillw, 50*fillh)

fill_perc = lambda percent: [percent*fillw, percent*fillh] 