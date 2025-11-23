from nevu_ui.struct import Struct, SubStruct
from nevu_ui.core_types import ConfigType
from nevu_ui.struct import Validator
from nevu_ui.style import default_style, Style
from typing import Any
from nevu_ui.struct import standart_config
from enum import StrEnum
import json
from nevu_ui.color import Color
from dataclasses import dataclass
import time

class ApplierBuffer:
    def __init__(self) -> None:
        self.lazy_init: dict = {}
        self.final_init: dict = {}

styles_buffer = None
colors_buffer = None
colorthemes_buffer = None

# ===== WARNING! =====
# Do NOT change order.
PROCESSING_ORDER = {"colors", "colorthemes", "styles", "window", "animations", "generated"}

def assert_buffers(): #Unused
    assert styles_buffer, "styles_buffer is not initialized"
    assert colors_buffer, "colors_buffer is not initialized"
    assert colorthemes_buffer, "colorthemes_buffer is not initialized"

class Applier:
    @staticmethod
    def apply_config(config: Struct):
        veryold_time = time.time()
        print("First stage - base validation...")
        Validator.check(config)
        print("Second stage - apply config...")
        old_time = time.time()  
        Applier.regen_buffers()
        for key in PROCESSING_ORDER:
            if key not in config.config:
                continue
            print(f"Applying {key}...")
            substruct = config.open(key, True)
            if structure_validators.get(key, 1) == 1:
                print("Not implemented yet, skipping...")
                continue
            substruct_validators = structure_validators.open(key)
            is_any = substruct_validators.config.get(Any)
            result, adds = Applier._validate_substruct(key, is_any, substruct, substruct_validators)
            if not result and adds:
                print(f"During {key} validation occured errors:")
                raise ValueError("\n".join(adds))
            else:
                print(f"{key} is valid...")
                attr = transform_to_basic_config[key]
                assert isinstance(substruct, SubStruct)
                strategy, stg_type = strategies.get(key, ApplierStrategy.CollectDict)
                if strategy == ApplierStrategy.CollectDict:
                    getattr(standart_config, attr, {}).update(substruct.config)
                elif strategy == ApplierStrategy.CollectList:
                    lst = list(substruct.config.values())
                    getattr(standart_config, attr, []).extend(lst)
                elif strategy == ApplierStrategy.AddObjectDict:
                    convert_func = stype_to_func[stg_type]
                    objects = convert_func()
                    getattr(standart_config, attr, {}).update(objects)
                print(f"...{key} is applied to {attr}")
        print("Config applied.", end=" ")
        print(f"time: {(time.time() - old_time)*1000:.2f} ms", end=", ")
        print(f"total time: {(time.time() - veryold_time)*1000:.2f} ms")
    
    @staticmethod
    def lazy_cycle(buffer: ApplierBuffer):
        first_start = True
        oldlen = float('inf')
        next_pop = []
        while first_start or oldlen > len(buffer.lazy_init):
            if first_start:
                oldlen = float('inf')
                first_start = False
            else:
                oldlen = len(buffer.lazy_init)
            for popname in next_pop:
                buffer.lazy_init.pop(popname)
                #print(f"Removed {popname}")
                next_pop = []
            for name, value in buffer.lazy_init.items():
                value: dict | str
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
    
    @staticmethod
    def _get_styles_from_verified_dict(styles_dict):
        return {name: Style(**value) for name, value in styles_dict.items()}
    
    @staticmethod
    def _style_convert_func():
        assert styles_buffer
        Applier.lazy_cycle(styles_buffer)
        return Applier._get_styles_from_verified_dict(styles_buffer.final_init)

    @staticmethod
    def _color_convert_func():
        assert colors_buffer
        Applier.lazy_cycle(colors_buffer)
        return colors_buffer.final_init
    
    @staticmethod
    def regen_buffers():
        global styles_buffer
        global colors_buffer
        global colorthemes_buffer
        styles_buffer = ApplierBuffer()
        colors_buffer = ApplierBuffer()
        colorthemes_buffer = ApplierBuffer()
        
    @staticmethod
    def _validate_substruct(key, is_any, substruct, validators):
        error_batch = []
        for name in substruct.config:
            item = substruct.config[name]
            
            if is_any:
                item_validator = lambda value: validators.config[Any](key=name, value=value)
            else:
                item_validator = validators.config[name]
                
            result, msg = item_validator(item)

            if not result:
                error_batch.append(f"({name}): {msg}")
        
        return (False, error_batch) if error_batch else (True, "All items are valid")
    
    @staticmethod
    def skip():
        return True, "skipped, no need to validate"
    
    @staticmethod
    def check_list_int(item, min):
        for i in item:
            if not isinstance(i, int):
                return False, f"{i} in {item} is not int"
            if i < min:
                return False, f"{i} in {item} is less than {min}"
        return True, f"{item} is list of ints"
    
    @staticmethod
    def check_int(item, min = None, max = None):
        if not isinstance(item, int):
            return False, f"{item} is not int"
        elif min and item < min:
            return False, f"{item} is less than {min}"
        elif max and item > max:
            return False, f"{item} is more than {max}"
        return True, f"{item} is int"
    
    @staticmethod
    def check_in_item(item, list):
        result = item in list
        text = f"{item} is in {list}" if result else f"{item} is not in {list}"
        return result, text
    
    @staticmethod
    def check_contains_in(item, list):
        item = set(item)
        for i in item:
            if i not in list:
                return False, f"{i} from {item} is not in {list}"
        return True, f"{item} is fully in {list}"
    
    @staticmethod
    def check_color(key, value):
        assert colors_buffer
        if converted_value := Applier._is_color_convertable(value):
            value = converted_value
        if Applier._is_color_value(value):
            colors_buffer.final_init[key] = tuple(value)
            return True, f"{value} is a valid color"
        if isinstance(value, (str, dict)):
            colors_buffer.lazy_init[key] = value
            return True, f"Added {key} to lazy init"

        return False, f"Invalid format for color '{key}'"
    
    @staticmethod
    def validate_style(key, value):
        assert styles_buffer
        exit_dest = 0 #0 - full, 1 - lazy
        for param, _val in value.items():
            param = param.lower().replace("_", "").strip()
            result = default_style.parameters_dict.get(param)
            if not result and param != "extends":
                return False, f"{param} is not in Style parameters"
            elif param == "extends":
                exit_dest = 1
                continue
            
            param_name, validator = result
            
            if not validator(_val)[0]:
                return False, f"{_val} is not valid for {param}"

            #print(f"{param}, {_val}, {validator(_val)}")

        if exit_dest == 0:
            styles_buffer.final_init[key] = value
        elif exit_dest == 1:
            styles_buffer.lazy_init[key] = value
            
        return True, f"{value} is valid for {key}"
        
    @staticmethod
    def _is_color_value(value):
        if not isinstance(value, (list, tuple)): return False
        if len(value) not in (3, 4): return False
        return not any(not isinstance(i, int) or not (0 <= i <= 255) for i in value)

    @staticmethod
    def _is_color_convertable(value):
        if not isinstance(value, str): return None
        if value.count(",") > 0:
            try:
                value = tuple(map(int, value.split(",")))
            except Exception:
                return None
            else:
                return value
        return None

