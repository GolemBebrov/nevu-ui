from nevu_ui.core.size.base import _PercentSizeRule, _SizeRule


class Px(_SizeRule):
    pass


class Fill(_PercentSizeRule):
    pass


class FillW(_PercentSizeRule):
    pass


class FillH(_PercentSizeRule):
    pass


class CFill(_PercentSizeRule):
    pass


class CFillW(_PercentSizeRule):
    pass


class CFillH(_PercentSizeRule):
    pass


_all_fillx = {Fill, FillW, FillH, CFill, CFillW, CFillH}


class Vh(_PercentSizeRule):
    pass


class Vw(_PercentSizeRule):
    pass


class Cvh(_PercentSizeRule):
    pass


class Cvw(_PercentSizeRule):
    pass


_all_vx = {Vh, Vw, Cvh, Cvw}


class Gc(_PercentSizeRule):
    pass


class Gcw(_PercentSizeRule):
    pass


class Gch(_PercentSizeRule):
    pass


class Cgc(_PercentSizeRule):
    pass


class Cgcw(_PercentSizeRule):
    pass


class Cgch(_PercentSizeRule):
    pass


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
