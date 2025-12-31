import json
import time
from enum import StrEnum
from typing import Any

from nevu_ui.core.classes import ConfigType
from nevu_ui.struct import check
from nevu_ui.struct import standart_config
from nevu_ui.style import default_style, Style

class ApplierBuffer:
    def __init__(self) -> None:
        self.lazy_init: dict = {}
        self.final_init: dict = {}

styles_buffer = None
colors_buffer = None
colorthemes_buffer = None

def regen_buffers():
    global styles_buffer
    global colors_buffer
    global colorthemes_buffer
    styles_buffer = ApplierBuffer()
    colors_buffer = ApplierBuffer()
    colorthemes_buffer = ApplierBuffer()

#!WARNING:
#!DO NOT change order.
PROCESSING_ORDER = {"colors", "colorthemes", "styles", "window", "animations", "generated"}

def _apply_config(config: dict):
    veryold_time = time.time()
    print("First stage - base validation...")
    check(config)
    print("Second stage - apply config...")
    old_time = time.time()  
    regen_buffers()
    for key in PROCESSING_ORDER:
        if key not in config: continue
        print(f"Applying {key}...")
        substruct = config[key]
        if not structure_validators.get(key, None):
            print("Not implemented.. yet, skipping..."); continue
        
        substruct_validators = structure_validators[key]
        is_any = Any in substruct_validators.keys()
        result, adds = _validate_substruct(key, is_any, substruct, substruct_validators)
        if not result and adds:
            print(f"During {key} validation occured errors:")
            raise ValueError("\n".join(adds))
        else:
            print(f"{key} is valid...")
            attr = transform_to_basic_config[key]
            strategy, convert_func = strategies.get(key, (None, None))
            if strategy is None and convert_func is None:
                raise ValueError(f"CRITICAL: Invalid strategy for: {key}")
            match strategy:
                case ApplierStrategy.CollectDict: getattr(standart_config, attr, {}).update(substruct)
                case ApplierStrategy.CollectList: getattr(standart_config, attr, []).extend(list(substruct.values()))
                case ApplierStrategy.AddObjectDict: getattr(standart_config, attr, {}).update(convert_func())
            print(f"...{key} is applied to {attr}")
    print("Config applied.", end=" ")
    print(f"time: {(time.time() - old_time)*1000:.2f} ms", end=", ")
    print(f"total time: {(time.time() - veryold_time)*1000:.2f} ms")

def lazy_cycle(buffer: ApplierBuffer):
    first_start = True
    oldlen = float('inf')
    next_pop = []
    while first_start or oldlen > len(buffer.lazy_init):
        if first_start:
            oldlen = float('inf')
            first_start = False
        else: oldlen = len(buffer.lazy_init)
        for popname in next_pop:
            buffer.lazy_init.pop(popname)
            next_pop = []
        for name, value in buffer.lazy_init.items():
            if isinstance(value, dict):
                extend_name = value.get("extends")
                if buffer.final_init.get(extend_name):
                    next_pop.append(name)
                    value.pop("extends")
                    extend_copy: dict = buffer.final_init[extend_name].copy()
                    extend_copy |= value
                    buffer.final_init[name] = extend_copy
            elif isinstance(value, str):
                if buffer.final_init.get(value):
                    next_pop.append(name)
                    buffer.final_init[name] = buffer.final_init[value]
    if buffer.lazy_init:
        remaining = ", ".join(buffer.lazy_init.keys())
        raise ValueError(f"Could not resolve style dependencies. Check for circular dependencies or missing styles: {remaining}")

def _get_styles_from_verified_dict(styles_dict):
    return {name: Style(**value) for name, value in styles_dict.items()}

#! Convertors !#
def _style_convert_func():
    assert styles_buffer
    lazy_cycle(styles_buffer)
    return _get_styles_from_verified_dict(styles_buffer.final_init)
def _color_convert_func():
    assert colors_buffer
    lazy_cycle(colors_buffer)
    return colors_buffer.final_init

