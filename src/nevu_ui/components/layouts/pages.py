from warnings import deprecated

@deprecated("Pages is deprecated")
class Pages:
    @deprecated("Pages is deprecated")
    def __init__(self, deprecated = True):
        raise DeprecationWarning("Pages is deprecated")