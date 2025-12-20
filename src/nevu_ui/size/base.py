class SizeRule:
    __slots__ = ('value',)
    def __init__(self, value: int | float) -> None:
        self.value = value
class PercentSizeRule(SizeRule):
    def __init__(self, value: int | float) -> None:
        if value < 0 or value > 100:
            raise ValueError("percentage must be between 0 and 100")
        self.value = value

class SizeUnit:
    __slots__ = ('_supported_types', '_size_rule')
    def __init__(self, size_rule, supported_types = None) -> None:
        self._supported_types = supported_types or (int | float)
        self._size_rule = size_rule
    def _create_rule(self, other_value):
        if isinstance(other_value, self._supported_types):
            return self._size_rule(other_value)
        return NotImplemented
    def __rmul__(self, other_value):
        return self._create_rule(other_value)
    def __mul__(self, other_value):
        return self._create_rule(other_value)