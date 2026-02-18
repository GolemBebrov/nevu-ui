from nevu_ui.core.size.base import SizeRule, PercentSizeRule

class Px(SizeRule): pass

class Fill(PercentSizeRule): pass
class FillW(PercentSizeRule): pass
class FillH(PercentSizeRule): pass
class CFill(PercentSizeRule): pass
class CFillW(PercentSizeRule): pass
class CFillH(PercentSizeRule): pass
_all_fillx = {Fill, FillW, FillH, CFill, CFillW, CFillH}

class Vh(PercentSizeRule): pass
class Vw(PercentSizeRule): pass
class Cvh(PercentSizeRule): pass
class Cvw(PercentSizeRule): pass
_all_vx = {Vh, Vw, Cvh, Cvw}

class Gc(PercentSizeRule): pass
class Gcw(PercentSizeRule): pass
class Gch(PercentSizeRule): pass
class Cgc(PercentSizeRule): pass
class Cgcw(PercentSizeRule): pass
class Cgch(PercentSizeRule): pass
_all_gcx = {Gc, Gcw, Gch, Cgc, Cgcw, Cgch}

class RuleMode:
    def __init__(self) -> None:
        self.to_dp = {
            Fill: CFill,
            FillW: CFillW,
            FillH: CFillH,
            Vh: Cvh,
            Vw: Cvw,
            Gc: Cgc,
            Gcw: Cgcw,
            Gch: Cgch
        }
        self.to_idp = {v: k for k, v in self.to_dp.items()}
    
    def dependent(self, size_rule: SizeRule):
        if type(size_rule) in self.to_dp:
            return self.to_dp[type(size_rule)](size_rule.value)
        return size_rule
    def dp(self, size_rule: SizeRule): return self.dependent(size_rule)
    
    def independent(self, size_rule: SizeRule):
        if type(size_rule) in self.to_idp:
            return self.to_idp[type(size_rule)](size_rule.value)
        return size_rule
    def idp(self, size_rule: SizeRule): return self.independent(size_rule)

rule_mode = RuleMode()