class _SizeRule:
    __slots__ = ("value",)
    def __init__(self, value: float) -> None:
        self.value = value

class _PercentSizeRule(_SizeRule):
    def __init__(self, value: float) -> None:
        self.value = value

class _AutoSizeRule(_SizeRule):
    def __init__(self, padding: int | tuple[int, int]) -> None:
        super().__init__(padding)

class _SizeUnit:
    __slots__ = ("_size_rule", "_supported_types")

    def __init__(self, size_rule, supported_types=None) -> None:
        self._supported_types = supported_types or (int | float)
        self._size_rule = size_rule

    def _create_rule(self, other_value):
        if isinstance(other_value, self._supported_types):
            return self._size_rule(other_value)
        return NotImplemented

    def __rmul__(self, other_value: float):
        return self._create_rule(other_value)

    def __mul__(self, other_value: float):
        return self._create_rule(other_value)

    def __rmod__(self, other_value: float):
        return self._create_rule(other_value)

    def __mod__(self, other_value: float):
        return self._create_rule(other_value)

class _AutoSizeUnit(_SizeUnit):
    def __init__(self, size_rule, supported_types=None) -> None:
        super().__init__(size_rule, None)
        self._supported_types = supported_types or (int | float | tuple)
    def __call__(self):
        return self._create_rule(0)
    def __add__(self, other_value: float | tuple[int, int]):
        return self._create_rule(other_value)
    def __radd__(self, other_value: float | tuple[int, int]):
        return self._create_rule(other_value)
    def __rmul__(self, other_value): raise NotImplementedError()
    def __mul__(self, other_value): raise NotImplementedError()
    def __rmod__(self, other_value): raise NotImplementedError()
    def __mod__(self, other_value): raise NotImplementedError()
