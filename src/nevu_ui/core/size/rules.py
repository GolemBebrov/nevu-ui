from nevu_ui.core.size.base import _PercentSizeRule, _SizeRule, _AutoSizeRule


class Px(_SizeRule): ...

class Fill(_PercentSizeRule): ...
class FillW(_PercentSizeRule): ...
class FillH(_PercentSizeRule): ...
class CFill(_PercentSizeRule): ...
class CFillW(_PercentSizeRule): ...
class CFillH(_PercentSizeRule): ...
_all_fillx = {Fill, FillW, FillH, CFill, CFillW, CFillH}

class Vh(_PercentSizeRule): ...
class Vw(_PercentSizeRule): ...
class Cvh(_PercentSizeRule): ...
class Cvw(_PercentSizeRule): ...
_all_vx = {Vh, Vw, Cvh, Cvw}


class Gc(_PercentSizeRule): ...
class Gcw(_PercentSizeRule): ...
class Gch(_PercentSizeRule): ...
class Cgc(_PercentSizeRule): ...
class Cgcw(_PercentSizeRule): ...
class Cgch(_PercentSizeRule): ...
_all_gcx = {Gc, Gcw, Gch, Cgc, Cgcw, Cgch}

class Auto(_AutoSizeRule): ...

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
            Gch: Cgch,
        }
        self.to_idp = {v: k for k, v in self.to_dp.items()}

    def dependent(self, size_rule: _SizeRule):
        if type(size_rule) in self.to_dp:
            return self.to_dp[type(size_rule)](size_rule.value)
        return size_rule

    def dp(self, size_rule: _SizeRule):
        return self.dependent(size_rule)

    def independent(self, size_rule: _SizeRule):
        if type(size_rule) in self.to_idp:
            return self.to_idp[type(size_rule)](size_rule.value)
        return size_rule

    def idp(self, size_rule: _SizeRule):
        return self.independent(size_rule)


rule_mode = RuleMode()
