from nevu_ui.fast.nvvector2 import NvVector2

class Convertor:
    @staticmethod
    def convert(item, to_type):
        if to_type is NvVector2:
            return Convertor._to_vector2(item)
        if to_type is tuple or to_type is list:
            return Convertor._to_iterable(item, to_type)
        if to_type is int:
            return Convertor.to_int(item)
        if to_type is float:
            return Convertor.to_float(item)
        return item

    @staticmethod
    def to_int(item):
        if isinstance(item, int):
            return item
        if isinstance(item, float):
            return int(item)
        if isinstance(item, NvVector2):
            return int(item.length)
        raise ValueError(f"Can't convert {type(item).__name__} to int")

    @staticmethod
    def to_float(item):
        if isinstance(item, float):
            return item
        if isinstance(item, int):
            return float(item)
        if isinstance(item, NvVector2):
            return float(item.length)
        raise ValueError(f"Can't convert {type(item).__name__} to float")

    @staticmethod
    def _to_vector2(item):
        if isinstance(item, NvVector2):
            return item
        if isinstance(item, (list, tuple)) and len(item) == 2:
            return NvVector2(item)
        raise ValueError(f"Can't convert {type(item).__name__} to Vector2")

    @staticmethod
    def _to_iterable(item, needed_type):
        if isinstance(item, needed_type):
            return item
        if isinstance(item, (list, tuple)):
            return needed_type(item)
        
        raise ValueError(f"Can't convert {type(item).__name__} to {needed_type.__name__}")