class ApplierStrategy(StrEnum):
    CollectDict = "collect_dict"
    CollectList = "collect_list"
    AddObjectDict = "create_style"

structure_validators = Struct({
    "window": {
        "title": lambda item: Applier.skip(),
        "size": lambda item: Applier.check_list_int(item, min = 1),
        "display": lambda item: Applier.check_in_item(item, list = ConfigType.Window.Display),
        "utils": lambda item: Applier.check_contains_in(item, list = ConfigType.Window.Utils.All),
        "fps": lambda item: Applier.check_int(item, min = 1),
        "resizable": lambda item: Applier.check_in_item(item, list = [True, False]),
        "ratio": lambda item: Applier.check_list_int(item, min = 1),
    },
    
    "styles": {
        Any: Applier.validate_style
    },
    
    "colors": {
        Any: Applier.check_color
    },
    
})

class StgType(StrEnum):
    Null = "null"
    Style = "style"
    Color = "color"

strategies = {
    "window": (ApplierStrategy.CollectDict, StgType.Null),
    "styles": (ApplierStrategy.AddObjectDict, StgType.Style),
    "colors": (ApplierStrategy.AddObjectDict, StgType.Color), #Warning: pseudo custom object, actually its just tuple
}

stype_to_func = {
    "style": Applier._style_convert_func,
    "color": Applier._color_convert_func
}

transform_to_basic_config = {
    "window": "win_config",
    "styles": "styles",
    "animations": "animations",
    "colors": "colors",
}

def apply_config(file_name: str):
    Applier.apply_config(Struct(json.load(open(file_name, "r"))))

if __name__ == "__main__":
    Applier.apply_config(Struct(json.load(open("structure_test.json", "r"))))
    print(standart_config.win_config)
    print(standart_config.styles)
    print(standart_config.colors)