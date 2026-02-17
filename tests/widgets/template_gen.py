from typing import TypedDict, NotRequired, get_args, get_origin, Any, Callable, Union
import typing
from typing import TypedDict, NotRequired
from nevu_ui.core.classes import Events
from nevu_ui import Style, TupleColorRole
from nevu_ui.overlay.tooltip import Tooltip
from nevu_ui.color import SubThemeRole
from nevu_ui.nevuobj.typehints import NevuObjectKwargs
from nevu_ui.color import PairColorRole
class Kwargs:
    function: NotRequired[Callable | None]
    on_toogle: NotRequired[Callable | None]
    toogled: NotRequired[bool]
    active: NotRequired[bool]
    active_rect_factor: NotRequired[Union[float, int]]
    active_factor: NotRequired[Union[float, int]]
def format_type(type_hint) -> str:
    """Рекурсивно превращает типы в строку с использованием |"""
    
    # Если это NoneType
    if type_hint is type(None):
        return "None"

    origin = get_origin(type_hint)
    args = get_args(type_hint)

    # Если это Union (например, Union[int, str] или int | str)
    if origin is Union:
        # Рекурсивно обрабатываем каждый аргумент внутри Union
        formatted_args = [format_type(arg) for arg in args]
        # Собираем через палку
        return " | ".join(formatted_args)

    # Если это обычный класс (int, str, CustomClass)
    if hasattr(type_hint, "__name__"):
        return type_hint.__name__

    # Если это что-то другое (например, List[int]), просто возвращаем как есть
    return str(type_hint).replace("typing.", "")

# --- ГЕНЕРАТОР КЛАССА ---
def print_dataclass_code(typed_dict_cls, new_cls_name="Template"):
    print("@dataclass")
    print(f"class {new_cls_name}:")
    
    annotations = typed_dict_cls.__annotations__
    if not annotations:
        print("    pass")
        return

    for name, type_hint in annotations.items():
        # Проверяем NotRequired
        if get_origin(type_hint) is NotRequired:
            # Получаем внутренний тип (например, int внутри NotRequired[int])
            inner_type = get_args(type_hint)[0]
            
            # Форматируем тип нашей функцией
            type_str = format_type(inner_type)
            
            # Поскольку это NotRequired, в датаклассе это поле может быть None
            # Добавляем | None, если его там еще нет
            if "None" not in type_str:
                type_str += " | None"
            
            print(f"    {name}: {type_str} = None")
        else:
            # Обязательные поля
            type_str = format_type(type_hint)
            print(f"    {name}: {type_str}")

# --- Запуск генератора ---
print("-" * 30)
print("СКОПИРУЙТЕ КОД НИЖЕ В СВОЙ ПРОЕКТ:")
print("-" * 30)
print("from dataclasses import dataclass")
print("")
print_dataclass_code(Kwargs, "ProgressBarTemplate")
print("-" * 30)