from dataclasses import dataclass
from enum import StrEnum

class _RoleAncestor(StrEnum):
    pass

class SubThemeRole(_RoleAncestor):
    PRIMARY = "primary"
    SECONDARY = "secondary"
    TERTIARY = "tertiary"
    ERROR = "error"

class PairColorRole(_RoleAncestor):
    BACKGROUND = "background"
    SURFACE = "surface"
    SURFACE_VARIANT = "surface_variant"
    INVERSE_SURFACE = "inverse_surface"

class TupleColorRole(_RoleAncestor):
    OUTLINE = "outline"
    INVERSE_PRIMARY = "inverse_primary"
@dataclass
class ColorPair:
    """Представляет пару цветов (основной цвет и цвет контента на нем)."""
    color: tuple
    oncolor: tuple

@dataclass
class ColorSubTheme:
    """Представляет часть цветовой схемы, основанную на ролях Material Design 3."""
    color: tuple
    oncolor: tuple
    container: tuple
    oncontainer: tuple

@dataclass
class ColorTheme:
    """
    Представляет полную, структурированную цветовую схему,
    организованную по ролям Material Design 3.
    """
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

    def get_subtheme(self, role: SubThemeRole) -> ColorSubTheme:
        assert isinstance(role, SubThemeRole)
        return getattr(self, role.value)
    
    def get_pair(self, role: PairColorRole) -> ColorPair:
        assert isinstance(role, PairColorRole)
        return getattr(self, role.value)

    def get_tuple(self, role: TupleColorRole) -> tuple:
        assert isinstance(role, TupleColorRole)
        return getattr(self, role.value)
    
    def get(self, any_role) -> ColorSubTheme | ColorPair | tuple:
        assert isinstance(any_role, _RoleAncestor)
        return getattr(self, any_role.value)