def _validate_substruct(key, is_any, substruct, validators):
    error_batch = []
    for name in substruct:
        item = substruct[name]
        if is_any: item_validator = lambda value: validators[Any](key=name, value=value)
        else: item_validator = validators[name]
        result, msg = item_validator(item)
        if not result:
            error_batch.append(f"({name}): {msg}")
    
    return (False, error_batch) if error_batch else (True, "All items are valid")

#! Checkers !#
def skip(): return True, "skipped, no need to validate"

def check_list_int(item, min):
    for i in item:
        if not isinstance(i, int):
            return False, f"{i} in {item} is not int"
        if i < min:
            return False, f"{i} in {item} is less than {min}"
    return True, f"{item} is list of ints"

def check_int(item, min = None, max = None):
    if not isinstance(item, int):
        return False, f"{item} is not int"
    elif min and item < min:
        return False, f"{item} is less than {min}"
    elif max and item > max:
        return False, f"{item} is more than {max}"
    return True, f"{item} is int"

def check_in_item(item, list):
    result = item in list
    text = f"{item} is in {list}" if result else f"{item} is not in {list}"
    return result, text

def check_contains_in(item, list):
    item = set(item)
    for i in item:
        if i not in list:
            return False, f"{i} from {item} is not in {list}"
    return True, f"{item} is fully in {list}"

def check_color(key, value):
    assert colors_buffer
    if converted_value := _is_color_convertable(value):
        value = converted_value
    if _is_color_value(value):
        colors_buffer.final_init[key] = tuple(value)
        return True, f"{value} is a valid color"
    if isinstance(value, (str, dict)):
        colors_buffer.lazy_init[key] = value
        return True, f"Added {key} to lazy init"
    return False, f"Invalid format for color '{key}'"

def check_style(key, value):
    assert styles_buffer
    is_lazy = False
    for param, _val in value.items():
        param = param.lower().replace("_", "").strip()
        result = default_style.parameters_dict.get(param)
        
        if not result and param != "extends":
            return False, f"{param} is not in Style parameters"
        elif param == "extends":
            is_lazy = True
            continue
        
        param_name, validator = result #type: ignore
        if not validator(_val)[0]: return False, f"{_val} is not valid for {param}"
        
    if not is_lazy: styles_buffer.final_init[key] = value
    else: styles_buffer.lazy_init[key] = value
        
    return True, f"{value} is valid for {key}"
    
def _is_color_value(value):
    if not isinstance(value, (list, tuple)): return False
    if len(value) not in (3, 4): return False
    return not any(not isinstance(i, int) or not (0 <= i <= 255) for i in value)

def _is_color_convertable(value):
    if not isinstance(value, str): return None
    if value.count(",") > 0:
        try:
            value = tuple(map(int, value.split(",")))
        except Exception: return None
        else: return value
    return None

#! Helpers !#
class ApplierStrategy(StrEnum):
    CollectDict = "collect_dict"
    CollectList = "collect_list"
    AddObjectDict = "create_style"

structure_validators = {
    "window": {
        "title": lambda item: skip(),
        "size": lambda item: check_list_int(item, min = 1),
        "display": lambda item: check_in_item(item, list = ConfigType.Window.Display),
        "utils": lambda item: check_contains_in(item, list = ConfigType.Window.Utils.All),
        "fps": lambda item: check_int(item, min = 1),
        "resizable": lambda item: check_in_item(item, list = [True, False]),
        "ratio": lambda item: check_list_int(item, min = 1),
    },
    
    "styles": {Any: check_style},
    "colors": {Any: check_color},
}
    
strategies = {
    "window": (ApplierStrategy.CollectDict, None),
    "styles": (ApplierStrategy.AddObjectDict, _style_convert_func),
    "colors": (ApplierStrategy.AddObjectDict, _color_convert_func), #Warning: pseudo custom object, actually its just tuple
}

transform_to_basic_config = {
    "window": "win_config",
    "styles": "styles",
    "animations": "animations",
    "colors": "colors",
}

#! Global functions
def apply_config(file_name: str): _apply_config(json.load(open(file_name, "r")))