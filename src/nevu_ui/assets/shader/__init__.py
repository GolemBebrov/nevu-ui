from pathlib import Path

_DIR = Path(__file__).parent
_STANDARD_DIR = _DIR / "standard"
_GLASSY_DIR = _DIR / "glassy"

STANDARD_BORDER = _STANDARD_DIR / "border.frag"
STANDARD_LINE = _STANDARD_DIR / "line.frag"
STANDARD_SDF = _STANDARD_DIR / "sdf.frag"
GLASSY_BORDER = _GLASSY_DIR / "border.frag"
GLASSY_SDF = _GLASSY_DIR / "sdf.frag"
BASE_VERTEX = _DIR / "base.vert"
GRADIENT = _DIR / "gradient.frag"

class ShaderLibrary:
    StandardBorder = STANDARD_BORDER.read_text()
    StandardLine = STANDARD_LINE.read_text()
    StandardSDF = STANDARD_SDF.read_text()
    GlassyBorder = GLASSY_BORDER.read_text()
    GlassySDF = GLASSY_SDF.read_text()
    Gradient = GRADIENT.read_text()
    BaseVertex = BASE_VERTEX.read_text()

__all__ = ["ShaderLibrary"]
