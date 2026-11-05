from pathlib import Path

_DIR = Path(__file__).parent
_STANDARD_DIR = _DIR / "standard"
_GLASSY_DIR = _DIR / "glassy"

STANDARD_BORDER = _STANDARD_DIR / "border.frag"
STANDARD_LINE = _STANDARD_DIR / "line.frag"
STANDARD_SDF = _STANDARD_DIR / "sdf.frag"
STANDARD_GRADIENT = _STANDARD_DIR / "gradient.frag"
GLASSY_BORDER = _GLASSY_DIR / "border.frag"
GLASSY_SDF = _GLASSY_DIR / "sdf.frag"
BASE_VERTEX = _DIR / "base.vert"


class ShaderLibrary:
    StandardBorder = STANDARD_BORDER
    StandardLine = STANDARD_LINE
    StandardSDF = STANDARD_SDF
    GlassyBorder = GLASSY_BORDER
    GlassySDF = GLASSY_SDF
    StandardGradient = STANDARD_GRADIENT
    BaseVertex = BASE_VERTEX

__all__ = ["ShaderLibrary"]
