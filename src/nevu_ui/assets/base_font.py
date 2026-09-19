from pathlib import Path

_DIR = Path(__file__).parent

INTER_REGULAR_FONT_PATH = str(_DIR / "inter.ttf")
INTER_ITALIC_FONT_PATH = str(_DIR / "inter_italic.ttf")
INTER_BOLD_FONT_PATH = str(_DIR / "inter_bold.ttf")
INTER_SEMIBOLD_FONT_PATH = str(_DIR / "inter_semibold.ttf")

JETBRAINS_MONO_REGULAR_FONT_PATH = str(_DIR / "mono.ttf")
JETBRAINS_MONO_BOLD_FONT_PATH = str(_DIR / "mono_bold.ttf")
JETBRAINS_MONO_ITALIC_FONT_PATH = str(_DIR / "mono_italic.ttf")
JETBRAINS_MONO_SEMIBOLD_FONT_PATH = str(_DIR / "mono_semibold.ttf")

class FontLibrary:
    InterRegular = INTER_REGULAR_FONT_PATH
    InterItalic = INTER_ITALIC_FONT_PATH
    InterBold = INTER_BOLD_FONT_PATH
    InterSemibold = INTER_SEMIBOLD_FONT_PATH

    JetBrainsMonoRegular = JETBRAINS_MONO_REGULAR_FONT_PATH
    JetBrainsMonoBold = JETBRAINS_MONO_BOLD_FONT_PATH
    JetBrainsMonoItalic = JETBRAINS_MONO_ITALIC_FONT_PATH
    JetBrainsMonoSemibold = JETBRAINS_MONO_SEMIBOLD_FONT_PATH
