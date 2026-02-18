from warnings import deprecated

from nevu_ui.components.layouts import Pages

@deprecated("Gallery_Pages is deprecated")
class Gallery_Pages(Pages):
    @deprecated("Gallery_Pages is deprecated")
    def __init__(self, deprecated = True):
        raise DeprecationWarning("Gallery_Pages is deprecated")