import json
from nevu_ui.struct import Struct, SubStruct, SubItem
from typing import Any
import time 
from typing import overload
class Validator:
    debug_char = "-"
    debug_char_count = 3
    err_msg_invalid_item = "Item {item} is not valid"
    err_msg_created = "Item {item} is already created"
    err_msg_invalid_type = "Item {item} has invalid type: {typeitem.__name__}, expected: {valid_item}"
    msg_valid = "items are valid"
    @staticmethod
    def dprint(*args, **kwargs):
        print(Validator.debug_char * Validator.debug_char_count, *args, **kwargs)
    @staticmethod
    def ddprint(*args, **kwargs):
        print(Validator.debug_char * Validator.debug_char_count, *args, Validator.debug_char * Validator.debug_char_count, **kwargs)
        
    @overload
    @staticmethod
    def check(config: dict): ...
    
    @overload
    @staticmethod
    def check(config: Struct): ...
    
    @staticmethod
    def check(config: dict | Struct):
        struct = Struct(config) if isinstance(config, dict) else config
        err_log = []
        old_time = time.time()
        Validator.ddprint("Started validation")
        Validator.dprint(f"groups to valid: {", ".join(struct.config.keys())}")
        for num, key in enumerate(struct.config.keys()):
            if key in Validator.valid_dict:
                Validator.dprint(f"Process: {num + 1}/{len(struct.config.keys())}, group: {key}", end = "")
                try:
                    is_valid, err_msg = Validator.valid_dict[key](struct.open(key, copy_dict=True))
                except Exception as e:
                    is_valid, err_msg = Validator.valid_dict[key](struct.open(key, copy_dict=True)), "Unknown error"

                if is_valid:
                    print(" - OK")
                else:
                    print(" - ERROR")
                    err_log.append(f"{key}: {err_msg}")
            else:
                Validator.dprint(f"Process: {num + 1}/{len(struct.config.keys())}, group: {key}", end = "")
                print(" - INVALID")
                
        Validator.ddprint("Finished validation")
        Validator.ddprint(f"Time: {(time.time() - old_time)*1000:.2f} ms")
        if err_log:
            Validator.ddprint("Errors have been occured during validation, raising exception...")
            raise ValueError(f"Validation errors:\n{"\n".join(err_log)}")
        
    @staticmethod
    def _validate_items(items: dict, valid_items: dict):
        v = Validator
        err_batch = []
        def _format_expected_types(expected):
            default_str = "expected "
            if isinstance(expected, (tuple, list)):
                return default_str + " or ".join(t.__name__ for t in expected)
            else:
                return default_str + expected.__name__
        _valid_keys = []
        _simple_mode = Any in valid_items and len(valid_items) == 1
        for item in items:
            if _simple_mode:
                if not isinstance(items[item], valid_items[Any]):
                    err_batch.append(f"{item}: {expected_type_str} but get {actual_type_str} '{items[item]}'")
                _valid_keys.append(item)
                continue
            if item not in valid_items.keys():
                if Any in valid_items:
                    if not isinstance(item, valid_items[Any]):
                        err_batch.append(f"{item}: {v.err_msg_invalid_type.format(item = item, valid_items = valid_items)}")
                    continue
                err_batch.append(f"{item}: {v.err_msg_invalid_item.format(item = item)}")
            elif item in _valid_keys:
                err_batch.append(f"{item}: {v.err_msg_created.format(item = item)}")
            else:
                _valid_keys.append(item)
        
        if not _simple_mode:
            for item in _valid_keys:
                if valid_items[item] is Any: continue
                if not isinstance(items[item], valid_items[item]):
                    err_batch.append(f"{item}: {_format_expected_types(valid_items[item]) + f" but get {type(items[item]).__name__} '{items[item]}'"}")
        if err_batch:
            return None, "\n"+ "\n".join(err_batch)
        return _valid_keys, v.msg_valid
    
    @staticmethod 
    def _validate_group(valid_items: dict, substruct: SubStruct):
        valid_items = valid_items
        items, msg = Validator._validate_items(substruct.config, valid_items)
        return True if items else (False, msg)
    @staticmethod
    def validate_window(window: SubStruct):
        valid_items = {
            "title": str,
            "size": (list, tuple),
            "display": str,
            "utils": list,
            "fps": int,
            "resizable": bool,
            "ratio": (list, tuple)
        }
        return Validator._validate_group(valid_items, window)
        
    @staticmethod
    def validate_animations(substruct: SubStruct):
        valid_items = {
            Any: dict,
        }
        return Validator._validate_group(valid_items, substruct)
    
    @staticmethod
    def validate_colors(substruct: SubStruct):
        valid_items = {
            Any: (list, tuple, str),
        }
        return Validator._validate_group(valid_items, substruct)
    
    @staticmethod
    def validate_styles(substruct: SubStruct):
        valid_items = {
            Any: (dict, str),
        }
        return Validator._validate_group(valid_items, substruct)
    
    @staticmethod
    def validate_generated(generated: SubItem):
        if isinstance(generated.value, bool):
            return True, Validator.msg_valid
        return False, Validator.err_msg_invalid_type.format(item = generated.name, typeitem = type(generated.value), valid_item = bool.__name__)
    
    valid_dict = {
        "window": validate_window,
        "animations": validate_animations,
        "colors": validate_colors,
        "styles": validate_styles,
        "generated": validate_generated
    }
    
    @staticmethod
    def add_validator(key: str, func):
        Validator.valid_dict[key] = func
    
    @staticmethod
    def remove_validator(key: str):
        Validator.valid_dict.pop(key)
        
if __name__ == "__main__":
    with open("structure_test.json", "r") as f:
        jsa = json.load(f)
    te_dict = Struct(jsa)

    a = Validator.check(te_dict.config)