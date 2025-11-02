from nevu_ui.struct import Struct, SubStruct
from nevu_ui.core_types import ConfigType
from nevu_ui.struct import Validator
from typing import Any
from nevu_ui.struct import standart_config
from enum import StrEnum
import json

class Applier:
    @staticmethod
    def apply_config(config: Struct):
        print("First stage - base validation...")
        Validator.check(config)
        print("Second stage - apply config...")
        for key in config.config:
            print(f"Applying {key}...")
            substruct = config.open(key, True)
            if structure_validators.get(key, 1) is 1:
                print("Not implemented yet, skipping...")
                continue
            substruct_validators = structure_validators.open(key)
            is_any = False
            result, errors = Applier._validate_substruct(is_any, substruct, substruct_validators)
            if not result and errors:
                print(f"During {key} validation occured errors:")
                raise ValueError("\n".join(errors))
            else:
                print(f"{key} is valid...")
                attr = transform_to_basic_config[key]
                assert isinstance(substruct, SubStruct)
                getattr(standart_config, attr, {}).update(substruct.config)
                print(f"...{key} is applied to {attr}")
            
    @staticmethod
    def _validate_substruct(is_any, substruct, validators):
        error_batch = []
        for name in substruct.config:
            item = substruct.config[name]
            if is_any:
                item_validator = validators.config[Any]
            else:
                item_validator = validators.config[name]
            result, msg = item_validator(item)
            if not result:
                error_batch.append(f"({name}): {msg}")
        
        return (False, error_batch) if error_batch else (True, None)
    
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
    def check_color(item):
        if isinstance(item, str):
            if item[0].strip() == "#":
                return False, "HEX colors are not supported yet"
            try:
                item = list(map(int, item.split(",")))
            except Exception as e:
                return False, f"Can't convert {item} to list, {e}"

        if len(item) not in (3, 4):
            return False, "RGBLike color must have 3 or 4 values"

        for i in item:
            result, _ = Applier.check_int(i, min = 0, max = 255)
            if not result:
                return False, f"{i} in {item} is not int"
        return True, f"{item} is a color"
    
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
    #"colors": {
    #    Any: lambda item: Applier.skip()
    #}
})

transform_to_basic_config = {
    "window": "win_config",
    "styles": "styles",
    "animations": "animations",
    "colors": "colors"
}

def apply_config(file_name: str):
    Applier.apply_config(Struct(json.load(open(file_name, "r"))))

if __name__ == "__main__":
    Applier.apply_config(Struct(json.load(open("structure_test.json", "r"))))
    print(standart_config.win_config)