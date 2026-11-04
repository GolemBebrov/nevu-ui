from dataclasses import dataclass
from enum import StrEnum


class _RoleAncestor(StrEnum): ...


class SubThemeRole(_RoleAncestor):
    Primary = "primary"
    Secondary = "secondary"
    Tertiary = "tertiary"
    Error = "error"


class PairColorRole(_RoleAncestor):
    Background = "background"
    Surface = "surface"
    SurfaceVariant = "surface_variant"
    InverseSurface = "inverse_surface"


class TupleColorRole(_RoleAncestor):
    Outline = "outline"
    InversePrimary = "inverse_primary"


@dataclass
class ColorPair:
    color: tuple
    on_color: tuple


@dataclass
class ColorSubTheme:
    color: tuple
    on_color: tuple
    container: tuple
    on_container: tuple


@dataclass
class ColorTheme:
    primary: ColorSubTheme
    secondary: ColorSubTheme
    tertiary: ColorSubTheme
    error: ColorSubTheme
    background: ColorPair
    surface: ColorPair
    surface_variant: ColorPair
    outline: tuple
    inverse_surface: ColorPair
    inverse_primary: tuple
    name: str = "Unnamed"

    def get_subtheme(self, role: SubThemeRole) -> ColorSubTheme:
        assert isinstance(role, SubThemeRole), (
            f"role must be SubThemeRole, {role} given"
        )
        return getattr(self, role.value)

    def get_pair(self, role: PairColorRole) -> ColorPair:
        assert isinstance(role, PairColorRole), (
            f"role must be PairColorRole, {role} given"
        )
        return getattr(self, role.value)

    def get_tuple(self, role: TupleColorRole) -> tuple:
        assert isinstance(role, TupleColorRole), (
            f"role must be TupleColorRole, {role} given"
        )
        return getattr(self, role.value)

    def get(self, any_role) -> ColorSubTheme | ColorPair | tuple:
        assert isinstance(any_role, _RoleAncestor), (
            f"role must be _RoleAncestor, {any_role} given"
        )
        return getattr(self, any_role.value)

from .presets import ColorThemeLibrary
__all__ = [
    "SubThemeRole",
    "PairColorRole",
    "TupleColorRole",
    "ColorPair",
    "ColorSubTheme",
    "ColorTheme",
    "ColorThemeLibrary",
]
